import pandas_datareader as pdr

stocks = ["MSFT", "AAPL", "AMZN"]

start = "2017-11-02"
end = "2018-11-02"
source = "yahoo"

data = {}

for symbol in stocks:
        data[symbol] = pdr.DataReader(symbol, data_source=source, start=start, end=end)['Adj Close']

print(data)