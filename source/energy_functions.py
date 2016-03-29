def correlation(portfolio, market):
    return np.corrcoef(portfolio, market)[0, 1]

def volatility(portfolio):
    return portfolio.std()

def sharpe(portfolio):
    return portfolio.mean() / portfolio.std()