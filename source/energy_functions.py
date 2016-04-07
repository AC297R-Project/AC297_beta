import numpy as np

def volatility(portfolio, market=None):
	"""
	Volatility of portfolio returns.
	"""
	return np.std(portfolio)

def correlation(portfolio, market):
	"""
	Correlation of portfolio returns with market returns.
	"""
	return np.abs(np.corrcoef(portfolio, market)[0, 1])

def neg_sharpe(portfolio, market=None):
	"""
	Negative portfolio returns Sharpe ratio (smaller is better).
	"""
	return -np.mean(portfolio) / np.std((portfolio))

def neg_returns(portfolio, market=None):
	"""
	Negative portfolio returns (smaller is better). Expects percentage returns.
	"""

	# Add one to the portfolio to go from percent returns to total percent of previous
	# day's portfolio value.
	# Example: 0.02 returns -> 1.02 of previous day's portfolio value.
	# Also adds a first entry of one in order to calculate percentage returns
	# relative to the initial portfolio value.
	portfolio = np.concatenate(([1], portfolio + 1))
	return np.cumprod(portfolio)[-1] - 1

def energy(volatility_coef=0, correlation_coef=0, neg_sharpe_coef=0,
		   neg_returns_coef=0):
	"""
	Returns a linear combination of volatility, correlation, negative Sharpe, and
	negative returns weighted by their respective coefficients.
	If a coefficient is zero, then that energy function component is ignored.
	"""
	def inner(portfolio, market):
		return volatility_coef * volatility(portfolio) + \
		correlation_coef * correlation(portfolio, market) + \
		neg_sharpe_coef * neg_sharpe(portfolio) + \
		neg_returns_coef * neg_returns(portfolio)
	return inner
