import numpy as np
import optuna
import optuna.logging
from optuna.samplers import TPESampler

# def calculate_downside_deviation(returns, risk_free_rate):
#     # Ensure that 'returns' is a DataFrame of floats
#     returns = returns.astype(float)
#     # Calculate downside deviations
#     downside_returns = returns.apply(lambda x: x.map(lambda y: min(0, y - risk_free_rate)))
#     return np.sqrt((downside_returns**2).mean())

def calculate_portfolio_performance(weights, returns, covariance, risk_free_rate, market_return):
    #std_market_return = np.std(market_return)
    #portfolio_beta = np.dot(weights.T, np.dot(covariance, np.ones(len(weights)))) / std_market_return if std_market_return > 0 else 1
    portfolio_return = np.sum(returns.mean() * weights)
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance, weights)))
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility
    return sharpe_ratio

def objective(trial, returns, covariance, risk_free_rate, market_return):
    n_stocks = returns.shape[1]

    # Generate weights with a maximum of 1 for each
    weights = np.array([trial.suggest_float(f'w{i}', -1, 1, step = 0.001) for i in range(n_stocks)])

    # Normalize weights to ensure their sum is 1
    weights /= np.sum(weights)

    return calculate_portfolio_performance(weights, returns, covariance, risk_free_rate, market_return)

def optimize_portfolio(returns, covariance, risk_free_rate, market_return, n_trials=100):
    # Set logging level to ERROR to suppress output
    #optuna.logging.set_verbosity(optuna.logging.ERROR)

    study = optuna.create_study(direction='minimize', sampler=TPESampler(seed=42))
    study.optimize(lambda trial: objective(trial, returns, covariance, risk_free_rate, market_return), n_trials=n_trials)

    # Retrieve the best parameters and normalize them
    best_params_raw = study.best_params
    best_weights_raw = np.array([best_params_raw[f'w{i}'] for i in range(len(best_params_raw))])
    best_weights_normalized = best_weights_raw / np.sum(best_weights_raw)

    # Print the maximized Sharpe ratio
    print(f"Maximized Sharpe Ratio: {-study.best_value}")

    # Return normalized weights
    return best_weights_normalized