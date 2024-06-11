import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def fetch_price_history(ticker="PFF"):
    # Fetch historical price data for PFF using yfinance
    pff = yf.Ticker(ticker)
    price_history = pff.history(period="1y", interval="1d", auto_adjust = False)  # Last 20 days

    # Keep only the necessary columns
    price_history = price_history[['Open', 'High', 'Low', 'Close']]

    # Reset index to have Date as a column
    price_history.reset_index(inplace=True)

    return price_history


if __name__ == "__main__":
    ticker = "PFF"

    # Fetch price history
    price_history_df = fetch_price_history(ticker)

    # Create candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=price_history_df['Date'],
        open=price_history_df['Open'],
        high=price_history_df['High'],
        low=price_history_df['Low'],
        close=price_history_df['Close'],
        name=ticker
    )])

    # Update layout for interactivity
    fig.update_layout(
        title=f'{ticker} Daily Candlestick Chart (Last 20 Days)',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        hovermode='x unified'
    )

    # Show the figure
    fig.show()
