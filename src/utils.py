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


def standard_deviation(daily_returns: pd.DataFrame, weights: np.ndarray) -> float:
    """
    Given daily stock data and weights for each security, this function calculates and 
    returns the standard deviation of the portfolio.
    """

    covariance_matrix: pd.DataFrame = daily_returns.cov()
    daily_std = np.sqrt(weights.T @ covariance_matrix @ weights)
    annualized_std = daily_std * np.sqrt(252) # total rows after cleaning = 5029. 5029/20 years = 251.45. However, I use 252 to avoid underestimating
    return annualized_std
