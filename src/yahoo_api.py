import pandas_datareader as pdr
import pandas as pd
import datetime
from db_engine import DbEngine


def s_and_p_500_tickers_by_sector():
    """Returns a dictionary of sectors with the corresponding tickers of all the companies in the S&P500
    """
    sectors_tickers={} #dictionary
    wikipedia_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    df = pd.read_html(wikipedia_url,header=0)[1]
    for i in df['GICS Sector'].unique():
        sectors_tickers[i]=[df['Symbol'][j] for j in df[df['GICS Sector']==i].index]
    return sectors_tickers


def store_data_csv(tickers, start, end):
    """Returns a csv file containing adjusted closing prices for a range of tickers.
    tickers = list of indexes of companies
    """

    closing_prices = pd.DataFrame()

    for i in tickers:
        closing_prices[i] = get_price_dataframe(i, start, end)
    closing_prices.to_csv("storedata.csv")


def get_price_dataframe(ticker_list, start=None, end=None, data_source="yahoo"):
    """Returns a dataframe of adjusted closing prices for the tickers in ticker_list.
    
    Parameters:
    ticker_list: A list of tickers to retrieve closing prices from. Also accepts a single ticker given as a string.
    start: Start date as either a "yyyy-mm-dd" string or a datetime object. Defaults to one year before the current date
    end: end date as either a "yyyy-mm-dd" string or a datetime object. Defaults to most recent closing price if left blank
    data_source: data source. Defaults to yahoo.
    """
    if start is None:
        start = datetime.datetime.now() - datetime.timedelta(days=365)
    df = pdr.DataReader(ticker_list, data_source=data_source, start=start, end=end)
    return df["Adj Close"]


if __name__ == "__main__":
    #The statement if __name__ == "__main__" checks if this file was imported or 
    #run directly. If this file was imported, __name__ == "__main__" evaluates to false.

    #The direct result of this is that importing this module using "import yahoo_api" will 
    #not cause the test code to run. 

    # Examples of how to use functions
    df = get_price_dataframe(["WELL", "AAPL", "WFC", "WDC", "GOOG"], "2017-11-02", "2018-11-02")
    print(df)
    store_data_csv(["WELL", "AAPL", "WFC", "WDC", "GOOG"], "2017-11-02", "2018-11-02")

    #created table in db containing price data for the 500 stocks
    db = DbEngine()
    db.delete_table('closing_prices_s_and_p_2')
    sectors_tickers= s_and_p_500_tickers_by_sector()
    stocks = [stock for sublist in sectors_tickers.values() for stock in sublist]
    data = get_price_dataframe(stocks, "2018-01-28", "2019-01-28")
    db.create_db_dataframe(data,'closing_prices_s_and_p_2')
    data_again = db.fetch_db_dataframe('closing_prices_s_and_p_2')
    print(data_again)
    db.append_db_dataframe(data, 'closing_prices_s_and_p_2')
    data_again1 = db.fetch_db_dataframe('closing_prices_s_and_p_2')
    print(data_again1)
