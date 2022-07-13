import pandas as pd
import yfinance as yf
import json
from stockstats import wrap
import os

# setting
WATCH_LIST_FILE = 'watch_list.json'
STOCK_DATA_DIR = 'stock_data'
STOCK_DATA_DIR_WITH_INDICATOR_DIR = 'stock_data_with_indicator'


# get watch list
file_path = os.path.dirname(__file__)
with open(os.path.join(file_path, WATCH_LIST_FILE)) as f:
    watch_list = json.load(f)

# create stock data dir if not exist
if not os.path.exists(os.path.join(file_path, STOCK_DATA_DIR)):
    os.makedirs(os.path.join(file_path, STOCK_DATA_DIR))

# fetch stock data from yahoo finance
for i, symbol in enumerate(watch_list):
    tk = yf.Ticker(f"{symbol}.BK")
    df = tk.history(period='3mo', interval='1d')
    df.to_csv(os.path.join(file_path, STOCK_DATA_DIR, f"{symbol}.csv"))
    print(f"{symbol} data fetched {i+1}/{len(watch_list)}")

# create stock data with indicator dir if not exist
if not os.path.exists(os.path.join(file_path, STOCK_DATA_DIR_WITH_INDICATOR_DIR)):
    os.makedirs(os.path.join(file_path, STOCK_DATA_DIR_WITH_INDICATOR_DIR))

# apply stock stats to stock data
for i, symbol in enumerate(watch_list):
    try:
        df = pd.read_csv(os.path.join(
            file_path, STOCK_DATA_DIR, f"{symbol}.csv"))
        df = wrap(df)
        df_ta = wrap(df)
        df_ta.init_all()
        df_ta.to_csv(os.path.join(
            file_path, STOCK_DATA_DIR_WITH_INDICATOR_DIR, f"{symbol}.csv"))
        print(f"{symbol} done {i+1}/{len(watch_list)}")
    except Exception as e:
        print(f"{symbol} error {e}")
        continue
