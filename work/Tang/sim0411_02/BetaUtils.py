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
        stock_window = np.array(stock[t:t+window])

        market_window = np.vstack([np.ones(window), market[t:t+window]]).T

        beta = np.dot(np.linalg.pinv(market_window), stock_window)
        
        results[:,t] = beta.T
        
    return results


def beta_hedging_ret(betas, port_ret, market_ret):
    assert len(market_ret) == len(betas) == len(port_ret), 'Beta, Market, Portfolio returns should have same dimension'
    assert not any(np.isnan(betas)), 'beta contains nan'
    assert not any(np.isnan(market_ret)), 'market contains nan'
    assert not any(np.isnan(port_ret)), 'portfolio contains nan'
    
    return np.array(port_ret) - np.array(betas)*np.array(market_ret)
    

def cum_ret(rets):
    prd = np.cumprod(np.array(rets)+1)
    return prd/prd[0]