import LoadData
import OptimizationScript
import Backtest

def main():
    # Define file paths and parameters
    #csv_file = 'S-and-P-500.csv'  # Replace with your CSV file path
    csv_file = 'DowJones.csv'
    start_date = '2020-01-01'  # Replace with your start date
    end_date = '2023-12-1'    # Replace with your end date
    market_return = 0.1       # Define the market return
    n_trials = 50             # Number of optimization trials
    investable_capital = 1000000  # Investable capital in USD

    # Load data
    filename = 'stock_data.pkl'  # Filename for saved data
    stock_data = LoadData.load_stock_data(filename)

    if stock_data is None:
        # Data loading and other steps from previous example
        tickers = LoadData.read_tickers(csv_file)
        stock_data = LoadData.fetch_stock_data(tickers, start_date, end_date)
        LoadData.save_stock_data(stock_data, filename)

    print(len(stock_data.columns), "stocks loaded")

    # Calculate returns and covariance
    returns = LoadData.calculate_returns(stock_data)
    covariance = LoadData.calculate_covariance(returns)

    risk_free_rate = LoadData.get_risk_free_rate(start_date, end_date)

    # Optimize the portfolio
    best_weights = OptimizationScript.optimize_portfolio(returns, covariance, risk_free_rate, market_return, n_trials)

    # BackTester
    tickers_list = returns.columns.to_list()
    start_date = '2020-01-01'  # Replace with your start date
    end_date = '2023-12-1'    # Replace with your end date
    Backtest.backtest_portfolio(start_date, end_date, investable_capital, best_weights, tickers_list, risk_free_rate)

if __name__ == "__main__":
    main()
