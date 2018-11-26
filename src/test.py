# import __hello__
# print("Use this file to practice interacting with git")
# print("Test out writing some random python")
# print("Ronan Brendan Prendiville is a fraud.")
# print("Short Tesla")
# print(2+2)
# print('Hello World')
# print('DSFSDFSDFSDFSDFf')
#
#
# """
# When you are ready to update the online version of the project
# (called as the remote repository, as opposed to your local repository which is on your computer)
# write the following commands in your terminal (found at bottom left of screen):
#
# - "git fetch": This command will go and check what the state of the remote repository is
# - "git status": This will compare your local and the remote repo and will output the status
# - "git pull": If git status says something along the lines of "you are x commits behind master",
# this means that your local repo is outdated and you will need to use git pull to update it.
# - "git add .": Run this command and git will start tracking the changes you have made.
# - "git commit -m "<insert message>" ": This will stage your changes to be uploaded. After -m insert
# a short message in quotes highlighting what was done in this commit e.g git commit -m "Wrote yahoo
# data retrieval function"
# - "git push": This pushes your local changes to the remote repository, updating it. Once this is
# done, others will need to git pull to retrieve your changes.
#
# Note: you may wish to only make an update to 1 file instead of the entire project. To do this
# use git add <filename> as opposed to git add . - the "." implies all files.
#
# """
#
# print("Hey Guys.. what's up!!!")
# print("Hey!")
# print("Testing")
#
# print("Hello Nathan")
#
# print("Hello")
#
# print("Hi")
#
# print("Mathletico > Matrix")
#
# print("Markowitz Team")
# print("git test")
#
# print("HHHHHHHHHHH")
# print("Hello")
#
# # Hey Clodagh, use the following code to insert rows into closing_prices table
# import db_functions as db
#
# # this is an example lst that. Your list needs to be of this format to insert into closing_prices
# lst = [
#         ('2017-11-02','63.107017517089844','165.0301971435547','54.87678146362305','86.27063751220703','1025.5799560546875'),
#         ('2017-11-03','63.507720947265625','169.33978271484375','54.750465393066406','84.7224349975586','1032.47998046875')
#       ]
#
# # to insert into closing_prices
# db.insert_closing_prices(lst)
#
# # prints out the rows from closing_prices
# db.select_closing_prices()
#
# # just a helper function if you want to execute any queries
# db.execute("DELETE from closing_prices")


# import numpy as np
# import pandas as pd
# import yahoo_api as yahoo
# import datetime
# from sqlalchemy import create_engine
#
# hostname = "smfquant.csu0cjmgqb8i.eu-west-1.rds.amazonaws.com"
# port = '8080'
# username = 'smfquantuser'
# password = 'smfquant2018'
# database = 'smfquant'
#
# stocks = ["JNJ", "ABBV", "HD", "DIS"]
# start = datetime.datetime(2017, 2, 11)
# end = datetime.datetime(2018, 2, 11)
# #
# # data = yahoo.get_price_dataframe(stocks, start, end)
# # print(data.head())
# #
# # engine = create_engine('postgresql://'+username+':'+password+'@'+hostname+':'+port+'/'+database)
# # # writing to database
# # data.to_sql(name='data_table', con=engine, if_exists='replace', index=True)
# # # reading from database
# # data_again = pd.read_sql('SELECT * from data_table', engine)
# # # trim out time component from Date column
# # data_again['Date'] = data_again['Date'].dt.date
# #
# # print(data_again.head())
#
#
# # Example for DB operations, create, append, fetch and delete
# import yahoo_api as yahoo
# import datetime
# from db_engine import DbEngine
# import pandas as pd
#
# db = DbEngine()
# # stocks = ["JNJ", "ABBV", "HD", "DIS"]
# # start = datetime.datetime(2017, 2, 11)
# # end = datetime.datetime(2018, 2, 11)
# # data = yahoo.get_price_dataframe(stocks, start, end)
# # db.create_db_dataframe(data,'test_df1')
# # data_again = db.fetch_db_dataframe('closing_prices_s_and_p')
# # print(data_again)
#
# # db.append_db_dataframe(data, 'test_df1')
# # data_again1 = db.fetch_db_dataframe('test_df1')
# # print(data_again1)
#
#
# # ranked_stocks_df = db.fetch_db_dataframe("rankings_table")
# # # print(ranked_stocks_df)
# # print(ranked_stocks_df.nsmallest(30, "Ranking_Score"))
#
# ranked_scores = db.fetch_db_dataframe("rankings_table")
# sectors = db.fetch_db_dataframe("sector_table")
# prices = db.fetch_db_dataframe("closing_prices_s_and_p")
#
# top30 = ranked_scores.nsmallest(30, "Ranking_Score")
#
# top30prices = pd.DataFrame(prices["Date"])
# # for stock in top30["Ticker"]:
# #     top30temp = prices[stock]
# #     # print(top30temp)
# #     top30prices.join(top30temp)
# #     print(top30prices.join(top30temp))
# # print(len(top30.index))
#
# ranked_scores = db.fetch_db_dataframe("rankings_table")
# top_30_ranking_scores = ranked_scores.nsmallest(30, "Ranking_Score")
# stocks = []
# for stock in top_30_ranking_scores["Ticker"]:
#     stocks.append(stock)
# print(stocks)
#
#
#
#
#
#

import pandas_datareader as pdr
import pandas as pd
import datetime
from db_engine import DbEngine


def get_adj_closing_prices(ticker, start=None, end=None, data_source="yahoo"):
    """Returns a pandas series of adjusted closing prices for a given ticker
    Parameters:
    ticker: The ticker of the company or index to retrieve closing prices from
    start: Start date as either a "yyyy-mm-dd" string or a datetime object. Defaults to one year before the current date
    end: end date as either a "yyyy-mm-dd" string or a datetime object. Defaults to most recent closing price if left blank
    data_source: data source
    """
    if start is None:
        start = datetime.datetime.now() - datetime.timedelta(days=365)
    df = pdr.DataReader(ticker, data_source=data_source, start=start, end=end)
    return df["Adj Close"]


def s_and_p_500_tickers_by_sector():
    """Returns a dictionary of sectors with the corresponding tickers of all the companies in the S&P500
    """
    sectors_tickers={} #dictionary
    wikipedia_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    df = pd.read_html(wikipedia_url,header=0)[0]
    for i in df['GICS Sector'].unique():
        sectors_tickers[i]=[df['Symbol'][j] for j in df[df['GICS Sector']==i].index]
    return sectors_tickers

def store_data_csv(tickers, start, end):
    """Returns a csv file containing adjusted closing prices for a range of tickers.
    tickers = list of indexes of companies
    """

    closing_prices = pd.DataFrame()

    for i in tickers:
        closing_prices[i] = get_adj_closing_prices(i, start, end)
    closing_prices.to_csv("storedata.csv")


def get_price_dataframe(tickers, start, end):
    """Same function as above however it returns a dataframe
    containing adjusted closing prices for a range of tickers """
    closing_prices = pd.DataFrame()
    for i in tickers:
        closing_prices[i] = get_adj_closing_prices(i, start, end)
    return closing_prices


if __name__ == "__main__":
    #The statement if __name__ == "__main__" checks if this file was imported or
    #run directly. If this file was imported, __name__ == "__main__" evaluates to false.

    #The direct result of this is that importing this module using "import yahoo_api" will
    #not cause the test code to run.

    # Examples of how to use functions
    # df = get_price_dataframe(["WELL", "AAPL", "WFC", "WDC", "GOOG"], "2017-11-02", "2018-11-02")
    # print(df)
    # store_data_csv(["WELL", "AAPL", "WFC", "WDC", "GOOG"], "2017-11-02", "2018-11-02")

    #created table in db containing price data for the 500 stocks
    db = DbEngine()

    # db.delete_table('closing_prices_s_and_p')
    sectors_tickers= s_and_p_500_tickers_by_sector()
    # stocks = ['AAPL', 'AMZN', 'GOOG']
    stocks = [stock for sublist in sectors_tickers.values() for stock in sublist]
    try:
        data = get_price_dataframe(stocks, "2017-11-23", "2018-11-23")
    except:
        data = get_price_dataframe(stocks, "2017-11-23", "2018-11-23")
    print(data)
    db.create_db_dataframe(data,'closing_prices_s_and_p')
    data_again = db.fetch_db_dataframe('closing_prices_s_and_p')
    print(data_again)
    db.append_db_dataframe(data, 'closing_prices_s_and_p')
    data_again1 = db.fetch_db_dataframe('closing_prices_s_and_p')
    print(data_again1)