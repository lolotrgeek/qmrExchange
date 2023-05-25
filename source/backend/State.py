
class State():
    def __init__(self, sim, queue=None):
        self.dt = sim.dt
        self.episode = sim.episode
        self.episodes = sim._episodes
        self.trades = sim.trades
        self.assets = sim.exchange.assets
        self.mempool = sim.exchange.mempool.transaction_log
        self.orderbook = sim.exchange.books
        self.latest_trade = sim.exchange.latest_trade
        self.quotes = sim.exchange.get_quotes
        self.best_bid = sim.exchange.get_best_bid
        self.best_ask = sim.exchange.get_best_ask
        self.mid_price = sim.exchange.mid_price
        self.get_price_bars = sim.exchange.get_price_bars
        self.tickers = sim.exchange.tickers

    # method for 1Min, 5Min, 15Min, 30Min, 1H, 4H, 1D, 1W, 1M, 1Y OHLCV
    def get_candles(self):
        candles = []
        for ticker in self.tickers:
            for interval in ['1Min', '5Min', '15Min', '30Min', '1H', '4H', '1D', '1W', '1M', '1Y']:
                candles.append(self.get_price_bars(ticker, bar_size=interval))
        return candles
    
    def sim_time(self):
        return {'sim_time': self.dt, 'episode': self.episode, 'episodes': self.episodes}

    def get_mempool(self):
        return self.mempool
    
    def get_order_book(self):
        return self.orderbook
    
    def get_trades(self):
        return self.trades
    
    def get_quotes(self):
        quotes = []
        for ticker in self.tickers:
            quotes.append(self.quotes(ticker))
    
    def get_best_bids(self, ticker):
        best_bids = []
        for ticker in self.tickers:
            best_bids.append(self.best_bid(ticker))
        return best_bids
    
    def get_best_asks(self, ticker):
        best_asks = []
        for ticker in self.tickers:
            best_asks.append(self.best_ask(ticker))
        return best_asks
    
    def get_mid_prices(self, ticker):
        mid_prices = []
        for ticker in self.tickers:
            mid_prices.append(self.mid_price(ticker))
        return mid_prices
    
    

