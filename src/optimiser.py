import pandas as pd
import pandas_datareader as pdr
import numpy as np
import matplotlib.pyplot as plt
from db_engine import DbEngine
import requests
import datetime

# User-Defined Inputs
if __name__ == '__main__':
    new_portfolio_name = 'bmf_test'
    rankings_table_name = 'test_rankings_table'
    closing_prices_table_name = 'test_closing_prices_s_and_p'
    price_for_purchase = 'end'  # string: date of prices to be used for calculating number of shares to buy per stock
                                # 'end' to use last date in closing_prices_table_name or 'today' for latest closing price.
                                # Can also pass a datetime string, e.g. '2018-05-25' to get the price as of that date
    number_of_ranked_stocks = 30
    new_portfolio_allocation = 95000
    risk_free_rate = 0.0
    num_of_simulations = 50000; info_log_frequency = 1000 # Must be a factor of num_of_simulations
    num_of_portfolios = 20000

def get_top_ranked_stocks(db, rankings_table_name, number_of_ranked_stocks):
    """Returns an array containing the top-ranked stocks.
    Parameters:
        rankings_table_name: Name of the db table containing stock rankings
        number_of_ranked_stocks: The number of top-ranked stocks to be retrieved.
    """

    print("-I- Fetching stock rankings from " + rankings_table_name)
    ranked_scores = db.fetch_db_dataframe(rankings_table_name)
    top_ranking_scores = ranked_scores.nsmallest(number_of_ranked_stocks, "Ranking_Score")
    stocks = [stock for stock in top_ranking_scores["Ticker"]]
    return stocks


def calculate_optimiser_inputs(db, tickers, closing_prices_table_name):
    """Returns two pandas DataFrames: mean (daily) returns for each
     stock in tickers and matrix of covariances between stocks' returns."""

    print("-I- Fetching closing prices from " + closing_prices_table_name)
    prices = db.fetch_db_dataframe(closing_prices_table_name)
    prices_of_top_30 = prices.loc[:, tickers]

    # Gets the mean of (daily) historical log returns and the covariance of stock log returns.
    print("-I- Calculating mean daily returns and covariances of returns")
    log_returns = np.log(prices_of_top_30).diff()
    mean = log_returns.mean()
    covariances = log_returns.cov()
    return mean, covariances


def run_simulations(num_of_simulations, num_of_portfolios, returns, covariances, risk_free_rate, info_log_frequency):
    """Returns a pandas DataFrame where each row is the portfolio with the best Sharpe ratio
    from each Monte Carlo simulation.
    """

    print("-I- Beginning Monte-Carlo simulations of " + str(num_of_portfolios) + " portfolios each")

    max_sharpe_portfolio_per_simulation = pd.DataFrame(columns=['Annual Log Return', 'Volatility', 'Sharpe Ratio']+stocks)
    for i in range(0, num_of_simulations):
        portfolios = simulate_portfolios(stocks, num_of_portfolios, returns, covariances, risk_free_rate)
        max_sharpe_ratio = portfolios['Sharpe Ratio'].max()
        max_sharpe_ratio_portfolio = portfolios.loc[portfolios['Sharpe Ratio'] == max_sharpe_ratio]
        max_sharpe_portfolio_per_simulation = max_sharpe_portfolio_per_simulation.append(max_sharpe_ratio_portfolio, ignore_index=True)

        if (i+1) % (num_of_simulations/info_log_frequency) == 0:
            print("-I- Finished " + str(i+1) + "/" + str(num_of_simulations) + " simulations")

    return max_sharpe_portfolio_per_simulation


def simulate_portfolios(tickers, num_of_portfolios, returns, covariances, risk_free_rate):
    """Returns a pandas DataFrame with the following columns: 'Return', 'Volatility', 'Sharpe Ratio', '<stock>',
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
    mean_return = (random_weights @ returns)
    # Equivalent to 
    # mean_return = np.array([weight.dot(returns) for weight in random_weights])
    
    # Find the variance of returns for each simulated portfolio
    variance_return = (random_weights @ covariances * random_weights).sum(axis=1)
    # Equivalent to 
    # np.array([weight.T @ covariances @ weight for weight in random_weights])
    
    volatility = np.sqrt(variance_return)
    sharpe = (mean_return - risk_free_rate)/volatility
    
    simulated_portfolios = pd.DataFrame(data=random_weights, columns=tickers)
    simulated_portfolios.insert(0, column="Annual Log Return", value=mean_return)
    simulated_portfolios.insert(1, column="Volatility", value=volatility)
    simulated_portfolios.insert(2, column="Sharpe Ratio", value=sharpe)
    
    return simulated_portfolios


def get_exchange_rate():
    """Returns most recent daily exchange rate for given currencies with USD.
    Uses currencylayer API first then tries pandas datareader (source: FRED),
    which has a less up-to-date rate. Function currently only allows EUR.
    NOTE: If access_key is expired/invalid, another one can be obtained from https://currencylayer.com/.
    Just sign up with a free account."""

    access_key = '850e3fc0a17849d164d52a579e381b61'
    params = {
        'access_key': access_key,
        'currencies': 'EUR',
        'format': 1
    }
    url = 'http://apilayer.net/api/live'

    try:
        r = requests.get(url, params)
        live_quote = r.json()
        fx_rate = live_quote['quotes']['USDEUR']
        date_of_rate = datetime.date.fromtimestamp(live_quote['timestamp'])
    except:
        print('-I- Could not fetch FX rate from currencylayer API. Using FRED API instead.')
        quote = pdr.DataReader('DEXUSEU', 'fred')
        today = datetime.datetime.now()
        fx_rate = quote.asof(today).iloc[0]
        date_of_rate = quote.loc[quote['DEXUSEU'] == fx_rate].iloc[-1].name

    fx_rate = fx_rate if (fx_rate > 1) else 1/fx_rate
    print('-I- Using EURUSD rate of', np.round(fx_rate, 5), 'as of', date_of_rate)

    return(fx_rate)


def create_optimiser_table(db, price_for_purchase, best_portfolio_weights, portfolio_allocation, closing_prices=closing_prices_table_name):
    """Returns a pandas DataFrame with information on how much capital to allocate to each stock and the corresponding
    number of shares.
    Parameters:
        best_portfolio_weights: A DataFrame representing a portfolio with specific weights ascribed to each stock in the
                                portfolio.
        portfolio_allocation: Amount (in euros) to be invested in the portfolio.

    Table Columns:
        Weight: The exact proportion of the initial capital to be allocated to each stock.
        Amount: The exact amount (in euros) to be allocated to each stock.
        Share Price: Stock price (in euros)
        Number of Shares: The exact number of shares to be bought for each stock.
        Rounded Off: The value of the 'Number of Shares' column rounded off.
        Amount Rounded Off: The cost of buying the number of shares specified by the 'Rounded Off' column.
        Rounded Up: The value of the 'Number of Shares' column rounded up.
        Amount Rounded Up: The cost of buying the number of shares specified by the 'Rounded Up' column.
        Rounded Down: The value of the 'Number of Shares' column rounded down.
        Amount Rounded Down: The cost of buying the number of shares specified by the 'Rounded Down' column.
        ..."""

    print("-I- Creating final table for optimal portfolio")
    if price_for_purchase == 'today':
        end = datetime.datetime.today()
    elif price_for_purchase == 'end':
        end = db.fetch_db_dataframe(closing_prices).iloc[-1,0]
    else:
        end = datetime.strptime(price_for_purchase)

    start = end-datetime.timedelta(days=7)
    end = end.__format__('%Y-%m-%d')
    start = start.__format__('%Y-%m-%d')
    eurusd = get_exchange_rate()

    optimiser_df = pd.DataFrame(best_portfolio_weights).rename(index=str, columns={0:'Weight'})

    amount = optimiser_df.loc[:]['Weight'] * portfolio_allocation
    optimiser_df.insert(len(optimiser_df.columns), 'Amount', amount)

    print("-I- Fetching last closing stock prices")
    share_price = pdr.DataReader(list(optimiser_df.index), data_source='yahoo', start=start, end=end)['Adj Close'].iloc[-1]/eurusd
    optimiser_df.insert(len(optimiser_df.columns), 'Share Price', share_price)

    number_of_shares = optimiser_df.loc[:]['Amount']/optimiser_df.loc[:]['Share Price']
    optimiser_df.insert(len(optimiser_df.columns), 'Number of Shares', number_of_shares)

    rounded_off = optimiser_df[:]['Number of Shares'].apply(lambda x: np.round(x))
    optimiser_df.insert(len(optimiser_df.columns), 'Rounded Off', rounded_off)

    amount_rounded_off = optimiser_df.loc[:]['Share Price'] * optimiser_df.loc[:]['Rounded Off']
    optimiser_df.insert(len(optimiser_df.columns), 'Amount Rounded Off', amount_rounded_off)

    rounded_up = optimiser_df[:]['Number of Shares'].apply(lambda x: np.ceil(x))
    optimiser_df.insert(len(optimiser_df.columns), 'Rounded Up', rounded_up)

    amount_rounded_up = optimiser_df.loc[:]['Share Price'] * optimiser_df.loc[:]['Rounded Up']
    optimiser_df.insert(len(optimiser_df.columns), 'Amount Rounded Up', amount_rounded_up)

    rounded_down = optimiser_df[:]['Number of Shares'].apply(lambda x: np.floor(x))
    optimiser_df.insert(len(optimiser_df.columns), 'Rounded Down', rounded_down)

    amount_rounded_down = optimiser_df.loc[:]['Share Price'] * optimiser_df.loc[:]['Rounded Down']
    optimiser_df.insert(len(optimiser_df.columns), 'Amount Rounded Down', amount_rounded_down)

    optimiser_df = pd.DataFrame(optimiser_df)

    columns = ['Weight', 'Amount', 'Share Price', 'Number of Shares', 'Rounded Off', 'Amount Rounded Off',
               'Rounded Up', 'Amount Rounded Up', 'Rounded Down', 'Amount Rounded Down']
    total = {}
    for column in columns:
        if column == 'Stock':
            total[column] = 'TOTAL'
        elif column == 'Share Price':
            total[column] = 'NA'
        else:
            total[column] = optimiser_df.loc[:][column].sum()
    total = pd.Series(total, name='TOTAL')
    final_optimiser_df = optimiser_df.append(total)

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


if __name__ == "__main__": #The following code will not be run when optimizer.py is imported

    """This is where I begin the implementation of the optimiser.
    """
    
    # Initialise Database Engine
    db = DbEngine()

    # Get list of top-ranked stocks and store it in an array
    stocks = get_top_ranked_stocks(db, rankings_table_name, number_of_ranked_stocks)

    # Calculate the mean returns and covariance of returns
    mean_historical_returns, covariance_of_returns = calculate_optimiser_inputs(db, stocks, closing_prices_table_name)

    # Run simulations and store the max-sharpe-ratio portfolio of each simulation
    max_sharpe_portfolio_per_simulation = run_simulations(num_of_simulations, num_of_portfolios, mean_historical_returns, covariance_of_returns, risk_free_rate, info_log_frequency)
    
    # Get the portfolio with the greatest sharpe ratio
    best_sharpe_ratio = max_sharpe_portfolio_per_simulation['Sharpe Ratio'].max()
    best_portfolio = max_sharpe_portfolio_per_simulation.loc[max_sharpe_portfolio_per_simulation['Sharpe Ratio'] == best_sharpe_ratio].reset_index()
    
    # Save a db table with portfolio info (return, volatility and sharpe ratio)
    print("-I- Fetching portfolio with the greatest Sharpe ratio")
    best_portfolio_info_df = best_portfolio.iloc[0][1:4].rename('Amount')
    best_portfolio_info_df.at['Annual Log Return'] *= 252
    best_portfolio_info_df.at['Volatility'] *= np.sqrt(252)
    best_portfolio_info_df = best_portfolio_info_df.append(pd.Series({'Total No. of Portfolios Generated': num_of_simulations*num_of_portfolios}))

    print("-I- Saving optimal portfolio info to database")
    db.delete_table(new_portfolio_name + '_info')
    db.create_db_dataframe(best_portfolio_info_df, new_portfolio_name + '_info')
    
    # Create the final output table from the optimiser and save to db
    best_portfolio_weights = best_portfolio.iloc[0][4:]
    final_optimiser_df = create_optimiser_table(db,price_for_purchase, best_portfolio_weights, new_portfolio_allocation)

    print("-I- Saving table for optimal portfolio to database")
    db.delete_table(new_portfolio_name)
    db.create_db_dataframe(final_optimiser_df, new_portfolio_name)
    
    # plot_portfolios(portfolios, max_sharpe_ratio_portfolio)