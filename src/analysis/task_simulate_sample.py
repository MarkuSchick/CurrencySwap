import json
import pickle

import numpy as np
import pytask
from recombinator.block_bootstrap import stationary_bootstrap
from recombinator.optimal_block_length import optimal_block_length

from src.config import BLD
from src.config import SRC


def generate_historical_one_year_returns(data, config):
    """
    Stack vectors of (all) historical periods starting
    from the introduction of the EURO in 1999 of length
    of 1 year (==trading days) on each other

    Args:
        data (np.array(N,1)): Timeseries of logarithmic EURO/USD returns
        config (dict): dictionary of simulation parameters

    Returns:
        [np.array(trading_days, K)]: Array of K historical series of
        1 year returns of length trading days
    """
    # settings
    trading_days = config["trading_days"]

    # initiate empty container
    simulated_historical_data = []

    # generate sample
    for i_start in range(len(data) - trading_days):
        i_end = i_start + trading_days
        simulated_historical_data.append(data[i_start:i_end].reshape((trading_days, 1)))

    simulated_historical_data = np.concatenate(simulated_historical_data)
    return simulated_historical_data


def _find_optimal_stationary_bootstrap_block_length(y):
    """The first number is the optimal block length for a stationary
    bootstrap, while the second number refers to the optimal block length
    for the circular bootstrap.
    """
    b_star = optimal_block_length(y)
    b_star_sb = b_star[0].b_star_sb
    return b_star_sb


def generate_bootstrapped_one_year_returns(data, config):
    """Uses the stationary bootstrapp method
    to generate bootsstrap_sim_num many vectors
    of 1 year length (==trading days). Optimal (average)
    block length is computed in program

    Args:
        data (np.array(N,1)): Timeseries of logarithmic EURO/USD returns
        config (dict): dictionary of simulation parameters

    Returns:
        [np.array(trading_days, bootsstrap_sim_num)]: Array of bootsstrap_sim_num
        bootstrapped 1 year returns of length trading days
    """

    # settings
    trading_days = config["trading_days"]
    bootsstrap_sim_num = config["bootsstrap_sim_num"]
    np.random.seed(config["simulation_seed"])

    # find optimal block length for stationary bootstrap
    optimal_block_length = _find_optimal_stationary_bootstrap_block_length(data)

    # generate block_bootstrap data
    sim_data = stationary_bootstrap(
        data,
        block_length=optimal_block_length,
        replications=bootsstrap_sim_num,
        sub_sample_length=trading_days,
    )

    return sim_data


specifications = (
    (
        eval(f"generate_{simulation_name}_one_year_returns"),
        BLD / "data" / f"simulated_data_{simulation_name}.pickle",
    )
    for simulation_name in ["historical", "bootstrapped"]
)


@pytask.mark.parametrize("simulation_function, produces", specifications)
@pytask.mark.depends_on(
    {
        "sim_config": SRC / "model_specs" / "simulation_config.json",
        "raw_data": BLD / "historical_data" / "raw_data.pickle",
    }
)
def task_simulate_sample(depends_on, simulation_function, produces):

    # Load locations after each round
    with open(depends_on["raw_data"], "rb") as f:
        raw_data = pickle.load(f)

    # drop first row
    raw_data.dropna(axis="index", inplace=True)
    log_return = raw_data["log_return"].to_numpy()

    # load simulation configurations
    sim_config = json.loads(depends_on["sim_config"].read_text(encoding="utf-8"))

    # run simulations
    simulation_sample = simulation_function(log_return, sim_config)

    with open(produces, "wb") as out_file:
        pickle.dump(simulation_sample, out_file)


if __name__ == "__main__":
    # Evaluate production functions.
    simulation_name = "bootstrapped"
    produces = BLD / "data" / f"simulated_data_{simulation_name}.pickle"

    simulation_function = generate_bootstrapped_one_year_returns

    depends_on = {
        "sim_config": SRC / "model_specs" / "simulation_config.json",
        "raw_data": BLD / "historical_data" / "raw_data.pickle",
    }

    task_simulate_sample(depends_on, simulation_function, produces)