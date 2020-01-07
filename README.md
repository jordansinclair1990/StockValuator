# StockValuator
Uses a DCF calculation to estimate the intrinsic value of a given stock.

This terminal-based app will take in a ticker symbol, find the historical free-cash-flow data,
and project future cash flows with the data and perform a discounted-cash-flow valuation
on the stock.

# How to use:
1. Clone this repository
2. Open terminal
3. cd into the StockValuator directory
4. Enter the following command: python3 stockvaluator.py
5. Enter the ticker which you would like to evaluate
6. Enter "Y" to continue with default settings, or "N" to change parameters
7. The program will return the Ticker, DCF-Value, and last price of the stock.

# How it works:
The program retrieves the free-cash-flow-per-share info from Morningstar. It then uses this data
and calculates a linear regression line for the free-cash-flow per year.
The program will then extrapolate the future cash flows using this regression line. The 
"short-term-forecast years" determines how many years will be extrapolated using the regression line.
after the short-term-forecast years have been calculated, the program will then take the last short
term forecast cashflow and then calculates a terminal value with the growth rate and the
discount rate that was entered.
