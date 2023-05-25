
class Requests():
    def __init__(self, conn) -> None:
        self.conn = conn

    def get_sim_time(self):
        self.conn.send({'get_sim_time': True})
        msg = self.conn.recv()
        return msg['sim_time']
    
    def get_candles(self, ticker, interval, limit):
        self.conn.send({'get_candles': {'ticker': ticker, 'interval': interval, 'limit': limit}})
        msg = self.conn.recv()
        return msg['candles']

    def create_asset(self, ticker, seed_price, seed_bid, seed_ask):
        self.conn.send({'create_asset': {'ticker': ticker, 'seed_price': seed_price, 'seed_bid': seed_bid, 'seed_ask': seed_ask}})
        msg = self.conn.recv()
        return msg['created_asset']

    def get_mempool(self, limit):
        self.conn.send({'get_mempool': {'limit': limit}})
        msg = self.conn.recv()
        return msg['mempool']

    def get_order_book(self, ticker):
        self.conn.send({'get_order_book': {'ticker': ticker}})
        msg = self.conn.recv()
        return msg['order_book']

    def get_latest_trade(self, ticker):
        self.conn.send({'get_latest_trade': {'ticker': ticker}})
        msg = self.conn.recv()
        return msg['latest_trade']

    def get_trades(self, ticker, limit):
        self.conn.send({'get_trades': {'ticker': ticker, 'limit': limit}})
        msg = self.conn.recv()
        return msg['trades']

    def get_quotes(self, ticker):
        self.conn.send({'get_quotes': {'ticker': ticker}})
        msg = self.conn.recv()
        return msg['quotes']

    def get_best_bid(self, ticker):
        self.conn.send({'get_best_bid': {'ticker': ticker}})
        msg = self.conn.recv()
        return msg['best_bid']

    def get_best_ask(self, ticker):
        self.conn.send({'get_best_ask': {'ticker': ticker}})
        msg = self.conn.recv()
        return msg['best_ask']

    def get_midprice(self, ticker):
        self.conn.send({'get_midprice': {'ticker': ticker}})
        msg = self.conn.recv()
        return msg

    def limit_buy(self, ticker, price, quantity, creator, fee):
        self.conn.send({'limit_buy': {'ticker': ticker, 'price': price, 'qty': quantity, 'creator': creator, 'fee': fee}})
        msg = self.conn.recv()
        return msg['limit_buy_placed']

    def limit_sell(self, ticker, price, quantity, creator, fee):
        self.conn.send({'limit_sell': {'ticker': ticker, 'price': price, 'qty': quantity, 'creator': creator, 'fee': fee}})
        msg = self.conn.recv()
        return msg['limit_sell_placed']
    
    def cancel_order(self, order_id):
        self.conn.send({'cancel_order': {'order_id': order_id}})
        msg = self.conn.recv()
        return msg['order_cancelled']

    def cancel_all_orders(self, ticker, agent):
        self.conn.send({'cancel_all_orders': {'ticker': ticker, 'agent': agent}})
        msg = self.conn.recv()
        return msg['orders_cancelled']

    def market_buy(self, ticker, quantity, creator, fee):
        self.conn.send({'market_buy': {'ticker': ticker, 'qty': quantity, 'buyer': creator, 'fee': fee}})
        msg = self.conn.recv()
        return msg['market_buy_placed']

    def market_sell(self, ticker, quantity, creator, fee):
        self.conn.send({'market_sell': {'ticker': ticker, 'qty': quantity, 'seller': creator, 'fee': fee}})
        msg = self.conn.recv()
        return msg['market_sell_placed']



    

    