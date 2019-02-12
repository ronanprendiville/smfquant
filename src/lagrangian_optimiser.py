import pandas as pd
import pandas_datareader as pdr
import numpy as np
import matplotlib.pyplot as plt
from db_engine import DbEngine
import requests
import datetime
import optimiser as opt

db = DbEngine()
desired_return = 0.1
rankings_table_name = 'rankings_table_2'
closing_prices_table_name = 'closing_prices_s_and_p_2'
number_of_ranked_stocks = 30
stocks = opt.get_top_ranked_stocks(db, rankings_table_name, number_of_ranked_stocks)

# def get_min_variance(desired_return_level, covariance_matrix, matrix_of_returns):

# Calculate the mean returns and covariance of returns
mean_historical_returns, covariance_of_returns = opt.calculate_optimiser_inputs(db, stocks, closing_prices_table_name)

# 1
returns = mean_historical_returns.values
covariances = covariance_of_returns.values
inv_covariances = np.linalg.inv(covariances)
ones = np.ones(number_of_ranked_stocks)

# 2
a = ones.transpose() @ inv_covariances @ ones
b = ones.transpose() @ inv_covariances @ returns
c = returns.transpose() @ inv_covariances @ returns

# 3
optim_1 = (c - b*desired_return) / (a*c - b**2)
optim_2 = (a*desired_return - b) / (a*c - b**2)

# 4
volatility = optim_1 + optim_2*desired_return
optimal_weights = inv_covariances @ (optim_1*ones + optim_2*returns)
print('desired return', desired_return)
print('volatility', volatility)
print('optimal weights', optimal_weights)