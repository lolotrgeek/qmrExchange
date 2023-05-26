from time import sleep

class Requests():
    def __init__(self, conn) -> None:
        self.conn = conn
        self.timeout = 5
        self.max_tries = 5

    def make_request(self, request, key:str, tries=0):
        if tries >= self.max_tries:
            error = {}
            error[key] = {'error': 'Max tries reached.'}
            return error
        self.conn.send(request)
        if(self.conn.poll(self.timeout)):
            try:
                msg = self.conn.recv()
                if msg is None or 'error' in msg or msg[key] is None or 'error' in msg[key]:
                    raise Exception('Error.')
                else:
                    return msg[key]
            except:
                tries += 1
                sleep(0.1)
                self.make_request(request, key, tries)
        else:
            error = {}
            error[key] = {'error': 'Timeout.'}
            return error

    def get_sim_time(self):
        return self.make_request({'get_sim_time': True}, 'sim_time')
    
    def get_candles(self, ticker, interval, limit):
        return self.make_request({'get_candles': {'ticker': ticker, 'interval': interval, 'limit': limit}}, 'candles')

    def create_asset(self, ticker, seed_price, seed_bid, seed_ask):
        return self.make_request({'create_asset': {'ticker': ticker, 'seed_price': seed_price, 'seed_bid': seed_bid, 'seed_ask': seed_ask}}, 'created_asset')

    def get_mempool(self, limit):
        return self.make_request({'get_mempool': {'limit': limit}}, 'mempool')

    def get_order_book(self, ticker):
        return self.make_request({'get_order_book': {'ticker': ticker}}, 'order_book')

    def get_latest_trade(self, ticker):
        return self.make_request({'get_latest_trade': {'ticker': ticker}}, 'latest_trade')

    def get_trades(self, ticker, limit):
        return self.make_request({'get_trades': {'ticker': ticker, 'limit': limit}}, 'trades')

    def get_quotes(self, ticker):
        return self.make_request({'get_quotes': {'ticker': ticker}}, 'quotes')

    def get_best_bid(self, ticker):
        return self.make_request({'get_best_bid': {'ticker': ticker}}, 'best_bid')

    def get_best_ask(self, ticker):
        return self.make_request({'get_best_ask': {'ticker': ticker}}, 'best_ask')

    def get_midprice(self, ticker):
        return self.make_request({'get_midprice': {'ticker': ticker}}, 'midprice')

    def limit_buy(self, ticker, price, quantity, creator, fee):
        return self.make_request({'limit_buy': {'ticker': ticker, 'price': price, 'qty': quantity, 'creator': creator, 'fee': fee}}, 'limit_buy_placed') 

    def limit_sell(self, ticker, price, quantity, creator, fee):
        return self.make_request({'limit_sell': {'ticker': ticker, 'price': price, 'qty': quantity, 'creator': creator, 'fee': fee}}, 'limit_sell_placed')
    
    def cancel_order(self, order_id):
        return self.make_request({'cancel_order': {'order_id': order_id}}, 'order_cancelled')

    def cancel_all_orders(self, ticker, agent):
        return self.make_request({'cancel_all_orders': {'ticker': ticker, 'agent': agent}}, 'orders_cancelled')

    def market_buy(self, ticker, quantity, creator, fee):
        return self.make_request({'market_buy': {'ticker': ticker, 'qty': quantity, 'buyer': creator, 'fee': fee}}, 'market_buy_placed')
    
    def market_sell(self, ticker, quantity, creator, fee):
        return self.make_request({'market_sell': {'ticker': ticker, 'qty': quantity, 'seller': creator, 'fee': fee}}, 'market_sell_placed')