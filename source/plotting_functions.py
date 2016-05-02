import pandas as pd
import numpy as np
# import sys
# sys.path.append('../../source')
import matplotlib.pylab as plt
# %matplotlib inline
import seaborn as sns
sns.set_style('white')
sns.set_context('talk')

from BetaUtils import beta_hedging_ret, get_beta
from energy_functions import correlation, neg_returns, volatility
from Hedge import Hedge

import datetime

def generate_results_as_ts(market, portfolio, start_test_date, end_test_date, stocks_dir='../../data/all_stocks.csv',\
                           spy_dir='../../data/spy.csv', period_len=20, window=60):
    """
    Generates results of beta-hedging, given a portfolio, a hedging market, a time period, and a number of desired
        periods.  
        
    Inputs:
    -------
    market: list of assets in the market that will be hedged against
    portfolio: list of assets in the portfolio that is being tested
    start_test_date: date that the testing period begins.  Given in 'yyyy-mm-dd' format.
    end_test_date: date that the testing period ends.  Given in 'yyyy-mm-dd' format.
    stocks_dir: path to a file containing the stock universe
    spy_dir: path to a file containing the results of the SPY ETF
    period_len: length in days of each time period for the time series
    ols_window: length in days of the window that is used to calculate beta using OLS
    
    Outputs:
    --------
    results: Pandas DataFrame of time series results with the following columns:
    market_correlation
    spy_correlation
    unhedged_correlation
    market_volatility
    spy_volatility
    unhedged_volatility
    market_neg_returns
    spy_neg_returns
    unhedged_neg_returns
    """
        
    hedge = Hedge(stocksdir=stocks_dir, spydir=spy_dir, begindate=start_test_date, enddate=end_test_date)
    hedge.market = market
    hedge.portfolio = portfolio
    spy = hedge.spy.pct_change()
    
    dates = hedge.allstockdf.index[window:]
    num_periods = len(dates[::period_len])
    
    # Create the columns for the df
    columns = []
    for mark in ['market','spy','unhedged']:
        for metric in ['correlation','volatility','neg_returns']:
            columns.append(mark+'_'+metric)
         
    results = pd.DataFrame(np.zeros((num_periods,9)),index=dates[::period_len], columns = columns)
    
    # Get returns hedged against market
    _, betas = get_beta(hedge.dollar_portfolio_sum_ret, hedge.dollar_market_sum_ret)
    market_hedged_returns = beta_hedging_ret(betas[1:],hedge.dollar_portfolio_sum_ret[window+1:],\
                                            hedge.dollar_market_sum_ret[window+1:])

    # Get returns hedged against S&P 500
    _, betas = get_beta(hedge.dollar_portfolio_sum_ret, hedge.spy.pct_change())
    spy_hedged_returns = beta_hedging_ret(betas[1:],hedge.dollar_portfolio_sum_ret[window+1:],\
                                            hedge.spy.pct_change()[window+1:])

    # Get unhedged returns
    unhedged_returns = hedge.dollar_portfolio_sum_ret[window+1:].values
      
    for ii,date in enumerate(dates[::period_len]):
        i_start = ii*period_len
        i_end = (ii+1)*period_len
        for metric in ['correlation','volatility','neg_returns']:
            results.loc[date,'market_' + metric]   = globals()[metric]\
                (market_hedged_returns[i_start:i_end],spy[window+1+i_start:window+1+i_end])
            results.loc[date,'spy_' + metric]      = globals()[metric]\
                (spy_hedged_returns[i_start:i_end],spy[window+1+i_start:window+1+i_end])
            results.loc[date,'unhedged_' + metric] = globals()[metric]\
                (unhedged_returns[i_start:i_end],spy[window+1+i_start:window+1+i_end])
    
    return results.sort_index()

def batch_results_plotter(portfolios, markets, states, starttime, endtime, stocks_dir='../../data/all_stocks.csv',\
                           spy_dir='../../data/spy.csv'):
    """
    Given portfolios, hedging markets, a history of Simulated Annealing energy states, and a time range, 
        function produces and saves summary plots.  t
        
    Inputs:
    -------
    portfolios: A text file of numbered portfolios.  Each portfolio is on a separate line.
    markets: A text file of numbered hedging markets.  Each market is on a separate line.  
    states: A text file of energy states from simulated annealing.  
    starttime: Starting date for plot generation, should begin 60 days prior to the first desired test day
        because of the OLS window
    endtime: Ending date for plot generation.  

    Outputs:
    --------
    Saves to file the following plots:
        
        States.png: Trace plots of all of the Simulated annealing runs
        
        Correlation_barplot.png: Bar plots comparing the mean Spy-hedged, Market-hedged, and Unhedged results,
            with error bars representing one standard deviation error.  
        Volatility_barplot.png: Same as above, for volatility.
        Returns_barplot.png: Same as above, for % returns.  
        
        Correlation_TSplot.png: Monthly time series plot comparing the three hedging strategies, with a shaded
            region around one standard deviation for each month.
        Volatility_TSplot.png: Same as above for volatility.
        Returns_TSplot.png: Same as above for % returns.
    """
    
    # Traces
    if states != None:
        with open(states, 'r') as f:
            stat = f.read().split(',')
        for ii, line in enumerate(stat):
            stat[ii] = map(float, line.replace('\n','').strip('[').strip(']').split())
            plt.plot(stat[ii])

        plt.title('Trace plots')
        plt.xlabel('SA Iterations')
        plt.ylabel('Energy')
        plt.savefig('States.png')
        plt.close()
    
    # Get results
    ports = []
    with open(portfolios, 'r') as f:
        for line in f.readlines():
            ports.append(line.strip().replace(' ','').split(',')[1:])
    
    marks = []
    with open(markets, 'r') as f:
        for line in f.readlines():
            marks.append(line.strip().replace(' ','').split(',')[1:])
            
    assert len(marks)==len(ports), "Must have the same number of markets and portfolios."
    
    # Bar Plots
    
    # For the bar plots I use generate_results_as_ts for convenience, with a nonsense (1000000) 
    #    period length to make one value for the whole test period.
    spy_correlation = []
    market_correlation = []
    unhedged_correlation = []
    spy_volatility = []
    market_volatility = []
    unhedged_volatility = []
    spy_returns = []
    market_returns = []
    unhedged_returns = []
    
    for ii, port in enumerate(ports):
        df = generate_results_as_ts(marks[ii], port, starttime, endtime, \
                                                 stocks_dir, spy_dir, period_len=1000000)
        
        spy_correlation.append(df['spy_correlation'])
        market_correlation.append(df['market_correlation'])
        unhedged_correlation.append(df['unhedged_correlation'])
        
        spy_volatility.append(df['spy_volatility'])
        market_volatility.append(df['market_volatility'])
        unhedged_volatility.append(df['unhedged_volatility'])
        
        spy_returns.append(-100*df['spy_neg_returns'])
        market_returns.append(-100*df['market_neg_returns'])
        unhedged_returns.append(-100*df['unhedged_neg_returns'])
        
    for metric in ['correlation', 'volatility', 'returns']:
        spy_mean = np.mean(locals()['spy_'+metric])
        spy_std = np.std(locals()['spy_'+metric])
        
        market_mean = np.mean(locals()['market_'+metric])
        market_std = np.std(locals()['market_'+metric])
        
        unhedged_mean = np.mean(locals()['unhedged_'+metric])
        unhedged_std = np.std(locals()['unhedged_'+metric])
        
        plt.bar([0,1,2],[spy_mean, market_mean, unhedged_mean], color=['b','g','r'],\
                yerr=[spy_std, market_std, unhedged_std], error_kw=dict(ecolor='black', lw=2, capsize=5, capthick=2))
        plt.xticks(np.array([0,1,2]) + 0.4, ('SPY_hedged', 'Market_hedged', 'Unhedged'))
        plt.xlim(-0.2,3.0)
        plt.title(metric.capitalize())
        plt.savefig(metric.capitalize()+'_barplot.png')
        plt.close()

    # Time Series Plots
    
    spy_correlation = []
    market_correlation = []
    unhedged_correlation = []
    spy_volatility = []
    market_volatility = []
    unhedged_volatility = []
    spy_returns = []
    market_returns = []
    unhedged_returns = []
    
    for ii, port in enumerate(ports):
        df = generate_results_as_ts(marks[ii], port, starttime, endtime, \
                                                 stocks_dir, spy_dir, period_len=20)
        spy_correlation.append(df['spy_correlation'])
        market_correlation.append(df['market_correlation'])
        unhedged_correlation.append(df['unhedged_correlation'])
        
        spy_volatility.append(df['spy_volatility'])
        market_volatility.append(df['market_volatility'])
        unhedged_volatility.append(df['unhedged_volatility'])
        
        spy_returns.append(-100*df['spy_neg_returns'])
        market_returns.append(-100*df['market_neg_returns'])
        unhedged_returns.append(-100*df['unhedged_neg_returns'])
        
    for metric in ['correlation', 'volatility', 'returns']:
        spy = pd.concat(locals()['spy_'+metric],axis=1)
        spy_mean = spy.mean(axis=1)
        spy_std = spy.std(axis=1)
        print spy
        
        market = pd.concat(locals()['market_'+metric],axis=1)
        market_mean = market.mean(axis=1)
        market_std = market.std(axis=1)
        print market
        
        unhedged = pd.concat(locals()['unhedged_'+metric],axis=1)
        unhedged_mean = unhedged.mean(axis=1)
        unhedged_std = unhedged.std(axis=1)
        print unhedged
        
        dates = [datetime.datetime.strptime(ii, '%Y-%m-%d') for ii in spy_mean.index]
        
        plt.plot(dates, spy_mean.values, color = 'b', label = 'SPY')
        plt.fill_between(dates, spy_mean.values-spy_std.values, \
                         spy_mean.values+spy_std.values, alpha=0.1, color = 'b')
        plt.plot(dates, market_mean.values, color = 'g', label='Market')
        plt.fill_between(dates, market_mean.values-market_std.values,\
                        market_mean.values+market_std.values, alpha=0.1, color = 'g')
        plt.plot(dates, unhedged_mean.values, color = 'r', label="Unhedged")
        plt.fill_between(dates, unhedged_mean.values-unhedged_std.values,\
                        unhedged_mean.values+unhedged_std.values, alpha=0.1, color = 'r')
        
        plt.legend(loc='best')
        plt.title(metric.capitalize())
        plt.savefig(metric.capitalize()+"_TSplot.png")
        plt.close()
    
    
    
    