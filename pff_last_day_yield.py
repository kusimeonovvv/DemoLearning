import yfinance as yf
import pandas as pd


def fetch_and_process_dividends(ticker="PFF"):
    # Fetch historical dividend data for PFF using yfinance
    pff = yf.Ticker(ticker)
    dividends = pff.dividends

    # Ensure the dividends index is timezone-naive
    dividends.index = dividends.index.tz_localize(None)

    # Manually add missing dividends
    missing_dividends = {
        '2020-02-03': 0.164,
        '2022-12-15': 0.237
    }

    for date, amount in missing_dividends.items():
        dividends.loc[pd.Timestamp(date)] = amount

    # Sort the dividends after adding new entries
    dividends.sort_index(inplace=True)

    return dividends


def fetch_price_history(ticker="PFF"):
    # Fetch historical price data for PFF using yfinance
    pff = yf.Ticker(ticker)
    price_history = pff.history(period="max")

    # Keep only the 'Close' prices
    price_history = price_history[['Close']]

    # Reset index to have Date as a column
    price_history.reset_index(inplace=True)

    return price_history


if __name__ == "__main__":
    ticker = "PFF"

    # Fetch and process data
    dividends = fetch_and_process_dividends(ticker)
    prices = fetch_price_history(ticker)

    # Get the last closing price
    last_closing_price = prices['Close'].iloc[-1]

    # Get the sum of the last 12 dividends
    last_12_dividends_sum = dividends.iloc[-12:].sum()

    # Calculate the yield
    yield_percentage = (last_12_dividends_sum / last_closing_price) * 100

    # Print the results
    print(f"Last Closing Price: ${last_closing_price:.2f}")
    print(f"Sum of Last 12 Dividends: ${last_12_dividends_sum:.2f}")
    print(f"Dividend Yield: {yield_percentage:.2f}%")
