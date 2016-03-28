import numpy as np
import pandas as pd

# Utility to convert dates to ints so that they can be compared
def date_to_int(date):
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]
    return int(year+month+day)

def portfolio_ize(portfolio, starting_value, weights):
    """
    Takes a data frame of daily close prices, the total portfolio starting value, and the relative weight of each 
        asset, and returns a data frame of the daily total values of each asset in the portfolio.
    
    Inputs:
    -------
    portfolio: Pandas DataFrame of daily close prices
    starting_value: float, Total starting value of the portfolio
    weights: vector of weights of each asset, in the same order as the columns of the df.  Must sum to 1.  
    
    Returns:
    --------
    df_values: Pandas DataFrame of daily total values of each asset in the portfolio.
    """
    
    assert np.sum(weights)==1, "Sum of weights vector must equal 1"
    
    # Get starting value in dollars of each asset in the portfolio
    starting_values = np.array(weights) * starting_value
    
    # Get number of shares of each asset in the portfolio by starting value by starting price
    top_row = portfolio.iloc[0,:]
    num_shares = starting_values/top_row
    
    # Multiply every row of the input data frame by the number of shares to give the value of each asset
    df_values = portfolio.apply(lambda x: x*num_shares, axis=1)
    
    assert np.sum(df_values.iloc[0,:])==starting_value, "Sum of top row is not equal to the starting value"
    
    return df_values
    
def portfolio_to_series(portfolio):
    """
    Takes a pandas dataframe containing daily prices, and returns a pandas series of the total daily value
    
    inputs:
    -------
    portfolio: pandas dataframe of daily prices
    
    outputs:
    --------
    series: pandas series of total daily price of the portfolio
    """
    return portfolio.apply(lambda x: np.sum(x), axis=1)
    

def beta_hedging(betas, market, portfolio):
    """
    Performs beta-hedging, given a portfolio, a market, and beta forecasts.
    
    Parameters:
    -----------
    betas: Pandas Series
        Beta forecasts matching length and frequency of the provided market and portfolio.
    market: Pandas Series
        Asset values of the market that is used to hedge the portfolio.
    portfolio: Pandas Series
        Asset values of the portfolio that is being traded.
    
    Returns:
    --------
    returns: Pandas Series
        Daily returns of the hedged portfolio
    """
    assert len(betas) == len(market) == len(portfolio), "Inputs must be same size"
    
    betasvals = betas.values.flatten()
    marketvals = market.values.flatten()
    portfoliovals = portfolio.values.flatten()
    
    length = len(betas)
    datestamps = betas.index
    returns = np.zeros(length-1)
    
    for day in range(length - 1):
        # Today and tomorrow's prices
        portfolio_buyprice = portfoliovals[day]
        portfolio_sellprice = portfoliovals[day+1]
        market_buyprice = marketvals[day]
        market_sellprice = marketvals[day+1]
        
        # Ratio used to correct for difference in price between market and portfolio
        price_ratio = portfolio_buyprice/market_buyprice
        
        # Daily returns of the portfolio and the hedge
        portfolio_price_change = portfolio_sellprice - portfolio_buyprice
        hedge_price_change = betasvals[day]*price_ratio*(market_sellprice-market_buyprice)
        
        # Daily returns are the difference between the portfolio and the hedge
        returns[day] = portfolio_price_change - hedge_price_change
    
    return pd.DataFrame(returns, datestamps[1:])
    