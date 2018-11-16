import yahoo_api as datareader
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import glob
import pprint

# These input arrays will be used to find portfolios with a specific
# risk/return level. Each element (which has to be between 0 and 1)
# represents a point along our range of possible values, e.g.
# if the range of portfolio returns in our simulation
# is [0,10], the target return will give portfolios with return values
# of approximately [2.5, 5.0, 7.5] with the least risk. Same with risk_preference
risk_preference = [0.25, 0.50, 0.75]
target_return = [0.25, 0.50, 0.75]

stocks = ["MSFT", "AAPL", "AMZN"]
start = datetime.datetime(2017, 2, 11)
end = datetime.datetime(2018, 2, 11)


def check_for_csv(csv_name):
    """Returns a boolean indicating if there is already a csv file
    with a name given by the csv_name parameter. Returns True if the csv
    exists in the current directory (src), False otherwise"""
    extension = 'csv'
    result = [i for i in glob.glob('*.{}'.format(extension))]
    return result.count(csv_name) > 0


def calculate_optimiser_inputs(tickers, start, end):
    """Returns two pandas DataFrames: mean (daily) returns for each
     stock in tickers and matrix of covariances between stocks' returns."""

    # Checks if the csv file for stock prices already exists in the local directory
    # If not, get the local prices directly from Yahoo! Finance
    if not check_for_csv('storedata.csv'):
        datareader.store_data_csv(tickers, start, end)

    # Stores the csv file into a DataFrame and fixes the date column so that
    # it is a datetime index as opposed to a specific column in the DataFrame
    closing_prices = pd.read_csv('storedata.csv', sep=',')
    closing_prices['Date'] = pd.to_datetime(closing_prices['Date'])
    closing_prices.set_index('Date', inplace=True)

    # Gets the mean of (daily) historical returns and the covariance of stock returns, stored in DataFrames.
    # To see the output of this, uncomment the three lines below and run the code
    returns = closing_prices.pct_change()
    mean = returns.mean()
    covariances = returns.cov()
    return mean, covariances

if check_for_csv('storedata.csv'): print('storedata.csv\n', pd.read_csv('storedata.csv',sep=',').head())
# meanTest, covariancesTest = calculate_optimiser_inputs(stocks, start, end)
# print("Matrix of Stock Returns\n", meanTest)
# print("\n\nCovariance of Stock Returns\n", covariancesTest)


def simulate_portfolios(tickers, num_of_portfolios, num_of_stocks, returns, covariances, risk_free_rate):
    """Returns a DataFrame with the following columns: 'Return', 'Volatility', 'Sharpe Ratio', '<stock> Weight',
    with each row index representing a specific portfolio with a different set of generated weights.
    Parameters:
        num_of_portfolios: The number of portfolios we wish to generate
        num_of_stocks: The number of stocks that will be included in the optimiser
        returns: DataFrame of stock returns
        covariances: DataFrame of covariances of stock returns
    To see the output for some of these, just uncomment the print lines of interest, then run the code."""

    # Initialises the pseudo-random number generator so that a different set of weights
    # is generated for each simulation.
    np.random.seed()

    # We initalise our arrays here, outside the for loop. Values are subsequently stored
    # into these arrays for every iteration in the loop.
    portfolio_returns = []
    portfolio_volatility = []
    portfolio_weights = []
    portfolio_sharpe_ratio = []

    for single_portfolio in range(num_of_portfolios):
        # Generates a random 'vector' of weights and then
        # scale the weights so that they sum to one (representing 100% of our capital)
        simulated_weights = np.random.random(num_of_stocks)
        simulated_weights /= np.sum(simulated_weights)

        # Calculates the portfolio's mean and volatility (standard deviation) of (daily) returns,
        # and the Sharpe Ratio, which is the risk-adjusted return (return for each unit of risk)
        # For a graphical picture, have a look at the following article (pg. 4,5)
        # https://faculty.washington.edu/ezivot/econ424/portfolioTheoryMatrix.pdf
        mean_return = np.dot(simulated_weights, returns)
        volatility = np.sqrt(np.dot(simulated_weights.T, np.dot(covariances, simulated_weights)))
        sharpe_ratio = (mean_return - risk_free_rate) / volatility

        # Print code for those who want to see what the values look like:
        # if single_portfolio == 0:
        #     print("simulated weights:", simulated_weights)
        #     print("\nportfolio mean daily return:", simulated_weights)
        #     print("\nportfolio volatility:", volatility)
        #     print("\nsharpe ratio:", sharpe_ratio)

        # Stores our calculated values into the arrays that we initialised before this loop
        portfolio_returns.append(mean_return)
        portfolio_volatility.append(volatility)
        portfolio_weights.append(simulated_weights)
        portfolio_sharpe_ratio.append(sharpe_ratio)

    # Here, I am cleaning up the data into an easy-to-read form.
    # I store the data from the portfolios, including the weight apportioned to each stock,
    # into a dictionary.
    portfolios = {
        'Return': portfolio_returns,
        'Volatility': portfolio_volatility,
        'Sharpe Ratio': portfolio_sharpe_ratio
    }
    for counter,stock in enumerate(tickers):
        portfolios[stock+' Weight'] = [weight[counter] for weight in portfolio_weights]
    column_order = ['Return', 'Volatility', 'Sharpe Ratio'] + [stock+' Weight' for stock in tickers]
    # print("\ncolumn order:",column_order)

    # The dictionary is then passed into a DataFrame object to make it look nice.
    simulated_portfolios = pd.DataFrame(portfolios, columns=column_order)

    # print("\n",simulated_portfolios.head())
    return simulated_portfolios

def get_portfolio_ranges(portfolios):
    """Returns a dictionary containing the range of mean returns and
    volatility of returns in the set of simulations. This is primarily
    used for getting the portfolios with a risk and return preference
    as explained at the beginning of this script."""

    range_dict = {
        'Return': {
            'min': portfolios['Return'].min(),
            'max': portfolios['Return'].max()
        },
        'Volatility': {
            'min': portfolios['Volatility'].min(),
            'max': portfolios['Volatility'].max()
        }
    }
    for key in range_dict:
        range_dict[key]['range'] = range_dict[key]['max'] - range_dict[key]['min']
    # print("Dictionary of Ranges")
    # pprint.pprint(range_dict)
    return range_dict


def plot_portfolios(portfolios, min_vol_port, max_ret_port, risk_spec_port, ret_spec_port):
    """This function will plot the simulated portfolios with risk (standard deviation)
    on the x-axis and return on the y-axis.
    The plot includes the portfolios of minimum volatility and maximum Sharpe ratio.
    I have also included portfolios which were specified for a given level of risk or level of return.
    The lines represent the actual level, and the points represent the most optimal portfolio
    for that specified level of return/risk:
        '+' for return-specified portfolio
        'v' (upside-down triangle) for risk-specified portfolio)"""

    plt.style.use('seaborn-dark')
    plt.autoscale(tight=True)
    plt.grid(True)
    plt.xlabel('Volatility (Standard Deviation)')
    plt.ylabel('Expected Returns')
    plt.title('Efficient Frontier')

    plt.scatter(portfolios['Volatility'], portfolios['Return'], s=3, c=portfolios['Sharpe Ratio'], cmap='RdYlGn')

    colorbar = plt.colorbar()
    colorbar.set_label('Sharpe Ratio')

    # Plots the points/portfolios of minimum volatility and maximum sharpe ratio
    min_volatility_plot = plt.scatter(min_vol_port['Volatility'], min_vol_port['Return'], c='red', s=100, marker='*')
    max_risk_adjusted_return_plot = plt.scatter(max_ret_port['Volatility'], max_ret_port['Return'], c='blue', s=100, marker='*')

    # Plots the points/portfolios for specified levels of return and risk
    risk_specified_plot = plt.scatter(risk_specified_portfolios['Volatility'],risk_specified_portfolios['Return'], c='purple', s=50, marker='v')
    return_specified_plot = plt.scatter(return_specified_portfolios['Volatility'],return_specified_portfolios['Return'], c='black', s=50, marker='+')
    for risk_val in risk_specified_portfolios['Choice of Risk']:
        plt.axvline(risk_val, linestyle='--', linewidth=0.4, color='purple')
    for return_val in return_specified_portfolios['Choice of Return']:
        plt.axhline(return_val, linestyle='--', linewidth=0.4, color='black')

    legend_handles = [min_volatility_plot, max_risk_adjusted_return_plot, risk_specified_plot, return_specified_plot]
    legend_labels = ['Portfolio of Lowest Volatility', 'Portfolio of Largest Risk-Adjusted Return', 'Risk-Specified Portfolio', 'Return-Specified Portfolio']
    plt.legend(handles=legend_handles, labels=legend_labels)
    plt.show()


"""This is where I begin the implementation of the optimiser.
"""
risk_free_rate = 0.0

# Calculate the mean returns and covariance of returns
mean_historical_returns, covariance_of_returns = calculate_optimiser_inputs(stocks, start, end)

# Specify the number of portfolios of varying weights we want to generate
num_of_portfolios = 50000
num_of_stocks = len(stocks)

portfolios = simulate_portfolios(stocks, num_of_portfolios, num_of_stocks, mean_historical_returns, covariance_of_returns, risk_free_rate)

"""Portfolios of interest (minimum volatility and maximum sharpe ratio)
"""
min_volatility = portfolios['Volatility'].min()
min_volatility_portfolio = portfolios.loc[portfolios['Volatility'] == min_volatility]

max_sharpe_ratio = portfolios['Sharpe Ratio'].max()
max_sharpe_ratio_portfolio = portfolios.loc[portfolios['Sharpe Ratio'] == max_sharpe_ratio]

""" User-specified portfolios
"""
portfolio_ranges = get_portfolio_ranges(portfolios)
range_tolerance = 1 / np.sqrt(num_of_portfolios)
risk_specified_portfolios = pd.DataFrame()
return_specified_portfolios = pd.DataFrame()

# Gets the actual risk value/s corresponding to each value given in the risk_preference array,
# gets all the portfolios that are within a certain range of the risk value/s, and picks
# the portfolio with the greatest return for that given level of risk
for value in risk_preference:
    risk_value = portfolio_ranges['Volatility']['min'] + value*(portfolio_ranges['Volatility']['max'] - portfolio_ranges['Volatility']['min'])
    risk_range_tolerance = range_tolerance*portfolio_ranges['Volatility']['range']
    portfolios_in_range = portfolios.loc[abs(portfolios['Volatility']-risk_value) <= risk_range_tolerance]
    max_return_portfolio = portfolios_in_range.loc[portfolios_in_range['Return'] == portfolios_in_range['Return'].max()]
    max_return_portfolio.insert(0, "Choice of Risk", risk_value)
    risk_specified_portfolios = risk_specified_portfolios.append(max_return_portfolio, ignore_index=True)

# Gets the actual return value/s corresponding to each value given in the target_return array,
# gets all the portfolios that are within a certain range of the return value/s, and picks
# the portfolio with the lowest risk for that given level of return
for value in target_return:
    return_value = portfolio_ranges['Return']['min'] + value*(portfolio_ranges['Return']['max'] - portfolio_ranges['Return']['min'])
    return_range_tolerance = range_tolerance*portfolio_ranges['Return']['range']
    portfolios_in_range = portfolios.loc[abs(portfolios['Return']-return_value) <= return_range_tolerance]
    min_risk_portfolio = portfolios_in_range.loc[portfolios_in_range['Volatility'] == portfolios_in_range['Volatility'].min()]
    min_risk_portfolio.insert(0, "Choice of Return", return_value)
    return_specified_portfolios = return_specified_portfolios.append(min_risk_portfolio, ignore_index=True)

plot_portfolios(portfolios, min_volatility_portfolio, max_sharpe_ratio_portfolio, risk_specified_portfolios, return_specified_portfolios)