import pandas as pd
import numpy as np

class Hedge(object):
    
    def __init__(self, stocksdir = '../../data/all_stocks.csv', spydir = '../../data/spy.csv', begindate = None, enddate = None):
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
        
        self.allstockdf = self.allstockdf.dropna(axis = 1).reset_index(drop = True)

        self._spy = spy[[i in self.allstockdf.Date.values for i in spy.Date]]

        assert len(self._spy) == len(self.allstockdf)
        
        # initialize portfolio to be empty
        self._portfolio = []
    
    def _dropRowsAccordingTo(self, df, colname):
        # TODO: may be useful when working on data
        pass
    
    def generateRandomPort(self, size = 20):
        self._portfolio = np.random.choice(self.allstockdf.columns[1:], size)
        return self._portfolio
    
    @property
    def portfolio(self):
        return self._portfolio
    
    @portfolio.setter
    def portfolio(self, portfolio):
        assert all([i in self.allstockdf.columns for i in portfolio])
        self._portfolio = portfolio
    
    @property
    def portfoliodf(self):
        return self.allstockdf[['Date']+list(self._portfolio)]

    @property
    def spy(self):
        return self._spy

    