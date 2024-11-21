import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

def check_ticker_exists(ticker):
    try:
        # Fetch ticker information
        data = yf.Ticker(ticker).info
        # Check if the 'symbol' field exists and matches the input ticker
        if data and 'symbol' in data:
            return True
        return False
    except Exception as e:
        # Log exception (optional)
        print(f"Error checking ticker {ticker}: {e}")
        # Return False for any issues (e.g., invalid ticker, network error)
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
        if len(etfs) < 2:
            print("Your portfolio needs at least 2 securities.")
        else:
            break
    elif check_ticker_exists(ticker) == True:
        print("Okay, I found it.")
        etfs.append(ticker)
        n += 1
    else:
        print("I can't find this ticker. Try again.")

portfolio_value = float(input("Input portfolio value in dollars: "))
print(etfs)

weights = get_etf_weights(etfs)
print("\nPortfolio Weights:")
print(weights)

years = 20
endDate = dt.datetime.now()
startDate = endDate - dt.timedelta(days=365*years)
returns = yf.download(etfs, start=startDate, end=endDate)['Adj Close']

log_returns = np.log(returns / returns.shift(1))
log_returns = log_returns.dropna()
historical_returns = (log_returns * weights).sum(axis =1)

# Calculate the average of the historical returns
average_log_return = historical_returns.mean()

# Annualize the log return (multiply by the number of trading days in a year)
annualized_log_return = average_log_return * 365

# Convert the annualized log return to an arithmetic return (since it's compounded)
annualized_return = np.exp(annualized_log_return) - 1

# Print the result
print(f'Annualized Weighted Return (with compounding, without inflation): {annualized_return:.4f}')


# Calculate the covariance matrix
cov_matrix = log_returns.cov()

# Calculate the portfolio standard deviation
std= np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
annual_std = std * np.sqrt(365)

print(f'Portfolio Annualized Standard Deviation: {annual_std:.4f}')

# Calculate Sharpe Ratio (assuming risk-free rate of 0.0439 for example)
risk_free_rate = 0.0439  # You could also fetch this dynamically
sharpe_ratio = (annualized_return - risk_free_rate) / annual_std
print(f'Portfolio Sharpe Ratio: {sharpe_ratio:.4f}')

# ... after historical returns calculation ...

def calculate_max_drawdown(returns):
    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.expanding().max()
    drawdowns = cumulative / rolling_max - 1
    return drawdowns.min()

max_drawdown = calculate_max_drawdown(historical_returns)
print(f'Maximum Drawdown: {max_drawdown:.4%}')

# ... after covariance matrix calculation ...

# Plot correlation matrix heatmap
correlation_matrix = log_returns.corr()

# ... after weights calculation ...

def calculate_diversification_score(weights, correlation_matrix):
    # Calculate concentration
    concentration = np.sum(weights ** 2)
    
    # Calculate portfolio correlation
    weighted_correlation = np.dot(np.dot(weights, correlation_matrix), weights)
    
    # Calculate diversification score (1 = poorly diversified, N = perfectly diversified)
    div_score = 1 / (concentration * weighted_correlation)
    
    # Calculate maximum possible score (number of assets)
    max_score = len(weights)
    
    # Calculate as a percentage of maximum possible diversification
    div_percentage = (div_score / max_score) * 100
    
    return div_score, div_percentage

div_score, div_percentage = calculate_diversification_score(weights, correlation_matrix)
print(f"\nDiversification Analysis:")
print(f"Diversification Score: {div_score:.2f}")
print("Interpretation:")
if div_score > len(weights):
    print("✓ Excellent diversification! Your assets have beneficial negative correlations.")
    print("  This means they tend to move in opposite directions, reducing portfolio risk.")
elif div_score > len(weights) * 0.7:
    print("✓ Good diversification. Your assets have low correlations with each other.")
else:
    print("! Consider adding more diversification. Your assets may be too correlated.")

days = 365
range_returns = historical_returns.rolling(window = days).sum()
range_returns = range_returns.dropna()

confidence_interval = 0.95

VaR = -np.percentile(range_returns, 100 - (confidence_interval * 100))
cvar = -range_returns[range_returns <= -VaR].mean()

# Output the results
print(f"VaR: There is a {(1-confidence_interval)*100:.2f}% chance that the portfolio loss will exceed {VaR*100:.2f}% in {days} days.")
print(f"CVaR: If the loss exceeds the VaR, the average loss is {cvar*100:.2f}% in {days} days.")

return_window = days
range_returns = historical_returns.rolling(window=return_window).sum()
range_returns = range_returns.dropna()
range_returns_dollar = range_returns * portfolio_value

plt.hist(range_returns_dollar.dropna(), bins=50, density=True)
plt.xlabel(f'{return_window}-Day Portfolio Return (Dollar Value)')
plt.ylabel('Frequency')
plt.title(f'Distribution of Portfolio {return_window}-Day Returns (Dollar Value)')
plt.axvline(-VaR*portfolio_value, color='r', linestyle='dashed', linewidth=2, label=f'VaR at {confidence_interval:.0%} confidence level')
plt.legend()
plt.show()