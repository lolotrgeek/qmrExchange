from ._utils import format_dataframe_rows_to_dict


class Responses():
    def __init__(self, sim, conn):
        self.sim = sim
        self.conn = conn

    def run(self):
        msg = self.conn.recv()
        # self.conn.poll()

        if ('get_sim_time' in msg):
            self.conn.send({'sim_time': self.sim.dt, 'episode': self.sim.episode, 'episodes': self.sim._episodes})

        elif ('get_candles' in msg):
            candles = self.sim.get_price_bars(msg['get_candles']['ticker'], bar_size=msg['get_candles']['interval']).head(msg['get_candles']['limit']).to_json()
            if candles:
                self.conn.send({"candles": candles})
            else:
                self.conn.send({'candles': {"error": {'No candles available.'} }} )

        elif ('create_asset' in msg):
            self.sim.exchange.create_asset(msg['create_asset']['ticker'], msg['create_asset']['seed_price'], msg['create_asset']['seed_bid'], msg['create_asset']['seed_ask'])
            self.conn.send({'created_asset': 'Asset created successfully.'})

        elif ('get_mempool' in msg):
            mempool = self.sim.exchange.blockchain.mempool.transaction_log
            if mempool:
                self.conn.send({"mempool": mempool.head(msg['get_mempool']['limit']).to_json()})
            else:
                self.conn.send({'mempool': {"error": {'No mempool available.'}}})

        elif ('get_order_book' in msg):
            order_book = self.sim.exchange.get_order_book(
                msg['get_order_book']['ticker'])
            if order_book:
                self.conn.send({"order_book": {"bids": format_dataframe_rows_to_dict(order_book.df['bids']), "asks": format_dataframe_rows_to_dict(order_book.df['asks'])}})
            else:
                self.conn.send({'order_book': {"error": {'Order book not found.'}}})

        elif ('get_latest_trade' in msg):
            latest_trade = self.sim.exchange.get_latest_trade(msg['get_latest_trade']['ticker'])
            if latest_trade:
                self.conn.send({'latest_trade': latest_trade.to_dict()})
            else:
                self.conn.send({'latest_trade': {"error": {'No trades available.'}}})

        elif ('get_trades' in msg):
            trades = self.sim.exchange.get_trades(msg['get_trades']['ticker']).head(msg['get_trades']['limit'])
            format_trades = format_dataframe_rows_to_dict(trades)
            if format_trades:
                self.conn.send({"trades": format_trades})
            else:
                self.conn.send({'trades': {"error": {'No trades available.'}}})

        elif ('get_quotes' in msg):
            quotes = self.sim.exchange.get_quotes(msg['get_quotes']['ticker'])
            if quotes:
                self.conn.send({'quotes': quotes})
            else:
                self.conn.send({'quotes': {"error": {'No quotes available.'}}})

        elif ('get_best_bid' in msg):
            best_bid = self.sim.exchange.get_best_bid(msg['get_best_bid']['ticker'])
            if best_bid:
                self.conn.send({'best_bid': best_bid.to_dict()})
            else:
                self.conn.send({'best_bid': {"error": {'No best bid available.'}}})

        elif ('get_best_ask' in msg):
            best_ask = self.sim.exchange.get_best_ask(
                msg['get_best_ask']['ticker'])
            if best_ask:
                self.conn.send({"best_ask": best_ask.to_dict()})
            else:
                self.conn.send({'best_ask': {"error": {'No best ask available.'}}})

        elif ('get_midprice' in msg):
            midprice = self.sim.exchange.get_midprice(msg['get_midprice']['ticker'])
            if midprice is not None:
                self.conn.send({'midprice': midprice})
            else:
                self.conn.send({'midprice': {"error": {'No midprice available.'}}})

        elif ('limit_buy' in msg):
            ticker = msg['limit_buy']['ticker']
            price = msg['limit_buy']['price']
            qty = msg['limit_buy']['qty']
            creator = msg['limit_buy']['creator']
            fee = msg['limit_buy']['fee']
            order = self.sim.exchange.limit_buy(ticker, price, qty, creator, fee)
            self.conn.send({"limit_buy_placed": order.to_dict()})

        elif ('limit_sell' in msg):
            ticker = msg['limit_sell']['ticker']
            price = msg['limit_sell']['price']
            qty = msg['limit_sell']['qty']
            creator = msg['limit_sell']['creator']
            fee = msg['limit_sell']['fee']
            order = self.sim.exchange.limit_sell(ticker, price, qty, creator, fee)
            self.conn.send({"limit_sell_placed": order.to_dict()})

        elif ('cancel_order' in msg):
            order_id = msg['cancel_order']['order_id']
            cancelled_order = self.sim.exchange.cancel_order(order_id)
            if cancelled_order:
                self.conn.send({'order_cancelled': cancelled_order.to_dict()})
            else:
                self.conn.send({'order_cancelled': {"error": {'Order not found.'}}})

        elif ('cancel_all_orders' in msg):
            ticker = msg['cancel_all_orders']['ticker']
            agent = msg['cancel_all_orders']['agent']
            self.sim.exchange.cancel_all_orders(agent, ticker)
            self.conn.send({'orders_cancelled': 'All orders cancelled.'})

        elif ('market_buy' in msg):
            ticker = msg['market_buy']['ticker']
            qty = msg['market_buy']['qty']
            buyer = msg['market_buy']['buyer']
            fee = msg['market_buy']['fee']
            self.sim.exchange.market_buy(ticker, qty, buyer, fee)
            self.conn.send({'market_buy_placed': 'Market buy order placed.'})

        elif ('market_sell' in msg):
            ticker = msg['market_sell']['ticker']
            qty = msg['market_sell']['qty']
            seller = msg['market_sell']['seller']
            fee = msg['market_sell']['fee']
            self.sim.exchange.market_sell(ticker, qty, seller, fee)
            self.conn.send({'market_sell_placed': 'Market sell order placed.'})
