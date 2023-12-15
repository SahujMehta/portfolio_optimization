import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pickle

# Load your CSV file
file_path = 'Parsed.csv'  # Replace with your file path
df = pd.read_csv(file_path)

# Creating dictionaries for tickers to company names and tickers to sectors
tickers_to_names = df.set_index('Ticker')['Security Name'].to_dict()
tickers_to_sectors = df.set_index('Ticker')['Sector'].to_dict()

# Function to get historical closing prices for a ticker
def get_historical_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data['Close'].to_dict()

# Set the date range for the past five years
end_date = datetime.today()
start_date = end_date - timedelta(days=365 * 5)

# Dictionary for the historical data
historical_data = {}

# Fetching the historical data for all tickers
for ticker in df['Ticker']:
    print(f"Fetching data for {ticker}")
    historical_data[ticker] = get_historical_data(ticker, start_date, end_date)

# Save the dictionaries for further use
# You can modify the file paths as needed
with open('tickers_to_names.pkl', 'wb') as file:
    pickle.dump(tickers_to_names, file)

with open('tickers_to_sectors.pkl', 'wb') as file:
    pickle.dump(tickers_to_sectors, file)

with open('historical_data.pkl', 'wb') as file:
    pickle.dump(historical_data, file)

print("Data processing complete.")
