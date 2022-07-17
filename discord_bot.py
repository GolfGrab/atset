import nextcord
from nextcord.ext import commands

import random
import os

from dotenv import load_dotenv

import yfinance as yf
import pandas as pd
from stockstats import wrap
import plotly.graph_objects as go
import datetime as dt
import pandas_ta as ta
from plotly.subplots import make_subplots

# load_dotenv reads from a file called .env in the same directory as the python files which should roughly look like BOT_TOKEN="1234567890"
load_dotenv()

token = os.getenv("BOT_TOKEN")

description = """An example bot to showcase the nextcord.ext.commands extension
module.
There are a number of utility commands being showcased here."""

intents = nextcord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="$",
                   description=description, intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)


@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split("d"))
    except ValueError:
        await ctx.send("Format has to be in NdN!")
        return

    result = ", ".join(str(random.randint(1, limit)) for _ in range(rolls))
    await ctx.send(result)


@bot.command(description="For when you wanna settle the score some other way")
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))


@bot.command()
async def repeat(ctx, times: int, content="repeating..."):
    """Repeats a message multiple times."""
    for _ in range(times):
        await ctx.send(content)


@bot.command()
async def joined(ctx, member: nextcord.Member):
    """Says when a member joined."""
    await ctx.send(f"{member.name} joined in {member.joined_at}")


@bot.group()
async def cool(ctx):
    """Says if a user is cool.
    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send(f"No, {ctx.subcommand_passed} is not cool")


@cool.command(name="bot")
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send("Yes, the bot is cool.")


@bot.command()
async def userinfo(ctx, member: nextcord.Member):
    """Shows info about a member."""
    await ctx.send(f"{member.name} joined in {member.joined_at}")
    await ctx.send(f"{member.name} is {member.status}")


@bot.command()
async def get_graph(ctx, symbol: str):
    """Shows 3 month graph of a stock with indicator."""
    try:
        tk = yf.Ticker(symbol)
        df = tk.history(period='3mo', interval='1d')
        if len(df) == 0:
            await ctx.send("No data found. symbol may be delisted or invalid. try ^SET.BK PTTGC.BK or search for it on https://finance.yahoo.com/")
            print("No data found. symbol may be delisted or invalid. try ^SET.BK PTTGC.BK or search for it on https://finance.yahoo.com/")
            return
        await ctx.send("making graph...")
        df = wrap(df)
        df["close_20_ema"]
        df["supertrend"]
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
            title=f"#{symbol} [last data {pd.to_datetime(df.index)[-1].strftime('YMD:[%Y/%m/%d]')}]<br>[ open = {df['open'].iloc[-1]:.2f} || high = {df['high'].iloc[-1]:.2f} || low = {df['low'].iloc[-1]:.2f} || close = {df['close'].iloc[-1]:.2f} ]")

        # hide bottom range slider
        fig.update_layout(xaxis_rangeslider_visible=False)

        # removing all empty dates
        dt_all = pd.date_range(start=df.index[0], end=df.index[-1])
        dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(df.index)]
        dt_breaks = [d for d in dt_all.strftime(
            "%Y-%m-%d").tolist() if not d in dt_obs]
        fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

        # save figure
        if not os.path.exists(os.path.join(os.getcwd(), "plot_output_discord", "supertrend")):
            os.makedirs(os.path.join(
                os.getcwd(), "plot_output_discord", "supertrend"))

        fig.write_image(os.path.join(os.getcwd(), "plot_output_discord",
                        "supertrend", f"{symbol}.webp"), format="webp", scale=8)

        # send figure
        await ctx.send(file=nextcord.File(os.path.join(os.getcwd(), "plot_output_discord", "supertrend", f"{symbol}.webp")))
        await ctx.send(f"here is your graph for {symbol}")
    except Exception as e:
        print(e)
        await ctx.send(f"Error : {e}")


@bot.command()
async def get_graph_macd_ema(ctx, symbol: str):
    """Shows graph of a stock with macd and ema indicator."""
    try:
        await ctx.send("making graph...")
        df = pd.DataFrame()
        df = df.ta.ticker(symbol, period="2y", interval="1d")
        if not type(df) == pd.DataFrame or df.empty:
            await ctx.send("No data found. symbol may be delisted or invalid. try ^SET.BK PTTGC.BK or search for it on https://finance.yahoo.com/")
            print("No data found. symbol may be delisted or invalid. try ^SET.BK PTTGC.BK or search for it on https://finance.yahoo.com/")
            return
        df.ta.macd(close='Close', fast=12, slow=26, signal=9, append=True)
        df.ta.ema(close='Close', length=200, append=True)
        df = df.tail(100)
        ##############       plot data using plotly         ##############
        fig = make_subplots(rows=2, cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.01,
                            row_heights=[0.7, 0.3])
        ####  create figure with ohlc data  ####
        fig.add_trace(go.Candlestick(x=df.index,
                                     open=df['Open'],
                                     high=df['High'],
                                     low=df['Low'],
                                     close=df['Close'],
                                     hoverlabel=dict(bgcolor='white'),
                                     name=symbol
                                     ),
                      row=1, col=1)

        fig.update_layout(
            title=f"#{symbol} [last data {pd.to_datetime(df.index)[-1].strftime('YMD:[%Y/%m/%d]')}]<br>[ open = {df['Open'].iloc[-1]:.2f} || high = {df['High'].iloc[-1]:.2f} || low = {df['Low'].iloc[-1]:.2f} || close = {df['Close'].iloc[-1]:.2f} ]")

        ####       remove range slider      ####
        fig.update_layout(xaxis_rangeslider_visible=False)

        ####    removing all empty dates    ####

        # build complete timeline from start date to end date
        dt_all = pd.date_range(start=df.index[0], end=df.index[-1])

        # retrieve the dates that ARE in the original dataset
        dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(df.index)]

        # define dates with missing values
        dt_breaks = [d for d in dt_all.strftime(
            "%Y-%m-%d").tolist() if not d in dt_obs]

        # remove dates that are missing from the original dataset
        fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

        ####    add EMA_200     ####
        fig.add_trace(go.Scatter(x=df.index,
                                 y=df['EMA_200'],
                                 opacity=0.7,
                                 line=dict(color='purple', width=2),
                                 name='EMA_200'))

        ####     add MACD       ####
        colors = ['green' if val >= 0
                  else 'red' for val in df['MACDh_12_26_9']]

        fig.add_trace(go.Bar(x=df.index,
                             y=df['MACDh_12_26_9'],
                             name='MACDh_12_26_9',
                             marker_color=colors
                             ), row=2, col=1,)
        fig.add_trace(go.Scatter(x=df.index,
                                 y=df['MACD_12_26_9'],
                                 line=dict(color='black', width=2),
                                 name='MACD_12_26_9'
                                 ), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index,
                                 y=df['MACDs_12_26_9'],
                                 line=dict(color='blue', width=1),
                                 name='MACDs_12_26_9'
                                 ), row=2, col=1)

        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="MACD", row=2, col=1)
        fig.update_layout(margin=go.layout.Margin(
            l=20,  # left margin
            r=20,  # right margin
            b=20,  # bottom margin
            t=40  # top margin
        ))
        if not os.path.exists(os.path.join(os.getcwd(), "plot_output_discord", "macd_ema")):
            os.makedirs(os.path.join(
                os.getcwd(), "plot_output_discord", "macd_ema"))
        fig.write_image(os.path.join(os.getcwd(), "plot_output_discord",
                        "macd_ema", f"{symbol}.webp"), format="webp", scale=8, width=1000, height=500)
        # send figure
        await ctx.send(file=nextcord.File(os.path.join(os.getcwd(), "plot_output_discord", "macd_ema", f"{symbol}.webp")))
        await ctx.send(f"here is your graph for {symbol}")
    except Exception as e:
        print(e)
        await ctx.send(f"Error : {e}")


@bot.command()
async def get_info(ctx, symbol: str):
    """Shows info about a stock."""
    try:
        tk = yf.Ticker(symbol)
        info = tk.info
        longname = info.get("longName")
        shortname = info.get("shortName")
        exchange = info.get("exchange")
        currency = info.get("currency")
        sym = info.get("symbol")
        industry = info.get("industry")
        sector = info.get("sector")
        country = info.get("country")
        longBusinessSummary = info.get("longBusinessSummary")[:1000]
        website = info.get("website")
        await ctx.send(f"""
longName : {longname}
shortName : {shortname}
exchange : {exchange}
currency : {currency}
symbol : {sym}
industry : {industry}
sector : {sector}
country : {country}
longBusinessSummary : {longBusinessSummary}...
website : {website}
""")
    except Exception as e:
        print(e)
        await ctx.send(f"Error : {e}")

bot.run(token)
