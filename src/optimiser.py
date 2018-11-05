from pandas_datareader import DataReader
from datetime import datetime as date       # Datetime arguments: datetime(yyyy, m/mm, d/dd)
import numpy as np
import math as m

# Calculates the mean, variance and standard deviation of a list of values
# given by the 'prices' argument.
def get_mean_and_volatility(prices):
    priceArr = np.array(prices)
    stockReturns = (priceArr[1:len(prices)] - priceArr[0:len(prices)-1]) / priceArr[0:len(prices)-1]

    mean = np.mean(stockReturns)
    sumSq = 0
    for stockReturn in stockReturns :
        sumSq += (stockReturn - mean)**2
    variance = sumSq / len(priceArr)
    stdDev = m.sqrt(variance)
    return mean, variance, stdDev
# Note: Variance/stdDev represent volatility of returns over a (business) day (I think)

stocks = ["MSFT", "AAPL", "AMZN"]
start = date(2017, 2, 11)
end = date(2018, 2, 11)
source = "yahoo"

# Fetch stock data from Yahoo
data = {}
for symbol in stocks:
    data[symbol] = DataReader(symbol, data_source=source, start=start, end=end)['Adj Close']

# Store mean and volatility of stock returns
means = {}
variances = {}
stdDevs = {}
for symbol in data:
    means[symbol], variances[symbol], stdDevs[symbol] = get_mean_and_volatility(data[symbol])

# Combine inputs into one (dictionary)
derivedData = {}
for symbol in data:
    derivedData[symbol] = {"Mean": means[symbol], "Variance": variances[symbol], "Standard Deviation": stdDevs[symbol]}

print(data["MSFT"])
print(derivedData["MSFT"])

# Covariance matrix of stock returns
