import pandas as pd
import numpy as np

class Hedge(object):
    
    def __init__(self, allstockdf, begindate = None, enddate = None):
        # Use AAPL dates to filter
        # preprossessing
        idxb = 0
        if begindate != None:
            idxb = np.where(allstockdf.Date>=begindate)[0][0]
        if enddate != None:
            idxe = np.where(allstockdf.Date<=enddate)[0][0]
            allstockdfsliced = allstockdf[idxb:idxe+1]
        else:
            allstockdfsliced = allstockdf[idxb:]
        
        # use AAPL as reference column to drop nan rows
        self.allstockdf = allstockdf.iloc[allstockdfsliced['AAPL'].dropna().index]
        
        self.allstockdf = self.allstockdf.dropna(axis = 1).reset_index(drop = True)
        
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