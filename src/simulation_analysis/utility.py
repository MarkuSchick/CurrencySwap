""" includes utility functions
used in the analysis task_swap_payout.py"""


from os import listdir
from os.path import isfile
from os.path import join

import pandas as pd


def get_total_exchange_rate_change(raw_data):
    total_change = raw_data.sum(axis="columns")
    return total_change
