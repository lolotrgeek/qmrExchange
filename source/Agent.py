import pandas as pd
from typing import List, Union
from .Exchange import Exchange
from .types.Trade import Trade
from .types.LimitOrder import LimitOrder
from uuid import uuid4 as UUID

class Agent():
    """The Agent class is the base class for developing different traders that participate in the simulated exchange.
    """
    def __init__(self, name:str, tickers:List[str], aum:int=10_000):
        self.name = name
        self.id = UUID()
        self.tickers = tickers
        self.exchange:Exchange = None
        self.cash = aum
        self.initial_cash = aum
        self._transactions = []

    def __repr__(self):
        return f'<Agent: {self.name}>'

    def __str__(self):
        return f'<Agent: {self.name}>'

    def get_latest_trade(self, ticker:str) -> Trade:
        """Returns the most recent trade of a given asset

        Args:
            ticker (str): the ticker of the corresponding asset

        Returns:
            Trade: the most recent trade
        """
        return self.exchange.get_latest_trade(ticker)

    def get_best_bid(self, ticker:str) -> LimitOrder:
        """Returns the current best limit buy order

        Args:
            ticker (str): the ticker of the asset

        Returns:
            LimitOrder: the current best limit buy order
        """
        return self.exchange.get_best_bid(ticker)

    def get_best_ask(self, ticker:str) -> LimitOrder:
        """Returns the current best limit sell order

        Args:
            ticker (str): the ticker of the asset

        Returns:
            LimitOrder: the current best limit sell order
        """
        return self.exchange.get_best_ask(ticker)
        
    def get_midprice(self, ticker:str) -> float:
        """Returns the current midprice of the best bid and ask orders in the orderbook of an asset

        Args:
            ticker (str): the ticker of the asset

        Returns:
            float: the current midprice
        """
        return self.get_midprice(ticker)

    def get_order_book(self,ticker):
        return self.exchange.get_order_book(ticker)

    def get_quotes(self,ticker):
        return self.exchange.get_quotes(ticker)

    def get_trades(self, ticker):
        return self.exchange.get_trades(ticker)

    def market_buy(self, ticker:str, qty:int, fee=0.0):
        """Places a market buy order. The order executes automatically at the best sell price if ask quotes are available.

        Args:
            ticker (str): the ticker of the asset.
            qty (int): the quantity of the asset to be acquired (in units)

        """
        return self.exchange.market_buy(ticker, qty, self.name, fee)

    def market_sell(self, ticker:str, qty:int, fee=0.0):
        """Places a market sell order. The order executes automatically at the best buy price if bid quotes are available.

        Args:
            ticker (str): the ticker of the asset.
            qty (int): the quantity of the asset to be sold (in units)

        """
        return self.exchange.market_sell(ticker, qty, self.name, fee)

    def limit_buy(self, ticker:str, price:float, qty:int, fee=0.0) -> LimitOrder:
        """Creates a limit buy order for a given asset and quantity at a certain price.

        Args:
            ticker (str): the ticker of the asset
            price (float): the limit price
            qty (int): the quantity to be acquired

        Returns:
            LimitOrder
        """
        return self.exchange.limit_buy(ticker,price,qty,self.name, fee)

    def limit_sell(self, ticker:str, price:float, qty:int, fee=0.0) -> LimitOrder:
        """Creates a limit sell order for a given asset and quantity at a certain price.

        Args:
            ticker (str): the ticker of the asset
            price (float): the limit price
            qty (int): the quantity to be sold

        Returns:
            LimitOrder
        """
        return self.exchange.limit_sell(ticker,price,qty,self.name, fee)

    def get_position(self,ticker):
        return sum(t['qty'] for t in self._transactions if t['ticker'] == ticker)

    def get_cash_history(self):
        return pd.DataFrame(self.__cash_history).set_index('dt')

    @property
    def trades(self):
        trades = self.exchange.trades
        trades = trades[trades[['buyer','seller']].isin([self.name]).any(axis=1)]
        return trades

    def _set_exchange(self,exchange):
        self.exchange = exchange

    def cancel_order(self, id:str) -> Union[LimitOrder,None]:
        """Cancels the order with a given id (if it exists)

        Args:
            id (str): the id of the limit order

        Returns:
            Union[LimitOrder,None]: the cancelled order if it is still pending. None if it does not exists or has already been filled/cancelled
        """
        self.exchange.cancel_order(id=id)

    def cancel_all_orders(self, ticker:str):
        """Cancels all remaining orders that the agent has on an asset.

        Args:
            ticker (str): the ticker of the asset.
        """
        self.exchange.cancel_all_orders(self.name,ticker)

    def get_price_bars(self, bar_size='1D'):
        return  self.exchange.get_price_bars(bar_size)

    def next(self):  
        pass
