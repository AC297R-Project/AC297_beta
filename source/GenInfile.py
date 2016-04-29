class GenInfile:
	def __init__(self):
		self.counter = 0

	def write_infile(self, begin_date, end_date, test_begin_date,
		test_end_date, ols_window, starting_market_id, portfolio_id,
		starting_temp, cool_by, min_temp, reanneal, num_iter, vol, corr,
		sharpe, returns, verbose):
		with open('in_{}.txt'.format(self.counter), 'w') as f:
			f.write('begin_date,end_date,test_begin_date,' + \
				'test_end_date,ols_window,starting_market_id,' + \
				'portfolio_id,starting_temp,cool_by,min_temp,' + \
				'reanneal,num_iter,''vol,corr,sharpe,returns,verbose\n')
			f.write('{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'\
				.format(begin_date, end_date, test_begin_date,
						test_end_date, ols_window, starting_market_id,
						portfolio_id, starting_temp, cool_by, min_temp,
						reanneal, num_iter, vol, corr, sharpe, returns,
						verbose))
		self.counter += 1
