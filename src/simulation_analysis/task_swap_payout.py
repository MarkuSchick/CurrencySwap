import json

import pandas as pd
import pytask

from src.config import BLD
from src.config import SRC
from src.financial_contracts.swap_contract import payout_currency_swap
from src.simulation_analysis.utility import get_total_exchange_rate_change


def calc_final_payout(total_change, leverage, USD_asset_allocation, scenario_config):
    """[summary]

    Args:
        total_change ([type]): [description]
        swap_config ([type]): [description]
        scenario_config ([type]): [description]

    Returns:
        [type]: [description]
    """

    # calculate payout data
    start_exchange_rate = 1
    final_exchange_rate = start_exchange_rate + total_change
    payout_data = payout_currency_swap(
        final_exchange_rate=final_exchange_rate,
        start_exchange_rate=start_exchange_rate,
        leverage=leverage,
        USD_asset_allocation=USD_asset_allocation,
        **scenario_config,
    )

    return payout_data


def filename_to_metadata(run_id, simulation_name, leverage, USD_asset_allocation):
    """Write information about payout rate to pandas dataframe
    with filename as identifier.

    Args:
        run_id (id): Id of simulation configuration
        metadata_file (str): Path of metadata file
        leverage (float): Leverage factor
        USD_asset_allocation (float): Assets invested in USD

    Returns:
        [pd.DataFrame]: information about run
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
            total_change = get_total_exchange_rate_change(raw_data)
            payout = calc_final_payout(
                total_change, leverage, USD_asset_allocation, scenario_config
            )
            payout["swap_config_id"] = swap_config_id
            payout_data_list.append(payout)

            # save metadata
            meta_data_list.append(
                filename_to_metadata(
                    swap_config_id, simulation_name, leverage, USD_asset_allocation
                )
            )
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

    simulation_name = "historical"
    scenario_config = SRC / "contract_specs" / "scenario_config.json"

    inFile = f"simulated_data_{simulation_name}.pickle"
    outFile = f"simulated_payout_{simulation_name}.pickle"
    metadataFile = f"metadata_payout_{simulation_name}.pickle"

    task_swap_payout(depends_on, inFile, outFile, metadataFile, simulation_name)
