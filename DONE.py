import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

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

def fetch_price_history(ticker="PFF", start_date="2023-01-01"):
    # Fetch unadjusted historical price data for PFF using yfinance
    pff = yf.Ticker(ticker)
    price_history = pff.history(start=start_date, end=pd.Timestamp.today(), auto_adjust=False)

    # Keep only the necessary columns
    price_history = price_history[['Open', 'High', 'Low', 'Close']]

    # Reset index to have Date as a column
    price_history.reset_index(inplace=True)

    return price_history

def calculate_yield_from_date(dividends, prices):
    results = []
    num_dividends_to_sum = 12

    # Ensure the Date columns are timezone-naive
    prices['Date'] = prices['Date'].dt.tz_localize(None)
    dividends.index = dividends.index.tz_localize(None)

    # Iterate over the dates in the prices DataFrame
    for date, closing_price in zip(prices['Date'], prices['Close']):
        # Select the last 12 dividends from the dividend dates before the current date
        relevant_dividends = dividends[dividends.index < date].tail(num_dividends_to_sum)

        # Ensure we have 12 dividends
        if len(relevant_dividends) == num_dividends_to_sum:
            last_12_dividends_sum = relevant_dividends.sum()
            yield_percentage = (last_12_dividends_sum / closing_price) * 100

            results.append({
                "Date": date,
                "Dividend Yield": yield_percentage
            })

    return results

if __name__ == "__main__":
    ticker = "PFF"
    start_date = "2023-01-01"

    # Fetch and process data
    dividends = fetch_and_process_dividends(ticker)
    prices = fetch_price_history(ticker, start_date)

    # Calculate yield from the start date to today
    yield_results = calculate_yield_from_date(dividends, prices)

    # Prepare data for plotting
    dates = [result['Date'] for result in yield_results]
    yields = [result['Dividend Yield'] for result in yield_results]

    # Create yield line chart
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=yields,
        mode='lines+markers',
        name='PFF Yield'
    ))

    # Update layout for interactivity
    fig.update_layout(
        title=f'{ticker} Daily Dividend Yield (From {start_date} to Present)',
        xaxis_title='Date',
        yaxis_title='Dividend Yield (%)',
        hovermode='x unified'
    )

    # Show the figure
    fig.show()
