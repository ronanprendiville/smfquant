import pandas as pd
import pandas_datareader as pdr
import numpy as np
import matplotlib.pyplot as plt
from db_engine import DbEngine
import requests
import datetime

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
    prices_of_top_30 = prices.loc[:,tickers]

    # Gets the mean of (daily) historical log returns and the covariance of stock log returns.
    log_returns = np.log(prices_of_top_30).diff()
    mean = log_returns.mean()
    covariances = log_returns.cov()
    return mean, covariances


def simulate_portfolios(tickers, num_of_portfolios, returns, covariances, risk_free_rate):
    """Returns a DataFrame with the following columns: 'Return', 'Volatility', 'Sharpe Ratio', '<stock>',
    with each row index representing a specific portfolio with a different set of generated weights.
    Parameters:
        num_of_portfolios: The number of portfolios we wish to generate
        returns: DataFrame of stock returns
        covariances: DataFrame of covariances of stock returns"""

    returns = np.array(returns)
    num_of_stocks = len(returns)
    covariances = np.array(covariances)
    
    random_weights = np.random.random(size=(num_of_portfolios, num_of_stocks))
    random_weights = random_weights/random_weights.sum(axis=1).reshape(-1,1)

    # Explanation of theory:
    # https://faculty.washington.edu/ezivot/econ424/portfolioTheoryMatrix.pdf

    # Note: @ is matrix multiplication, * is elementwise multiplication

    # Find the mean return for each simulated portfolio
    mean_return  = (random_weights @ returns) 
    # Equivalent to 
    # mean_return = np.array([weight.dot(returns) for weight in random_weights])
    
    # Find the variance of returns for each simulated portfolio
    variance_return  = (random_weights @ covariances * random_weights).sum(axis=1)
    # Equivalent to 
    # np.array([weight.T @ covariances @ weight for weight in random_weights])
    
    volatility = np.sqrt(variance_return)
    sharpe = (mean_return - risk_free_rate)/volatility
    
    simulated_portfolios = pd.DataFrame(data=random_weights, columns=tickers)
    simulated_portfolios.insert(0, column="Return", value=mean_return)
    simulated_portfolios.insert(1, column="Volatility", value=volatility)
    simulated_portfolios.insert(2, column="Sharpe Ratio", value=sharpe)
    
    return simulated_portfolios


def get_exchange_rate():
    """Returns most recent daily exchange rate for given currencies with USD.
    Uses currencylayer API first then tries pandas datareader (source: FRED),
    which has a less up-to-date rate. Function currently only allows EUR.
    NOTE: If access_key is expired/invalid, another one can be obtained from https://currencylayer.com/.
    Just sign up with a free account."""
    access_key = '850e3fc0a17849d164d52a579e381b61';
    params = {
        'access_key': access_key,
        'currencies': 'EUR',
        'format': 1
    }
    url = 'http://apilayer.net/api/live'

    try:
        r = requests.get(url,params)
        live_quote = r.json()
        fx_rate = live_quote['quotes']['USDEUR']
        date_of_rate = datetime.date.fromtimestamp(live_quote['timestamp'])
    except:
        print('-I- Could not fetch FX rate from currencylayer API. Using FRED API instead.')
        quote = pdr.DataReader('DEXUSEU', 'fred')
        today = datetime.datetime.now()
        fx_rate = quote.asof(today).iloc[0]
        date_of_rate = quote.loc[quote['DEXUSEU']==fx_rate].iloc[-1].name

    fx_rate = fx_rate if fx_rate>1 else 1/fx_rate
    print('-I- Using EURUSD rate of', fx_rate, 'as of', date_of_rate)

    return(fx_rate)


def create_optimiser_table(max_sharpe_portfolios, max_sharpe_index, portfolio_allocation):
    eurusd = get_exchange_rate()
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
for i in range(0, num_of_simulations):
    portfolios = simulate_portfolios(stocks, num_of_portfolios, mean_historical_returns, covariance_of_returns, risk_free_rate)
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