import yahoo_api as datareader
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt

# Calculates the mean, variance and standard deviation of a list of values
# given by the 'prices' argument.

""" Initial user-specified parameters
"""
risk_free_rate = 0.0
risk_preference = [0.25, 0.50, 0.75]
return_preference = [0.25, 0.50, 0.75]

""" Test Stocks
"""
stocks = ["MSFT", "AAPL", "AMZN"]
start = datetime.datetime(2017, 2, 11)
end = datetime.datetime(2018, 2, 11)

# Get closing prices for chosen stocks and calculate % returns
# datareader.store_data_csv(stocks, start, end)
closing_prices_df = pd.read_csv('storedata.csv', sep=',')
closing_prices_df['Date'] = pd.to_datetime(closing_prices_df['Date'])
closing_prices_df.set_index('Date', inplace=True)

returns_df = closing_prices_df.pct_change()

# Get mean and covariance of stock returns
mean_historical_returns_df = returns_df.mean()
covariance_of_returns_df = returns_df.cov()

""" This is where we simulate the imaginary combinations of portfolios
    for different vectors of weights.
"""
number_of_simulated_portfolios = 5000
number_of_stocks = len(stocks)

portfolio_returns = []
portfolio_volatility = []
portfolio_weights = []
portfolio_sharpe_ratio = []

np.random.seed()
for single_portfolio in range(number_of_simulated_portfolios):
    simulated_weights = np.random.random(number_of_stocks)
    simulated_weights /= np.sum(simulated_weights)
    returns = np.dot(simulated_weights, mean_historical_returns_df)
    volatility = np.sqrt(np.dot(simulated_weights.T, np.dot(covariance_of_returns_df, simulated_weights)))
    sharpe_ratio = (returns - risk_free_rate) / volatility
    portfolio_returns.append(returns)
    portfolio_volatility.append(volatility)
    portfolio_weights.append(simulated_weights)
    portfolio_sharpe_ratio.append(sharpe_ratio)

portfolios = {
    'Return': portfolio_returns,
    'Volatility': portfolio_volatility,
    'Sharpe Ratio': portfolio_sharpe_ratio
}

for counter,stock in enumerate(stocks):
    portfolios[stock+' Weight'] = [weight[counter] for weight in portfolio_weights]

column_order = ['Return', 'Volatility', 'Sharpe Ratio'] + [stock+' Weight' for stock in stocks]
portfolios_df = pd.DataFrame(portfolios, columns=column_order)

""" Finding portfolios of interest
"""

min_volatility = portfolios_df['Volatility'].min()
min_volatility_portfolio = portfolios_df.loc[portfolios_df['Volatility'] == min_volatility]
# print("Portfolio of Minimum Volatility\n", min_volatility_portfolio.T)

max_sharpe_ratio = portfolios_df['Sharpe Ratio'].max()
max_sharpe_ratio_portfolio = portfolios_df.loc[portfolios_df['Sharpe Ratio'] == max_sharpe_ratio]
# print("Portfolio of Maximum Adjusted Return\n", max_sharpe_ratio_portfolio.T)

portfolio_ranges = {
    'Return': {
        'min': portfolios_df['Return'].min(),
        'max': portfolios_df['Return'].max()
    },
    'Volatility': {
        'min': portfolios_df['Volatility'].min(),
        'max': portfolios_df['Volatility'].max()
    }
}
for key in portfolio_ranges:
    portfolio_ranges[key]['range'] = portfolio_ranges[key]['max'] - portfolio_ranges[key]['min']
# print("Range of Portfolio Returns:\n", portfolio_ranges['Return'])
# print("Range of Portfolio Volatility:\n", portfolio_ranges['Volatility'])

""" User-specified portfolios
"""
risk_specified_portfolios = pd.DataFrame()
return_specified_portfolios = pd.DataFrame()
range_tolerance = 1 / np.sqrt(number_of_simulated_portfolios)
print("range tolerance", range_tolerance)
for value in risk_preference:
    risk_value = portfolio_ranges['Volatility']['min'] + value*(portfolio_ranges['Volatility']['max'] - portfolio_ranges['Volatility']['min'])
    risk_range_tolerance = range_tolerance*portfolio_ranges['Volatility']['range']
    portfolios_in_range = portfolios_df.loc[abs(portfolios_df['Volatility']-risk_value) <= risk_range_tolerance]
    max_return_portfolio = portfolios_in_range.loc[portfolios_in_range['Return'] == portfolios_in_range['Return'].max()]
    max_return_portfolio.insert(0, "Choice of Risk", risk_value)
    risk_specified_portfolios = risk_specified_portfolios.append(max_return_portfolio, ignore_index=True)

for value in return_preference:
    return_value = portfolio_ranges['Return']['min'] + value*(portfolio_ranges['Return']['max'] - portfolio_ranges['Return']['min'])
    return_range_tolerance = range_tolerance*portfolio_ranges['Return']['range']
    portfolios_in_range = portfolios_df.loc[abs(portfolios_df['Return']-return_value) <= return_range_tolerance]
    min_risk_portfolio = portfolios_in_range.loc[portfolios_in_range['Volatility'] == portfolios_in_range['Volatility'].min()]
    min_risk_portfolio.insert(0, "Choice of Return", return_value)
    return_specified_portfolios = return_specified_portfolios.append(min_risk_portfolio, ignore_index=True)

print("risk_specified_portfolios:\n",risk_specified_portfolios)
print("return_specified_portfolios:\n",return_specified_portfolios)

plt.style.use('seaborn-dark')
plt.autoscale(tight=True)
plt.grid(True)
plt.scatter(portfolios_df['Volatility'], portfolios_df['Return'], s=3, c=portfolios_df['Sharpe Ratio'], cmap='RdYlGn')
colorbar = plt.colorbar()
colorbar.set_label('Sharpe Ratio')
min_volatility_plot = plt.scatter(min_volatility_portfolio['Volatility'], min_volatility_portfolio['Return'], c='red', s=100, marker='*')
max_risk_adjusted_return_plot = plt.scatter(max_sharpe_ratio_portfolio['Volatility'], max_sharpe_ratio_portfolio['Return'], c='blue', s=100, marker='*')
legend_handle1 = plt.scatter(risk_specified_portfolios['Volatility'],risk_specified_portfolios['Return'], c='purple', s=50, marker='v')
for risk_val in risk_specified_portfolios['Choice of Risk']:
    plt.axvline(risk_val, linestyle='--', linewidth=0.4, color='purple')
for return_val in return_specified_portfolios['Choice of Return']:
    plt.axhline(return_val, linestyle='--', linewidth=0.4, color='black')
legend_handle2 = plt.scatter(return_specified_portfolios['Volatility'],return_specified_portfolios['Return'], c='black', s=50, marker='+')
legend_handles = [min_volatility_plot, max_risk_adjusted_return_plot, legend_handle1, legend_handle2]
legend_labels = ['Portfolio of Lowest Volatility', 'Portfolio of Largest Risk-Adjusted Return', 'Risk-Specified Portfolio', 'Return-Specified Portfolio']
plt.legend(handles=legend_handles, labels=legend_labels)
plt.xlabel('Volatility (Standard Deviation)')
plt.ylabel('Expected Returns')
plt.title('Efficient Frontier')
plt.show()