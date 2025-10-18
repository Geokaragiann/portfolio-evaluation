from typing import Tuple
import numpy as np
import pandas as pd


def geometric_portfolio_returns(daily_returns: pd.DataFrame, weights: np.ndarray) -> Tuple[float, pd.Series]:
    """
    Given daily returns and weights for each security, this function calculates and 
    returns the average annual return & annual returns for the portfolio.
    """
    

    daily_portfolio_return: pd.Series = (daily_returns @ weights).squeeze()

    annual_returns: pd.Series = daily_portfolio_return.groupby(daily_portfolio_return.index.year).apply(
        lambda year_data: (1 + year_data).prod() - 1
    )
    average_annual_return = annual_returns.mean()
    
    return average_annual_return, annual_returns


def standard_seviation(daily_prices: pd.DataFrame, weights: np.ndarray) -> float:
    """
     Given daily stock data and weights for each security, this function calculates and 
    returns the standard deviation of the portfolio.
    """

