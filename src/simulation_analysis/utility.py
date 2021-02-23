from os import listdir
from os.path import isfile
from os.path import join

import pandas as pd


def get_total_exchange_rate_change(raw_data):
    total_change = raw_data.sum(axis="columns")
    return total_change


def filename_to_metadata(
    outFile, metadata_file, simulation_name, leverage, USD_asset_allocation
):
    """Write information about payout rate to pandas dataframe
    with filename as identifier.
    Create new file if it does not exist

    Args:
        outFile (str): Name of simulated payout file
        metadata_file (str): Path of metadata file
        leverage (float): Leverage factor
        USD_asset_allocation (float): Assets invested in USD
    """
    try:
        old_file = pd.read_pickle(metadata_file)
        new_row = pd.DataFrame(
            {
                "filename": outFile,
                "simulation_name": simulation_name,
                "leverage": leverage,
                "USD_asset_allocation": USD_asset_allocation,
            },
            index=[0],
        )
        new_file = old_file.append(new_row, ignore_index=True)
        new_file.to_pickle(metadata_file)
    except FileNotFoundError:

        new_file = pd.DataFrame(
            {
                "filename": outFile,
                "simulation_name": simulation_name,
                "leverage": leverage,
                "USD_asset_allocation": USD_asset_allocation,
            },
            index=[0],
        )
        new_file.to_pickle(metadata_file)


def get_pickle_in_directory(directory):
    pickle_files = [
        f
        for f in listdir(directory)
        if isfile(join(directory, f)) and f.endswith(".pickle")
    ]
    return pickle_files


def format_decimal(decimal_number):
    return str(decimal_number).replace(".", "_")
