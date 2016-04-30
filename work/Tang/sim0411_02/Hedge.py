import pandas as pd
import numpy as np

class Hedge(object):
    
    def __init__(self, stocksdir = '../data/all_stocks.csv', spydir = '../data/spy.csv', begindate = None, enddate = None):
        """
        parameters
        -----
        stocksdir: all stocks directory
        spydir: sp index directory
        begindate: default to None, which is from the very beginning
        enddate: default to None, which is from the very end
        """
        # Use AAPL dates to filter
        # preprossessing
        allstockdf = pd.read_csv(stocksdir)
        spy = pd.read_csv(spydir)

        idxb = 0
        if begindate != None:
            idxb = np.where(allstockdf.Date>=begindate)[0][0]
        if enddate != None:
            try:
                idxe = np.where(allstockdf.Date>=enddate)[0][0]
                allstockdfsliced = allstockdf[idxb:idxe+1]
            except:
                allstockdfsliced = allstockdf[idxb:]
            
        else:
            allstockdfsliced = allstockdf[idxb:]
        
        # use AAPL as reference column to drop nan rows
        self.allstockdf = allstockdf.iloc[allstockdfsliced['AAPL'].dropna().index]
        
        self.allstockdf = self.allstockdf.dropna(axis = 1)

        self._spy = spy[[i in self.allstockdf.Date.values for i in spy.Date]]
        self.allstockdf = self.allstockdf.set_index(['Date'])
        self._spy = self._spy.set_index(['Date']).sort_index()

        assert len(self._spy) == len(self.allstockdf)
        
        # initialize portfolio to be empty
        self._portfolio = []
    
    def _dropRowsAccordingTo(self, df, colname):
        # TODO: may be useful when working on data
        pass
    
    def generateRandomPort(self, size = 20):
        self._portfolio = np.random.choice(self.allstockdf.columns, size)
        self._portfolio_size = len(self._portfolio)
        self.generate_dollar_portfolio()
        return self._portfolio

    def generateRandomMarket(self, size = 20):
        self._market = np.random.choice(self.allstockdf.columns, size)
        self._market_size = len(self._market)
        self.generate_dollar_market()
        return self._market

    @property
    def market(self):
        return self._market
    
    @market.setter
    def market(self, market):
        assert all([i in self.allstockdf.columns for i in market])
        self._market = market
        self._market_size = len(self._market)
        self.generate_dollar_market()

    @property
    def marketdf(self):
        return self.allstockdf[list(self._market)]

    def generate_dollar_market(self, start_val = 1000, allocation = None):
        """
        allocation: list of weights, if None, assuming equal money value
        """
        if allocation == None:
            allocation = [1.]*self._market_size
        else:
            assert len(allocation) == self._market_size
        self._dollar_market = self._create_dollar_portfolio(self.marketdf, start_val, allocation)

    @property
    def dollar_market(self):
        return self._dollar_market

    @property
    def portfolio(self):
        return self._portfolio
    
    @portfolio.setter
    def portfolio(self, portfolio):
        assert all([i in self.allstockdf.columns for i in portfolio])
        self._portfolio = portfolio
        self._portfolio_size = len(self._portfolio)
        self.generate_dollar_portfolio()

    
    @property
    def portfoliodf(self):
        return self.allstockdf[list(self._portfolio)]

    @property
    def spy(self):
        return self._spy['Adj Close']

    def generate_dollar_portfolio(self, start_val = 1000, allocation = None):
        """
        allocation: list of weights, if None, assuming equal money value
        """
        

        if allocation == None:
            allocation = [1.]*self._portfolio_size
        else:
            assert len(allocation) == self._portfolio_size
        self._dollar_portfolio = self._create_dollar_portfolio(self.portfoliodf, start_val, allocation)

    @property
    def dollar_portfolio(self):
        return self._dollar_portfolio

    def _create_dollar_portfolio(self, portfolio, starting_value, weights):
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
        weights = np.array(weights)/sum(weights)
        
        # Get starting value in dollars of each asset in the portfolio
        starting_values = np.array(weights) * starting_value
        
        # Get number of shares of each asset in the portfolio by starting value by starting price
        #top_row = portfolio.iloc[0,1:]
        top_row = portfolio.iloc[0,:]
        num_shares = starting_values / top_row
        
        # Multiply every row of the input data frame by the number of shares to give the value of each asset
        #return portfolio.apply(lambda x: np.insert(x[1:]*num_shares,0,x[0]), axis=1)
        return portfolio.apply(lambda x: x*num_shares, axis=1)

    @property
    def allstock_return(self):
        return self.allstockdf.pct_change()

    @property
    def portfolio_return(self):
        return self.portfoliodf.pct_change()

    @property
    def market_return(self):
        return self.marketdf.pct_change()

    @property
    def dollar_portfolio_sum(self):
        return self._dollar_portfolio.sum(axis=1)

    @property
    def dollar_portfolio_sum_ret(self):
        return self._dollar_portfolio.sum(axis=1).pct_change()

    @property
    def dollar_market_sum(self):
        return self._dollar_market.sum(axis=1)

    @property
    def dollar_market_sum_ret(self):
        return self._dollar_market.sum(axis=1).pct_change()

    @property
    def stockuniverse(self):
        return self.allstockdf.columns