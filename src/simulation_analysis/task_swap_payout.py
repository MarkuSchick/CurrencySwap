import json

import pandas as pd
import pytask

from src.config import BLD
from src.config import SRC
from src.financial_contracts.swap_contract import payout_currency_swap
from src.simulation_analysis.utility import get_total_exchange_rate_change


def calc_final_payout(
    cumulative_forex_change, leverage, USD_asset_allocation, scenario_config
):
    """Calculate the finale payout of the currency swap contract given macroeconomic conditions
    and configurations

    Args:
        cumulative_forex_change (pd.Series): cumulative EUR/USD exchange rate change over 1
        year.
        leverage (float): Leverage factor of the currency swap. Must be larger than 1.
        USD_asset_allocation (float): Share of assets invested in USD. Must be between 0 and 1.
        scenario_config (dict): assumed macroeconomic conditions.

    Returns:
        (pd.DataFrame): Payout of swap contract (in EURO & USD).
    """
    assert leverage > 1, "Leverage factor must be higher than 1"
    assert 0 <= USD_asset_allocation <= 1, "Share of assets invested must be positive"

    # initialize
    start_exchange_rate = 1
    final_exchange_rate = start_exchange_rate + cumulative_forex_change

    # calculate payout data
    payout_data = payout_currency_swap(
        final_exchange_rate=final_exchange_rate,
        start_exchange_rate=start_exchange_rate,
        leverage=leverage,
        USD_asset_allocation=USD_asset_allocation,
        **scenario_config,
    )

    # calculate payout in EURO terms
    payout_data = payout_data.rename(
        columns={
            "EURlong payout": "EURlong payout in USD",
            "EURshort payout": "EURshort payout in USD",
        }
    )
    payout_data["exchange_rate"] = final_exchange_rate
    payout_data["EURlong payout in EURO"] = payout_data["EURlong payout in USD"].div(
        payout_data["exchange_rate"]
    )
    payout_data["EURshort payout in EURO"] = payout_data["EURshort payout in USD"].div(
        payout_data["exchange_rate"]
    )
    return payout_data


def filename_to_metadata(run_id, simulation_name, leverage, USD_asset_allocation):
    """Write information about simulation configurations to a pd.DataFrame

    Args:
        run_id (id): Id of simulation configuration.
        simulation_name (str): Path of metadata file.
        leverage (float): Leverage factor of the currency swap
        USD_asset_allocation (float): Share of assets invested in USD. Must be between 0 and 1.

    Returns:
        (pd.DataFrame): background information of the simulation run.
    """
    metadata = pd.DataFrame(
        {
            "swap_config_id": run_id,
            "simulation_name": simulation_name,
            "leverage": leverage,
            "USD_asset_allocation": USD_asset_allocation,
        },
        index=[0],
    )
    return metadata


# varying specifications
specifications = (
    (
        f"simulated_data_{simulation_name}.pickle",
        f"simulated_payout_{simulation_name}.pickle",
        f"metadata_payout_{simulation_name}.pickle",
        simulation_name,
    )
    for simulation_name in ["historical", "bootstrapped"]
)


@pytask.mark.parametrize(
    "inFile, outFile, metadataFile, simulation_name",
    specifications,
)
# fix specifications
@pytask.mark.depends_on(
    {
        "scenario_config": SRC / "contract_specs" / "scenario_config.json",
        "swap_config": SRC / "contract_specs" / "swap_config.json",
        "inFile_folder": BLD / "simulated_data",
        "outFile_folder": BLD / "simulated_payout",
        "metadata_folder": BLD / "metadata",
    }
)
def task_swap_payout(depends_on, inFile, outFile, metadataFile, simulation_name):
    # initialize
    swap_config_id = 0
    payout_data_list = []
    meta_data_list = []

    # parse json data
    swap_config = json.loads(depends_on["swap_config"].read_text(encoding="utf-8"))
    scenario_config = json.loads(
        depends_on["scenario_config"].read_text(encoding="utf-8")
    )

    # calculate payout for all configurations
    for leverage in swap_config["leverage"]:
        for USD_asset_allocation in swap_config["USD_asset_allocation"]:

            # load files
            raw_data = pd.read_pickle(depends_on["inFile_folder"] / inFile)

            # simulate payout given parameterization
            cumulative_change = get_total_exchange_rate_change(raw_data)
            payout = calc_final_payout(
                cumulative_change, leverage, USD_asset_allocation, scenario_config
            )
            payout["swap_config_id"] = swap_config_id
            payout_data_list.append(payout)

            # save metadata
            meta = filename_to_metadata(
                swap_config_id, simulation_name, leverage, USD_asset_allocation
            )
            meta_data_list.append(meta)

            swap_config_id += 1

    # append datafiles
    payout_data = pd.concat(payout_data_list).set_index("swap_config_id")
    meta_data = pd.concat(meta_data_list).set_index("swap_config_id")

    # save files
    payout_data.to_pickle(depends_on["outFile_folder"] / outFile)
    meta_data.to_pickle(depends_on["metadata_folder"] / metadataFile)


if __name__ == "__main__":
    depends_on = {
        "scenario_config": SRC / "contract_specs" / "scenario_config.json",
        "swap_config": SRC / "contract_specs" / "swap_config.json",
        "inFile_folder": BLD / "simulated_data",
        "outFile_folder": BLD / "simulated_payout",
        "metadata_folder": BLD / "metadata",
    }

    simulation_name = "bootstrapped"
    scenario_config = SRC / "contract_specs" / "scenario_config.json"

    inFile = f"simulated_data_{simulation_name}.pickle"
    outFile = f"simulated_payout_{simulation_name}.pickle"
    metadataFile = f"metadata_payout_{simulation_name}.pickle"

    task_swap_payout(depends_on, inFile, outFile, metadataFile, simulation_name)
