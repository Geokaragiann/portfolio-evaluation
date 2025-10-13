from typing import Tuple
from numpy import ndarray
from pandas import DataFrame, Series


def geometric_portfolio_returns(daily_prices: DataFrame, weights: ndarray) -> Tuple[float, Series]:
    """
    Given daily stock data and weights for each security, this function calculates and 
    returns the CAGR & Expected Annual Return.
    """

    daily_returns:  DataFrame = daily_prices.pct_change().dropna()
    daily_portfolio_return: Series = daily_returns @ weights.squeeze()

    CAGR: Series = daily_portfolio_return.groupby(daily_portfolio_return.index.year).apply(
        lambda year_data: (1 + year_data).prod() - 1
    )
    expected_annual_return = CAGR.mean()
    
    return expected_annual_return, CAGR

