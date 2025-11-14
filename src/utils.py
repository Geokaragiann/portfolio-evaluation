from typing import Tuple
import numpy as np
import pandas as pd


def portfolio_returns(daily_returns: pd.DataFrame, weights: np.ndarray) -> Tuple[float, pd.Series]:
    """
    Given daily returns and weights for each security, this function calculates and 
    returns the average annual return, annual returns, and for the portfolio.
    """
    

    daily_portfolio_return: pd.Series = (daily_returns @ weights).squeeze()

    annual_returns: pd.Series = daily_portfolio_return.groupby(daily_portfolio_return.index.year).apply(
        lambda year_data: (1 + year_data).prod() - 1
    )
    average_annual_return = annual_returns.mean()
    
    return average_annual_return, annual_returns

def cagr(daily_prices: pd.DataFrame, weights: np.ndarray) -> float:
    return (((daily_prices.iloc[-1]/daily_prices.iloc[0])-1) @ weights)**(252/2583)

def standard_deviation(daily_returns: pd.DataFrame, weights: np.ndarray) -> Tuple[float, float]:
    """
    Given daily stock data and weights for each security, this function calculates and 
    returns the standard deviation of the portfolio.
    """

    covariance_matrix: pd.DataFrame = daily_returns.cov()
    daily_std = np.sqrt(weights.T @ covariance_matrix @ weights)
    annualized_std = daily_std * np.sqrt(252)
    return annualized_std, daily_std
