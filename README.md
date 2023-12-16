# Portfolio Optimization
## Sahuj Mehta | Math 420

The goal of this project was to identify ways to optimize the allocation of securities in a portfolio, through optimization techniquest. For this project, I focused on Maximizing the Sharpe Ratio for the S&P 500 and the Dow Jones Index.

The Sharpe Ratio is a metric used to assess the risk-adjusted return of an investment or a trading strategy. It was developed by Nobel laureate William F. Sharpe in 1966. The formula to calculate the Sharpe Ratio is:

$$
\text{Sharpe Ratio} = \frac{R_p - R_f}{\sigma_p}
$$

Where:
- $R_p$ is the return of the portfolio.
- $R_f$ is the risk-free rate of return, typically the yield of a 3-month government Treasury bill.
- $\sigma_p$ is the standard deviation of the portfolio's excess return (the portfolio's return over the risk-free rate).

  The Sharpe Ratio is essentially a measure of excess return (compared to risk-free return). It represents the additional return gained for the increase in risk. Maximizing the Sharpe ratio limits risk in comparison to the risk-free returns of an asset such as a treasury bill, while also allowing the returns of the portfolio to be maximized.
The Sharpe Ratio is however not without its own limitations. First, it assumes that the returns of investments are normally distributed, which is not always true. It also assumes that the risk_free rate is relatively stable, which is also not always the case. Finally, it fails to take into account any metrics about the actual quality of any company, and past performance is not always indicative of future performance.

For this project my goal was to maximize the Sharpe Ratio as follows: 

$\text{Maximize: } \frac{\sum_{i=1}^{n} w_i \cdot R_i - R_f}{\sqrt{\sum_{i=1}^{n}\sum_{j=1}^{n} w_i \cdot w_j \cdot \text{Cov}(R_i, R_j)}}$

  Where $\text{w}$ represents a decision variable for the weight of the stock in the portfolio. The weight can range from -1 to 1 to represent a short of the value of the entire portfolio or a long of a stock representing the value of the entire portfolio.
Constraining the decision variables limits the max investment size of the stock in relation to the portfolio.

  I started initially in python trying to write a script that would maximize the Sharpe ratio while enabling the individual to constrain the max investment of a stock in a given sector and also the max size of any investment. The goal was to test this by trying to optimize a list of stocks composed of securities in the S&P 500 with five years of data. This approach led me to two main problems, #1 at the time, the Yahoo Finance API for python was broken (https://github.com/ranaroussi/yfinance/issues/1729) and my attempts at manually loading data led me to believe that the sheer number of calculations that would need to occur would take far too long in python.

  Thus, I switched to Rust for development. My thought process was that since it had a working API for getting stock data and also is a system language, that it would work significantly faster for the copious amounts of calculations. I opted not to use C due to the difficulties with memory management and library usage in C. In Rust, I began by setting up by loading the data from 5 years of S&P 500 returns to CSVs with the goal of limiting API calls. I then processed the data into lookup tables for fast memory access. My next step was to attempt linear optimization in Rust. I chose to use the good_lp (https://docs.rs/good_lp/latest/good_lp/) crate since it supported several different methods of linear optimization through other packages that it acts as a wrapper for. I managed to get it mostly working with basic examples such as just maximizing the expected returns of a portfolio, however when I started to try to use it for maximizing the Sharpe Ratio, it wouldn't work, and it wasn't until I realized that it wouldn't work for nonlinear programming that I moved past it since maximizing the Sharpe ratio does require decision variables to be multiplied together.

  After the example on exam 2, I began to research TPE (Tree Parzen Estimator) as a method for dealing with the problems I was having trying to deal with the nonlinear problem in rust. There is a TPE library in Rust, but it doesn't allow for dynamic variable allocation, which meant that my program would only ever be able to work on a fixed number of stocks which I didn't want. I was investigating writing a wrapper for a TPE library in C or writing a library for Rust based on a paper about various algorithms for optimization of hyperparameters(https://proceedings.neurips.cc/paper_files/paper/2011/file/86e8f7ab32cfd12577bc2619bc635690-Paper.pdf) but at that point implementation of such an algorithm would take way too long to get a working project done in the scope of the class. Some of my Rust Code from these attempts can be found in the Rust Code Archive folder.

  These developments led me to return to Python, where I began iterating off the Gekko and Hyperopt example that was given in Exam 2. As I began working off this I realized that the covariance part was going to cause significant problems since the objective function in python is incredibly long and the Gekko model solver only supports equations of up to 15000 characters (https://github.com/BYU-PRISM/GEKKO/issues/72), which limited the project to a max of 17 different securities due to how long the risk management part of the expression would be. I began experimenting with optimizing the model so that it could handle larger model by using the `M.Intermediate()` expression. This optimization could only go so far though before it would break the code by causing missing memory allocation errors with pandas frames. I tried several things to reduce the model further but could only get a max of 23 securities to work with the function. Some working code from these attempts can be found in the Python Code Archive Folder.

  For my latest attempt, I stuck with python, but tried a few different libraries such as scipy-optimize, cvxpy. and optuna. They each presented different challenges, but ultimately, I found that using optuna worked the best since it seemed to be the best optimized library and could handle the large volume of data. The current rendition of the project uses the TPE sampler for optuna and attempts to optimize a portfolio based on this data. It loads the data into pickle files to prevent excess API calls then attempts to optimize the Sharpe Ratio using the optuna library and the TPE method of sampling. The back testing is incredibly rudimentary since I was unable to get Zipline working with any modern data, Moonshot is locked behind a paywall, and quantconnect is incredibly slow. The way back testing is handled, is that the portfolio is optimized based on a CSV file for old data, then given an initial investment makes a purchase just once and monitors the way it pays off. While given enough iterations, the optimization will reach a stable Sharpe ratio, the strategy of just buying once and never rebalancing produces mixed results. Here is a figure of the returns trained on Dow Jones data from 2010-2019 and then tested on the market from 2020 to present.

![DJIData](https://github.com/SahujMehta/portfolio_optimization/assets/51139362/050e5033-98c9-4d25-86e5-0cef4c146de2). 

  This data only lead to a maximized Sharpe ratio of 0.83, which definitely could be improved by exploring other strategies, since I thing the TPE might be reaching a local minimum. While the data does indicate that the Sharpe Ratio was maximized, rebalancing just once means that in effect the portfolio is a rebalanced index rather than a brand-new strategy, so that its something that I intend to improve in the future. Here is a picture of the returns vs the S&P500 to show how it compares to that data. In this optimization, the maximized Sharpe ratio was 0.63. This example also demonstrates the problem with my back testing approach.

![SPY Picture](https://github.com/SahujMehta/portfolio_optimization/assets/51139362/2f99d347-23c6-473f-9176-7bc167023a15)

If trained on the same data that it is then tested on, the optimization strategy performs really well. Here, the Maximized Sharpe Ratio was 1.92.

![DJISameDate](https://github.com/SahujMehta/portfolio_optimization/assets/51139362/a736f483-185c-4a89-b62e-a17e08f471ee)

I have several plans to improve this algorithm in the future. First, I am going to revamp the back testing portion, to make this strategy a more viable option. Next, I am going to try to implement this in C to try to improve speed and test out a wider variety of algorithms for tuning hyperparameters. I would like to try to use some CUDA libraries and hardware acceleration to speed up this process, since it often takes a long time to get data. I would like to use a wider variety of assets too. I am curious to know if there can be more optimization if lower risk assets were also mixed in such as municipal bonds. Additionally, I would like to add support for other metrics outside the Sharpe Ratio due to some of its limitations I listed earlier, adding the ability to maximize other metrics such as the Sortino Ratio or Treynor Ratio could lead to a better strategy. I think there is a lot of potential for improvements on this project, and that exploring more non-linear programming techniques could lead to significant improvements.
