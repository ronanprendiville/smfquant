import yahoo_api as datareader
import datetime
from db_engine import DbEngine

tickers = ["MSFT", "AAPL", "AMZN"]
start = datetime.datetime(2017, 11, 10)
end = datetime.datetime(2018, 11, 10)
data = datareader.get_price_dataframe(tickers, start, end)

db = DbEngine()
pe_df = db.fetch_db_dataframe("pe_table")


def get_percentage_change_dictionary(dataframe, stocks):
    """Returns the percentage change in the stock price for a stock contained in a pandas dataframe.
    Uses the function (last-first)/first.
    Note that a pandas dataframe has a unique way of accessing an index. More on this online.
    """
    pct_change_dict = {}
    for stock in stocks:
        pc_change = (dataframe.iloc[-1][stock]-dataframe.iloc[0][stock])/dataframe.iloc[0][stock]
        pct_change_dict[stock] = pc_change

    return pct_change_dict


def get_pe_dictionary(pe_values, stocks):
    pe_dict = {}
    for stock in stocks:
        pe_dict[stock] = pe_values[(pe_values.Ticker == stock)].iloc[0]["PE"]
    return pe_dict


def rank_values(dictionary, by="High to Low"):
    """A Function Which:
    (i) Sorts a dictionary of values
    (ii) Creates dictionary containing each stock and associated ranks
    (iii) Returns dictionary created in (iii)"""

    # (i)
    # Note that the sorted function returns a list of tuples - try a print statement to see this.
    # At the end of the sorted function you'll see what's called an 'anonymous function'.
    # This anonymous function tells sorted what to sort by.
    # If instead of kv[1] we had kv[0] it would sort by stock ticker instead of % price changes
    # kv is just an abbreviation of 'key value', kv can be changed to anything at all.
    sorted_by_pc_change = sorted(dictionary.items(), key=lambda kv: kv[1])

    # Try uncommenting these print statements and running the function to understand better how our sorted list works.
    # print(sorted_by_pc_change)
    # print(sorted_by_pc_change[0])
    # print(sorted_by_pc_change[0][0])

    # (ii)
    # Number of stocks = len(sorted_by_pc_change)
    rank_dict = {}
    if by == "High to Low":
        for i in range(0, len(sorted_by_pc_change)):
            rank_dict[sorted_by_pc_change[i][0]] = len(sorted_by_pc_change)-i
    elif by == "Low to High":
        for i in range(0, len(sorted_by_pc_change)):
            rank_dict[sorted_by_pc_change[i][0]] = i+1
    # (iii)
    return rank_dict


pe_dictionary = get_pe_dictionary(pe_df, tickers)
print(pe_dictionary)

ranked_by_pe = rank_values(pe_dictionary, by="Low to High")
print(ranked_by_pe)

prices_dictionary = get_percentage_change_dictionary(data,tickers)
print(prices_dictionary)
ranked_by_price_change = rank_values(prices_dictionary)
print(ranked_by_price_change)

rankings = {key: ranked_by_pe[key] + ranked_by_price_change[key]
            for key in ranked_by_pe}

print(rankings)

