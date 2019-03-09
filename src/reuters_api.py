import eikon as ek
import pandas as pd
import numpy as np
import yahoo_api as y
from db_engine import DbEngine


def get_pe_value(ticker):
    if "." in ticker:
        # Wikipedia has BRK.B and BF.B, but eikon has BRKb and BFb
        # This converts wikipedia's names to eikon's names
        parts = ticker.split(".")
        ticker = parts[0] + parts[1].lower()

    for suffix in ["", ".K", ".O"]:
        pe = ek.get_data(ticker + suffix, 'TR.PE')[0].iloc[0, 1] 
        if not np.isnan(pe):
            print("{:7} {:.4f}".format(ticker + suffix, pe))
            return pe
    return 0


if __name__ == "__main__":
    ek.set_app_key("d14a6a14480842328de35bc001771c605538616a")
    tickers = y.s_and_p_500_tickers()
    
    pe_dict = {}
    for i, ticker in enumerate(tickers, 1):
        pe_dict[ticker] = get_pe_value(ticker)
        if i % 10 == 0:
            print("{} of 505".format(i))
    
    df = pd.DataFrame(list(pe_dict.items()), columns=("Ticker", "PE"))
    df.set_index("Ticker", inplace=True)
    db = DbEngine()
    db.delete_table("pe_table_3")
    db.create_db_dataframe(df, "pe_table_3")
    test = db.fetch_db_dataframe("pe_table_3")
    print(test)
            