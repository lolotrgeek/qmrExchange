from .utils._utils import get_datetime_range, get_pandas_time
import pandas as pd
from typing import List, Union
from .types.Trade import Trade
from .types.LimitOrder import LimitOrder
from uuid import uuid4 as UUID

class Agent():
    """The Agent class is the base class for developing different traders that participate in the simulated exchange.
    """
    def __init__(self, name:str, tickers:List[str], aum:int=10_000, requester=None):
        self.id = UUID()
        self.name = name + str(self.id)[0:8]
        self.tickers = tickers
        self.requests = requester
        self.cash = aum
        self.initial_cash = aum

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
        return self.requests.get_latest_trade(ticker)

    def get_best_bid(self, ticker:str) -> LimitOrder:
        """Returns the current best limit buy order

        Args:
            ticker (str): the ticker of the asset

        Returns:
            LimitOrder: the current best limit buy order
        """
        return self.requests.get_best_bid(ticker)

    def get_best_ask(self, ticker:str) -> LimitOrder:
        """Returns the current best limit sell order

        Args:
            ticker (str): the ticker of the asset

        Returns:
            LimitOrder: the current best limit sell order
        """
        return self.requests.get_best_ask(ticker)
        
    def get_midprice(self, ticker:str) -> float:
        """Returns the current midprice of the best bid and ask orders in the orderbook of an asset

        Args:
            ticker (str): the ticker of the asset

        Returns:
            float: the current midprice
        """
        return self.requests.get_midprice(ticker)

    def get_order_book(self,ticker):
        return self.requests.get_order_book(ticker)

    def get_quotes(self,ticker):
        return self.requests.get_quotes(ticker)

    def get_trades(self, ticker, limit=20):
        return self.requests.get_trades(ticker, limit=limit)

    def market_buy(self, ticker:str, qty:int, fee=0.0):
        """Places a market buy order. The order executes automatically at the best sell price if ask quotes are available.

        Args:
            ticker (str): the ticker of the asset.
            qty (int): the quantity of the asset to be acquired (in units)

        """
        order = self.requests.market_buy(ticker, qty, self.name, fee)
        return order

    def market_sell(self, ticker:str, qty:int, fee=0.0):
        """Places a market sell order. The order executes automatically at the best buy price if bid quotes are available.

        Args:
            ticker (str): the ticker of the asset.
            qty (int): the quantity of the asset to be sold (in units)

        """
        order = self.requests.market_sell(ticker, qty, self.name, fee)
        return order

    def limit_buy(self, ticker:str, price:float, qty:int, fee=0.0) -> LimitOrder:
        """Creates a limit buy order for a given asset and quantity at a certain price.

        Args:
            ticker (str): the ticker of the asset
            price (float): the limit price
            qty (int): the quantity to be acquired

        Returns:
            LimitOrder
        """
        order = self.requests.limit_buy(ticker,price,qty,self.name, fee)
        return order

    def limit_sell(self, ticker:str, price:float, qty:int, fee=0.0) -> LimitOrder:
        """Creates a limit sell order for a given asset and quantity at a certain price.

        Args:
            ticker (str): the ticker of the asset
            price (float): the limit price
            qty (int): the quantity to be sold

        Returns:
            LimitOrder
        """
        order = self.requests.limit_sell(ticker,price,qty,self.name, fee)
        return order


    def get_position(self,ticker):
        agent = self.requests.get_agent(self.name)
        _transactions = agent['_transactions']
        return sum(t['qty'] for t in _transactions if t['ticker'] == ticker)

    def cancel_order(self, id:str) -> Union[LimitOrder,None]:
        """Cancels the order with a given id (if it exists)

        Args:
            id (str): the id of the limit order

        Returns:
            Union[LimitOrder,None]: the cancelled order if it is still pending. None if it does not exists or has already been filled/cancelled
        """
        return self.requests.cancel_order(id=id)

    def cancel_all_orders(self, ticker:str):
        """Cancels all remaining orders that the agent has on an asset.

        Args:
            ticker (str): the ticker of the asset.
        """
        return self.requests.cancel_all_orders(ticker, self.name)

    def get_price_bars(self,ticker, bar_size='1D', limit=20):
        return  self.requests.get_price_bars(ticker, bar_size, limit=limit)
    
    def get_cash(self):
        return self.requests.get_cash(self.name)
    
    def get_assets(self):
        return self.requests.get_assets(self.name)
    
    def get_portfolio_history(self, agent):
        #TODO: update for process
        return None
        bar_size = get_pandas_time(self._time_unit)
        portfolio = pd.DataFrame(index=get_datetime_range(self._from_date, self.dt, self._time_unit))
        transactions = pd.DataFrame(agent._transactions).set_index('dt')
        for ticker in list(self.exchange.books.keys()):
            qty_asset = pd.DataFrame(transactions[transactions['ticker'] == ticker]['qty'])
            qty_asset = qty_asset.resample(bar_size).agg('sum').cumsum()
            price = pd.DataFrame(index=get_datetime_range(self._from_date, self.dt, self._time_unit))
            price = price.join(self.get_price_bars(ticker=ticker, bar_size=bar_size)['close']).ffill()
            price = price.join(qty_asset).ffill()
            portfolio[ticker] = (price['close'] * price['qty'])
        portfolio['cash'] = transactions['cash_flow'].resample(bar_size).agg('sum').ffill()
        portfolio.fillna(0, inplace=True)
        portfolio['cash'] = portfolio['cash'].cumsum()
        portfolio['aum'] = portfolio.sum(axis=1)
        return portfolio  
    
    def register(self):
        return self.requests.register_agent(self.name, self.initial_cash)

    def next(self):  
        pass
