import scipy.optimize as sco
from db_engine import DbEngine
import numpy as np
import time
import pandas as pd

new_portfolio_allocation = 60000
risk_free_rate = 0
bounds = (0, 1) # All weights will be in this range
penalty = 0 # The higher this is, the fewer nontrivial weights there will be

def calculate_optimiser_inputs(tickers):
    """Returns two pandas DataFrames: mean (daily) returns for each
     stock in tickers and matrix of covariances between stocks' returns."""

    prices = db.fetch_db_dataframe("closing_prices_s_and_p_3")
    prices_of_top_30 = prices.loc[:,tickers]

    # Gets the mean of (daily) historical log returns and the covariance of stock log returns.
    log_returns = np.log(prices_of_top_30).diff()
    mean = log_returns.mean()
    covariances = log_returns.cov()
    return mean, covariances

def neg_sharpe(weights, penalty=0):
    portfolio_sd = np.sqrt(weights @ covariance_of_returns.values @ weights * 252)
    portfolio_ev = weights @ mean_historical_returns.values * 252
    sharpe = (portfolio_ev - risk_free_rate)/portfolio_sd
    return -sharpe + penalty * np.sum(weights**2)

def optimise_portfolio_slsqp(mean_historical_returns, 
                            covariance_of_returns, 
                            risk_free_rate=0, 
                            bounds=(0, 1),
                            penalty=0):
    res = sco.minimize(
        neg_sharpe,
        args=(penalty),
        x0=np.random.uniform(size=30),
        method="SLSQP",
        bounds=[bounds] * 30,
        constraints=[{"type": "eq", "fun": lambda x: np.sum(x) - 1}]
    )
    if np.abs(np.sum(res.x) - 1) > 0.0001:
        print("=" * 50 + "\nWARNING: portfolio weights do not sum to 1\n" + "=" * 50)
    return res.x * new_portfolio_allocation

if __name__ == "__main__":
    # Initialise Database Engine


    start = time.time()

    db = DbEngine()

    ranked_scores = db.fetch_db_dataframe("rankings_table_3")
    top_ranking_scores = ranked_scores.nsmallest(30, "Ranking_Score")
    stocks = [stock for stock in top_ranking_scores["Ticker"]]

    # Get list of top-ranked stocks and store it in an array
    # Calculate the mean returns and covariance of returns

    mean_historical_returns, covariance_of_returns = calculate_optimiser_inputs(stocks)
    portfolio = optimise_portfolio_slsqp(mean_historical_returns, 
                              covariance_of_returns,
                              risk_free_rate=risk_free_rate,
                              bounds=bounds,
                              penalty=penalty)
    
    print(np.round(portfolio, 3))
    weights = portfolio/np.sum(portfolio)
    # Percentage allocated to each stock

    portfolio_sd = np.sqrt(weights @ covariance_of_returns.values @ weights * 252)
    portfolio_ev = weights @ mean_historical_returns.values * 252
    sharpe = (portfolio_ev - risk_free_rate)/portfolio_sd

    print("Sharpe Ratio: {}".format(sharpe))
    print("Mean Return: {}".format(portfolio_ev))
    print("Standard Deviation: {}".format(portfolio_sd))

    print("Finished in {} seconds".format(time.time() - start))