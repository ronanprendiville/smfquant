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