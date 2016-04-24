import argparse
from experiment_helpers import (
	get_market,
	get_params,
	get_portfolio,
	simulated_annealing,
	write_results
)
from BetaUtils import get_beta, beta_hedging_ret, cum_ret
from energy_functions import energy
from Hedge import Hedge
import matplotlib.pyplot as plt
import sys
import numpy as np

def experiment():
	# List of parameters that get passed in, as well as written out with the results.
	# There is also a debug parameter that is passed in but not written out.
	param_list = [
		'begin_date',
		'end_date',
		'test_begin_date',
		'test_end_date',
		'ols_window',
		'starting_market_id',
		'portfolio_id',
		'starting_temp',
		'cool_by',
		'min_temp',
		'reanneal',
		'num_iter',
		'vol',
		'corr',
		'sharpe',
		'returns',
		]


	#########################################################################
	### Get, read, and parse input file, and write header to output file. ###
	#########################################################################

	parser = argparse.ArgumentParser(description='Reads the names of a text file containing \
		simulated annealing input parameters and a file for writing output.')
	parser.add_argument('infile', metavar='in', type=str, nargs=1, help='name of a text file \
		containing simulated annealing parameters')
	parser.add_argument('outfile', metavar='out', type=str, nargs=1, help='name of a text file \
		to store output')
	parser.add_argument('outbestmarket', metavar='out', type=str, nargs=1, help='name of a text file \
		to store output')
	parser.add_argument('outstates', metavar='out', type=str, nargs=1, help='name of a text file \
		to store output')
	parser.add_argument('error', metavar='out', type=str, nargs=1, help='name of a text file \
		to store output')

	args = parser.parse_args()
	infile = args.infile[0]
	outfile = args.outfile[0]
	outbestmarket = args.outbestmarket[0]
	outstates = args.outstates[0]
	error = args.error[0]
	parameters = []

	with open(infile, 'r') as f:
		f.readline()  # First line describes file formatting
		for line in f:
			parameters.append(line.split(','))

	# Clear files
	with open(error, 'w') as f:
		f.write("Error Header\n")

	with open(outstates, 'w') as f:
		pass

	with open(outbestmarket, 'w') as f:
		pass

	###########################################
	### Do an experiment and write results. ###
	###########################################

	n_experiments = len(parameters)
	for n in range(n_experiments):
		try:
			print 'start iteration {}'.format(n)
			# Get appropriate portfolio and market.
			# Reading over each file for each experiment takes a little while, but it's
			# ulimately insignificant compared to simulated annealing, and it eliminates the
			# memory pressure that would result from storing all portfolios and markets.
			params = get_params(parameters[n], param_list)
			# for ii in params.items(): print ii
			window = int(params['ols_window'])
			hedge = Hedge(begindate=params['begin_date'], enddate=params['end_date'])
			hedge_test = Hedge(begindate=params['test_begin_date'], enddate=params['test_end_date'])

			# Drop stocks that are not in both time windows
			invalid = list((set(hedge.allstockdf.columns) - set(hedge_test.allstockdf.columns)))
			hedge.allstockdf.drop(invalid, axis=1, inplace=True)
			hedge.portfolio = get_portfolio(params, invalid)
			hedge.market = get_market(params, invalid)
			energy_func = energy(
				volatility_coef=float(params['vol']),
				correlation_coef=float(params['corr']),
				neg_sharpe_coef=float(params['sharpe']),
				neg_returns_coef=float(params['returns']))

			states, best_market = simulated_annealing(
				hedge=hedge, init_temp=float(params['starting_temp']),
				min_temp=float(params['min_temp']), cool_by=float(params['cool_by']),
				reanneal=int(params['reanneal']), num_iter=int(params['num_iter']),
				energy_func=energy_func, window=window, verbose=params['verbose'])


			with open(outstates, 'a') as f:
				f.write('{},\n'.format(states))

			with open(outbestmarket, 'a') as f:
				f.write('{},\n'.format(best_market))

			# Test set
			# Get returns hedged against optimal market
			hedge_test.portfolio = hedge.portfolio
			hedge_test.market = best_market
			_, betas = get_beta(hedge_test.dollar_portfolio_sum_ret,
								hedge_test.dollar_market_sum_ret)
			beta_hedging_returns = beta_hedging_ret(
				betas[1:],
				hedge_test.dollar_portfolio_sum_ret[window+1:],
				hedge_test.dollar_market_sum_ret[window+1:])
			market_hedged_returns = beta_hedging_returns

			# Get returns hedged against S&P 500
			_, betas = get_beta(hedge_test.dollar_portfolio_sum_ret, hedge_test.spy.pct_change())
			beta_hedging_returns = beta_hedging_ret(
				betas[1:],
				hedge_test.dollar_portfolio_sum_ret[window+1:],
				hedge_test.spy.pct_change()[window+1:])
			spy_hedged_returns = beta_hedging_returns


			# Get unhedged returns
			unhedged_returns = hedge_test.dollar_portfolio_sum_ret[window+1:].values

			# Write results to file
			write_results(outfile, market_hedged_returns, spy_hedged_returns,
				unhedged_returns, hedge_test.spy.pct_change(), params, param_list, window, states)

		# If something bad happens, write an error message and run the next iteration
		except Exception as e:
			with open(error, 'a') as f:
				f.write('Exception on run {}: {}\n'.format(n, e))
				sys.exit()

if __name__ == '__main__':
	experiment()
