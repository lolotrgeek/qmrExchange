import pandas as pd
from typing import List
from .OrderBook import OrderBook
from .Trade import Trade
from .LimitOrder import LimitOrder
from .OrderSide import OrderSide
from .Blockchain import Blockchain
from .Fees import Fees

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

    def create_asset(self, ticker: str, seed_price=100, seed_bid=.99, seed_ask=1.01):
        """_summary_

        Args:
            ticker (str): the ticker of the new asset
            seed_price (int, optional): Price of an initial trade that is created for ease of use. Defaults to 100.
            seed_bid (float, optional): Limit price of an initial buy order, expressed as percentage of the seed_price. Defaults to .99.
            seed_ask (float, optional): Limit price of an initial sell order, expressed as percentage of the seed_price. Defaults to 1.01.
        """
        self.books[ticker] = OrderBook(ticker)
        self._process_trade(ticker, 1, seed_price, 'init_seed', 'init_seed',)
        self.limit_buy(ticker, seed_price * seed_bid, 1, 'init_seed')
        self.limit_sell(ticker, seed_price * seed_ask, 1, 'init_seed')
        return self.books[ticker]

    def _process_trade(self, ticker, qty, price, buyer, seller, fee=0):
        self.trade_log.append(
            Trade(ticker, qty, price, buyer, seller,self.datetime)
        )
        if(self.crypto):
            #NOTE: the `fee` is the network fee and the exchange fee since the exchange fee is added to the transaction before it is added to the blockchain
            # while not how this works, this is makes calulating the overall fee easier for the simulator
            self.blockchain.add_transaction(ticker, fee, amount=qty*price, sender=seller, recipient=buyer, dt=self.datetime)
            self.__update_agents_currency(self.blockchain.mempool.transactions[-1])
        else:
            transaction = [
                {'agent':buyer,'cash_flow':-qty*price,'ticker':ticker,'qty': qty},
                {'agent':seller,'cash_flow':qty*price,'ticker':ticker,'qty': -qty}
            ]
            # self.agents_cash_updates.extend(transaction)
            self.__update_agents_cash(transaction)

    def limit_buy(self, ticker: str, price: float, qty: int, creator: str, fee=0):
        if not self.crypto:
            price = round(price,2)
        # check if we can match trades before submitting the limit order
        while qty > 0:
            best_ask = self.get_best_ask(ticker)
            if best_ask and price >= best_ask.price:
                trade_qty = min(qty, best_ask.qty)
                taker_fee = self.fees.taker_fee(qty)
                self.fees.total_fee_revenue += taker_fee
                self._process_trade(ticker, trade_qty, best_ask.price, creator, best_ask.creator, fee=fee+taker_fee)
                qty -= trade_qty
                self.books[ticker].asks[0].qty -= trade_qty
                self.books[ticker].asks = [ask for ask in self.books[ticker].asks if ask.qty > 0]
            else:
                break
        queue = len(self.books[ticker].bids)
        for idx, order in enumerate(self.books[ticker].bids):
            if price > order.price:
                queue = idx
                break
        maker_fee = self.fees.maker_fee(qty)
        self.fees.total_fee_revenue += maker_fee
        new_order = LimitOrder(ticker, price, qty, creator, OrderSide.BUY, self.datetime,fee=fee+maker_fee)
        self.books[ticker].bids.insert(queue, new_order)
        return new_order

    def limit_sell(self, ticker: str, price: float, qty: int, creator: str, fee=0):
        if not self.crypto:
            price = round(price,2)
        # check if we can match trades before submitting the limit order
        while qty > 0:
            best_bid = self.get_best_bid(ticker)
            if best_bid and price <= best_bid.price:
                trade_qty = min(qty, best_bid.qty)
                taker_fee = self.fees.taker_fee(qty)
                self.fees.total_fee_revenue += taker_fee
                self._process_trade(ticker, trade_qty, best_bid.price, best_bid.creator, creator, fee=fee+taker_fee)
                qty -= trade_qty
                self.books[ticker].bids[0].qty -= trade_qty
                self.books[ticker].bids = [bid for bid in self.books[ticker].bids if bid.qty > 0]
            else:
                break
        queue = len(self.books[ticker].asks)
        for idx, order in enumerate(self.books[ticker].asks):
            if price < order.price:
                queue = idx
                break
        maker_fee = self.fees.maker_fee(qty)
        self.fees.total_fee_revenue += maker_fee
        new_order = LimitOrder(ticker, price, qty, creator, OrderSide.SELL, self.datetime, fee=fee+maker_fee)
        self.books[ticker].asks.insert(queue, new_order)
        return new_order

    def cancel_order(self, id):
        for book in self.exchange.books:
            bid = next(([idx,o] for idx, o in enumerate(self.exchange.books[book].bids) if o.id == id),None)
            if bid:
                self.exchange.books[book].bids[bid[0]]
                self.exchange.books[book].bids.pop(bid[0])
                return bid
            ask = next(([idx,o] for idx, o in enumerate(self.exchange.books[book].asks) if o.id == id),None)
            if ask:
                self.exchange.books[book].asks.pop(ask[0])
                return ask
        return None

    def cancel_all_orders(self, agent, ticker):
        self.books[ticker].bids = [b for b in self.books[ticker].bids if b.creator != agent]
        self.books[ticker].asks = [a for a in self.books[ticker].asks if a.creator != agent]
        return None

    def market_buy(self, ticker: str, qty: int, buyer: str, fee=0):
        for idx, ask in enumerate(self.books[ticker].asks):
            trade_qty = min(ask.qty, qty)
            self.books[ticker].asks[idx].qty -= trade_qty
            qty -= trade_qty
            taker_fee = self.fees.taker_fee(qty)
            self.fees.total_fee_revenue += taker_fee
            self._process_trade(ticker, trade_qty,ask.price, buyer, ask.creator, fee=fee+taker_fee)
            if qty == 0:
                break
        self.books[ticker].asks = [
            ask for ask in self.books[ticker].asks if ask.qty > 0]

    def market_sell(self, ticker: str, qty: int, seller: str, fee=0):
        for idx, bid in enumerate(self.books[ticker].bids):
            trade_qty = min(bid.qty, qty)
            self.books[ticker].bids[idx].qty -= trade_qty
            qty -= trade_qty
            taker_fee = self.fees.taker_fee(qty)
            self.fees.total_fee_revenue += taker_fee
            self._process_trade(ticker, trade_qty,bid.price, bid.creator, seller, fee=fee+taker_fee)
            if qty == 0:
                break
        self.books[ticker].bids = [
            bid for bid in self.books[ticker].bids if bid.qty > 0]

    @property
    def trades(self):
        return pd.DataFrame.from_records([t.to_dict() for t in self.trade_log]).set_index('dt')

    def _set_datetime(self, dt):
        self.datetime = dt

    def register_agent(self, name, initial_cash):
        self.agents.append({'name':name,'cash':initial_cash,'_transactions':[]})

    def get_cash(self, agent):
        return self.get_agent(agent).cash
    
    def get_assets(self, agent):
        return self.get_agent(agent)._transactions
    
    def __update_agents_cash(self, transaction):
        for side in transaction:
            agent_idx = self.__get_agent_index(side['agent'])
            if agent_idx is not None:
                self.agents[agent_idx].cash += side['cash_flow']
                self.agents[agent_idx]._transactions.append({'dt':self.dt,'cash_flow':side['cash_flow'],'ticker':side['ticker'],'qty':side['qty']})

    def __update_agents_currency(self, transaction):
        if transaction.confirmed:
            buyer_idx = self.__get_agent_index(transaction.recipient)
            seller_idx = self.__get_agent_index(transaction.sender)
            if(buyer_idx is None or seller_idx is None):
                return
            buyer = self.agents[buyer_idx]
            seller = self.agents[seller_idx]
            #TODO: have cash be an asset that is some currency
            buyer.cash -= transaction.amount + transaction.fee #NOTE: transaction.fee includes the exchange fee and the network fee
            seller.cash += transaction.amount
            buyer._transactions.append({'dt':self.dt,'cash_flow':-(transaction.amount+transaction.fee),'ticker':transaction.ticker,'qty':transaction.amount})
            seller._transactions.append({'dt':self.dt,'cash_flow':transaction.amount,'ticker':transaction.ticker,'qty':transaction.amount})

    def get_agent(self, agent_name):
        return next((d for (index, d) in enumerate(self.agents) if d.name == agent_name), None)

    def __get_agent_index(self,agent_name):
        return next((index for (index, d) in enumerate(self.agents) if d.name == agent_name), None)