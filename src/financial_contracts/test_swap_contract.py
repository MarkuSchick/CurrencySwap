""" Testing the payout currency swap function



"""
import numpy as np
import pandas as pd
import pytest
from pandas._testing import assert_series_equal

from src.financial_contracts.swap_contract import payout_currency_swap
#from swap_contract import payout_currency_swap

@pytest.fixture
def default_data():

    out = {}
    out["final_exchange_rate"] = pd.Series(data = np.ones(3) + 0.1)
    out["start_exchange_rate"] = 1
    out["USD_asset_allocation"] = 0.5
    out["leverage"] = 5
    out["return_on_euro_deposits"] = 0
    out["return_on_usd_deposits"] = 0

    return out

def test_swap_no_exchange_rate_change(default_data):
    data_no_change = default_data
    data_no_change["final_exchange_rate"] = pd.Series(data = np.ones(3))

    Eurlong_payout, _ = payout_currency_swap(**data_no_change)
    expected_Eurlong_payout = pd.Series(data = np.ones(3), name = "EURlong payout")
    pd.testing.assert_series_equal(Eurlong_payout, expected_Eurlong_payout, atol=0.0001)

    _, EURshort_payout = payout_currency_swap(**data_no_change)
    expected_EURshort_payout = pd.Series(data = np.ones(3), name = "EURshort payout")
    pd.testing.assert_series_equal(EURshort_payout, expected_EURshort_payout, atol=0.0001)

    """ the unintuitive design that payout of 1 is generated
    comes from the fact that rights to participate in this lottery
    have to be bought for a price of 1 per unit
    """
    
def test_swap_small_exchange_rate_change_usd_only(default_data):
    data_small_change_usd_only = default_data
    data_small_change_usd_only["USD_asset_allocation"] = 1

    Eurlong_payout, _ = payout_currency_swap(**data_small_change_usd_only)
    expected_Eurlong_payout = pd.Series(data = np.ones(3) + 0.5, name = "EURlong payout")
    pd.testing.assert_series_equal(Eurlong_payout, expected_Eurlong_payout, atol=0.0001)

    _, EURshort_payout = payout_currency_swap(**data_small_change_usd_only)
    expected_EURshort_payout = pd.Series(data = np.ones(3) - 0.50 , name = "EURshort payout")
    pd.testing.assert_series_equal(EURshort_payout, expected_EURshort_payout, atol=0.0001)


def test_swap_small_exchange_rate_change_euro_rise(default_data):   

    Eurlong_payout, _ = payout_currency_swap(**default_data)
    expected_Eurlong_payout = pd.Series(data = np.ones(3) + 0.5 + 0.075, name = "EURlong payout")
    pd.testing.assert_series_equal(Eurlong_payout, expected_Eurlong_payout, atol=0.0001)

    _, EURshort_payout = payout_currency_swap(**default_data)
    expected_EURshort_payout = pd.Series(data = np.ones(3) - 0.5 + 0.025 , name = "EURshort payout")
    pd.testing.assert_series_equal(EURshort_payout, expected_EURshort_payout, atol=0.0001)


def test_swap_small_exchange_rate_change_euro_fall(default_data):   
    default_data["final_exchange_rate"] = pd.Series(data = np.ones(3) - 0.1)

    Eurlong_payout, _ = payout_currency_swap(**default_data)
    expected_Eurlong_payout = pd.Series(data = np.ones(3) - 0.5 - 0.025, name = "EURlong payout")
    pd.testing.assert_series_equal(Eurlong_payout, expected_Eurlong_payout, atol=0.0001)

    _, EURshort_payout = payout_currency_swap(**default_data)
    expected_EURshort_payout = pd.Series(data = np.ones(3) + 0.5 - 0.075 , name = "EURshort payout")
    pd.testing.assert_series_equal(EURshort_payout, expected_EURshort_payout, atol=0.0001)



if __name__ == "__main__":
    out = {}
    out["final_exchange_rate"] = pd.Series(data = np.ones(3) + 0.1)
    out["start_exchange_rate"] = 1
    out["USD_asset_allocation"] = 0.5
    out["leverage"] = 5
    out["return_on_euro_deposits"] = 0
    out["return_on_usd_deposits"] = 0

    data = out
    test_swap_small_exchange_rate_change(data)