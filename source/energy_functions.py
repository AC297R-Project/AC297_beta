import numpy as np

def correlation(portfolio, spy):
    return np.corrcoef(portfolio, spy)[0, 1]

def volatility(portfolio, spy=None):
    return portfolio.std()

def sharpe(portfolio, spy=None):
    return -portfolio.mean() / portfolio.std()