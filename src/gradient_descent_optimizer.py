from db_engine import DbEngine
import tensorflow as tf
import numpy as np
import time
import pandas as pd

new_portfolio_allocation = 60000
risk_free_rate = 0

def calculate_optimiser_inputs(tickers):
    """Returns two pandas DataFrames: mean (daily) returns for each
     stock in tickers and matrix of covariances between stocks' returns."""

    prices = db.fetch_db_dataframe("closing_prices_s_and_p_2")
    prices_of_top_30 = prices.loc[:,tickers]

    # Gets the mean of (daily) historical log returns and the covariance of stock log returns.
    log_returns = np.log(prices_of_top_30).diff()
    mean = log_returns.mean()
    covariances = log_returns.cov()
    return mean, covariances


def optimise_portfolio_gd(mean_historical_returns, 
                          covariance_of_returns, 
                          risk_free_rate=0, 
                          max_iters=60000):
    """
    Attempts to find an optimized portfolio using Gradient Descent

    :param mean_historical_returns: pandas Series of mean historical returns
    :param covariance_of_returns: pandas Dataframe of covariance of returns
    :param max_iters: Max number of iterations of gradient descent to run.
    :return: Pandas Series representing the optimized portfolio.
    """

    # Commented code is for creating tensorboard graphs

    mu = np.array(mean_historical_returns, dtype=np.float32)
    Sigma = np.array(covariance_of_returns, dtype=np.float32)
    
    num_stocks = Sigma.shape[0]
    
    tf.reset_default_graph()
    #now = dt.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    #root_logdir = "tf_logs2"
    #logdir = f"{root_logdir}/run-{now}"

    Sigma = tf.constant(Sigma, name="Sigma")
    mu = tf.constant(mu.reshape(-1,1), name="mu")
    x = tf.Variable(tf.random.uniform((num_stocks, 1)), name="x")

    with tf.name_scope("scale_inputs"):
        scaled_x = tf.sigmoid(x)
        # There may be better bijective functions that make scaled weights positive
        scaled_x = scaled_x/tf.reduce_sum(scaled_x)

    with tf.name_scope("calc_mean"):
        mu_port = tf.transpose(mu) @ scaled_x

    with tf.name_scope("calc_sd"):
        var_port = tf.transpose(scaled_x) @ Sigma @ scaled_x
        sd_port = tf.sqrt(var_port)

    rfr = tf.constant(risk_free_rate, name="risk_free_rate", dtype=tf.float32)
    
    with tf.name_scope("calc_sharpe"):
        sharpe = (mu_port - rfr)/sd_port

    #sharpe_summary = tf.summary.scalar("Sharpe", tf.reshape(sharpe, []))
    #mu_port_summary = tf.summary.scalar("Expected_Return", tf.reshape(mu_port, []))
    #sd_port_summary = tf.summary.scalar("Volatility", tf.reshape(sd_port, []))
    
    optimizer = tf.train.AdamOptimizer()
    #penalty = reg_strength * tf.norm(scaled_x) # L2 regularization
    
    target = -sharpe #-penalty
    #target_summary = tf.summary.scalar("target", tf.reshape(target, []))
    
    training_op = optimizer.minimize(target, var_list=[x])

    #file_writer = tf.summary.FileWriter(logdir, tf.get_default_graph())
    
    init = tf.global_variables_initializer()
    
    best = 0 # Best sharpe ratio found so far
    iterations_between_reports = 100 # Check how we are doing every 100 iterations
    # Checking every iteration can potentially slow down the program
    reports_since_improvement = 0 
    # Keep track of number of reporting iterations since sharpe ratio improved

    with tf.Session() as sess:
        sess.run(init)
        for i in range(max_iters):
            if i % iterations_between_reports == 0:
                #print("{} iterations completed".format(i))
                target_value = target.eval()
                if target_value < best or i == 0: 
                    # If we have found a better sharpe ratio, save those weights
                    best = target_value
                    best_weights = scaled_x.eval()
                    reports_since_improvement = 0
                else:
                    reports_since_improvement += 1
                
                if reports_since_improvement > 5:
                    # Stop gradient descent if no improvement after 5 reporting iterations
                    print("Gradient Descent stopped after {} iterations".format(i))
                    break
                                
                #file_writer.add_summary(target_summary.eval(), i)
                #file_writer.add_summary(sharpe_summary.eval(), i)
                #file_writer.add_summary(mu_port_summary.eval(), i)
                #file_writer.add_summary(sd_port_summary.eval(), i)

            sess.run(training_op)
        else:
            # for-else loop
            # This code runs if the above for loop never reaches a break statement
            print("Max iterations reached. Increasing max_iters could improve results")
            best_weights = scaled_x.eval()
        #file_writer.close()
        
    portfolio = pd.Series(index=mean_historical_returns.index,
                          data=np.round(best_weights.flatten() * new_portfolio_allocation, 3))
    return portfolio


if __name__ == "__main__":
    # Initialise Database Engine
    start = time.time()

    db = DbEngine()
    ranked_scores = db.fetch_db_dataframe("rankings_table_2")
    top_ranking_scores = ranked_scores.nsmallest(30, "Ranking_Score")
    stocks = [stock for stock in top_ranking_scores["Ticker"]]
    # Get list of top-ranked stocks and store it in an array
    # Calculate the mean returns and covariance of returns

    mean_historical_returns, covariance_of_returns = calculate_optimiser_inputs(stocks)
    portfolio = optimise_portfolio_gd(mean_historical_returns, 
                              covariance_of_returns,
                              risk_free_rate=risk_free_rate)
    
    print(portfolio)
    weights = portfolio.values

    portfolio_sd = np.sqrt(weights @ covariance_of_returns.values @ weights * 252)
    portfolio_ev = weights @ mean_historical_returns.values * 252
    sharpe = (portfolio_ev - risk_free_rate)/portfolio_sd

    print("Sharpe Ratio: {}".format(sharpe))
    print("Mean Return: {}".format(portfolio_ev))
    print("Standard Deviation: {}".format(portfolio_sd))

    print("Finished in {} seconds".format(time.time() - start))