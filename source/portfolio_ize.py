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
    
    assert np.sum(weights) == 1, "Sum of weights vector must equal 1"
    
    # Get starting value in dollars of each asset in the portfolio
    starting_values = np.array(weights) * starting_value
    
    # Get number of shares of each asset in the portfolio by starting value by starting price
    top_row = portfolio.iloc[0,:]
    num_shares = starting_values / top_row
    
    # Multiply every row of the input data frame by the number of shares to give the value of each asset
    df_values = portfolio.apply(lambda x: x*num_shares, axis=1)
    
    assert np.sum(df_values.iloc[0,:]) == starting_value, "Sum of top row is not equal to the starting value"
    
    return df_values