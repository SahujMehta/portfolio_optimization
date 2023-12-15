import pickle
import pandas as pd
import numpy as np

# Load the saved dictionaries
with open('tickers_to_names.pkl', 'rb') as file:
    tickers_to_names = pickle.load(file)

with open('tickers_to_sectors.pkl', 'rb') as file:
    tickers_to_sectors = pickle.load(file)

with open('historical_data.pkl', 'rb') as file:
    historical_data = pickle.load(file)

# Function to print historical data for a given ticker
def print_historical_data(ticker):
    if ticker in historical_data:
        print(f"Historical closing prices for {tickers_to_names.get(ticker, 'Unknown')} ({ticker}):")
        for date, price in historical_data[ticker].items():
            print(f"{date}: {price}")
    else:
        print(f"No historical data available for ticker '{ticker}'.")

# Prompting user input for ticker symbol
ticker_input = input("Enter a ticker symbol: ").upper().strip()

# Print historical data for the entered ticker
print_historical_data(ticker_input)
