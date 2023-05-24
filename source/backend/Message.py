from ._utils import format_dataframe_rows_to_dict

class Message():
    def __init__(self, sim, queue, conn):
        self.sim = sim
        self.queue = queue
        self.conn = conn

    def run(self):
        msg = self.conn.recv()
        if(msg['get_sim_time']):
            self.conn.send({'sim_time': self.sim.dt, 'episode': self.sim.episode, 'episodes': self.sim._episodes})
        
        elif(msg['get_candles']):
            candles = self.sim.get_price_bars(msg['get_candles']['ticker'], bar_size=msg['get_candles']['interval']).head(msg['get_candles']['limit']).to_json()
            if candles:
                self.conn.send({"candles": candles})
            else:
                self.conn.send({'message': 'No candles available.'})
        
        elif(msg['get_trades']):
            trades = self.sim.trades.head(msg['get_trades']['limit']).to_json()
            if trades:
                self.conn.send(trades)
            else:
                self.conn.send({'message': 'No trades available.'})
        
        elif(msg['create_asset']):
            self.sim.exchange.create_asset(msg['create_asset']['ticker'], msg['create_asset']['seed_price'], msg['create_asset']['seed_bid'], msg['create_asset']['seed_ask'])
            self.conn.send({'message': 'Asset created successfully.'}) 
        
        elif(msg['get_mempool']):
            mempool = self.sim.exchange.blockchain.mempool.transaction_log
            if mempool:
                self.conn.send(mempool.head(msg['get_mempool']['limit']).to_json())
            else:
                self.conn.send({'message': 'No mempool available.'})
        
        elif(msg['get_order_book']):
            order_book = self.sim.exchange.get_order_book(msg['get_order_book']['ticker'])
            if order_book:
                self.conn.send({"bids": order_book.df['bids'].to_dict(), "asks": order_book.df['asks'].to_dict()})
            else:
                self.conn.send({'message': 'Order book not found.'})
        
        elif(msg['get_latest_trade']):
            latest_trade = self.sim.exchange.get_latest_trade(msg['get_latest_trade']['ticker'])  
            if latest_trade:
                self.conn.send(latest_trade.to_dict())
            else:
                self.conn.send({'message': 'No trades available.'})
        
        elif(msg['get_trades']):
            trades = self.sim.exchange.get_trades(msg['get_trades']['ticker']).head(msg['get_trades']['limit'])
            format_trades = format_dataframe_rows_to_dict(trades)
            if format_trades:
                self.conn.send(format_trades)
            else:
                self.conn.send({'message': 'No trades available.'})
        
        elif(msg['get_quotes']):
            quotes = self.sim.exchange.get_quotes(msg['get_quotes']['ticker'])
            if quotes:
                self.conn.send(quotes)
            else:
                self.conn.send({'message': 'No quotes available.'})
        
        elif(msg['get_best_bid']):
            best_bid = self.sim.exchange.get_best_bid(msg['get_best_bid']['ticker'])
            if best_bid:
                self.conn.send(best_bid.to_dict())
            else:
                self.conn.send({'message': 'No best bid available.'})
        
        elif(msg['get_best_ask']):
            best_ask = self.sim.exchange.get_best_ask(msg['get_best_ask']['ticker'])
            if best_ask:
                self.conn.send(best_ask.to_dict())
            else:
                self.conn.send({'message': 'No best ask available.'})

        elif(msg['get_midprice']):
            midprice = self.sim.exchange.get_midprice(msg['get_midprice']['ticker'])
            if midprice:
                self.conn.send({'midprice': midprice})
            else:
                self.conn.send({'message': 'No midprice available.'})
        
        elif(msg['limit_buy']):
            ticker = msg['limit_buy']['ticker']
            price = msg['limit_buy']['price']
            qty = msg['limit_buy']['qty']
            creator = msg['limit_buy']['creator']
            fee = msg['limit_buy']['fee']
            order = self.sim.exchange.limit_buy(ticker, price, qty, creator, fee)
            self.conn.send(order.to_dict())
        
        elif(msg['limit_sell']):
            ticker = msg['limit_sell']['ticker']
            price = msg['limit_sell']['price']
            qty = msg['limit_sell']['qty']
            creator = msg['limit_sell']['creator']
            fee = msg['limit_sell']['fee']
            order = self.sim.exchange.limit_sell(ticker, price, qty, creator, fee)
            self.conn.send(order.to_dict())

        elif(msg['cancel_order']):
            order_id = msg['cancel_order']['order_id']
            cancelled_order = self.sim.exchange.cancel_order(order_id)
            if cancelled_order:
                self.conn.send(cancelled_order.to_dict())
            else:
                self.conn.send({'message': 'Order not found.'})
        
        elif(msg['cancel_all_orders']):
            ticker = msg['cancel_all_orders']['ticker']
            agent = msg['cancel_all_orders']['agent']
            self.sim.exchange.cancel_all_orders(agent, ticker)
            self.conn.send({'message': 'All orders cancelled.'})
        
        elif(msg['market_buy']):
            ticker = msg['market_buy']['ticker']
            qty = msg['market_buy']['qty']
            buyer = msg['market_buy']['buyer']
            fee = msg['market_buy']['fee']
            self.sim.exchange.market_buy(ticker, qty, buyer, fee)
            self.conn.send({'message': 'Market buy order placed.'})
        
        elif(msg['market_sell']):
            ticker = msg['market_sell']['ticker']
            qty = msg['market_sell']['qty']
            seller = msg['market_sell']['seller']
            fee = msg['market_sell']['fee']
            self.sim.exchange.market_sell(ticker, qty, seller, fee)
            self.conn.send({'message': 'Market sell order placed.'})
    








            
