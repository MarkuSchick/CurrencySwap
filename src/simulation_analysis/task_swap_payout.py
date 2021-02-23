import json

import pandas as pd
import pytask

from src.config import BLD
from src.config import SRC
from src.financial_contracts.swap_contract import payout_currency_swap
from src.simulation_analysis.utility import filename_to_metadata
from src.simulation_analysis.utility import format_decimal
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
    # load configurations
    scenario_config = json.loads(scenario_config.read_text(encoding="utf-8"))

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


# varying specifications
specifications = (
    (
        f"simulated_data_{simulation_name}.pickle",
        f"simulated_payout_{simulation_name}_leverage{leverage} \
        _usd_{format_decimal(USD_asset_allocation)}.pickle",
        leverage,
        USD_asset_allocation,
    )
    for simulation_name in ["historical", "bootstrapped"]
    for leverage in [3, 5, 7, 10]
    for USD_asset_allocation in [0, 0.2, 0.4, 0.6, 0.8, 1]
)


@pytask.mark.parametrize(
    "inFile, outFile, leverage, USD_asset_allocation",
    specifications,
)
# fix specifications
@pytask.mark.depends_on(
    {
        "scenario_config": SRC / "contract_specs" / "scenario_config.json",
        "inFile_folder": BLD / "simulated_data",
        "outFile_folder": BLD / "simulated_payout",
        "metadata_file": BLD / "metadata" / "simulation_payout_metadata.pickle",
    }
)
def task_swap_payout(depends_on, inFile, outFile, leverage, USD_asset_allocation):

    # load files
    raw_data = pd.read_pickle(depends_on["inFile_folder"] / inFile)

    total_change = get_total_exchange_rate_change(raw_data)
    payout_data = calc_final_payout(
        total_change, leverage, USD_asset_allocation, depends_on["scenario_config"]
    )

    # save configurations
    filename_to_metadata(
        outFile, depends_on["metadata_file"], leverage, USD_asset_allocation
    )

    # save files
    payout_data.to_pickle(depends_on["outFile_folder"] / outFile)


if __name__ == "__main__":
    depends_on = {
        "scenario_config": SRC / "contract_specs" / "scenario_config.json",
        "inFile_folder": BLD / "simulated_data",
        "outFile_folder": BLD / "simulated_payout",
        "metadata_file": BLD / "metadata" / "simulation_payout_metadata.pickle",
    }

    leverage = 5
    USD_asset_allocation = 0.2
    simulation_name = "historical"
    scenario_config = SRC / "contract_specs" / "scenario_config.json"

    inFile = f"simulated_data_{simulation_name}.pickle"
    outFile = f"simulated_payout_{simulation_name}_leverage{leverage} \
    _usd_{format_decimal(USD_asset_allocation)}.pickle"

    task_swap_payout(depends_on, inFile, outFile, leverage, USD_asset_allocation)
