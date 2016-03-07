import Quandl
import pandas as pd
import numpy as np

#Global Variables
SECTORS = ['Basic Industries', 'Capital Goods', 'Consumer Durables', 'Consumer Non-Durables','Consumer Services',
           'Energy', 'Finance', 'Health Care', 'Miscellaneous', 'Public Utilities', 'Technology', 'Transportation', 'n/a']
MARKETS = ['NYSE', 'NASDAQ', 'AMEX']

def getStockUniverse(directory = '../../data/', NYSE = True, NASDAQ = True, AMEX = True):
    """
    Reads in the stored stock data, including symbol, Name, Cap, Sector, Industry from NYSE, NASDAQ and AMEX

    Returns
    -------
    A pandas frame concatenating all the stock universe from NYSE, NASDAQ and AMEX
    """
    nyse = pd.read_csv(directory+'companylist_nyse.csv')
    nyse['Market'] = 'NYSE'
    nasdaq = pd.read_csv(directory+'companylist_nasdaq.csv')
    nasdaq['Market'] = 'NASDAQ'
    amex = pd.read_csv(directory+'companylist_amex.csv')
    amex['Market'] = 'AMEX'

    allstocks = pd.concat([nyse,nasdaq,amex])

    # The following parses the market cap into more readable fashion
    # eg. $1.15B = 1150, n/a = -1
    def parseMarketCap(allstocks):
        cap = allstocks['MarketCap'].values
        def computeCap(s):
            if s=='n/a':
                return -1
            elif s[-1:]=='B':
                return float(s[1:-1])*1000
            elif s[-1:]=='M':
                return float(s[1:-1])
        allstocks['MarketCap'] = map(computeCap, cap)

    allstocks = allstocks.drop('Unnamed: 8', axis = 1)
    parseMarketCap(allstocks)

    allstocks = allstocks.drop_duplicates('Name')    #Drop duplicates, eg. GOOG instead of GOOGL

    return allstocks.sort_values(by = 'MarketCap', ascending = False).reset_index().drop('index', axis=1)



def getSamplePortfolio(stock_universe, n = 10, capThreshold = 2000,
                       sector = None, descendingByCap = False, market = ['NYSE', 'NASDAQ']):
    """
    Get a sample portfolio from the stock universe, preferably a generated one from getStockUniverse.
    With specified parameters.

    Parameters
    ----------
    stock_universe : pandas frame with symbols, Cap and Sector
    n : number of samples
    capThreshold : sample should be larger than this threshold, initially set ot 2000
    sector : list of specific sectors to sample from, default to None with no preference
    DescendingByCap: Sample the largest caps, otherwise random sampling.
    market : specific market to sample from, NYSE, NASDAQ and AMEX, default is NYSE and NASDAQ.

    Returns
    ------
    A list of symbols
    """

    reduced_universe = stock_universe

    if capThreshold != None:# and line['MarketCap'].value <capThreshold:
        reduced_universe = reduced_universe[reduced_universe['MarketCap']>=capThreshold]

    if sector != None:
        reduced_universe = reduced_universe[map(lambda x: x in sector, reduced_universe['Sector'].values)]

    if market != None:
        reduced_universe = reduced_universe[map(lambda x: x in market, reduced_universe['Market'].values)]

    if len(reduced_universe)<n:
        print '*******Warning: insufficient candidates, reduce number of samples'
        n = len(reduced_universe)

    if descendingByCap:
        # getting rid of redundant quotes, eg. goog and googl
        reduced_universe = reduced_universe.sort_values(by = 'MarketCap', ascending=False)[:n]

    else:
        reduced_universe = reduced_universe.sample(n)

    print 'Top 5 rows of selected portfolio:'
    print reduced_universe[['Symbol', 'Name', 'MarketCap', 'Sector', 'industry', 'Market']].head()

    return reduced_universe.Symbol.values


def getStocks(symbols, trim_start="2005-01-01", trim_end="2015-12-31"):
    """
    Paramters
    ---------
    symbols: list of string symbols. eg. ['AAPL', 'KCG']

    Returns
    -------
    a dictionary of pandas data frames containing all the close prices.
    """
    print symbols
    dfs = {}
    for symbol in symbols:
        print symbol,
        flag = False
        #Get data from either Yahoo or Google
        for source in ['','YAHOO/', 'WIKI/', 'GOOG/NYSE_', 'GOOG/NASDAQ_', 'GOOG/AMEX_']:
            try:
                data = Quandl.get(source+symbol,authtoken='c2365v55yoZrWKxbVxwK',
                                  trim_start = trim_start, trim_end = trim_end)
                flag = True
                break
            except:
                pass

        if not flag:
            print 'Retrieving ' + symbol + ' unsuccessful. - No symbol. Suggesting:******'
            suggest = Quandl.search(symbol,authtoken='c2365v55yoZrWKxbVxwK', verbose=False)
            print suggest[0]['name'], suggest[0]['code']
            continue

        else:
            try:
                data = data[['Adjusted Close']]
                data.columns = ['Close']
            except:
                try:
                    data = data[['Close']]
                except:
                    print 'Retrieving ' + symbol + ' unsuccessful. - No close data. Output whatever is returned.'

        dfs[symbol] = data

    return dfs
