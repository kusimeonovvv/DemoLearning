import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def fetch_and_process_dividends(ticker="PFF"):
    pff = yf.Ticker(ticker)
    dividends = pff.dividends
    dividends.index = dividends.index.tz_localize(None)
    missing_dividends = {
        '2020-02-03': 0.164,
        '2022-12-15': 0.237
    }
    for date, amount in missing_dividends.items():
        dividends.loc[pd.Timestamp(date)] = amount
    dividends.sort_index(inplace=True)
    return dividends

def fetch_price_history(ticker="PFF", start_date="2023-01-01"):
    pff = yf.Ticker(ticker)
    price_history = pff.history(start=start_date, end=pd.Timestamp.today(), auto_adjust=False)
    price_history = price_history[['Open', 'High', 'Low', 'Close']]
    price_history.reset_index(inplace=True)
    return price_history

def fetch_tnx_data(period='2y'):
    tnx = yf.download(['^TNX'], period=period, auto_adjust=True)
    tnx.reset_index(inplace=True)
    return tnx

def calculate_yield_from_date(dividends, prices):
    results = []
    num_dividends_to_sum = 12
    prices['Date'] = prices['Date'].dt.tz_localize(None)
    dividends.index = dividends.index.tz_localize(None)
    for date, closing_price in zip(prices['Date'], prices['Close']):
        relevant_dividends = dividends[dividends.index < date].tail(num_dividends_to_sum)
        if len(relevant_dividends) == num_dividends_to_sum:
            last_12_dividends_sum = relevant_dividends.sum()
            yield_percentage = (last_12_dividends_sum / closing_price) * 100
            results.append({
                "Date": date,
                "Dividend Yield": yield_percentage
            })
    return results

def find_extremums_and_compare(pff_yield, tnx):
    pff_df = pd.DataFrame(pff_yield)
    tnx_df = tnx[['Date', 'Close']].rename(columns={'Close': 'TNX Close'})
    merged_df = pd.merge(pff_df, tnx_df, on='Date', how='inner')
    merged_df['Spread'] = merged_df['Dividend Yield'] - merged_df['TNX Close']
    pff_max = merged_df['Dividend Yield'].max()
    pff_min = merged_df['Dividend Yield'].min()
    tnx_max = merged_df['TNX Close'].max()
    tnx_min = merged_df['TNX Close'].min()
    spread_max = merged_df['Spread'].max()
    spread_min = merged_df['Spread'].min()
    avg_difference = merged_df['Spread'].mean()
    return merged_df, {
        "pff_max": pff_max, "pff_min": pff_min,
        "tnx_max": tnx_max, "tnx_min": tnx_min,
        "spread_max": spread_max, "spread_min": spread_min,
        "avg_difference": avg_difference
    }

if __name__ == "__main__":
    ticker = "PFF"
    start_date = "2023-01-01"
    dividends = fetch_and_process_dividends(ticker)
    prices = fetch_price_history(ticker, start_date)
    tnx_data = fetch_tnx_data()
    yield_results = calculate_yield_from_date(dividends, prices)
    merged_df, comparison_results = find_extremums_and_compare(yield_results, tnx_data)
    print("Comparison Results:")
    for key, value in comparison_results.items():
        print(f"{key}: {value}")

    dates = merged_df['Date']
    pff_yields = merged_df['Dividend Yield']
    tnx_closes = merged_df['TNX Close']
    spreads = merged_df['Spread']

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=pff_yields,
        mode='lines+markers',
        name='PFF Yield'
    ))

    fig.add_trace(go.Scatter(
        x=dates,
        y=tnx_closes,
        mode='lines+markers',
        name='TNX Close'
    ))

    fig.add_trace(go.Scatter(
        x=dates,
        y=spreads,
        mode='lines+markers',
        name='Spread (PFF Yield - TNX Close)'
    ))

    fig.add_trace(go.Scatter(
        x=[dates[spreads.idxmax()]],
        y=[spreads.max()],
        mode='markers+text',
        text=["Max Spread"],
        textposition="top center",
        name='Max Spread'
    ))

    fig.add_trace(go.Scatter(
        x=[dates[spreads.idxmin()]],
        y=[spreads.min()],
        mode='markers+text',
        text=["Min Spread"],
        textposition="bottom center",
        name='Min Spread'
    ))

    fig.update_layout(
        title=f'{ticker} Daily Dividend Yield vs TNX Close (From {start_date} to Present)',
        xaxis_title='Date',
        yaxis_title='Value',
        hovermode='x unified'
    )

    fig.update_traces(
        hovertemplate=
        '<b>Date</b>: %{x}<br>'+
        '<b>Value</b>: %{y:.2f}<br>'+
        '<b>Current Difference</b>: %{customdata[0]:.2f}<br>'+
        '<b>Average Difference</b>: {:.2f}<br>'.format(comparison_results["avg_difference"]) +
        '<b>Max Difference</b>: {:.2f}<br>'.format(comparison_results["spread_max"]) +
        '<b>Min Difference</b>: {:.2f}<br>'.format(comparison_results["spread_min"])
    )

    fig.show()
