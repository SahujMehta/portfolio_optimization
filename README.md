The Sharpe Ratio is a metric used to assess the risk-adjusted return of an investment or a trading strategy. It was developed by Nobel laureate William F. Sharpe in 1966. The formula to calculate the Sharpe Ratio is:

$$
\text{Sharpe Ratio} = \frac{R_p - R_f}{\sigma_p}
$$

Where:
- $R_p$ is the return of the portfolio.
- $R_f$ is the risk-free rate of return, typically the yield of a 3-month government Treasury bill.
- $\sigma_p$ is the standard deviation of the portfolio's excess return (the portfolio's return over the risk-free rate).

The Sharpe Ratio is essentially a measure of excess return (compared to risk free return). It represents the additional return gained for the increase in risk. Maximizing the sharpe ratio limits risk in comparision to the risk free returns of an asset such as a treasury bill, while also allowing the returns of the portfolio to be maximized.
The Sharpe Ratio is however not without its own limitations. First, it assumes that the returns of investments are normally distributed which is not always true. It also assumes that the risk_free rate is relatively stable which is also not always the case. Finally, it fails to take into account any metrics about the actual quality of any company and past performance is not always indicative of future performance.

For this project my goal was to maximize the Sharpe Ratio as follows: 

$\text{Maximize: } \frac{\sum_{i=1}^{n} w_i \cdot R_i - R_f}{\sqrt{\sum_{i=1}^{n}\sum_{j=1}^{n} w_i \cdot w_j \cdot \text{Cov}(R_i, R_j)}}$

Where $\text{w}$ represents a decision variable for the weight of the stock in the portfolio. The weight can range from -1 to 1 to represent a short of the value of the entire portfolio or a long of a stock representing the value of the entire portfolio.
Constraining the decision variables limits the max investment size of the stock in relation to the portfolio.

I started initially in python trying to write a script that would maximize the sharpe ratio while enabling the individual to constrain the max investment of a stock in a given sector and also the max size of any investment. The goal was to test this by trying to optimize a list of stocks composed of securities in the S&P 500 with five years of data. This approach lead me to two main problems, #1 at the time, the yahoo finance api for python was broken (https://github.com/ranaroussi/yfinance/issues/1729) and my attempts at manually loading data led me to believe that the shear number of calculations that would need to occur would take far too long in python.

Thus I switched to Rust for development. My thought process was that since it had a working API for getting stock data and also is a system language, that it would work significantly faster for the copious amounts of calculations. I opted not to use C due to the difficulties with memory management and library usage in C. In Rust
