import requests
import pandas as pd
import yahoo_api as yapi
import db_engine as db
import psycopg2

cookie = "AQIC5wM2LY4SfcwGo4Vryf5aH9MrOdQ6ybGV%2BPn9RPbVJxw%3D%40AAJTSQACMTAAAlNLABQtMzkxMjk0ODA5MTYxNjA1OTY1OQACUzEAAjI2%23"
headers = {"Cookie": "iPlanetDirectoryPro=" + cookie + ";Path=/"}
tickers_by_sector = yapi.s_and_p_500_tickers_by_sector()

"""
Not all stocks are represented solely by their ticker value. Some have extra letters added to their ticker
which describes an additional attribute of the stock.
According to Investopaedia:
-  K is a fifth letter added to a four-letter Nasdaq stock symbol indicating that the stock has no voting rights.
-  O is a component of a stock symbol that indicates the shares of that stock are a second class of preferred shares.

As these additional letters are part of the link where we get our P/E ratios for certain stocks, we need to find
which stocks have additional letters, hence the 'k' and 'o' arrays.
"""
k = ["ALLE", "ARNC", "FBHS", "NLSN",
      "ABBV", "ANTM", "PRGO",
      "ANET", "JNPR", "KEYS", "ORCL",
      "TWTR",
      "APTV", "KORS", "NCLH",
      "EVRG",
      "CBOE", "SCHW", "MSCI", "SPGI",
      "DWDP",
      "CBRE", "WELL",
      "COTY",
      "BHGE"]
o = ["AAL", "CHRW", "CTAS", "CPRT", "CSX", "EXPD", "FAST", "INFO", "JBHT", "PCAR", "SRCL", "UAL", "VRSK",
      "ABMD", "ALXN", "ALGN", "AMGN", "BIIB", "CELG", "CERN", "XRAY", "ESRX", "GILD", "HSIC", "HOLX", "IDXX",
      "ILMN", "INCY", "ISRG", "MYL", "NKTR", "REGN", "VRTX",
      "ADBE", "AMD", "AKAM", "ADI", "ANSS", "AAPL", "AMAT", "ADSK", "ADP", "AVGO", "CDNS", "CSCO", "CTXS",
      "CTSH", "FFIV", "FISV", "FLIR", "FTNT", "INTC", "INTU", "IPGP", "JKHY", "KLAC", "LRCX", "MCHP", "MU",
      "MSFT", "NTAP", "NVDA", "PAYX", "PYPL", "QRVO", "QCOM", "STX", "SWKS", "SYMC", "SNPS", "TXN", "VRSN",
      "WDC", "XLNX",
      "ATVI", "GOOGL", "GOOG", "CHTR", "CMCSA", "DISCA", "DISCK", "DISH", "EA", "FB", "NFLX", "NWSA", "NWS",
      "TTWO", "TRIP", "FOXA", "FOX", "VIAB",
      "AMZN", "BKNG", "DLTR", "EBAY", "EXPE", "GRMN", "GT", "HAS", "LKQ", "MAR", "MAT", "ORLY", "ROST", "SBUX",
      "TSCO", "ULTA", "WYNN",
      "XEL",
      "BHF", "CINF", "CME", "ETFC", "FITB", "HBAN", "NDAQ", "NTRS", "PBCT", "PFG", "SIVB", "TROW", "WLTW", "ZION",
      "EQIX", "REG", "SBAC",
      "COST", "KHC", "MDLZ", "MNST", "PEP", "WBA"]

def get_pe_vals(tickers):
    pe_dict = {}
    for stock in tickers:
        # If it fails, uncomment this print statement to see what stock it fails on.
        # Note that it may be an internet slippage or you may need a new cookie.
        print(stock)

        # Here we add the additional letters to the stocks in the arrays above so that our link will find them.
        # The temp variable is created in order to convert the stocks back to their original values afterwards.
        # This is needed as in the database they are stored without additional letters
        temp = ""
        if (stock in k):
            temp = stock
            stock = stock + ".K"
        if (stock in o):
            temp = stock
            stock = stock + ".O"

        # Sheer Awkwardness (i)
        if(stock in ["BRK-B", "BF-B"]):
            temp = stock
            stock = stock.replace("-B", "b")

        # Here we retrieve the html of the Eikon page and parse it using pandas
        r = requests.get("https://emea1.apps.cp.thomsonreuters.com/Explorer/EVzCORPxFUNDTALSzRATIO.aspx?taxonomy=global&s=" + stock + "&st=RIC&mode=full-topMenu-banner-tabBar-leftMenu-relNav&tempcss=schema4&embeddedView=true&trace=", headers=headers)
        tables = pd.read_html(r.text, header=0, index_col=0)

        # Stocks with additional letters are converted back into their original values
        if (temp in k):
            stock = temp
        if (temp in o):
            stock = temp

        # Sheer Awkwardness (ii)
        if(temp in ["BRK-B", "BF-B"]):
            stock = temp


        # This finds the P/E values in our parsed html.
        # For some reason the values are located in slightly different places for some stocks.
        if(stock in
                ["BA","FLR", "HON", "AET", "JNJ", "PFE", "VRTX", "SWKS", "IPG", "FOXA",
                 "FOX", "VZ", "DIS", "EXPE", "LEN", "NWL", "AWK", "CMS", "NRG", "BBT",
                 "C", "FITB", "JPM", "MS", "WLTW", "PLD", "KMB", "APA", "CVX", "DVN", "XOM",
                 "NOV", "WMB"]):
            pe = tables[10].loc["Curr P/E Excl Extra, LTM:", "LTM"]
        else:
            pe = tables[7].loc["Curr P/E Excl Extra, LTM:", "LTM"]

        if(pe == '--'):
            pe = '0'

        # Adds the stock and p/e value to a dictionary
        pe_dict[stock] = pe
    return pe_dict

# Note that the P/E is not calculated on Eikon when the EPS LTM is less than or equal to zero, hence returning '--'
# print(get_pe_vals(tickers_by_sector["Energy"]))

# Create DB Engine
pe_engine = db.DbEngine()

blank_canvas = pd.Series(name="PE")
blank_canvas.index.name="Ticker"
pe_engine.create_db_dataframe(blank_canvas, "pe_table")

# Create DB Table & Append PE Values
for industry in tickers_by_sector:
    series = pd.Series(get_pe_vals(tickers_by_sector[industry]),name="PE")
    series.index.name="Ticker"
    pe_engine.append_db_dataframe(series, "pe_table")

# for industry in tickers_by_sector:
#     print(industry)

# To delete existing table, uncomment next line
# pe_engine.delete_table("pe_table")





