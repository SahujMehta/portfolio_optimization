import yfinance as yf
from pathlib import Path
import os
import csv
from typing import Dict, List, Tuple
from statistics import mean
from gekko import GEKKO
from hyperopt import fmin, tpe, hp
from hyperopt import STATUS_OK, STATUS_FAIL
import numpy as np

def calculate_covariance(file_path1: str, file_path2: str) -> float:
    with open(file_path1, newline='') as csvfile1, open(file_path2, newline='') as csvfile2:
        reader1 = csv.reader(csvfile1)
        reader2 = csv.reader(csvfile2)

        prices1 = [float(record[0]) for record in reader1 if record]
        prices2 = [float(record[0]) for record in reader2 if record]

        len_prices = len(prices1)
        if len_prices != len(prices2) or len_prices == 0:
            raise ValueError("Invalid data length or empty file")

        mean1 = mean(prices1)
        mean2 = mean(prices2)

        covariance = sum((prices1[i] - mean1) * (prices2[i] - mean2) for i in range(len_prices))
        covariance /= len_prices

        return covariance

def create_covariance_lookup(duration: str) -> Dict[str, float]:
    data_folder = "./data"
    covariance_lookup = {}

    tickers = [ticker.strip('_{}_Quotes.csv'.format(duration)) for ticker in os.listdir(data_folder)
               if ticker.endswith('{}_Quotes.csv'.format(duration))]

    print("Tickers:", tickers)
    print("Number of tickers:", len(tickers))

    for i, ticker1 in enumerate(tickers):
        for ticker2 in tickers[i + 1:]:
            file_path1 = f"{data_folder}/{ticker1}_{duration}_Quotes.csv"
            file_path2 = f"{data_folder}/{ticker2}_{duration}_Quotes.csv"

            try:
                covariance = calculate_covariance(file_path1, file_path2)
                covariance_lookup[f"{ticker1}-{ticker2}"] = covariance
                covariance_lookup[f"{ticker2}-{ticker1}"] = covariance  # Assuming covariance is symmetric
            except Exception as e:
                print(f"Error calculating covariance for {ticker1}-{ticker2}: {e}")

    return covariance_lookup

def save_covariance_lookup(duration: str) -> None:
    covariance_lookup = create_covariance_lookup(duration)

    print("Covariance Lookup Table:")
    for key, value in covariance_lookup.items():
        print(f"{key}: {value}")

    file_name = f"covariance_lookup_{duration}.csv"
    csv_data = "\n".join([f"{key},{value}" for key, value in covariance_lookup.items()])

    folder_path = "data"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = f"{folder_path}/{file_name}"
    with open(file_path, 'w') as file:
        file.write(csv_data)

    print(f"Covariance lookup has been saved successfully in file: {file_path}")

def load_covariance_lookup(duration: str) -> Tuple[Dict[str, float], List[str]]:
    file_name = f"covariance_lookup_{duration}.csv"
    file_path = f"data/{file_name}"

    covariance_lookup = {}
    unique_tickers = []

    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for record in reader:
            if len(record) >= 2:
                ticker_pair, value = record[0], float(record[1])

                tickers = ticker_pair.split('-')
                unique_tickers.extend(tickers)

                covariance_lookup[ticker_pair] = value

    unique_tickers = list(set(unique_tickers))
    return covariance_lookup, unique_tickers

def print_missing_tickers(unique_tickers: List[str], covariance_map: Dict[str, float]) -> None:
    for ticker in unique_tickers:
        found = any(ticker in key for key in covariance_map.keys())
        if not found:
            print(f"Ticker '{ticker}' is not in the covariance map keys")

def calculate_returns(unique_tickers: List[str], duration: str) -> Dict[str, float]:
    total_returns_percentage = {}

    for ticker in unique_tickers:
        file_path = f"data/{ticker}_{duration}_Quotes.csv"

        with open(file_path, newline='') as file:
            reader = csv.reader(file)
            prices = [float(record[0]) for record in reader if record]

            if prices:
                initial_price, final_price = prices[0], prices[-1]
                total_return_percentage = ((final_price - initial_price) / initial_price) * 100.0
                total_returns_percentage[ticker] = total_return_percentage
            else:
                print(f"Invalid price data for {ticker}")

    return total_returns_percentage


async def load_from_list(file_path: str, range: str) -> None:
    with open(file_path, newline='') as csvfile:
        rdr = csv.reader(csvfile)
        
        # Process tickers
        print("\nFetching data for tickers:")
        counter = 0
        error_counter = 0
        for record in rdr:
            if counter % 1 == 0:  # Fetch data for every third item
                ticker = record[0]
                print(f"Fetching data for {ticker}")
                try:
                    await fetch_and_store_data(ticker, range)
                except Exception as err:
                    print(f"Error fetching data for {ticker}: {err}")
                    error_counter += 1
            counter += 1

        print(f"Attempted to fetch and store data for {counter} tickers, {error_counter} tickers failed")

def fetch_and_store_data(ticker: str, range: str) -> None:
    ticker_data = yf.download(ticker, period=range)
    
    # Extracting the 'Close' prices
    quotes = ticker_data['Close']
    
    # Prepare CSV data
    csv_data = "\n".join([f"{close}" for close in quotes])

    folder_path = "data"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Write to CSV file
    file_name = f"{folder_path}/{ticker}_{range}_Quotes.csv"
    with open(file_name, 'w') as file:
        file.write(csv_data)

    print(f"Data has been fetched and stored successfully in file: {file_name}")

async def fetch_risk_free_rate(ticker: str) -> float:
    ticker_data = yf.download(ticker, period="1d")
    
    # Extracting the 'Close' price for risk-free rate (assuming it represents a daily rate)
    if not ticker_data.empty:
        risk_free_rate = ticker_data['Close'].iloc[0] / 100.0
        return risk_free_rate

    raise Exception("No quotes found")

def create_sector_lookup(file_path: str) -> Dict[str, List[str]]:
    sector_lookup = {}

    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # Skip headers

        for record in reader:
            ticker = record[0]
            sector = record[2]

            # Create or update the sector lookup
            tickers_for_sector = sector_lookup.setdefault(sector, [])
            tickers_for_sector.append(ticker)

    return sector_lookup

def maximize_sharpe_ratio(returns_map, covariance_map, ticker_map, max_investment_size, min_investment_size, max_number_of_stocks, max_investment_per_sector, risk_free_rate, sector_lookup):
    print("\nCalculating optimal portfolio...")

    # Define the objective function for Hyperopt
    def objective(params):
        m = GEKKO(remote=False)
        x = [m.Var(lb=0, ub=max_investment_size) for _ in range(len(ticker_map))]
        for i, var in enumerate(x):
            var.value = params[f'x{i+1}']

        total_investment = sum(returns_map[i] * x[i] for i in range(len(returns_map)))

        # Objective: Maximizing Sharpe Ratio
        expected_return = sum(returns_map[i] * x[i] for i in range(len(returns_map))) * sum(returns_map[i] * x[i] for i in range(len(returns_map)))
        std_dev = sum(sum(covariance_map.get(f"{ticker_map[i]}-{ticker_map[j]}", 0) * x[i] * x[j]
                         for j in range(len(ticker_map)))
                     for i in range(len(ticker_map)))


        sharpe_ratio = (expected_return - risk_free_rate) / std_dev
        m.Maximize(sharpe_ratio)

        # Constraints and investment size limitations here...
        m.Equation(sum(x[i] for i in range(len(x))) == 1)


        # for sector, sector_tickers in sector_lookup.item():
        #     sector_weights = [returns_map[ticker_map[index]] for index, ticker in enumerate(ticker_map) if ticker in sector_tickers]
        #     total_sector_investment = sum(sector_weights)

        #     # Constraint: Total investment within each sector <= max_investment_per_sector
        #     m.Equation(total_sector_investment <= max_investment_per_sector)

        m.options.SOLVER = 1
        m.solve(disp=False, debug=False)
        obj = m.options.objfcnval
        if m.options.APPSTATUS == 1:
            s = STATUS_OK
        else:
            s = STATUS_FAIL
        m.cleanup()
        return {'loss': -obj, 'status': s, 'x': x}  # Negative for maximization

    space = {f'x{i+1}': hp.quniform(f'x{i+1}', 0, 1, 1) for i in range(len(ticker_map))}
    
    # Perform optimization
    best = fmin(objective, space, algo=tpe.suggest, max_evals=100)

    sol = objective(best)
    print(f"Solution Status: {sol['status']}")
    print(f"Objective: {sol['loss']:.3f}")  # Negative, so we negate it back
    print(f"Solution: {sol['x']}")



async def main() -> None:
    file_path = "S-and-P-500-list.csv"

    range = "5y"
    load_data = False
    if load_data:
        await load_from_list(file_path, range)

    risk_free_rate = await fetch_risk_free_rate("^IRX")
    print(f"\nFetching risk-free rate...{risk_free_rate}")

    generate_covariance_lookup = False
    if generate_covariance_lookup:
        save_covariance_lookup(range)

    covariance_map, unique_tickers = load_covariance_lookup(range)

    try:
        print(f"Number of Unique Tickers: {len(unique_tickers)}")
        print(f"Number of Covariance Values: {len(covariance_map)}")
    except Exception as err:
        print(f"Error: {err}")
        unique_tickers, covariance_map = [], {}

    print_missing_tickers(unique_tickers, covariance_map)

    returns = calculate_returns(unique_tickers, range)

    sector_lookup = create_sector_lookup(file_path)

    max_investment_size = 0.1
    min_investment_size = 0.00
    max_number_of_stocks = 30
    max_investment_per_sector = 0.3

    ticker_map: Dict[int, str] = {index: ticker for index, ticker in enumerate(unique_tickers)}

    returns_map: Dict[int, float] = {index: returns[ticker] for index, ticker in ticker_map.items()}

    # print("Checking returns_map and ticker_map:")
    # print("Returns Map:")
    # for ticker, ret in returns_map.items():
    #     print(f"{ticker}: {ret}")

    # print("\nTicker Map:")
    # for index, ticker in ticker_map.items():
    #     print(f"{index}: {ticker}")


    # CALCULATE OPTIMAL PORTFOLIO
    maximize_sharpe_ratio(
        returns_map,
        covariance_map,
        ticker_map,
        max_investment_size,
        min_investment_size,
        max_number_of_stocks,
        max_investment_per_sector,
        sector_lookup,
        risk_free_rate
    )

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
