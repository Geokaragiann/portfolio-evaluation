import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm


def check_ticker_exists(ticker):
    try:
        # Attempt to download data for the ticker
        data = yf.Ticker(ticker).info
        # Check if 'longName' exists in the info dictionary
        if not data or 'longName' not in data:
            return False
        return True
    except Exception as e:
        # If any exception occurs (e.g., network error, invalid ticker), consider it as non-existent
        return False

def get_etf_weights(etfs):
    while True:
        weights_list = []
        total_weight = 0
        # Request the weight for each ETF
        for ticker in etfs:
            while True:
                try:
                    weight = float(input(f'Enter the weight for {ticker} (in %): '))
                    weight /= 100  # Convert percentage to decimal
                    if 0 <= weight <= 1:
                        weights_list.append(weight)
                        total_weight += weight
                        break
                    else:
                        print("Please enter a value between 0 and 100.")
                except ValueError:
                    print("Please enter a valid number.")
        
        # Check if the total weight equals 100%
        if abs(total_weight - 1) < 0.01:  # Allow for some small floating point tolerance
            break
        else:
            print("The weights do not add up to 100%. Please enter them again.")
    
    # Create a Series with the weights and tickers as the index
    weights = pd.Series(weights_list, index=etfs)
    return weights



#START

etfs =  []
n = 1
while True:
    ticker = input('Give ETF/Index number {} or 0 to finish: '.format(n)).upper()
    if ticker == '0':
        break
    elif check_ticker_exists(ticker) == True:
        print("Okay, I found it.")
        etfs.append(ticker)
        n += 1
    else:
        print("I can't find this ticker. Try again.")

print(etfs)

weights = get_etf_weights(etfs)
print("\nPortfolio Weights:")
print(weights)

returns = yf.download(etfs, end='2024-08-31')['Adj Close'].pct_change().dropna()

# Calculate cumulative return
cumulative_return = (1 + returns).prod() - 1
trading_days = 252

# Calculate annualized return
annualized_return = (1 + cumulative_return) ** (trading_days / len(returns)) - 1

# Calculate the weighted average return
weighted_average_return = (annualized_return * weights).sum()

print(f'Weighted Average Return: {weighted_average_return:.2%}')


# Calculate the covariance matrix
cov_matrix = returns.cov()

# Calculate the portfolio standard deviation
std= np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
annual_std = std * np.sqrt(trading_days)

print(f'Portfolio Annualized Standard Deviation: {annual_std:.4f}')

# Number of bootstrap samples
n_samples = 100000

# Simulate portfolio returns by randomly sampling from the historical data
bootstrap_returns = np.random.choice(returns.mean(axis=1) * trading_days, n_samples, replace=True)

# Calculate the probability of returns over the target return
prob_over_target = np.mean(bootstrap_returns > 0.06)

print(f'Probability that the portfolio will have returns over 6% (bootstrap): {prob_over_target:.2%}')

