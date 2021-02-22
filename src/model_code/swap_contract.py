def _convert_to_USD(exchange_rate, EURO_amount):
    return EURO_amount * exchange_rate


def _apply_return(
    euro_deposits, usd_deposits, return_on_euro_deposits, return_on_usd_deposits
):
    euro_deposits = (1 + return_on_euro_deposits) * euro_deposits
    usd_deposits = (1 + return_on_usd_deposits) * usd_deposits
    return euro_deposits, usd_deposits


def _get_collateral_value(
    euro_deposits,
    usd_deposits,
    return_on_euro_deposits,
    return_on_usd_deposits,
    exchange_rate,
):
    euro_deposits, usd_deposits = _apply_return(
        euro_deposits, usd_deposits, return_on_euro_deposits, return_on_usd_deposits
    )
    total_deposits = usd_deposits + _convert_to_USD(exchange_rate, euro_deposits)
    return total_deposits


def _get_payout_factor(exchange_rate, start_exchange_rate, leverage):
    EURlong_payout_fac = (
        1 + (exchange_rate - start_exchange_rate) / start_exchange_rate * leverage
    )
    EURshort_payout_fac = 2 - EURlong_payout_fac
    return EURlong_payout_fac, EURshort_payout_fac


def payout_currency_swap(
    final_exchange_rate,
    start_exchange_rate,
    USD_asset_allocation,
    leverage,
    return_on_euro_deposits=0.0,
    return_on_usd_deposits=0.0,
):
    """
    Simulates payoff profile of some currency swap contract.

    Args:
        final_exchange_rate (pd.DataFrame(n,1)): Final EURO/USD exchange rate
        start_exchange_rate (float): Initial EURO/USD exchange rate
        USD_asset_allocation (float): Share of collateral invested in USD [0,1]
        leverage (float): Leverage (payout) factor
        return_on_euro_deposits (float, optional): Return on euro deposits. Defaults to 0.
        return_on_usd_deposits (float, optional): Return on usd deposits. Defaults to 0.

    Returns:
        EURlong_payout (pd.DataFrame(n,1)): Payout of 1 unit of a EURlong
        EURshort_payout (pd.DataFrame(n,1)): Payout of 1 unit of a EURshort
    """
    # allocate assets
    usd_deposits = USD_asset_allocation
    euro_deposits = 1 - USD_asset_allocation

    # calculate current value of collateral
    underlying_collateral = _get_collateral_value(
    euro_deposits,
    usd_deposits,
    return_on_euro_deposits,
    return_on_usd_deposits,
    final_exchange_rate
    )

    # get payout factor
    EURlong_payout_fac, EURshort_payout_fac = _get_payout_factor(
        final_exchange_rate, start_exchange_rate, leverage
    )

    # redeem EURlong, EURshort
    EURlong_payout = EURlong_payout_fac * underlying_collateral
    EURshort_payout = EURshort_payout_fac * underlying_collateral

    return EURlong_payout, EURshort_payout
