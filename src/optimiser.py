import pandas as pd
import pandas_datareader as pdr
import numpy as np
import matplotlib.pyplot as plt
from db_engine import DbEngine

# User-Defined Inputs
new_portfolio_name = "optimised_portfolio_2"
new_portfolio_allocation = 95000
risk_free_rate = 0.0
num_of_simulations = 3
num_of_portfolios = 50

def calculate_optimiser_inputs(tickers):
    """Returns two pandas DataFrames: mean (daily) returns for each
     stock in tickers and matrix of covariances between stocks' returns."""

    prices = db.fetch_db_dataframe("closing_prices_s_and_p")

    prices_of_top_30 = pd.DataFrame(prices["Date"])
    for stock in tickers:
        prices_of_top_30 = prices_of_top_30.join(prices[stock])
    prices_of_top_30["Date"] = pd.to_datetime(prices_of_top_30["Date"])
    prices_of_top_30.set_index("Date", inplace=True)
    # Stores the csv file into a DataFrame and fixes the date column so that
    # it is a datetime index as opposed to a specific column in the DataFrame
    # closing_prices = pd.read_csv('storedata.csv', sep=',')
    # closing_prices['Date'] = pd.to_datetime(closing_prices['Date'])
    # closing_prices.set_index('Date', inplace=True)

    # Gets the mean of (daily) historical returns and the covariance of stock returns, stored in DataFrames.
    # To see the output of this, uncomment the three lines below and run the code
    returns = prices_of_top_30.pct_change()
    mean = returns.mean()
    covariances = returns.cov()
    return mean, covariances


def simulate_portfolios(tickers, num_of_portfolios, num_of_stocks, returns, covariances, risk_free_rate):
    """Returns a DataFrame with the following columns: 'Return', 'Volatility', 'Sharpe Ratio', '<stock>',
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
        portfolios[stock] = [weight[counter] for weight in portfolio_weights]
    column_order = ['Return', 'Volatility', 'Sharpe Ratio'] + [stock for stock in tickers]
    # print("\ncolumn order:",column_order)

    # The dictionary is then passed into a DataFrame object to make it look nice.
    simulated_portfolios = pd.DataFrame(portfolios, columns=column_order)

    # print("\n",simulated_portfolios.head())
    return simulated_portfolios


def create_optimiser_table(max_sharpe_portfolios, max_sharpe_index, portfolio_allocation):
    eurusd = pdr.DataReader('DEXUSEU', 'fred').iloc[-1][0]
    optimiser_dict = max_sharpe_portfolios[max_sharpe_index].iloc[0][3:].mul(portfolio_allocation).to_dict()
    optimiser_stocks = list(optimiser_dict.keys())
    optimiser_amounts = list(optimiser_dict.values())

    optimiser_stocks_dict = {}
    optimiser_amounts_dict = {}
    for count, value in enumerate(optimiser_stocks): optimiser_stocks_dict[count] = value
    for count, value in enumerate(optimiser_amounts): optimiser_amounts_dict[count] = value

    optimiser_dict = {
        'Stock': optimiser_stocks_dict,
        'Amount': optimiser_amounts_dict,
        'Number of Shares': {},
        'Rounded Off': {},
        'Rounded Down': {},
        'Rounded Up': {},
        'Amount Rounded Off': {},
        'Amount Rounded Down': {},
        'Amount Rounded Up': {},
        'Share Price': {}
    }

    for index, val in enumerate(optimiser_dict['Amount']):
        stock_name = optimiser_dict['Stock'][index]
        amount = optimiser_dict['Amount'][index]/eurusd
        last_price = pdr.DataReader(stock_name, data_source='yahoo', start=2018-11-26, end=2018-11-26).iloc[-1][stock_name]/eurusd
        num_of_shares = amount / last_price
        rounded_off = np.round(num_of_shares)
        rounded_up = np.ceil(num_of_shares)
        rounded_down = np.floor(num_of_shares)
        optimiser_dict['Number of Shares'][index] = num_of_shares
        optimiser_dict['Rounded Off'][index] = rounded_off
        optimiser_dict['Rounded Up'][index] = rounded_up
        optimiser_dict['Rounded Down'][index] = rounded_down
        optimiser_dict['Share Price'][index] = last_price
        optimiser_dict['Amount Rounded Off'][index] = last_price * rounded_off
        optimiser_dict['Amount Rounded Up'][index] = last_price * rounded_up
        optimiser_dict['Amount Rounded Down'][index] = last_price * rounded_down

    total = {
        'Stock': 'TOTALS',
        'Amount': sum(optimiser_dict.get('Amount').values()),
        'Share Price': 0,
        'Number of Shares': sum(optimiser_dict.get('Number of Shares').values()),
        'Rounded Off': sum(optimiser_dict.get('Rounded Off').values()),
        'Amount Rounded Off': sum(optimiser_dict.get('Amount Rounded Off').values()),
        'Rounded Up': sum(optimiser_dict.get('Rounded Up').values()),
        'Amount Rounded Up': sum(optimiser_dict.get('Amount Rounded Up').values()),
        'Rounded Down': sum(optimiser_dict.get('Rounded Down').values()),
        'Amount Rounded Down': sum(optimiser_dict.get('Amount Rounded Down').values())
    }
    column_order = ['Stock', 'Amount', 'Share Price', 'Number of Shares', 'Rounded Off',
                    'Amount Rounded Off', 'Rounded Up', 'Amount Rounded Up', 'Rounded Down', 'Amount Rounded Down']

    final_optimiser_df = pd.DataFrame(optimiser_dict, columns=column_order).append(total, ignore_index=True).set_index('Stock')

    return final_optimiser_df


def plot_portfolios(portfolios, max_ret_port):
    """This function will plot the simulated portfolios with risk (standard deviation)
    on the x-axis and return on the y-axis.
    The plot includes the portfolios of minimum volatility and maximum Sharpe ratio."""

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
    max_risk_adjusted_return_plot = plt.scatter(max_ret_port['Volatility'], max_ret_port['Return'], c='blue', s=100, marker='*')

    legend_handle = [max_risk_adjusted_return_plot]
    legend_label = ['Portfolio of Largest Risk-Adjusted Return']
    plt.legend(handles=legend_handle, labels=legend_label)
    plt.show()


"""This is where I begin the implementation of the optimiser.
"""

# Initialise Database Engine
db = DbEngine()

# Get list of top-ranked stocks and store it in an array
ranked_scores = db.fetch_db_dataframe("rankings_table")
top_ranking_scores = ranked_scores.nsmallest(30, "Ranking_Score")
stocks = [stock for stock in top_ranking_scores["Ticker"]]

# Calculate the mean returns and covariance of returns
mean_historical_returns, covariance_of_returns = calculate_optimiser_inputs(stocks)

# Run simulations and store the max-sharpe-ratio portfolio at the end of each one
max_sharpe_simulation = []
num_of_stocks = len(stocks)
for i in range(0, num_of_simulations):
    portfolios = simulate_portfolios(stocks, num_of_portfolios, num_of_stocks, mean_historical_returns, covariance_of_returns, risk_free_rate)
    max_sharpe_ratio = portfolios['Sharpe Ratio'].max()
    max_sharpe_ratio_portfolio = portfolios.loc[portfolios['Sharpe Ratio'] == max_sharpe_ratio]
    max_sharpe_simulation.append(max_sharpe_ratio_portfolio)

# Get the portfolio with the greatest sharpe ratio
max_sharpes = []
for i in range(0, num_of_simulations): max_sharpes.append(max_sharpe_simulation[i].iloc[0]['Sharpe Ratio'])
max_sharpe_index = max_sharpes.index(max(max_sharpes))

# Save a db table with portfolio info (return, volatility and sharpe ratio)
portfolio_info_df = pd.DataFrame(data=max_sharpe_simulation[max_sharpe_index].iloc[0][0:3])
portfolio_info_df.columns = ['Value']
db.delete_table(new_portfolio_name + '_info')
db.create_db_dataframe(portfolio_info_df, new_portfolio_name + '_info')

# Create the final output table from the optimiser and save to db
final_optimiser_df = create_optimiser_table(max_sharpe_simulation, max_sharpe_index, new_portfolio_allocation)
db.delete_table(new_portfolio_name)
db.create_db_dataframe(final_optimiser_df, new_portfolio_name)

# plot_portfolios(portfolios, max_sharpe_ratio_portfolio)