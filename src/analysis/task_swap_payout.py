import pickle

import pytask
import json

from src.analysis.utility import get_total_exchange_rate_change
from src.config import BLD
from src.config import SRC
from src.model_code.swap_contract import payout_currency_swap

def calc_final_payout(total_change, leverage, USD_asset_allocation, scenario_config):
    """[summary]

    Args:
        total_change ([type]): [description]
        swap_config ([type]): [description]
        scenario_config ([type]): [description]

    Returns:
        [type]: [description]
    """
    # load configurations
    scenario_config = json.loads(scenario_config.read_text(encoding="utf-8"))
    

    # calculate payout data
    start_exchange_rate = 1
    final_exchange_rate = start_exchange_rate + total_change
    payout_data = payout_currency_swap(final_exchange_rate = final_exchange_rate, start_exchange_rate = start_exchange_rate, leverage = leverage, USD_asset_allocation = USD_asset_allocation, **scenario_config)

    return payout_data


specifications = (
    (
        BLD / "simulated_data" / f"simulated_data_{simulation_name}.pickle",
        BLD / "simulated_payout" / f"simulated_payout_{simulation_name}_{leverage}_leverage.pickle",
        SRC / "model_specs" / "scenario_config.json",
        leverage,
        USD_asset_allocation,

    )
    for simulation_name in ["historical", "bootstrapped"]
    for leverage in [3, 5, 7, 10]
    for USD_asset_allocation in [0.5]
)


@pytask.mark.parametrize("depends_on, produces, scenario_config, leverage, USD_asset_allocation", specifications)
def task_swap_payout(depends_on, produces, leverage, USD_asset_allocation,  scenario_config):
    # load files
    with open(depends_on, "rb") as f:
        raw_data = pickle.load(f)

    total_change = get_total_exchange_rate_change(raw_data)
    payout_data = calc_final_payout(total_change, leverage, USD_asset_allocation, scenario_config)

  
    # save files
    with open(produces, "wb") as out_file:
        pickle.dump(payout_data, out_file)
