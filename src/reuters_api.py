import requests
import pandas as pd
import yahoo_api as yapi

cookie = "AQIC5wM2LY4SfczmIvCB0s3thxuTx5pbrX9wvcJ4fAwN8c8%3D%40AAJTSQACMTAAAlNLABQtMjUxMTUxMzgyMTk3MDg1NTY2MgACUzEAAjI4%23"
headers = {"Cookie": "iPlanetDirectoryPro=" + cookie + ";Path=/"}
tickers = ["MSFT", "AAPL", "AMZN"]

pe_dict = {}

tickers_by_sector = yapi.s_and_p_500_tickers_by_sector()
for industry in tickers_by_sector:
    for stock in tickers_by_sector[industry]:
        r = requests.get("https://emea1.apps.cp.thomsonreuters.com/Explorer/EVzCORPxFUNDTALSzRATIO.aspx?taxonomy=global&s=" + stock + ".O&st=RIC&mode=full-topMenu-banner-tabBar-leftMenu-relNav&tempcss=schema4&embeddedView=true&trace=", headers=headers)
        tables = pd.read_html(r.text, header=0, index_col=0)
        pe = tables[7].loc["Curr P/E Excl Extra, LTM:", "LTM"]
        pe_dict[stock] = pe
print(pe_dict)