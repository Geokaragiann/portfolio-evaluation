import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

# Constants
ANALYSIS_PERIOD_YEARS = 20
ROLLING_WINDOW_DAYS = 365
CONFIDENCE_LEVEL = 0.95
RISK_FREE_RATE = 0.0439
MIN_PORTFOLIO_ASSETS = 2

def check_ticker_exists(ticker):
    """Verify if a ticker exists in yfinance database."""
    try:
        data = yf.Ticker(ticker).info
        return bool(data and 'symbol' in data)
    except Exception as e:
        print(f"Error checking ticker {ticker}: {e}")
        return False

def get_portfolio_weights(tickers):
    """Get user input for portfolio weights ensuring they sum to 100%."""
    while True:
        weights_list = []
        total_weight = 0
        
        for ticker in tickers:
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
        
        if abs(total_weight - 1) < 0.01:
            break
        else:
            print("The weights do not add up to 100%. Please enter them again.")
    
    return pd.Series(weights_list, index=tickers)

def calculate_portfolio_metrics(daily_returns, portfolio_weights):
    """Calculate key portfolio metrics."""
    # Portfolio returns
    portfolio_returns = (daily_returns * portfolio_weights).sum(axis=1)
    
    # Calculate rolling returns (365-day window)
    range_returns = portfolio_returns.rolling(window=ROLLING_WINDOW_DAYS).sum()
    range_returns = range_returns.dropna()
    
    # Calculate returns standard deviation
    returns_std = range_returns.std()
    
    # Calculate average daily return and annualize it
    avg_daily_return = portfolio_returns.mean()
    annualized_return = np.exp(avg_daily_return * 365) - 1
    
    # Sharpe ratio
    sharpe_ratio = (annualized_return - RISK_FREE_RATE) / returns_std
    
    return {
        'returns': portfolio_returns,
        'range_returns': range_returns,
        'returns_std': returns_std,
        'annualized_return': annualized_return,
        'sharpe_ratio': sharpe_ratio
    }
def calculate_max_drawdown(returns):
    """Calculate maximum drawdown of portfolio."""
    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.expanding().max()
    drawdowns = cumulative / rolling_max - 1
    return drawdowns.min()

def calculate_diversification_score(portfolio_weights, correlation_matrix):
    """
    Calculate portfolio diversification ratio.
    DR = weighted sum of individual volatilities / portfolio volatility
    A higher ratio indicates better diversification.
    """
    # Calculate individual volatilities
    volatilities = np.sqrt(np.diag(correlation_matrix))
    
    # Weighted sum of individual volatilities
    weighted_sum_vol = np.sum(portfolio_weights * volatilities)
    
    # Calculate portfolio volatility
    portfolio_vol = np.sqrt(np.dot(portfolio_weights, np.dot(correlation_matrix, portfolio_weights)))
    
    # Calculate diversification ratio
    div_ratio = weighted_sum_vol / portfolio_vol if portfolio_vol != 0 else 0
    
    # Calculate as percentage of maximum possible diversification
    max_ratio = np.sqrt(len(portfolio_weights))  # Theoretical maximum with perfect negative correlation
    div_percentage = (div_ratio / max_ratio) * 100
    
    return div_ratio, div_percentage

def calculate_risk_metrics(portfolio_returns, portfolio_value):
    """Calculate VaR and CVaR."""
    rolling_returns = portfolio_returns.rolling(window=ROLLING_WINDOW_DAYS).sum()
    rolling_returns = rolling_returns.dropna()
    
    value_at_risk = -np.percentile(rolling_returns, 100 - (CONFIDENCE_LEVEL * 100))
    conditional_var = -rolling_returns[rolling_returns <= -value_at_risk].mean()
    
    return {
        'rolling_returns': rolling_returns,
        'value_at_risk': value_at_risk,
        'conditional_var': conditional_var
    }

def plot_returns_distribution(rolling_returns, portfolio_value, value_at_risk, annualized_return):
    """Plot the distribution of portfolio returns."""
    returns_dollar = rolling_returns * portfolio_value
    
    plt.figure(figsize=(12, 6))
    plt.hist(returns_dollar.dropna(), bins=50, density=True)
    plt.xlabel(f'{ROLLING_WINDOW_DAYS}-Day Portfolio Return (Dollar Value)')
    plt.ylabel('Frequency')
    plt.title(f'Distribution of Portfolio {ROLLING_WINDOW_DAYS}-Day Returns (Dollar Value)')
    
    # Add VaR line
    plt.axvline(-value_at_risk * portfolio_value, 
                color='r', 
                linestyle='dashed', 
                linewidth=2, 
                label=f'VaR at {CONFIDENCE_LEVEL:.0%} confidence level')
    
    # Add average return line
    plt.axvline(annualized_return * portfolio_value, 
                color='black', 
                linestyle='dashed', 
                linewidth=2, 
                label='365-day rolling average')
    
    plt.legend()
    plt.show()

def print_portfolio_analysis(metrics, risk_metrics, div_score, div_percentage, max_drawdown):
    """Print all portfolio analysis results."""
    print("\nPortfolio Analysis Results:")
    print("-" * 50)
    print(f"Annualized Return: {metrics['annualized_return']:.2%}")
    print(f"Annual Standard Deviation: {metrics['returns_std']:.2%}")s
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.4f}")  # Added this line
    print(f"Maximum Drawdown: {max_drawdown:.2%}")
    
    print("\nDiversification Analysis:")
    print(f"Diversification Score: {div_score:.2f}")
    print(f"Diversification Percentage: {div_percentage:.2f}%")
    
    if div_score > 1.5:
        print("✓ Excellent diversification! Assets have favorable correlations.")
    elif div_score > 1.2:
        print("✓ Good diversification. Consider additional decorrelation for improvement.")
    else:
        print("! Low diversification. Your portfolio may be concentrated or highly correlated.")
    
    print("\nRisk Metrics:")
    print(f"VaR: There is a {(1-CONFIDENCE_LEVEL)*100:.1f}% chance that the portfolio loss")
    print(f"     will exceed {risk_metrics['value_at_risk']*100:.2f}% in {ROLLING_WINDOW_DAYS} days.")
    print(f"CVaR: If the loss exceeds the VaR, the average loss is {risk_metrics['conditional_var']*100:.2f}%")
    print(f"      in {ROLLING_WINDOW_DAYS} days.")



"""Main execution flow."""
# Get portfolio tickers
portfolio_tickers = []
ticker_count = 1

while True:
    ticker = input(f'Enter ETF/Index number {ticker_count} or 0 to finish: ').upper()
    if ticker == '0':
        if len(portfolio_tickers) < MIN_PORTFOLIO_ASSETS:
            print(f"Your portfolio needs at least {MIN_PORTFOLIO_ASSETS} securities.")
        else:
            break
    elif check_ticker_exists(ticker):
        print("Ticker found.")
        portfolio_tickers.append(ticker)
        ticker_count += 1
    else:
        print("Invalid ticker. Please try again.")

# Get portfolio value and weights
portfolio_value = float(input("Input portfolio value in dollars: "))
portfolio_weights = get_portfolio_weights(portfolio_tickers)

# Download and process data
end_date = dt.datetime.now()
start_date = end_date - dt.timedelta(days=365*ANALYSIS_PERIOD_YEARS)
daily_prices = yf.download(portfolio_tickers, start=start_date, end=end_date)['Adj Close']
daily_returns = np.log(daily_prices / daily_prices.shift(1)).dropna()

# Calculate all metrics
metrics = calculate_portfolio_metrics(daily_returns, portfolio_weights)
risk_metrics = calculate_risk_metrics(metrics['returns'], portfolio_value)
max_drawdown = calculate_max_drawdown(metrics['returns'])
correlation_matrix = daily_returns.corr()
div_score, div_percentage = calculate_diversification_score(portfolio_weights, correlation_matrix)

# Print results and plot
print_portfolio_analysis(metrics, risk_metrics, div_score, div_percentage, max_drawdown)
plot_returns_distribution(risk_metrics['rolling_returns'], 
                        portfolio_value,
                        risk_metrics['value_at_risk'],
                        metrics['annualized_return'])