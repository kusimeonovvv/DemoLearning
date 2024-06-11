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

    # Calculate yearly dividend data
    dividends_yearly = dividends.resample('YE').sum()

    # Create a DataFrame with Year and Total Dividends
    dividends_yearly_df = dividends_yearly.reset_index()
    dividends_yearly_df['Year'] = dividends_yearly_df['Date'].dt.year
    dividends_yearly_df.rename(columns={'Dividends': 'Total Amount'}, inplace=True)

    # Calculate the number of dividends per year
    dividends_yearly_df['# Dividends'] = dividends.resample('YE').count().values

    # Calculate Year-over-Year change in dividends
    dividends_yearly_df['% Chg Year-over-Year'] = dividends_yearly_df['Total Amount'].pct_change() * 100

    # Fill NaN values for the first year
    dividends_yearly_df.fillna(0, inplace=True)

    return dividends, dividends_yearly_df

if __name__ == "__main__":
    dividends, dividends_yearly_df = fetch_and_process_dividends()
    print(dividends_yearly_df)
    # Save the processed data to CSV files
    dividends.to_csv('PFF_Dividends_All.csv')
    dividends_yearly_df.to_csv('PFF_Dividends_Yearly.csv')
