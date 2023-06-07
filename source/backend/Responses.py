from ._utils import format_dataframe_rows_to_dict
from time import sleep
from Messaging import Responder

class Responses():
    def __init__(self):
        self.max_tries = 5
        self.Responder = Responder()

    def send(self, value, key, tries=0):
        if tries >= self.max_tries:
            error = {}
            error[key] = {'error': 'Max tries reached.'}
            return error
        msg = {}
        if value is not None:
            msg[key] = value
            if msg:
                self.conn.put(msg)
            else:
                tries += 1
                sleep(0.1)
                self.send(value, key, tries)
        else:
            error = {}
            error[key] = {'error': f'No {key} available.'}
            self.conn.put(error)

    def listen(self, msg):
        
        if ('get_sim_time' in msg):
            self.send({'sim_time': self.sim.dt, 'episode': self.sim.episode, 'episodes': self.sim._episodes}, 'sim_time')

        elif ('get_candles' in msg):
            candles = self.sim.get_price_bars(msg['get_candles']['ticker'], bar_size=msg['get_candles']['interval']).head(msg['get_candles']['limit']).to_json()
            self.send(candles, 'candles')

        elif ('create_asset' in msg):
            self.sim.exchange.create_asset(msg['create_asset']['ticker'], msg['create_asset']['seed_price'], msg['create_asset']['seed_bid'], msg['create_asset']['seed_ask'])
            self.send('Asset created.', 'created_asset')

        elif ('get_mempool' in msg):
            mempool = self.sim.exchange.blockchain.mempool.transaction_log.head(msg['get_mempool']['limit']).to_json()
            self.send(mempool, 'mempool')

        elif ('get_order_book' in msg):
            order_book = self.sim.exchange.get_order_book(msg['get_order_book']['ticker'])
            self.send({"bids": format_dataframe_rows_to_dict(order_book.df['bids']), "asks": format_dataframe_rows_to_dict(order_book.df['asks'])}, 'order_book')

        elif ('get_latest_trade' in msg):
            latest_trade = self.sim.exchange.get_latest_trade(msg['get_latest_trade']['ticker']).to_dict()
            self.send(latest_trade, 'latest_trade')

        elif ('get_trades' in msg):
            trades = self.sim.exchange.get_trades(msg['get_trades']['ticker']).head(msg['get_trades']['limit'])
            self.send(format_dataframe_rows_to_dict(trades), 'trades')

        elif ('get_quotes' in msg):
            quotes = self.sim.exchange.get_quotes(msg['get_quotes']['ticker'])
            self.send(quotes, 'quotes')

        elif ('get_best_bid' in msg):
            best_bid = self.sim.exchange.get_best_bid(msg['get_best_bid']['ticker'])
            if best_bid is not None:
                best_bid = best_bid.to_dict()
                self.send(best_bid, 'best_bid')
            else:
                self.send(0, 'best_bid')

        elif ('get_best_ask' in msg):
            best_ask = self.sim.exchange.get_best_ask(msg['get_best_ask']['ticker'])
            if best_ask is not None:
                best_ask = best_ask.to_dict()
                self.send(best_ask, 'best_ask')
            else:
                self.send(0, 'best_ask')

        elif ('get_midprice' in msg):
            midprice = self.sim.exchange.get_midprice(msg['get_midprice']['ticker'])
            self.send({"midprice": midprice}, 'midprice')

        elif ('limit_buy' in msg):
            ticker = msg['limit_buy']['ticker']
            price = msg['limit_buy']['price']
            qty = msg['limit_buy']['qty']
            creator = msg['limit_buy']['creator']
            fee = msg['limit_buy']['fee']
            order = self.sim.exchange.limit_buy(ticker, price, qty, creator, fee).to_dict()
            self.send(order, 'limit_buy_placed')

        elif ('limit_sell' in msg):
            ticker = msg['limit_sell']['ticker']
            price = msg['limit_sell']['price']
            qty = msg['limit_sell']['qty']
            creator = msg['limit_sell']['creator']
            fee = msg['limit_sell']['fee']
            order = self.sim.exchange.limit_sell(ticker, price, qty, creator, fee).to_dict()
            self.send(order, 'limit_sell_placed')

        elif ('cancel_order' in msg):
            order_id = msg['cancel_order']['order_id']
            cancelled_order = self.sim.exchange.cancel_order(order_id).to_dict()
            self.send(cancelled_order, 'order_cancelled')

        elif ('cancel_all_orders' in msg):
            ticker = msg['cancel_all_orders']['ticker']
            agent = msg['cancel_all_orders']['agent']
            self.sim.exchange.cancel_all_orders(agent, ticker)
            self.send('All orders cancelled.', 'orders_cancelled')

        elif ('market_buy' in msg):
            ticker = msg['market_buy']['ticker']
            qty = msg['market_buy']['qty']
            buyer = msg['market_buy']['buyer']
            fee = msg['market_buy']['fee']
            self.sim.exchange.market_buy(ticker, qty, buyer, fee)
            self.send('Market buy order placed.', 'market_buy_placed')

        elif ('market_sell' in msg):
            ticker = msg['market_sell']['ticker']
            qty = msg['market_sell']['qty']
            seller = msg['market_sell']['seller']
            fee = msg['market_sell']['fee']
            self.sim.exchange.market_sell(ticker, qty, seller, fee)
            self.send('Market sell order placed.', 'market_sell_placed')
