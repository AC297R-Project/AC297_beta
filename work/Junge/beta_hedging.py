import numpy as np
import pandas as pd

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
    