import pandas as pd
from typing import List
from .types.OrderBook import OrderBook
from .types.Trade import Trade
from .types.LimitOrder import LimitOrder
from .types.OrderSide import OrderSide
from .Blockchain import Blockchain
from .types.Fees import Fees
from .utils._utils import format_dataframe_rows_to_dict
# Creates an Orderbook and Assets
class Exchange():
    def __init__(self, datetime= None):
        self.agents = []
        self.books = {}
        self.trade_log: List[Trade] = []
        self.datetime = datetime
        self.agents_cash_updates = []
        self.fees = Fees()
        self.crypto = False
        self.blockchain = self.crypto if self.crypto else Blockchain(datetime=datetime)

    def __str__(self):
        return ', '.join(ob for ob in self.books)

    def create_asset(self, ticker: str, market_qty=1000, seed_price=100, seed_bid=.99, seed_ask=1.01) -> OrderBook:
        """_summary_

        Args:
            ticker (str): the ticker of the new asset
            marekt_qty (int, optional): the total amount of the asset in circulation. Defaults to 1000.
            seed_price (int, optional): Price of an initial trade that is created for ease of use. Defaults to 100.
            seed_bid (float, optional): Limit price of an initial buy order, expressed as percentage of the seed_price. Defaults to .99.
            seed_ask (float, optional): Limit price of an initial sell order, expressed as percentage of the seed_price. Defaults to 1.01.
        """
        self.books[ticker] = OrderBook(ticker)
        self.agents.append({'name':'init_seed','cash':market_qty * seed_price,'_transactions':[], 'assets': {ticker: market_qty}})
        self._process_trade(ticker, market_qty, seed_price, 'init_seed', 'init_seed',)
        self.limit_buy(ticker, seed_price * seed_bid, 1, 'init_seed')
        self.limit_sell(ticker, seed_price * seed_ask, market_qty, 'init_seed')
        return self.books[ticker]

    def get_order_book(self, ticker: str) -> OrderBook:
        """Returns the OrderBook of a given Asset

        Args:
            ticker (str): the ticker of the asset

        Returns:
            OrderBook: the orderbook of the asset.
        """
        return self.books[ticker]
     
    def get_latest_trade(self, ticker:str) -> Trade:
        """Retrieves the most recent trade of a given asset

        Args:
            ticker (str): the ticker of the trade

        Returns:
            Trade
        """
        latest_trade = next(trade for trade in self.trade_log[::-1] if trade.ticker == ticker).to_dict()
        return latest_trade

    def get_quotes(self, ticker):
        try:
            # TODO: if more than one order has the best price, add the quantities.
            best_bid = self.books[ticker].bids[0]
            best_ask = self.books[ticker].asks[0]
        except IndexError :
            best_bid = LimitOrder(ticker, 0, 0, 'null_quote', OrderSide.BUY, self.datetime)
            best_ask = LimitOrder(ticker, 0, 0, 'null_quote', OrderSide.SELL, self.datetime)

        quotes = {
            'ticker': ticker,
            'bid_qty': best_bid.qty,
            'bid_p': best_bid.price,
            'ask_qty': best_ask.qty,
            'ask_p': best_ask.price,
        }
        return quotes

    def get_midprice(self, ticker:str) -> float:
        """Returns the current midprice of the best bid and ask quotes.

        Args:
            ticker (str): the ticker of the asset

        Returns:
            float: the current midprice
        """
        quotes = self.get_quotes(ticker)
        return {"midprice" :(quotes['bid_p'] + quotes['ask_p']) / 2}

    def get_trades(self, ticker:str, limit=20) -> list:
        """Retrieves all past trades of a given asset

        Args:
            ticker (str): the ticker of the asset

        Returns:
            pd.DataFrame: a dataframe containing all trades
        """
        trades = pd.DataFrame.from_records([t.to_dict() for t in self.trade_log if t.ticker == ticker]).head(limit)
        return format_dataframe_rows_to_dict(trades)
    
    def get_price_bars(self, ticker, limit=20, bar_size='1D'):
        #TODO: not resampling correctly
        trades = self.trades
        trades = trades[trades['ticker']== ticker]
        trades.index = pd.to_datetime(trades.index)
        df = trades.resample(bar_size).agg({'price': 'ohlc', 'qty': 'sum'})
        df.columns = df.columns.droplevel()
        df.rename(columns={'qty':'volume'},inplace=True)
        return format_dataframe_rows_to_dict(df.head(limit))
    
    def _process_trade(self, ticker, qty, price, buyer, seller, fee=0.0):
        trade = Trade(ticker, qty, price, buyer, seller, self.datetime, fee=fee)
        self.trade_log.append(trade)
        if(self.crypto):
            #NOTE: the `fee` is the network fee and the exchange fee since the exchange fee is added to the transaction before it is added to the blockchain
            # while not how this works, this is makes calulating the overall fee easier for the simulator
            self.blockchain.add_transaction(ticker, fee, amount=qty*price, sender=seller, recipient=buyer, dt=self.datetime)
            self.__update_agents_currency(self.blockchain.mempool.transactions[-1])
        else:
            transaction = [
                {'agent':buyer,'cash_flow':-qty*price,'ticker':ticker,'qty': qty, 'fee':fee, 'type': 'buy'},
                {'agent':seller,'cash_flow':qty*price,'ticker':ticker,'qty': -qty, 'fee':fee, 'type': 'sell'}
            ]
            # self.agents_cash_updates.extend(transaction)
            self.__update_agents_cash(transaction)

    def get_best_ask(self, ticker:str) -> LimitOrder:
        """retrieves the current best ask in the orderbook of an asset

        Args:
            ticker (str): the ticker of the asset.

        Returns:
            LimitOrder
        """
        if self.books[ticker].asks and self.books[ticker].asks[0]:
            return self.books[ticker].asks[0]
        else:
            return LimitOrder(ticker, 0, 0, 'null_quote', OrderSide.SELL, self.datetime)

    def get_best_bid(self, ticker:str) -> LimitOrder:
        """retrieves the current best bid in the orderbook of an asset

        Args:
            ticker (str): the ticker of the asset.

        Returns:
            LimitOrder
        """
        if self.books[ticker].bids and self.books[ticker].bids[0]:
            return self.books[ticker].bids[0]
        else:
            return LimitOrder(ticker, 0, 0, 'null_quote', OrderSide.BUY, self.datetime)

    def limit_buy(self, ticker: str, price: float, qty: int, creator: str, fee=0, tif='GTC'):
        if self.agent_has_cash(creator, price, qty):
            if not self.crypto:
                price = round(price,2)
            # check if we can match trades before submitting the limit order
            unfilled_qty = qty
            while unfilled_qty > 0:
                if tif == 'TEST':
                    break
                best_ask = self.get_best_ask(ticker)
                if best_ask.creator != 'null_quote' and price >= best_ask.price:
                    trade_qty = min(unfilled_qty, best_ask.qty)
                    taker_fee = self.fees.taker_fee(trade_qty)
                    self.fees.total_fee_revenue += taker_fee
                    if(type(fee) is str): fee = float(fee)
                    self._process_trade(ticker, trade_qty, best_ask.price, creator, best_ask.creator, fee=fee+taker_fee)
                    unfilled_qty -= trade_qty
                    self.books[ticker].asks[0].qty -= trade_qty
                    self.books[ticker].asks = [ask for ask in self.books[ticker].asks if ask.qty > 0]
                else:
                    break
            queue = len(self.books[ticker].bids)
            for idx, order in enumerate(self.books[ticker].bids):
                if price > order.price:
                    queue = idx
                    break
            maker_fee = 0
            if unfilled_qty > 0:
                maker_fee = self.fees.maker_fee(unfilled_qty)
                self.fees.total_fee_revenue += maker_fee
            new_order = LimitOrder(ticker, price, unfilled_qty, creator, OrderSide.BUY, self.datetime,fee=fee+maker_fee)
            self.books[ticker].bids.insert(queue, new_order)
            initial_order = new_order
            initial_order.qty = qty
            return initial_order
        else:
            return LimitOrder("error", 0, 0, 'insufficient_funds', OrderSide.BUY, self.datetime)

    def limit_sell(self, ticker: str, price: float, qty: int, creator: str, fee=0, tif='GTC'):
        if self.agent_has_assets(creator, ticker, qty):
            if not self.crypto:
                price = round(price,2)
            # check if we can match trades before submitting the limit order
            unfilled_qty = qty
            while unfilled_qty > 0:
                if tif == 'TEST':
                    break
                best_bid = self.get_best_bid(ticker)
                if best_bid.creator != 'null_quote' and price <= best_bid.price:
                    trade_qty = min(unfilled_qty, best_bid.qty)
                    taker_fee = self.fees.taker_fee(trade_qty)
                    self.fees.total_fee_revenue += taker_fee
                    if(type(fee) is str): fee = float(fee)
                    self._process_trade(ticker, trade_qty, best_bid.price, best_bid.creator, creator, fee=fee+taker_fee)
                    unfilled_qty -= trade_qty
                    self.books[ticker].bids[0].qty -= trade_qty
                    self.books[ticker].bids = [bid for bid in self.books[ticker].bids if bid.qty > 0]
                else:
                    break
            queue = len(self.books[ticker].asks)
            for idx, order in enumerate(self.books[ticker].asks):
                if price < order.price:
                    queue = idx
                    break
            maker_fee = 0
            if unfilled_qty > 0:
                maker_fee = self.fees.maker_fee(unfilled_qty)
                self.fees.total_fee_revenue += maker_fee
            new_order = LimitOrder(ticker, price, unfilled_qty, creator, OrderSide.SELL, self.datetime, fee=fee+maker_fee)
            self.books[ticker].asks.insert(queue, new_order)
            initial_order = new_order
            initial_order.qty = qty
            return initial_order
        else:
            return LimitOrder("error", 0, 0, 'insufficient_assets', OrderSide.SELL, self.datetime)

    def get_order(self, id):
        for book in self.books:
            bid = next(([idx,o] for idx, o in enumerate(self.books[book].bids) if o.id == id),None)
            if bid:
                return bid
            ask = next(([idx,o] for idx, o in enumerate(self.books[book].asks) if o.id == id),None)
            if ask:
                return ask
        return None

    def cancel_order(self, id):
        for book in self.books:
            bid = next(([idx,o] for idx, o in enumerate(self.books[book].bids) if o.id == id),None)
            if bid:
                self.books[book].bids[bid[0]]
                self.books[book].bids.pop(bid[0])
                return {"cancelled_order": id}
            ask = next(([idx,o] for idx, o in enumerate(self.books[book].asks) if o.id == id),None)
            if ask:
                self.books[book].asks.pop(ask[0])
                return {"cancelled_order": id}
        return {"cancelled_order": "order not found"}

    def cancel_all_orders(self, agent, ticker):
        self.books[ticker].bids = [b for b in self.books[ticker].bids if b.creator != agent]
        self.books[ticker].asks = [a for a in self.books[ticker].asks if a.creator != agent]
        return {"cancelled_all_orders": ticker}

    def market_buy(self, ticker: str, qty: int, buyer: str, fee=0.0):
        if self.agent_has_cash(buyer, self.get_best_ask(ticker).price, qty):
            fills = []
            for idx, ask in enumerate(self.books[ticker].asks):
                trade_qty = min(ask.qty, qty)
                self.books[ticker].asks[idx].qty -= trade_qty
                qty -= trade_qty
                taker_fee = self.fees.taker_fee(qty)
                self.fees.total_fee_revenue += taker_fee
                if(type(fee) is str): fee = float(fee)
                fills.append({'qty': trade_qty, 'price': ask.price, 'fee': fee+taker_fee})
                self._process_trade(ticker, trade_qty,ask.price, buyer, ask.creator, fee=fee+taker_fee)
                if qty == 0:
                    break
            self.books[ticker].asks = [ask for ask in self.books[ticker].asks if ask.qty > 0]
            return {"market_buy": ticker, "buyer": buyer, "fills": fills}
        else:
            return {"market_buy": "insufficient funds"}

    def market_sell(self, ticker: str, qty: int, seller: str, fee=0.0):
        if self.agent_has_assets(seller, ticker, qty):
            fills = []
            for idx, bid in enumerate(self.books[ticker].bids):
                trade_qty = min(bid.qty, qty)
                self.books[ticker].bids[idx].qty -= trade_qty
                qty -= trade_qty
                taker_fee = self.fees.taker_fee(qty)
                self.fees.total_fee_revenue += taker_fee
                if(type(fee) is str): fee = float(fee)
                fills.append({'qty': trade_qty, 'price': bid.price, 'fee': fee+taker_fee})
                self._process_trade(ticker, trade_qty,bid.price, bid.creator, seller, fee=fee+taker_fee)
                if qty == 0:
                    break
            self.books[ticker].bids = [bid for bid in self.books[ticker].bids if bid.qty > 0]
            return {"market_sell": ticker, "seller": seller, "fills": fills }
        else:
            return {"market_sell": "insufficient assets"}

    def agent_has_cash(self, agent, price, qty):
        agent_cash = self.get_cash(agent)['cash']
        return agent_cash >= price * qty
    
    def agent_has_assets(self, agent, ticker, qty):
        agent_assets = self.get_assets(agent)['assets']
        if ticker in agent_assets:
            return agent_assets[ticker] >= qty
        else: 
            return False

    @property
    def trades(self):
        return pd.DataFrame.from_records([t.to_dict() for t in self.trade_log]).set_index('dt')

    def _set_datetime(self, dt):
        self.datetime = dt

    def register_agent(self, name, initial_cash):
        #TODO: use an agent class???
        self.agents.append({'name':name,'cash':initial_cash,'_transactions':[], 'assets': {}})
        return {'registered_agent':name}

    def get_cash(self, agent_name):
        return {'cash':self.get_agent(agent_name)['cash']}
    
    def get_assets(self, agent):
        return {'assets': self.get_agent(agent)['assets']}
    
    def __update_agents_cash(self, transaction):
        for side in transaction:
            agent_idx = self.__get_agent_index(side['agent'])
            if agent_idx is not None:
                self.agents[agent_idx]['cash'] += side['cash_flow']
                self.agents[agent_idx]['_transactions'].append({'dt':self.datetime,'cash_flow':side['cash_flow'],'ticker':side['ticker'],'qty':side['qty']})
                if side['ticker'] in self.agents[agent_idx]['assets']: 
                    # print('updating... ',side['type'] , ' ', self.agents[agent_idx]['name'],' ',self.agents[agent_idx]['assets'][side['ticker']],'to',self.agents[agent_idx]['assets'][side['ticker']] + side['qty'])
                    self.agents[agent_idx]['assets'][side['ticker']] += side['qty']
                else: self.agents[agent_idx]['assets'][side['ticker']] = side['qty']
                 
    def __update_agents_currency(self, transaction):
        if transaction.confirmed:
            buyer_idx = self.__get_agent_index(transaction.recipient)
            seller_idx = self.__get_agent_index(transaction.sender)
            if(buyer_idx is None or seller_idx is None):
                return
            buyer = self.agents[buyer_idx]
            seller = self.agents[seller_idx]
            #TODO: have cash be an asset that is some currency
            buyer['cash'] -= transaction.amount + transaction.fee #NOTE: transaction.fee includes the exchange fee and the network fee
            seller['cash'] += transaction.amount
            buyer['_transactions'].append({'dt':self.datetime,'cash_flow':-(transaction.amount+transaction.fee),'ticker':transaction.ticker,'qty':transaction.amount})
            seller['_transactions'].append({'dt':self.datetime,'cash_flow':transaction.amount,'ticker':transaction.ticker,'qty':transaction.amount})

    def get_agent(self, agent_name):
        return next((d for (index, d) in enumerate(self.agents) if d['name'] == agent_name), None)

    def __get_agent_index(self,agent_name):
        return next((index for (index, d) in enumerate(self.agents) if d['name'] == agent_name), None)