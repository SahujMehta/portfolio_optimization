import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def backtest_portfolio(start_date, end_date, investible_capital, weights, tickers, risk_free_rate):
    # Fetch historical data
    data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']

    # Allocate initial capital based on weights
    initial_prices = data.iloc[0]
    capital_allocation = investible_capital * weights
    shares = np.round(capital_allocation / initial_prices).fillna(0)
    

    # Calculate the actual invested capital and cash remaining
    invested_capital = (shares * initial_prices).sum()
    cash_remaining = investible_capital - invested_capital

    # Portfolio value over time
    portfolio_value = (data * shares).sum(axis=1) + cash_remaining

    # SPY and Risk-Free Rate data for comparison
    spy = yf.download('SPY', start=start_date, end=end_date)['Adj Close']
    dji = yf.download('^DJI', start=start_date, end=end_date)['Adj Close']
    risk_free_daily = np.exp(risk_free_rate / 365) - 1  # Convert annual rate to daily
    risk_free_value = investible_capital * (1 + risk_free_daily) ** np.arange(len(data))

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_value.index, portfolio_value, label='DJI Optimized Portfolio')
    #plt.plot(spy.index, spy/spy.iloc[0]*investible_capital, label='SPY')
    plt.plot(dji.index, dji/dji.iloc[0]*investible_capital, label='DJI')
    plt.plot(data.index, risk_free_value, label='Risk-Free Asset')
    plt.legend()
    plt.title('DJI Portfolio Backtest')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value')
    plt.show()

    # Results
    print(f"Cash remaining: ${cash_remaining:.2f}")
    return cash_remaining
