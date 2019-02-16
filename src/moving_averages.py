# Common MA periods: 50,100, 200
# 200 "especially significant in stock trading"
# 50-day MA > 200-day MA => bullish trend ; crossover to the downside of 200-day => bearish trend
# Common EMA: 12 or 26 for short term;  50 and 200 for long-term
# Example:  If 20 DEMA decreases to a crossover with 50 DEMA => bearish
#           If 20 DEMA increases to a crossover with 50 DEMA => bullish
# DEMA general formula: DEMA = 2*EMA(n) - EMA(EMA(n)),    n = period
# Steps to calculating an EMA:
#   1.) Get SMA for the initial EMA value
#   2.) Calculate the weighting multiplier
#   3.) Calculate the EMA for each day between the initial EMA and today, using the price,
#       the multiplier, and the previous period's EMA
#    EMA general formula: EMA = (Close - (previous EMA)) * (2/(n+1)) + (previous EMA)



# Note that I am using Quandl here instead of Yahoo Finance (through Pandas DataReader) as it seems Yahoo Finance!
# API has been discontinued and hence has some data quality issues.
# See: https://quant.stackexchange.com/questions/35019/is-yahoo-finance-data-good-or-bad-now


import quandl
import pandas as pd
import pandas_datareader as pdr
from pandas_datareader.quandl import QuandlReader as qdr
import numpy as np
import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY, date2num
from mpl_finance import candlestick_ohlc
import yahoo_api as y

start = datetime.datetime(2018, 2, 12)
print(start)
end = datetime.datetime.today()


# print(pdr.get_data_yahoo("SPY", start, end, interval="d"))
dict = {
    'sma': [10,21],
    'ema': [10,22]
}
print(max(max(dict.values())))


def generate_ma_table(frequency, start=None, end=None, ma_list=None, market_ticker='^GSPC'):
    """

    :param frequency: ['w','d']
    :param ma_list: ['SMA','EMA','DMA']:Period
    :param start:
    :param end:
    :param :market_ticker:
    :return:
    """
    end = datetime.datetime.today() if end == None else end
    start = end - datetime.timedelta(days=365) if start == None else start

    if frequency == 'w':
        max_period = 100 if ma_list==None else max(max(ma_list.values()))
        timedelta = datetime.timedelta(weeks=max_period)
    else:
        max_period = 365 if ma_list==None else max(max(ma_list.values()))
        timedelta = datetime.timedelta(days=max_period)

    prices = pdr.get_data_yahoo(market_ticker, interval=frequency)['Close']

    datetest = datetime.datetime(2019, 2, 12)
    # print(prices)
    # print(type(prices))
    # print(prices.asof(datetest))
    print(prices)
    print(prices[prices.keys() == str(datetest)])

    # print(prices.take())
    pd.rolling(10)


generate_ma_table('d')
# Picture of system:
# Input:    Frequency (Hours, Days, Weeks, Months, etc.), Period,
#           CHOICE of output of table and plot (SMA, EMA, DEMA), market (SNP500),
#
#
# Output:   Plots (candlestick + MAs; with a choice in inputs on what lines we want to see),
#
#