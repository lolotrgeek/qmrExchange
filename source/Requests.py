from time import sleep
import json
import traceback

class Requests():
    def __init__(self, requester):
        self.requester = requester
        self.timeout = 5
        self.max_tries = 1
        self.debug = False
        
    def make_request(self, topic:str, message:dict, factory, tries=0):
        try:
            message['topic'] = topic
            msg = self.requester.request(message)
            if msg is None:
                raise Exception(f'{topic} is None, {msg}')
            elif type(msg) is str:
                return json.loads(msg)
            elif type(msg) is list:
                return msg
            elif type(msg) is not dict:
                raise Exception(f'{topic} got type {type(msg)} expected dict. Message{msg}')
            elif 'error' in msg:
                raise Exception(f'{topic} error, {msg}')
            else:
                return msg
        except Exception as e:
            tries += 1
            if tries >= self.max_tries:
                error = {}
                error[topic] = f"[Request Error] {e}"
                if self.debug == True:
                    print("[Request Error] ", e) 
                    print(traceback.format_exc())
                return error
            sleep(0.1)
            return self.make_request(topic, message, factory, tries)

    
    def get_price_bars(self, ticker, interval, limit):
        return self.make_request('candles', {'ticker': ticker, 'interval': interval, 'limit': limit}, self.requester)

    def create_asset(self, ticker, qty, seed_price, seed_bid, seed_ask):
        return self.make_request('create_asset', {'ticker': ticker, 'qty': qty,'seed_price': seed_price, 'seed_bid': seed_bid, 'seed_ask': seed_ask}, self.requester)

    def get_mempool(self, limit):
        return self.make_request('mempool', {'limit': limit}, self.requester)

    def get_order_book(self, ticker):
        return self.make_request('order_book', {'ticker': ticker}, self.requester)

    def get_latest_trade(self, ticker):
        return self.make_request('latest_trade', {'ticker': ticker}, self.requester)

    def get_trades(self, ticker, limit):
        return self.make_request('trades', {'ticker': ticker, 'limit': limit}, self.requester)

    def get_quotes(self, ticker):
        return self.make_request('quotes', {'ticker': ticker}, self.requester)

    def get_best_bid(self, ticker):
        return self.make_request('best_bid', {'ticker': ticker}, self.requester)

    def get_best_ask(self, ticker):
        return self.make_request('best_ask', {'ticker': ticker}, self.requester)

    def get_midprice(self, ticker):
        return self.make_request('midprice', {'ticker': ticker}, self.requester)

    def limit_buy(self, ticker, price, quantity, creator, fee=0.0):
        return self.make_request('limit_buy', {'ticker': ticker, 'price': price, 'qty': quantity, 'creator': creator, 'fee': fee}, self.requester) 

    def limit_sell(self, ticker, price, quantity, creator, fee=0.0):
        return self.make_request('limit_sell', {'ticker': ticker, 'price': price, 'qty': quantity, 'creator': creator, 'fee': fee}, self.requester)
    
    def cancel_order(self, id):
        return self.make_request('cancel_order', {'order_id': id}, self.requester)

    def cancel_all_orders(self, ticker, agent):
        return self.make_request('cancel_all_orders', {'ticker': ticker, 'agent': agent}, self.requester)

    def market_buy(self, ticker, quantity, creator, fee=0.0):
        return self.make_request('market_buy', {'ticker': ticker, 'qty': quantity, 'buyer': creator, 'fee': fee}, self.requester)
    
    def market_sell(self, ticker, quantity, creator, fee=0.0):
        return self.make_request('market_sell', {'ticker': ticker, 'qty': quantity, 'seller': creator, 'fee': fee}, self.requester)
    
    def get_cash(self, agent):
        return self.make_request('cash', {'agent': agent}, self.requester)
    
    def get_assets(self, agent):
        return self.make_request('assets', {'agent': agent}, self.requester)
    
    def register_agent(self, name, initial_cash):
        return self.make_request('register_agent', {'name': name, 'initial_cash': initial_cash}, self.requester)
    
    def get_agent(self, name):
        return self.make_request('get_agent', {'name': name}, self.requester)