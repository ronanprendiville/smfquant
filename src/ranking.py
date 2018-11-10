import yahoo_api as datareader
import datetime

tickers = ["MSFT", "AAPL", "AMZN"]
start = datetime.datetime(2017, 11, 10)
end = datetime.datetime(2018, 11, 10)

data = datareader.get_price_dataframe(tickers, start, end)


def get_percentage_change(dataframe, stock):
    """Returns the percentage change in the stock price for a stock contained in a pandas dataframe.
    Uses the function (last-first)/first.
    Note that a pandas dataframe has a unique way of accessing an index. More on this online.
    """
    pc_change = (dataframe.iloc[-1][stock]-dataframe.iloc[0][stock])/dataframe.iloc[0][stock]
    return pc_change


def rank_stocks(stocks):
    """A Function Which:
    (i) Creates a dictionary containing each stock and associated percentage change
    (ii) Sorts this dictionary
    (iii) Creates dictionary containing each stock and associated ranks
    (iv) Returns dictionary created in (iii)"""

    # (i)
    # A dictionary is a data structure containing keys and values
    # A dictionary is created using {} as opposed to an array which uses []
    # In this case our keys are tickers and values are % price changes
    pct_change_dict = {}
    for stock in stocks:
        pct_change_dict[stock] = get_percentage_change(data, stock)
    # print(pct_change_dict)

    # (ii)
    # Note that the sorted function returns a list of tuples - try a print statement to see this.
    # At the end of the sorted function you'll see what's called an 'anonymous function'.
    # This anonymous function tells sorted what to sort by.
    # If instead of kv[1] we had kv[0] it would sort by stock ticker instead of % price changes
    # kv is just an abbreviation of 'key value', kv can be changed to anything at all.
    sorted_by_pc_change = sorted(pct_change_dict.items(), key=lambda kv: kv[1])

    # Try uncommenting these print statements and running the function to understand better how our sorted list works.
    # print(sorted_by_pc_change)
    # print(sorted_by_pc_change[0])
    # print(sorted_by_pc_change[0][0])

    # (iii)
    # Number of stocks = len(sorted_by_pc_change)
    rank_dict = {}
    for i in range(0, len(sorted_by_pc_change)):
        rank_dict[sorted_by_pc_change[i][0]] = len(sorted_by_pc_change)-i

    # (iv)
    return rank_dict


# print(rank_stocks(tickers))
