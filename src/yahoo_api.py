import pandas_datareader as pdr
import pandas as pd
import datetime


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


def s_and_p_500_tickers():
    """Returns a list of the tickers of every company on the S&P500
    """
    wikipedia_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    df = pd.read_html(wikipedia_url, header=0)[0]
    return list(df['Symbol'])


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
    # Examples of how to use functions
    get_price_dataframe(["WELL", "AAPL", "WFC", "WDC", "GOOG"], "2017-11-02", "2018-11-02")
    store_data_csv(["WELL", "AAPL", "WFC", "WDC", "GOOG"], "2017-11-02", "2018-11-02")
