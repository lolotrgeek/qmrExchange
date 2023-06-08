from time import sleep
from .Messaging import Puller, Requester
import traceback

class Requests():
    def __init__(self, exchange_channel):
        self.order_factory = Requester(exchange_channel)
        self.market_factory = self.order_factory
        self.candle_factory = self.order_factory
        self.trades_factory = self.order_factory
        self.timeout = 5
        self.max_tries = 5
        
    def make_request(self, topic:str, request:dict, factory, tries=0):
        if tries >= self.max_tries:
            error = {}
            error[topic] = {'error': 'Max tries reached.'}
            return error
        try:
            msg = factory.request(topic, request)
            if msg is None or 'error' in msg:
                raise Exception(f'{topic} error')
            elif type(msg) is not dict:
                raise Exception(f'{topic} Not dict...')
            elif msg.get(topic) is None:
                raise Exception(f'{topic} Not {topic}...')
            else:
                return msg
        except Exception as e:
            print(e)
            traceback.print_exc()
            tries += 1
            sleep(0.1)
            return self.make_request(topic, request, factory, tries)
    
    def get_candles(self, ticker, interval, limit):
        return self.make_request('candles', {'ticker': ticker, 'interval': interval, 'limit': limit}, self.candle_factory)

    def create_asset(self, ticker, seed_price, seed_bid, seed_ask):
        return self.make_request('create_asset', {'ticker': ticker, 'seed_price': seed_price, 'seed_bid': seed_bid, 'seed_ask': seed_ask}, self.market_factory)

    def get_mempool(self, limit):
        #TODO: add mempool to market
        return self.make_request('mempool', {'limit': limit}, self.market_factory)

    def get_order_book(self, ticker):
        return self.make_request('order_book', {'ticker': ticker}, self.market_factory)

    def get_latest_trade(self, ticker):
        return self.make_request('latest_trade', {'ticker': ticker}, self.market_factory)

    def get_trades(self, ticker, limit):
        return self.make_request('trades', {'ticker': ticker, 'limit': limit}, 'trades', self.trades_factory)

    def get_quotes(self, ticker):
        return self.make_request('quotes', {'ticker': ticker}, self.market_factory)

    def get_best_bid(self, ticker):
        return self.make_request('best_bid', {'ticker': ticker}, self.market_factory)

    def get_best_ask(self, ticker):
        return self.make_request('best_ask', {'ticker': ticker}, self.market_factory)

    def get_midprice(self, ticker):
        return self.make_request('midprice', {'ticker': ticker}, self.market_factory)

    def limit_buy(self, ticker, price, quantity, creator, fee):
        return self.make_request('limit_buy', {'ticker': ticker, 'price': price, 'qty': quantity, 'creator': creator, 'fee': fee}, self.order_factory) 

    def limit_sell(self, ticker, price, quantity, creator, fee):
        return self.make_request('limit_sell', {'ticker': ticker, 'price': price, 'qty': quantity, 'creator': creator, 'fee': fee}, self.order_factory)
    
    def cancel_order(self, order_id):
        return self.make_request('cancel_order', {'order_id': order_id}, self.order_factory)

    def cancel_all_orders(self, ticker, agent):
        return self.make_request('cancel_all_orders', {'ticker': ticker, 'agent': agent}, self.order_factory)

    def market_buy(self, ticker, quantity, creator, fee):
        return self.make_request('market_buy', {'ticker': ticker, 'qty': quantity, 'buyer': creator, 'fee': fee}, self.order_factory)
    
    def market_sell(self, ticker, quantity, creator, fee):
        return self.make_request('market_sell', {'ticker': ticker, 'qty': quantity, 'seller': creator, 'fee': fee}, self.order_factory)
    
    def get_cash(self, agent):
        return self.make_request('cash', {'agent': agent}, self.order_factory)
    
    def get_assets(self, agent):
        return self.make_request('assets', {'agent': agent}, self.order_factory)
    
    def get_transactions(self, agent):
        return self.make_request('transactions', {'agent': agent}, self.order_factory)
    
    def register_agent(self, name, initial_cash):
        return self.make_request('register_agent', {'name': name, 'initial_cash': initial_cash}, self.order_factory)