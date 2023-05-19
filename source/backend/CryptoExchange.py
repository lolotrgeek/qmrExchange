from .Exchange import Exchange
from .MemPool import MemPool
from .Trade import Trade
from .LimitOrder import LimitOrder
from .OrderSide import OrderSide

class CryptoExchange(Exchange):
    def __init__(self, datetime= None):
        super().__init__(datetime)
        self.crypto = True
        self.mempool = MemPool()


    def _process_trade(self, ticker, qty, price, buyer, seller, fee=0):
        self.trade_log.append(
            Trade(ticker, qty, price, buyer, seller,self.datetime)
        )

        self.mempool.add_transaction(ticker, fee, amount=qty*price, sender=seller, recipient=buyer, dt=self.datetime)     

        self.agents_cash_updates.extend([
            {'agent':buyer,'cash_flow':-qty*price,'ticker':ticker,'qty': qty},
            {'agent':seller,'cash_flow':qty*price,'ticker':ticker,'qty': -qty}
        ])
       
    def limit_buy(self, ticker: str, price: float, qty: int, creator: str, fee=0):
        price = round(price,2)
        # check if we can match trades before submitting the limit order
        while qty > 0:
            best_ask = self.get_best_ask(ticker)
            if best_ask and price >= best_ask.price:
                trade_qty = min(qty, best_ask.qty)
                self._process_trade(ticker, trade_qty,
                                    best_ask.price, creator, best_ask.creator, fee)
                qty -= trade_qty
                self.books[ticker].asks[0].qty -= trade_qty
                self.books[ticker].asks = [
                    ask for ask in self.books[ticker].asks if ask.qty > 0]
            else:
                break
        queue = len(self.books[ticker].bids)
        for idx, order in enumerate(self.books[ticker].bids):
            if price > order.price:
                queue = idx
                break
        new_order = LimitOrder(ticker, price, qty, creator, OrderSide.BUY, self.datetime)
        self.books[ticker].bids.insert(queue, new_order)
        return new_order
    
    def limit_sell(self, ticker: str, price: float, qty: int, creator: str, fee=0):
        price = round(price,2)
        # check if we can match trades before submitting the limit order
        while qty > 0:
            best_bid = self.get_best_bid(ticker)
            if best_bid and price <= best_bid.price:
                trade_qty = min(qty, best_bid.qty)
                self._process_trade(ticker, trade_qty,
                                    best_bid.price, best_bid.creator, creator, fee)
                qty -= trade_qty
                self.books[ticker].bids[0].qty -= trade_qty
                self.books[ticker].bids = [
                    bid for bid in self.books[ticker].bids if bid.qty > 0]
            else:
                break
        queue = len(self.books[ticker].asks)
        for idx, order in enumerate(self.books[ticker].asks):
            if price < order.price:
                queue = idx
                break
        new_order = LimitOrder(ticker, price, qty, creator, OrderSide.SELL, self.datetime)
        self.books[ticker].asks.insert(queue, new_order)
        return new_order

    def market_buy(self, ticker: str, qty: int, buyer: str, fee=0):
        for idx, ask in enumerate(self.books[ticker].asks):
            trade_qty = min(ask.qty, qty)
            self.books[ticker].asks[idx].qty -= trade_qty
            qty -= trade_qty
            self._process_trade(ticker, trade_qty,
                                ask.price, buyer, ask.creator, fee)
            if qty == 0:
                break
        self.books[ticker].asks = [
            ask for ask in self.books[ticker].asks if ask.qty > 0]

    def market_sell(self, ticker: str, qty: int, seller: str, fee=0):
        for idx, bid in enumerate(self.books[ticker].bids):
            trade_qty = min(bid.qty, qty)
            self.books[ticker].bids[idx].qty -= trade_qty
            qty -= trade_qty
            self._process_trade(ticker, trade_qty,
                                bid.price, bid.creator, seller, fee)
            if qty == 0:
                break
        self.books[ticker].bids = [
            bid for bid in self.books[ticker].bids if bid.qty > 0]
