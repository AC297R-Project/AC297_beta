import statsmodels.api as sm
import numpy as np

def get_beta(stock, market, start=None, end=None, window=60):
    """
    Produces a day-by-day prediction of beta for the stock against the market. Each beta is predicted using
    a rolling ordinary least squares approach that information from the previous number of days given by windows.
    
    Parameters
    ----------
    
    stock : list or ndarray
        Array of stock returns.
    market: list or ndarray
        Array of market returns.
    start : int
        Index at which to begin computing beta. If neither start nor end is specified, do the computation over
        all of stock and market. If either start or end is specified, then both should be specified.
    end : int
        Index at which to stop computing beta.
    window : int
        The size of the time period on which the beta estimate is based.
    
    Returns
    -------
    results : ndarray
        List of alpha and beta values. The length is the number of days in the sample minus the window, since there
        isn't enough past data to compute beta values for the first day(s). The first row is alpha values and the
        second row is beta values.
    """
    
    # Check preconditions
    if (not start and not end):
        # If there's no specific start and end date, then market and stock must have the same length
        assert len(stock) == len(market), "stock values and market values must have same length"
    if ((start and not end) or (not start and end)):
        raise ValueError("if either start or end is specified, then both must be specified")
        
    # Compute the number of days of data
    if (start and end):
        n_days = end - start
    else:
        n_days = len(stock)
    
    # Array to store results
    results = np.empty((2, n_days - window))
    
    for t in range(n_days - window):
        # Choose the window to calculate beta
        stock_window = stock[t:t+window]
        market_window = market[t:t+window]
        
        # Use OLS to calculate beta
        market_window = sm.add_constant(market_window)
        ols = sm.OLS(endog=stock_window, exog=market_window)
        alpha, beta = ols.fit().params
        results[0, t], results[1, t] = alpha, beta
        
    return results