import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Fetch historical dividend data for PFF using yfinance
ticker = "PFF"
pff = yf.Ticker(ticker)

# Fetch historical dividends data
dividends = pff.dividends

# Check the first few rows of dividends data
print(dividends.head())

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

# Display the DataFrame
print(dividends_yearly_df)

# Visualizing the total dividends by year
plt.figure(figsize=(10, 6))
plt.bar(dividends_yearly_df['Year'].astype(str), dividends_yearly_df['Total Amount'], color='blue')
plt.xlabel('Year')
plt.ylabel('Total Dividend Amount')
plt.title('PFF Total Dividends by Year')
plt.show()

# Visualizing the percentage change year-over-year
plt.figure(figsize=(10, 6))
plt.plot(dividends_yearly_df['Year'].astype(str), dividends_yearly_df['% Chg Year-over-Year'], marker='o', color='green')
plt.xlabel('Year')
plt.ylabel('% Change Year-over-Year')
plt.title('PFF % Change in Dividends Year-over-Year')
plt.grid(True)
plt.show()
