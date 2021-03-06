import scipy.optimize as sco
from db_engine import DbEngine
import numpy as np
import time
import pandas as pd
from itertools import product
import sys
import argparse


def calculate_optimiser_inputs(db, num_stocks, rankings_table, prices_table):
    """Returns two pandas DataFrames: mean (daily) returns for each
     stock in tickers and matrix of covariances between stocks' returns."""

    prices = db.fetch_db_dataframe(prices_table)
    ranked_scores = db.fetch_db_dataframe(rankings_table)
    top_ranking_scores = ranked_scores.nsmallest(num_stocks, "Ranking_Score")
    stocks = list(top_ranking_scores['Ticker'])
    prices_of_top_30 = prices[stocks]

    # Gets the mean of (daily) historical log returns and the covariance of stock log returns.
    log_returns = np.log(prices_of_top_30).diff()
    mean = log_returns.mean()
    covariances = log_returns.cov()
    return mean, covariances


def neg_sharpe(weights, mu, Sigma,
               penalty=0, risk_free_rate=0):
    """
    Calculates the sharpe ratio of a portfolio given a set of weights, 
    expected returns, a covariance matrix and risk_free_rate
    """

    portfolio_sd = np.sqrt(weights @ Sigma.values @ weights * 252)
    portfolio_ev = weights @ mu.values * 252
    sharpe = (portfolio_ev - risk_free_rate)/portfolio_sd
    return -sharpe + penalty * np.sum(weights**2)


class Optimizer:
    def __init__(self, mu, Sigma, bounds=(0, 1),
                 penalty=0, risk_free_rate=0, warnings=False):
        """
        :param mu: Mean of returns
        :param Sigma: Covariance matrix of returns
        :param bounds: Min and max weights to be assigned to any individual 
        stock. Defaults to 0 and 1
        :param penalty: Increasing this results in fewer nonzero weights
        :param risk_free_rate: Risk free rate to be used in sharpe ratio calculations
        :param warnings: Whether to print a warning when the weights don't add
        up to 1
        """

        self._mu = mu
        self._Sigma = Sigma
        self._bounds = bounds
        self._penalty = penalty
        self._risk_free_rate = risk_free_rate
        num_stocks = len(mu)

        res = sco.minimize(
            neg_sharpe,
            args=(mu, Sigma, penalty, risk_free_rate),
            x0=np.random.uniform(size=num_stocks),
            method="SLSQP",
            bounds=[bounds] * num_stocks,
            constraints=[{"type": "eq", "fun": lambda x: np.sum(x) - 1}]
        )

        if warnings and np.abs(np.sum(res.x) - 1) > 0.0001:
            print("WARNING: Weights do not sum up to 1")

        self._weights = res.x

    @property
    def weights(self):
        return self._weights

    @property
    def bounds(self):
        return self._bounds
    
    @property
    def penalty(self):
        return self._penalty

    @property
    def mean(self):
        return self._weights @ self._mu.values * 252
    
    @property
    def sd(self):
        return np.sqrt(self._weights @ self._Sigma.values @ self._weights * 252)

    @property
    def sharpe(self):
        return (self.mean - self._risk_free_rate) / self.sd

    def print_summary(self):
        """Prints a summary of the optimized portfolio
        Includes sharpe ratio, mean and standard deviation as well as the bounds 
        and penalty used
        Also prints the percentage allocated to each stock
        """
        print(50 * "=")
        if np.abs(np.sum(self._weights) - 1) > 0.001:
            print(f"Weights add up to {np.sum(self._weights)}")
        print(f"sharpe: {self.sharpe:.4f} mean: {self.mean:.4f} sd: \
{self.sd:.4f} bounds: {self.bounds} penalty {self.penalty}")
        percent_weights = np.round(100 * self._weights, 2)
        print(sorted(percent_weights, reverse=True))

    def __str__(self):
        percent_weights = np.round(100 * self._weights, 4)
        return " ".join(str(x) for x in (sorted(percent_weights, reverse=True)))

    @property
    def portfolio(self):
        return pd.Series(data=self.weights, index=self._mu.index).sort_values(
            ascending=False
        ).round(6)


if __name__ == "__main__":
    db = DbEngine()
    mu, Sigma = calculate_optimiser_inputs(
        db,
        30,
        "rankings_table_3",
        "closing_prices_s_and_p_3"
    )

    if len(sys.argv) > 1:
        """
        type
        python 5 0.025 0.08 
        in the command line to optimize a portfolio using bounds of (0.025, 0.08)
        and a penalty of 5 and print the results.
        If no command line arguments are specified, this code will not run
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("penalty", nargs="?", default=0, type=float)
        parser.add_argument("lower_bound", nargs="?", default=0, type=float)
        parser.add_argument("upper_bound", nargs="?", default=1, type=float)
        args = parser.parse_args()

        o = Optimizer(mu, Sigma, (args.lower_bound, args.upper_bound), 
                      args.penalty)
        o.print_summary()
        weights = o.weights
        print(o.portfolio)
        print(f"{np.sum(weights - weights.min() < 0.001)} weights at min")
        raise SystemExit

    portfolios_df = pd.DataFrame()
    # A dataframe containing info on all of the portfolios found

    gammas = [0] # Range of penalty values to loop through
    lbs = np.linspace(0.01, 0.44, 100) # Range of lower bounds to loop through
    ubs = np.linspace(0.01, 0.44, 10) # Range of upper bounds to loop through

    for gamma, lb, ub in product(gammas, lbs, ubs):
        if lb >= ub:
            continue
        print(gamma, lb, ub, end="\r")
        o = Optimizer(mu, Sigma, bounds=(lb, ub), penalty=gamma)
        if np.abs(np.sum(o.weights) - 1) > 0.001:
            continue
        params = {"sharpe":o.sharpe, "mean":o.mean, "sd":o.sd, 
                  "bounds":o.bounds, "penalty":o.penalty}
        portfolios_df = portfolios_df.append(params, ignore_index=True)
        #o.print_summary()
    print()
    sorted_pf = portfolios_df.sort_values(by=["sharpe"],
                                          ascending=False)
    # Portfolios ranked by sharpe ratio
    print(sorted_pf)                                    

    sorted_pf[['sharpe', 'bounds', 'penalty']].to_csv("sharpe.csv")
    

