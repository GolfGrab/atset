import pandas as pd
import pandas_ta as ta
import numpy as np
import plotly.graph_objects as go
import settrade.openapi as setapi
import datetime
import pytz


def get_ohlcv(symbol: str, interval: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Get OHLCV data from SET API
    """
    n = (end_date - start_date)/np.timedelta64(1, 'D')
