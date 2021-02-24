
import pandas as pd

import pytask

from src.config import BLD
from src.simulation_analysis.utility import get_pickle_in_directory




def _get_out_name_file(original_name, out_path):
    out_filename = original_name.replace("simulated_payout", "simulated_payout").replace(
        ".pickle", ".png")
    out_filename_path = out_path / out_filename
    return out_filename_path


def _plot_probability_bound(raw_data, out_name):
    d1, d2 = raw_data
    print("here")

# varying specifications
specifications = (
    (
        f"simulated_data_{simulation_name}.pickle",
        f"simulated_payout_{simulation_name}.pickle",
        f"metadata_payout_{simulation_name}.pickle",
        simulation_name
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
def task_swap_payout_analysis(depends_on, produces):

    simulation_overview = pd.read_pickle(depends_on["metadata_file"])
    

    filenames = _get_pickle_in_directory(depends_on["data_folder"])
    

    for file_name in filenames:

        # load files


        out_filename_path = _get_out_name_file(file_name, produces)

        _plot_probability_bound(raw_data, out_filename_path)
   


if __name__ == "__main__":
    depends_on = {
    "data_folder": BLD / "simulated_payout",
    "metadata_file": BLD / "metadata" / "simulation_payout_metadata.pickle"
    }
    produces =  BLD / "figures"

    task_swap_payout_analysis(depends_on, produces)

"""