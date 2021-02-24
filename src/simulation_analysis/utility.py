from os import listdir
from os.path import isfile
from os.path import join

import pandas as pd


def get_total_exchange_rate_change(raw_data):
    total_change = raw_data.sum(axis="columns")
    return total_change



def get_pickle_in_directory(directory):
    pickle_files = [
        f
        for f in listdir(directory)
        if isfile(join(directory, f)) and f.endswith(".pickle")
    ]
    return pickle_files


def format_decimal(decimal_number):
    return str(decimal_number).replace(".", "_")
