import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html

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

    current_pff = merged_df.iloc[-1]['Dividend Yield']
    current_tnx = merged_df.iloc[-1]['TNX Close']
    current_spread = merged_df.iloc[-1]['Spread']

    pff_52wk_avg = merged_df['Dividend Yield'].mean()
    tnx_52wk_avg = merged_df['TNX Close'].mean()
    spread_52wk_avg = merged_df['Spread'].mean()

    pff_52wk_high = merged_df['Dividend Yield'].max()
    tnx_52wk_high = merged_df['TNX Close'].max()
    spread_52wk_high = merged_df['Spread'].max()

    pff_52wk_low = merged_df['Dividend Yield'].min()
    tnx_52wk_low = merged_df['TNX Close'].min()
    spread_52wk_low = merged_df['Spread'].min()

    return merged_df, {
        "current_pff": current_pff, "current_tnx": current_tnx, "current_spread": current_spread,
        "pff_52wk_avg": pff_52wk_avg, "tnx_52wk_avg": tnx_52wk_avg, "spread_52wk_avg": spread_52wk_avg,
        "pff_52wk_high": pff_52wk_high, "tnx_52wk_high": tnx_52wk_high, "spread_52wk_high": spread_52wk_high,
        "pff_52wk_low": pff_52wk_low, "tnx_52wk_low": tnx_52wk_low, "spread_52wk_low": spread_52wk_low
    }

# Data Preparation
ticker = "PFF"
start_date = "2023-01-01"
dividends = fetch_and_process_dividends(ticker)
prices = fetch_price_history(ticker, start_date)
tnx_data = fetch_tnx_data()
yield_results = calculate_yield_from_date(dividends, prices)
merged_df, comparison_results = find_extremums_and_compare(yield_results, tnx_data)

# Create static table data
table_data = {
    "Metric": ["Current", "52 Wk Avg", "52 Wk High", "52 Wk Low"],
    "PFF Yield": [
        round(comparison_results["current_pff"], 2),
        round(comparison_results["pff_52wk_avg"], 2),
        round(comparison_results["pff_52wk_high"], 2),
        round(comparison_results["pff_52wk_low"], 2)
    ],
    "TNX Close": [
        round(comparison_results["current_tnx"], 2),
        round(comparison_results["tnx_52wk_avg"], 2),
        round(comparison_results["tnx_52wk_high"], 2),
        round(comparison_results["tnx_52wk_low"], 2)
    ],
    "Spread": [
        round(comparison_results["current_spread"], 2),
        round(comparison_results["spread_52wk_avg"], 2),
        round(comparison_results["spread_52wk_high"], 2),
        round(comparison_results["spread_52wk_low"], 2)
    ]
}
table_df = pd.DataFrame(table_data)

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(
        id='comparison-graph',
        figure={
            'data': [
                go.Scatter(
                    x=merged_df['Date'],
                    y=merged_df['Dividend Yield'],
                    mode='lines+markers',
                    name='PFF Yield'
                ),
                go.Scatter(
                    x=merged_df['Date'],
                    y=merged_df['TNX Close'],
                    mode='lines+markers',
                    name='TNX Close'
                ),
                go.Scatter(
                    x=merged_df['Date'],
                    y=merged_df['Spread'],
                    mode='lines+markers',
                    name='Spread (PFF Yield - TNX Close)'
                )
            ],
            'layout': go.Layout(
                title='PFF Daily Dividend Yield vs TNX Close (From 2023-01-01 to Present)',
                xaxis={'title': 'Date'},
                yaxis={'title': 'Value'},
                hovermode='x unified'
            )
        }
    ),
    dcc.Store(id='merged-data', data=merged_df.to_dict('records')),
    html.Div(id='table-container', children=[
        dcc.Graph(
            id='comparison-table',
            figure={
                'data': [
                    go.Table(
                        header=dict(values=list(table_df.columns),
                                    fill_color='paleturquoise',
                                    align='left'),
                        cells=dict(values=[table_df.Metric, table_df['PFF Yield'], table_df['TNX Close'], table_df.Spread],
                                   fill_color='lavender',
                                   align='left'))
                ],
                'layout': go.Layout(
                    title='Comparison Table of PFF Yield, TNX Close, and Spread'
                )
            }
        )
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
