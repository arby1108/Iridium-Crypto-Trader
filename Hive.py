from Trader import *

class HiveNet(object):
	"""docstring for ClassName"""
	def __init__(self):
		self.hive = []
		self.perf_grid = None

	def setWindow(self, day_window):
		self.window = day_window

	def loadBotNet(self, index):
		i=0
		self.index = []
		for x in index:
			try: 
				new_bot = Trader('Iridium-'+str(i), x, 'usd', 'Sim')
				self.hive.append(new_bot)
				self.index.append(new_bot.coin)
			except KeyError: print(x + " doesn't work...")
			except ValueError: print(x + " doesn't work...")
			i+=1

	def learn_performance(self, day_window, inv_amt, pct):
			for bot in self.hive:
				print(bot.coin + "-" + bot.coin2)
				unit_cost = bot.hist['price'].iloc[day_window*24]
				order_amount = inv_amt/unit_cost
				bot.learn_and_sim(day_window*24)
				bot.hist_to_pnl(order_amount, order_amount*pct)
			hive_perf = pd.DataFrame()
			returns = []
			for bot in self.hive:
				hive_perf[bot.coin] = bot.coin_hist['algo_rt']
				x = bot.coin_hist['algo_rt'].tail(1).iloc[0]
				returns.append((x))
			hive_perf['mean_returns'] = hive_perf.mean(axis=1)
			self.perf = hive_perf

	def networkToPerf(self):
		total_revenue = 0
		total_cost = 0
		total_asset_val = 0
		start_asset_val = 0
		pnl = 0

		for bot in self.hive:
			start_asset_val += bot.coin_hist['q'].iloc[self.window*24] * bot.coin_hist['price'].iloc[self.window*24]
			total_revenue += bot.coin_hist['sell_rev'].sum()
			total_cost += bot.coin_hist['buy_cost'].sum()
			q = bot.coin_hist['q'].tail(1).values[0]
			p = bot.coin_hist['price'].tail(1).values[0]
			total_asset_val += int(q*p)
			pnl += bot.coin_hist['pnl'].tail(1).values[0]

		self.total_revenue = total_revenue
		self.total_cost = total_cost
		self.total_asset_val = total_asset_val
		self.start_asset_val = start_asset_val
		self.pnl = pnl

	def learn(self, day_window):
		for bot in self.hive:
			print(bot.coin + "-" + bot.coin2 + " processed...")
			bot.learn(day_window*24)

	def process_orders(self):
		for bot in self.hive:
			buy = int(bot.decision[6]) == 1
			sell = int(bot.decision[6] == 1)
			if buy or sell :
				print(bot.coin + "-" + bot.coin2 + ": " + str(bot.decision))

index = pd.read_csv('data/00_coinlist.csv')['coin_id'][0:100]
index = ['ethereum', 'dogecoin', 'binancecoin', 'cardano', 'cosmos', 'chainlink']
network = HiveNet()
network.loadBotNet(index)
network.setWindow(28)
network.learn_performance(28, 1000, 0.10)
network.learn(28)
network.process_orders()
