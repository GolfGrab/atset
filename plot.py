import os
import plotly.graph_objects as go
from tradingview_ta import TA_Handler, Interval
import pandas as pd

file_path = os.path.dirname(__file__)


def get_suggestion(symbol: str):
    handler = TA_Handler(
        symbol=symbol,
        exchange="SET",
        screener="thailand",
        interval=Interval.INTERVAL_1_DAY,
        timeout=None
    )
    return handler.get_analysis().summary


def plot_supertrend(symbol: str, df: pd.DataFrame):
    suggest = get_suggestion(symbol)

    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['open'],
                                         high=df['high'],
                                         low=df['low'],
                                         close=df['close'],
                                         hoverlabel=dict(bgcolor='white'),
                                         name=symbol,
                                         )])

    fig.add_trace(go.Scatter(
        x=df.index, y=df["supertrend"], line_shape='spline', name="supertrend"))

    fig.add_trace(go.Scatter(
        x=df.index, y=df["close_20_ema"], line_shape='spline', name="close_20_ema",))
    # add labels
    fig.update_layout(
        title=f"#{symbol} [last data {pd.to_datetime(df.index)[-1].strftime('y%Y/ m%d/ d%m')}]<br>{' || '.join([f'{k} : {v}' for k,v in suggest.items()])}<br>[ open = {df['open'].iloc[-1]:.2f} || high = {df['high'].iloc[-1]:.2f} || low = {df['low'].iloc[-1]:.2f} || close = {df['close'].iloc[-1]:.2f} ]")

    # hide bottom range slider
    fig.update_layout(xaxis_rangeslider_visible=False)

    # removing all empty dates
    dt_all = pd.date_range(start=df.index[0], end=df.index[-1])
    dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(df.index)]
    dt_breaks = [d for d in dt_all.strftime(
        "%Y-%m-%d").tolist() if not d in dt_obs]
    fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

    # save figure
    if not os.path.exists(os.path.join(file_path, "plot_output", "supertrend")):
        os.makedirs(os.path.join(file_path, "plot_output", "supertrend"))

    fig.write_image(os.path.join(file_path, "plot_output",
                    "supertrend", f"{symbol}.webp"), format="webp", scale=4)
