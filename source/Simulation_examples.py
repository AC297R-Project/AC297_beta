from Hedge import Hedge
from Simulation import *
import matplotlib.pyplot as plt

from BetaUtils import get_beta, beta_hedging_ret, cum_ret
from energy_functions import *



def simulated_annealing_example():
	hedge = Hedge(begindate='2014-01-01', enddate='2014-12-31')
	hedge.portfolio = ['FLIR', 'IVC', 'KNDI', 'MHO', 'EVC', 'PCO', 'COWN', 'NILE', 'MIW',
		   'ANAC', 'ADHD', 'PLBC', 'ESXB', 'JRO', 'WES', 'HURC', 'MQT', 'EROS',
		   'RPAI', 'HMNF']
	hedge.market = ['GPX', 'GRMN', 'MPWR', 'ENR', 'CTHR', 'PRFZ', 'SUMR', 'CUBE',
		   'ACTS', 'ANF', 'MYI', 'SON', 'SSL', 'PW', 'KT', 'TWN', 'IPWR',
		   'AAN', 'CASH', 'DISCA', 'RFP', 'HPS', 'WMB', 'VRSN', 'ETN', 'WPZ',
		   'RAI', 'BOXC', 'ARCI', 'EMN', 'LMOS', 'EXPD', 'NQS', 'GB', 'KNOP',
		   'CNL', 'ENDP', 'SPSC', 'SCVL', 'EPAY']


	st, bm = simulated_annealing(hedge, init_temp=0.01, min_temp=0.001, cool_by=0.99, reanneal=100, num_iter=100, \
						energy_func=neg_sharpe)


	hedge.market = bm

	_, betas = get_beta(hedge.dollar_portfolio_sum_ret, hedge.dollar_market_sum_ret)
	bhr = beta_hedging_ret(betas[1:], hedge.dollar_portfolio_sum_ret[61:], hedge.dollar_market_sum_ret[61:])

	plt.plot(bhr)
	plt.plot(hedge.dollar_portfolio_sum_ret[61:].values)
	plt.show()


	plt.plot(cum_ret(bhr))
	plt.plot(cum_ret(hedge.dollar_portfolio_sum_ret[61:].values))
	plt.plot(cum_ret(hedge.spy.pct_change()[61:].values))
	plt.plot(cum_ret(hedge.dollar_market_sum_ret[61:].values))
	plt.show()


	print neg_sharpe((bhr)), neg_sharpe(hedge.dollar_portfolio_sum_ret[61:]),neg_sharpe(hedge.dollar_market_sum_ret[61:]), neg_sharpe(hedge.spy.pct_change()[61:])



if __name__ == '__main__':
	simulated_annealing_example()