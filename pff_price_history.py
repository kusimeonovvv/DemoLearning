import yfinance as yf
import pandas as pd


def fetch_price_history(ticker="PFF"):
    # Fetch historical price data for PFF using yfinance
    pff = yf.Ticker(ticker)
    price_history = pff.history(period="1y", interval="1d", auto_adjust = False)  # Last 20 days

    # Keep only the 'Close' prices
    price_history = price_history[['Close']]

    # Reset index to have Date as a column
    price_history.reset_index(inplace=True)

    return price_history


if __name__ == "__main__":
    price_history_df = fetch_price_history()
    print(price_history_df)
    # Save the price history to a CSV file
    price_history_df.to_csv('PFF_Price_History.csv', index=False)
