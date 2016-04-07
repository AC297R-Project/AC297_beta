from BetaUtils import get_beta, beta_hedging_ret
from energy_functions import volatility, correlation, neg_sharpe, neg_returns
from Hedge import Hedge
import numpy as np

def get_portfolio(params, invalid):
	with open('portfolios.txt', 'r') as f:
		for line in f:
			portfolio = line.replace("'", " ").replace(" ", "").split(',')
			# Check if portfolio ids match.
			if (portfolio[0] == params['portfolio_id']):
				portfolio = portfolio[1:]
                return [stock for stock in portfolio if stock not in invalid]
	raise IOError('Portfolio ID {} not found'.format(params['portfolio_id']))


def get_market(params, invalid):
	with open('markets.txt', 'r') as f:
		for line in f:
			market = line.replace("'", " ").replace(" ", "").split(',')
			# Check if market ids match.
			if (market[0] == params['starting_market_id']):
				market = market[1:]
                return [stock for stock in market if stock not in invalid]
	raise IOError('Starting market ID {} not found'.format(params['starting_market_id']))


def get_params(parameters, param_list):
	params = {}
	for ii, jj in zip(param_list, parameters[:-1]):
		params[ii] = jj
	params['verbose'] = parameters[-1]
	return params


def write_results(infile, market_hedged_returns, spy_hedged_returns,
	unhedged_returns, spy, params, param_list, window):
	with open(infile, 'a') as f:
		# Write experiment parameters
		for ii in param_list:
			f.write('{},'.format(params[ii]))

		# Write unhedged statistics
		f.write('{},{},{},{},'.format(
			volatility(unhedged_returns),
			correlation(unhedged_returns, spy[window+1:]),
			-neg_sharpe(unhedged_returns),
			-neg_returns(unhedged_returns)))

		# Write optimal market hedged statistics
		f.write('{},{},{},{},'.format(
			volatility(market_hedged_returns),
			correlation(market_hedged_returns, spy[window+1:]),
			-neg_sharpe(market_hedged_returns),
			-neg_returns(market_hedged_returns)))

		# Write S&P hedged returns
		f.write('{},{},{},{}\n'.format(
			volatility(spy_hedged_returns),
			correlation(spy_hedged_returns, spy[window+1:]),
			-neg_sharpe(spy_hedged_returns),
			-neg_returns(spy_hedged_returns)))


def simulated_annealing(hedge, init_temp, min_temp, cool_by, reanneal, num_iter,
	energy_func, window, verbose=False):
    """
    Inputs:
    -------
    hedge: 
        hedge object that already has an instantiated market and portfolio. 
    init_temp: 
        float that controls the initial temperature of the algorithm
    min_temp: 
        float that acts as a floor for the decreasing temperature.  When this is hit, we heat back up to init_temp.  
    cool_by: 
        float that controls the speed that the cooling occurs
    reanneal: 
        integer that controls how many iterations pass between cooling steps
    num_iter: 
        integer that controls the total number of iterations that the algorithm runs
    energy_func:
        function that determines the energy state, eg correlation, volatility, sharpe ratio
    verbose:
    	controls whether iteration numbers are printed
    
    Returns:
    --------
    states: 
        a history of the current energy state at each iteration
    best_market: 
        list of the symbols for the best hedging market found
    """
    
    portfolio_values = hedge.dollar_portfolio_sum
    portfolio_returns = hedge.dollar_portfolio_sum_ret
    
    market = list(hedge.market)
    market_values = hedge.dollar_market_sum
    market_returns = hedge.dollar_market_sum_ret
    
    spy_returns = hedge.spy.pct_change()[window+1:]
    
    # Get betas from portfolio returns and market returns.
    _, betas = get_beta(portfolio_returns, market_returns)
    
    # Perform beta hedging.
    hedged_returns = beta_hedging_ret(
    	betas[1:],
    	portfolio_returns[window+1:],
    	market_returns[window+1:])
        
    # A running account of the best market found.  This is updated as better markets are found.       
    best_market_energy = energy_func(hedged_returns[1:], spy_returns[1:])
    best_market = hedge.market
    
    # Initial value for old_E is the initial total value of the starting point.
    old_E = best_market_energy
    
    temperature = init_temp
    
    # A history of the current state of the algorithm.
    states = np.zeros(num_iter)
    
    for i in range(num_iter):
    	if verbose:
	        if i%100==0:
	            print 'Iteration {}'.format(i),
        
        # Switch the bag up a little bit and recalculate market values and returns.  
        market = list(hedge.market)
        hedge.market = _swap(market, hedge.stockuniverse)
        
        market_values = hedge.dollar_market_sum
        market_returns = hedge.dollar_market_sum_ret
        
        # Get betas from portfolio returns and market returns.
        _, betas = get_beta(portfolio_returns, market_returns)
    
        # Perform beta hedging.
        hedged_returns = beta_hedging_ret(
        	betas[1:],
        	portfolio_returns[window+1:],
        	market_returns[window+1:])
    
        # Examine energy state of the new bag.
        new_E = energy_func(hedged_returns[1:], spy_returns[1:])
        
        delta_E = new_E - old_E
        
        # We always accept an improvement.
        if new_E < old_E:
            #market = proposed_market
            states[i] = new_E
            old_E = new_E
            # Update our running best bag found.
            if new_E < best_market_energy:
                best_market_energy = new_E
                best_market = market[:]
        # We sometimes accept a decline because this can get us out of a local minimum.
        elif np.random.rand() < np.exp(-delta_E / temperature):
            #market = proposed_proposed
            states[i] = new_E
            old_E = new_E

        # And sometimes we just stay where we are until something better comes along.
        else: 
            states[i] = old_E
            # Put the old market back in
            hedge.market = market
            
        # Cool down slowly at the defined interval.
        if num_iter % reanneal == 0:
            temperature = temperature * cool_by
            
            # Reheat when the temperature gets too cold.
            if temperature < min_temp:
                temperature = init_temp
    
    hedge.market = best_market
    return states, best_market


def _swap(market_symbols, year_symbols):
    """
    Randomly changes the symbols in a market. Can either grow or shrink the market by 1 asset.  
    
    Inputs:
    -------
    market_symbols: list of symbols that are in a market
    year_symbols:   list of all the possible symbols for a given year
    
    Output:
    -------
    symbols: list of symbols in the market after the random change.  
    
    """
    coin_flip = np.random.binomial(1, 0.5)
    
    if (coin_flip == 0) and len(market_symbols) > 10: # Shrink the market by one asset
        # Pick a random list index and pop that symbol off
        market_symbols.pop(np.random.randint(len(market_symbols)))
        return market_symbols
    
    else: # Grow the market by one asset
        # Get a list of the symbols for that year that are not already in the portfolio
        potential_symbols = list(set(year_symbols) - set(market_symbols))
        symbol_to_add = np.random.choice(potential_symbols)
        market_symbols.append(symbol_to_add)
        return market_symbols
