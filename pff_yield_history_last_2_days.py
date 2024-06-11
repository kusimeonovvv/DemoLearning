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


def calculate_yield_for_last_n_bars(dividends, prices, n=2):
    results = []
    num_dividends_to_sum = 12

    # Ensure the Date columns are timezone-naive
    prices['Date'] = prices['Date'].dt.tz_localize(None)
    dividends.index = dividends.index.tz_localize(None)

    # Iterate from the last date backward
    for i in range(1, n + 1):
        closing_price = prices['Close'].iloc[-i]
        date = prices['Date'].iloc[-i]

        # Select the last 12 dividends from the dividend dates before the current date
        relevant_dividends = dividends[dividends.index < date].tail(num_dividends_to_sum)

        # Ensure we have 12 dividends
        if len(relevant_dividends) == num_dividends_to_sum:
            last_12_dividends_sum = relevant_dividends.sum()
            yield_percentage = (last_12_dividends_sum / closing_price) * 100

            results.append({
                "Date": date,
                "Closing Price": closing_price,
                "Sum of Last 12 Dividends": last_12_dividends_sum,
                "Dividend Yield": yield_percentage
            })

    return results


if __name__ == "__main__":
    ticker = "PFF"

    # Fetch and process data
    dividends = fetch_and_process_dividends(ticker)
    prices = fetch_price_history(ticker)

    # Calculate yield for the last 2 bars
    results = calculate_yield_for_last_n_bars(dividends, prices, n=2)

    # Print the results
    for result in results:
        print(f"Date: {result['Date']}")
        print(f"Last Closing Price: ${result['Closing Price']:.2f}")
        print(f"Sum of Last 12 Dividends: ${result['Sum of Last 12 Dividends']:.2f}")
        print(f"Dividend Yield: {result['Dividend Yield']:.2f}%")
        print("---")
