import requests
from bs4 import BeautifulSoup
import re

cookie = "AQIC5wM2LY4Sfcyvehmk6JH4q3hXRkRWNeTeLiytQM6PeVY%3D%40AAJTSQACMTAAAlNLABQtODIyODM0Nzg5OTI4NDg4MTU3OQACUzEAAjI3%23"
headers = {"Cookie": "iPlanetDirectoryPro=" + cookie + ";Path=/"}
tickers = ["MSFT", "AAPL", "AMZN"]


for stock in tickers:
    r = requests.get("https://emea1.apps.cp.thomsonreuters.com/Explorer/EVzCORPxFUNDTALSzRATIO.aspx?taxonomy=global&s=" + stock + ".O&st=RIC&mode=full-topMenu-banner-tabBar-leftMenu-relNav&tempcss=schema4&embeddedView=true&trace=", headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    div = soup.find("div", id="EVzCORPxFUNDTALSzRATIO")
    table = div.find("table")
    td = table.find_all('td')[3:4]
    print(td[0])
    table2 = td.find("table")
    tr = table2.find("tr", class_="dr row-o")
    span= tr.find("span", class_="profitable")
    print(span)