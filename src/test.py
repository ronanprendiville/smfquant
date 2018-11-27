import yahoo_api as datareader
import pandas as pd
import pandas_datareader as pdr
import numpy as np
import datetime
import matplotlib.pyplot as plt
import glob
import pprint
from db_engine import DbEngine
#
eurusd = 1.1291
db = DbEngine()
price_data = db.fetch_db_dataframe('closing_prices_s_and_p')

closing_prices = pd.read_csv('optimised portfolio.csv', sep=',', index_col=False)
closing_prices_dict = closing_prices.to_dict()
closing_prices_dict['Number of Shares'] = {}
closing_prices_dict['Rounded Off'] = {}
closing_prices_dict['Rounded Down'] = {}
closing_prices_dict['Rounded Up'] = {}
closing_prices_dict['Amount Rounded Off'] = {}
closing_prices_dict['Amount Rounded Down'] = {}
closing_prices_dict['Amount Rounded Up'] = {}
closing_prices_dict['Share Price'] = {}

for index in closing_prices_dict['Amount']:
    stock_name = closing_prices_dict['Stock'][index]
    amount = closing_prices_dict['Amount'][index]/eurusd
    last_price = pdr.DataReader(stock_name, data_source='yahoo', start=2018-11-26, end=2018-11-26).iloc[-1][stock_name]/eurusd
    num_of_shares = amount / last_price
    rounded_off = np.round(num_of_shares)
    rounded_up = np.ceil(num_of_shares)
    rounded_down = np.floor(num_of_shares)
    closing_prices_dict['Number of Shares'][index] = num_of_shares
    closing_prices_dict['Rounded Off'][index] = rounded_off
    closing_prices_dict['Rounded Up'][index] = rounded_up
    closing_prices_dict['Rounded Down'][index] = rounded_down
    closing_prices_dict['Share Price'][index] = last_price
    closing_prices_dict['Amount Rounded Off'][index] = last_price * rounded_off
    closing_prices_dict['Amount Rounded Up'][index] = last_price * rounded_up
    closing_prices_dict['Amount Rounded Down'][index] = last_price * rounded_down

total = {
    'Stock': 'TOTALS',
    'Amount': sum(closing_prices_dict.get('Amount').values()),
    'Share Price': 0,
    'Number of Shares': sum(closing_prices_dict.get('Number of Shares').values()),
    'Rounded Off': sum(closing_prices_dict.get('Rounded Off').values()),
    'Amount Rounded Off': sum(closing_prices_dict.get('Amount Rounded Off').values()),
    'Rounded Up': sum(closing_prices_dict.get('Rounded Up').values()),
    'Amount Rounded Up': sum(closing_prices_dict.get('Amount Rounded Up').values()),
    'Rounded Down': sum(closing_prices_dict.get('Rounded Down').values()),
    'Amount Rounded Down': sum(closing_prices_dict.get('Amount Rounded Down').values())
}
column_order = ['Stock', 'Amount', 'Share Price', 'Number of Shares', 'Rounded Off',
                'Amount Rounded Off', 'Rounded Up', 'Amount Rounded Up', 'Rounded Down', 'Amount Rounded Down']
thing_of_beauty = pd.DataFrame(closing_prices_dict, columns=column_order).append(total, ignore_index=True).set_index('Stock')
print(thing_of_beauty)
# db.delete_table('Optimised Portfolio #1')
# db.create_db_dataframe(thing_of_beauty,'Optimised Portfolio #1')