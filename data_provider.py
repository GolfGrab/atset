from user import market
from watch_list import set100
import pandas as pd
import datetime as dt

WATCH_LIST = set100

for symbol in WATCH_LIST:
    fetched_data = market.get_candlestick(
        symbol=symbol,
        interval="1d",
        limit=1000,
        start=dt.datetime(year=2019, month=6, day=8).isoformat(),
        end=dt.datetime.now().isoformat(),
        is_adjusted=True)
    df = pd.DataFrame.from_dict(data=fetched_data['data'])
    df = df.drop(columns=["last_sequence", ])
    df.to_csv(f"data\{symbol}.csv", index=False)
