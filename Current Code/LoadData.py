import pandas as pd
import yfinance as yf
import pickle
import numpy as np


def read_tickers(csv_file):
    """
    Read stock tickers from a CSV file.
    Assumes the CSV has a column named 'Tickers'.
    """
    data = pd.read_csv(csv_file)
    tickers = data['Ticker'].tolist()
    return tickers

def fetch_stock_data(tickers, start_date, end_date):
    """
    Fetch historical stock data for the given tickers using yfinance.
    Preallocates space for the DataFrame to improve efficiency.
    Skips tickers if data is not available.
    """
    # Estimate the number of trading days in the date range
    # This is a rough estimate; you might need to adjust this based on your specific date range
    num_trading_days = pd.date_range(start=start_date, end=end_date, freq='B').shape[0]

    # Preallocate space for the DataFrame
    stock_data = pd.DataFrame(index=pd.date_range(start=start_date, end=end_date, freq='B'), columns=tickers)

    for ticker in tickers:
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
            if not data.empty:
                # Use 'Adj Close' for adjusted close prices
                stock_data[ticker] = data['Adj Close']
        except Exception as e:
            print(f"Failed to fetch data for {ticker}: {e}")

    # Drop any columns (tickers) that were not populated
    stock_data = stock_data.dropna(axis=1, how='all')
    
    return stock_data

def calculate_returns(stock_data):
    """
    Manually calculate the daily returns of the stocks.
    Drops stocks that don't have the same number of data points as 95% of the other stocks.
    Preallocates the DataFrame to avoid fragmentation.
    """
    num_days = len(stock_data)
    num_stocks = len(stock_data.columns)
    
    # Preallocate the DataFrame with NaN values
    returns = pd.DataFrame(np.nan, index=stock_data.index, columns=stock_data.columns)

    for stock in stock_data.columns:
        # Calculate daily return manually
        for i in range(1, num_days):
            previous_price = stock_data[stock].iloc[i - 1]
            current_price = stock_data[stock].iloc[i]
            if pd.notna(previous_price) and pd.notna(current_price):
                daily_return = (current_price - previous_price) / previous_price
                returns.at[stock_data.index[i], stock] = daily_return

    # Determine the 95% threshold for the number of data points
    threshold = int(returns.notna().sum().quantile(0.95))

    # Drop columns (stocks) with fewer data points than the threshold
    valid_stocks = returns.notna().sum() >= threshold
    returns = returns.loc[:, valid_stocks]

    # Drop rows with NaN values
    returns = returns.dropna()

    return returns


def calculate_covariance(returns):
    """
    Calculate the covariance matrix of the stock returns.
    """
    covariance = returns.cov()
    return covariance

def save_stock_data(stock_data, filename):
    with open(filename, 'wb') as file:
        pickle.dump(stock_data, file)

def load_stock_data(filename):
    try:
        with open(filename, 'rb') as file:
            stock_data = pickle.load(file)
        return stock_data
    except (FileNotFoundError, EOFError, pickle.UnpicklingError):
        return None

def get_risk_free_rate(start_date, end_date):
    # Fetch ^IRX data for the given date range
    irx_data = yf.download('^IRX', start=start_date, end=end_date)

    # Calculate the mean of the 'Adj Close' values
    mean_irx = irx_data['Adj Close'].mean()

    # The mean value is an annualized percentage
    # To convert it to a decimal, divide by 100
    risk_free_rate = mean_irx / 100

    return risk_free_rate

