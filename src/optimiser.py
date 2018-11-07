import yahoo_api as datareader
import pandas as pd
import numpy as np
import datetime

# Calculates the mean, variance and standard deviation of a list of values
# given by the 'prices' argument.

""" Test Stocks
"""
stocks = ["MSFT", "AAPL", "AMZN"]
start = datetime.datetime(2017, 2, 11)
end = datetime.datetime(2018, 2, 11)

# Get closing prices for chosen stocks and calculate % returns
closing_prices_df = datareader.get_price_dataframe(stocks, start, end) # pd.DataFrame(columns=stocks)
returns_df = closing_prices_df.pct_change()

# Get mean and covariance of stock returns
mean_historical_returns_df = returns_df.mean()
covariance_of_returns_df = returns_df.cov()

# Just a randomised set of weights for now
np.random.seed()
weights = pd.DataFrame(np.random.uniform(low=0, high=1 ,size=(1,3)), columns=stocks)

# Rescale weights so that their sum is one
weights_divisor = weights.sum(axis=1)[0]
weights = weights.truediv(weights_divisor)

# Get the return and s.d. of the portfolio with corresponding weights
portfolio_return = weights.dot(mean_historical_returns_df).values[0]*252
portfolio_standard_deviation = np.sqrt(weights.dot(covariance_of_returns_df).dot(weights.transpose()).values[0][0]) * np.sqrt(252)