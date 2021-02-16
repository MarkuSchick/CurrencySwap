""" Downloads the daily EURO/USD exchange rate from
FRED and saves output as a pickle
see: https://fred.stlouisfed.org/series/DEXUSEU
Does not use any checks if download was successfull
since this is historical data.
"""

import pickle
import datetime
from datetime import date
import pandas_datareader as pdr
import pytask
import numpy as np

import pandas_datareader.data as web

from src.config import BLD




def _download_data():
    start = datetime.datetime(1999, 1, 4)
    end = date.today()
    fred_object = pdr.fred.FredReader('DEXUSEU', start, end)
    data = fred_object.read()
    return data


def _summarize_data(data):
    print(f"Describe data: \n {data.describe()} \n \n")
    print(f"Missing values: {data.isna().sum()} \n")
    print(f"Data types: {data.dtypes}")

def get_data():
    data = _download_data()
    _summarize_data(data)
    return data

def _clean_data(data):
    # replace missing values
    data.interpolate(method="time", limit=2, inplace=True)
    is_missing = data.notna().all().all()
    assert  is_missing, "Missing values remain. Try increasing the limit of the interpolate function"

    # rename column
    data = data.rename(columns={"DEXUSEU": "price"})

    return data

def _calculate_returns(data):
    data['pct_change'] = data["price"].pct_change()
    data['log_return'] = np.log(1 + data['pct_change'])
    return data

def transform_data(data):
    data = _clean_data(data)
    data = _calculate_returns(data)
    return data

@pytask.mark.produces(BLD / "historical_data" / "raw_data.pickle")
def task_get_exchange_rate_data(produces):
    eurusd_data = get_data()
    eurusd_data = transform_data(eurusd_data)

    # Store dictionary with locations once
    with open(produces, "wb") as out_file:
        pickle.dump(eurusd_data, out_file)
