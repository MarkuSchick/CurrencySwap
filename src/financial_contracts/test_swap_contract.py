""" Testing the payout of the Currency Swap.
We test along 2 dimensions: |
1) exchange rate changes |
2) asset allocations |

"""
import numpy as np
import pandas as pd
import pytest

from src.financial_contracts.swap_contract import payout_currency_swap


@pytest.fixture
def default_data():

    out = {}
    out["final_exchange_rate"] = pd.Series(data=np.ones(3) + 0.1)
    out["start_exchange_rate"] = 1
    out["USD_asset_allocation"] = 0.5
    out["leverage"] = 5
    out["return_on_euro_deposits"] = 0
    out["return_on_usd_deposits"] = 0

    return out


""" test exchange rate changes """


def test_swap_no_exchange_rate_change(default_data):
    data_no_change = default_data
    data_no_change["final_exchange_rate"] = pd.Series(data=np.ones(3))

    realized_payout = payout_currency_swap(**data_no_change)
    expected_payout = pd.DataFrame(
        {"EURlong payout": np.ones(3), "EURshort payout": np.ones(3)}
    )

    pd.testing.assert_frame_equal(realized_payout, expected_payout, atol=0.0001)

    """ the unintuitive design that payout of 1 is generated
    comes from the fact that rights to participate in this lottery
    have to be bought for a price of 1 per unit
    """


def test_swap_small_exchange_rate_change_usd_only(default_data):
    data_small_change_usd_only = default_data
    data_small_change_usd_only["USD_asset_allocation"] = 1

    realized_payout = payout_currency_swap(**data_small_change_usd_only)
    expected_payout = pd.DataFrame(
        {"EURlong payout": np.ones(3) + 0.5, "EURshort payout": np.ones(3) - 0.50}
    )

    pd.testing.assert_frame_equal(realized_payout, expected_payout, atol=0.0001)


def test_swap_small_exchange_rate_change_euro_rise(default_data):

    realized_payout = payout_currency_swap(**default_data)
    expected_payout = pd.DataFrame(
        {
            "EURlong payout": np.ones(3) + 0.5,
            "EURshort payout": np.ones(3) - 0.5 + 0.1,
        }
    )

    pd.testing.assert_frame_equal(realized_payout, expected_payout, atol=0.0001)


def test_swap_small_exchange_rate_change_euro_fall(default_data):
    default_data["final_exchange_rate"] = pd.Series(data=np.ones(3) - 0.1)

    realized_payout = payout_currency_swap(**default_data)
    expected_payout = pd.DataFrame(
        {
            "EURlong payout": np.ones(3) - 0.5,
            "EURshort payout": np.ones(3) + 0.5 - 0.1,
        }
    )

    pd.testing.assert_frame_equal(realized_payout, expected_payout, atol=0.0001)


""" test asset allocations """


def test_swap_total_payout_usd_50(default_data):
    default_data["final_exchange_rate"] = pd.Series(data=[0.9, 1, 1.1])

    realized_total_payout = payout_currency_swap(**default_data).sum(axis="columns")
    expected_total_payout = pd.Series(data=[1.9, 2.0, 2.1])

    pd.testing.assert_series_equal(
        realized_total_payout, expected_total_payout, atol=0.0001
    )


def test_swap_total_payout_usd_100(default_data):
    default_data["final_exchange_rate"] = pd.Series(data=[0.9, 1, 1.1])
    default_data["USD_asset_allocation"] = 1
    realized_total_payout = payout_currency_swap(**default_data).sum(axis="columns")
    expected_total_payout = pd.Series(data=[2.0, 2.0, 2.0])

    pd.testing.assert_series_equal(
        realized_total_payout, expected_total_payout, atol=0.0001
    )


def test_swap_total_payout_usd_0(default_data):
    default_data["final_exchange_rate"] = pd.Series(data=[0.9, 1, 1.1])
    default_data["USD_asset_allocation"] = 0

    realized_total_payout = payout_currency_swap(**default_data).sum(axis="columns")
    expected_total_payout = pd.Series(data=[1.8, 2, 2.2])

    pd.testing.assert_series_equal(
        realized_total_payout, expected_total_payout, atol=0.0001
    )


if __name__ == "__main__":
    out = {}
    out["final_exchange_rate"] = pd.Series(data=[np.ones(3) + 0.1])
    out["start_exchange_rate"] = 1
    out["USD_asset_allocation"] = 0.5
    out["leverage"] = 5
    out["return_on_euro_deposits"] = 0
    out["return_on_usd_deposits"] = 0

    data = out
    test_swap_total_payout_usd_50(data)
