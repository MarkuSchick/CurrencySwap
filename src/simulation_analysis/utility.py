""" includes utility functions
used in the analysis task_swap_payout.py/task_swap_payout_analysis.py"""
import os
from pathlib import Path

def get_total_exchange_rate_change(raw_data):
    total_change = raw_data.sum(axis="columns")
    return total_change

def generate_missing_directories(out_paths):
    """Generate directories if they do not exist

    Args:
        out_paths (dict): {'filename': 'outpath'}
    """
    for file_path in out_paths.values():
        file_directory = Path(os.path.dirname(file_path))
        if not file_directory.exists():
            file_directory.mkdir(parents=True, exist_ok=True)
    print("hello")


def merge_many_to_one_metadata(not_aggregated_data, metadata):
    """ m : 1 merge. Raises error if rows are only identified
        in one dataset """
    merged_dataset = not_aggregated_data.merge(
        metadata,
        left_index=True,
        right_index=True,
        validate="many_to_one",
        indicator=True,
    )
    assert not (
        merged_dataset["_merge"] != "both"
    ).any(), "Rows can not be merged/ Metadata fraudulent"
    merged_dataset.drop(columns=["_merge"], inplace=True)
    return merged_dataset


def merge_one_to_one_metadata(aggregated_data, metadata):
    """ 1 : 1 merge. Raises error if rows are only identified
    in one dataset """
    merged_dataset = aggregated_data.merge(
        metadata,
        left_index=True,
        right_index=True,
        validate="one_to_one",
        indicator=True,
    )
    assert not (
        merged_dataset["_merge"] != "both"
    ).any(), "Rows can not be merged/ Metadata fraudulent"
    merged_dataset.drop(columns=["_merge"], inplace=True)
    return merged_dataset

def extract_simulation_name(data_path): 
    """ expected path is from type /filename_with_underscore_SimulationName
        returns SimulationName

    Args:
        data_path (str): Windows path of file

    Returns:
        [str]: name of simulation
    """
    filename = data_path.stem 
    simulation_name = filename[filename.rfind('_') + 1:]
    return simulation_name
