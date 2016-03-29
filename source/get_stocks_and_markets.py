# Sample code to get data

# Get data
# spy = pd.read_csv('../../data/spy.csv')
# stock_df = pd.read_csv('../../data/all_stocks.csv')

# Reindex market data
# spy = spy.set_index('Date')['Close']

def get_stocks_and_market(stocks, market=spy, start='2010-01-01', end='2010-12-31',
                          stock_df=stock_df, valid_years=valid_years):
    """
    Returns a series of percentage portfolio returns and percentage market (S&P 500) returns for a given year
    and a given list of stocks. First indices are removed to deal with NaNs.
    
    Parameters
    ----------
    stocks : Pandas dataframe
    market : Pandas dataframe
    start : str or datetime
    end : str or datetime
    stock_df : dataframe
    valid_years : dict
    
    Returns
    -------
    portfolio : Pandas series
    spy_year : Pandas series
    """
    # Get portfolio data for given year
    n_stocks = len(stocks)
    portfolio = stock_df[stocks][(stock_df.index > start) & (stock_df.index < end)]
    portfolio = portfolio.dropna()
    portfolio = portfolio_ize(portfolio, 1000, [1. / n_stocks] * n_stocks)
    portfolio = portfolio.sum(axis=1)  # sum all the stocks up into one portfolio

    # Get market data for given year
    spy_year = spy[(spy.index > start) & (spy.index < end)]
    spy_year = spy_year.sort_index()
    
    # Find valid years
    valid_idx = []
    for idx in spy_year.index:
        try:
            portfolio[idx]
            valid_idx.append(idx)
        except KeyError:
            pass
        
    portfolio = portfolio.pct_change() 
    spy_year = spy_year[valid_idx]
    spy_year = spy_year.pct_change()
    
    # Make sure both series have the same length
    assert len(portfolio) == len(spy_year), '{} {}'.format(len(po), len(spy_year))
    
    return portfolio[1:], spy_year[1:]