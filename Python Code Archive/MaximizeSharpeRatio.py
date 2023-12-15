import pickle
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
from gekko import GEKKO
from hyperopt import fmin, tpe, hp
from hyperopt import STATUS_OK, STATUS_FAIL

# Function to calculate returns for each stock in a given window
def calculate_returns(stock_data, start_date, end_date):
    data_window = {date: price for date, price in stock_data.items() if start_date <= date <= end_date}
    prices = list(data_window.values())
    returns = [0 if i == 0 else (prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]
    return returns


# Load historical data and other dictionaries
with open('historical_data.pkl', 'rb') as file:
    historical_data = pickle.load(file)
with open('tickers_to_names.pkl', 'rb') as file:
    tickers_to_names = pickle.load(file)
with open('tickers_to_sectors.pkl', 'rb') as file:
    tickers_to_sectors = pickle.load(file)

# User input for date window
start_date = datetime.strptime(input("Enter start date (YYYY-MM-DD): "), "%Y-%m-%d")
end_date = datetime.strptime(input("Enter end date (YYYY-MM-DD): "), "%Y-%m-%d")

risk_free_rate_data = yf.download("^IRX", start_date, end_date)
risk_free_rate = np.mean(risk_free_rate_data['Close'].to_list())/100.0


# Calculate returns for each stock in the given window and track lengths
returns_length = []
returns_data = {}
for ticker, data in historical_data.items():
    stock_returns = calculate_returns(data, start_date, end_date)
    returns_length.append(len(stock_returns))
    returns_data[ticker] = stock_returns

# Determine the 90th percentile length
cutoff_length = np.percentile(returns_length, 95)

# Filter out tickers that don't meet the criterion from all dictionaries
filtered_historical_data = {}
filtered_tickers_to_names = {}
filtered_tickers_to_sectors = {}
filtered_returns_data = {}
for ticker in returns_data:
    if len(returns_data[ticker]) >= cutoff_length:
        filtered_historical_data[ticker] = historical_data[ticker]
        filtered_tickers_to_names[ticker] = tickers_to_names[ticker]
        filtered_tickers_to_sectors[ticker] = tickers_to_sectors[ticker]
        filtered_returns_data[ticker] = returns_data[ticker]

# Check if there is sufficient data
if not filtered_historical_data:
    raise ValueError("Insufficient data in the specified date range.")

# Create a DataFrame for returns and calculate covariance matrix
returns_df = pd.DataFrame(filtered_returns_data)
covariance_matrix = returns_df.cov()

historical_data = filtered_historical_data
tickers_to_names = filtered_tickers_to_names
tickers_to_sectors = filtered_tickers_to_sectors
returns_data = filtered_returns_data

for ticker, returns in returns_data.items():
    print(f"{tickers_to_names[ticker]} ({ticker}): {np.sum(returns):.3f} total return, "
          f"{np.std(returns):.3f} standard deviation")

# Stock information including current price and calculated average return
stocks = {}
for ticker, data in historical_data.items():
    avg_return = np.sum(returns_data[ticker])
    current_price = list(data.values())[-1]  # Last known price
    stocks[ticker] = {'return': avg_return, 'price': current_price}

# print("Stocks:")
# for ticker, data in stocks.items():
#     print(f"{tickers_to_names[ticker]} ({ticker}): {data['return']:.3f} average return, "
#           f"{data['price']:.2f} current price")

# Optimization setup
space = {f'x{i+1}': hp.quniform(f'x{i+1}', 0, 100, 1) for i in range(len(stocks))}

# Define the objective function for Hyperopt
def objective(params):
    m = GEKKO(remote=False)
    x = [m.Var(lb=0, integer=True) for _ in range(len(stocks))]
    for i, var in enumerate(x):
        var.value = params[f'x{i+1}']

    # Total investment and weights
    total_investment = sum(stocks[stock]['price'] * x[i] for i, stock in enumerate(stocks))
    weights = [stocks[stock]['price'] * x[i] / total_investment for i, stock in enumerate(stocks)]

    # Portfolio return and risk (standard deviation)
    total_quantity = m.sum(x)
    portfolio_return = m.Intermediate(sum(stocks[stock]['return'] * weights[i] for i, stock in enumerate(stocks))/total_quantity)
    # portfolio_risk = m.Intermediate(sum(sum(weights[i] * weights[j] * covariance_matrix.iloc[i, j]
    #                                for j in range(len(stocks))) for i in range(len(stocks))))

    weighted_cov_contributions = []
    for i in range(len(stocks)):
        for j in range(len(stocks)):
            contribution = m.Intermediate(weights[i] * weights[j] * covariance_matrix.iloc[i, j])
            weighted_cov_contributions.append(contribution)
    
    total_risk_contribution = m.Intermediate(m.sum(weighted_cov_contributions))
    portfolio_risk = m.Intermediate(m.sqrt(total_risk_contribution))

    # Sharpe Ratio (Assuming risk-free rate is negligible)
    sharpe_ratio = (portfolio_return-risk_free_rate) / portfolio_risk

    m.Maximize(-sharpe_ratio)

    # Constraints
    m.Equation(total_investment <= 10000)
    m.Equation(total_investment >= 8000)
    for i, weight in enumerate(weights):
        m.Equation(weight <= 0.2)


    m.options.SOLVER = 1
    m.solve(disp=True, debug=True)

    obj = m.options.objfcnval
    if m.options.APPSTATUS == 1:
        s = STATUS_OK
    else:
        s = STATUS_FAIL

    m.cleanup()
    return {'loss': obj, 'status': s, 'x': [var.value[0] for var in x]}

# Perform optimization
best = fmin(objective, space, algo=tpe.suggest, max_evals=50)

sol = objective(best)
print(f"Solution Status: {sol['status']}")
print(f"Objective: {sol['loss']:.3f}")
print(f"Solution: {sol['x']}")
