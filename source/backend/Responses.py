from ._utils import format_dataframe_rows_to_dict, dumps
from time import sleep

class Responses():
    def __init__(self, exchange, listener):
        self.exchange = exchange
        self.listener = listener
        self.max_tries = 5

    def create_asset_response(self, msg):
          create_asset = self.exchange.create_asset(msg['ticker'], msg['seed_price'], msg['seed_bid'], msg['seed_ask']).to_dict()
          return dumps(create_asset)
    
    def limit_buy_response(self, msg):
        ticker = msg['ticker']
        price = msg['price']
        qty = msg['qty']
        creator = msg['creator']
        fee = msg['fee']        
        order = self.exchange.limit_buy(ticker, price, qty, creator, fee).to_dict()
        return dumps(order)

    def limit_sell_response(self, msg):
        ticker = msg['ticker']
        price = msg['price']
        qty = msg['qty']
        creator = msg['creator']
        fee = msg['fee']
        order = self.exchange.limit_sell(ticker, price, qty, creator, fee).to_dict()
        return dumps(order)       

    def cancel_order_response(self, msg):
        order_id = msg['order_id']
        cancelled_order = self.exchange.cancel_order(order_id).to_dict()
        return dumps(cancelled_order)

    def cancel_all_orders_response(self, msg):
        ticker = msg['ticker']
        agent = msg['agent']
        self.exchange.cancel_all_orders(agent, ticker)
        return 'All orders cancelled.'

    def market_buy_response(self, msg):
        ticker = msg['ticker']
        qty = msg['qty']
        buyer = msg['buyer']
        fee = msg['fee']
        self.exchange.market_buy(ticker, qty, buyer, fee)
        return 'Market buy order placed.'
    
    def market_sell_response(self, msg):
        ticker = msg['ticker']
        qty = msg['qty']
        seller = msg['seller']
        fee = msg['fee']
        self.exchange.market_sell(ticker, qty, seller, fee)
        return 'Market sell order placed.'
    
    def get_cash_response(self, msg):
        agent = msg['agent']
        return self.exchange.get_cash(agent)

    def get_assets_response(self, msg):
        agent = msg['agent']
        return self.exchange.get_assets(agent)
    
    def get_transactions_response(self, msg):
        agent = msg['agent']
        return self.exchange.get_transactions(agent)
    
    def register_agent_response(self, msg):
        name = msg['name']
        initial_cash = msg['initial_cash']
        return self.exchange.register_agent(name, initial_cash)

    def get_mempool_response(self, msg):
        return self.exchange.blockchain.mempool.transaction_log.head(msg['limit']).to_json()

    def candle_response(self, msg):
        return self.market.get_price_bars(msg['ticker'], bar_size=msg['interval']).head(msg['limit']).to_json()

    def get_order_book_response(self, msg):
        order_book = self.exchange.get_order_book(msg['ticker'])
        return {"bids": format_dataframe_rows_to_dict(order_book.df['bids']), "asks": format_dataframe_rows_to_dict(order_book.df['asks'])}

    def get_latest_trade_response(self, msg):
        return self.exchange.get_latest_trade(msg['ticker'])
    
    def get_trades_response(self, msg):
        trades = self.exchange.get_trades(msg['ticker']).head(msg['limit'])
        return format_dataframe_rows_to_dict(trades)

    def get_quotes_response(self, msg):
        quotes = self.exchange.get_quotes(msg['ticker'])
        return quotes

    def get_best_bid_response(self, msg):
        best_bid = self.exchange.get_best_bid(msg['ticker'])
        return best_bid.to_dict()

    def get_best_ask_response(self, msg):
        best_ask = self.exchange.get_best_ask(msg['ticker'])
        return best_ask.to_dict()

    def get_midprice_response(self, msg):
        midprice = self.exchange.get_midprice(msg['ticker'])
        return midprice

    def listen(self):
        self.listener.respond('candles', self.candle_response)
        self.listener.respond('mempool', self.get_mempool_response)
        self.listener.respond('order_book', self.get_order_book_response)
        self.listener.respond('latest_trade', self.get_latest_trade_response)
        self.listener.respond('trades', self.get_trades_response)
        self.listener.respond('quotes', self.get_quotes_response)
        self.listener.respond('best_bid', self.get_best_bid_response)
        self.listener.respond('best_ask', self.get_best_ask_response)
        self.listener.respond('midprice', self.get_midprice_response)           
        self.listener.respond('create_asset', self.create_asset_response)
        self.listener.respond('limit_buy', self.limit_buy_response)
        self.listener.respond('limit_sell', self.limit_sell_response)
        self.listener.respond('cancel_order', self.cancel_order_response)
        self.listener.respond('cancel_all_orders', self.cancel_all_orders_response)
        self.listener.respond('market_buy', self.market_buy_response)
        self.listener.respond('market_sell', self.market_sell_response)
        self.listener.respond('cash', self.get_cash_response)
        self.listener.respond('assets', self.get_assets_response)
        self.listener.respond('transactions', self.get_transactions_response)
        self.listener.respond('register_agent', self.register_agent_response)
