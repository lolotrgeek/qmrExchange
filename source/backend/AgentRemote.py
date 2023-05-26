import pandas as pd
from typing import List, Union
from .Exchange import Exchange
from .Trade import Trade
from .LimitOrder import LimitOrder
from .OrderBook import OrderBook
from uuid import uuid4 as UUID
from requests import get, post
import aiohttp
import asyncio
import json

class AgentRemote():
    """The Agent class is the base class for developing different traders that participate remotely in the simulated exchange.
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

    async def get_latest_trade(self, ticker:str) -> Trade:
        """Returns the most recent trade of a given asset

        Args:
            ticker (str): the ticker of the corresponding asset

        Returns:
            Trade: the most recent trade
        """
        async with aiohttp.ClientSession() as session:
            url = f'http://localhost:5000/api/v1/get_latest_trade?ticker={ticker}'
            async with session.get(url) as response:
                
                dict_response = await response.json()
                return Trade(dict_response['ticker'], dict_response['qty'], dict_response['price'], dict_response['buyer'], dict_response['seller'], dict_response['dt'], dict_response['fee'])

    async def get_best_bid(self, ticker:str) -> LimitOrder:
        """Returns the current best limit buy order

        Args:
            ticker (str): the ticker of the asset

        Returns:
            LimitOrder: the current best limit buy order
        """
        async with aiohttp.ClientSession() as session:
            url = f'http://localhost:5000/api/v1/get_best_bid?ticker={ticker}'
            async with session.get(url) as response:
                
                dict_response = await response.json()
                # dict_response = json.loads(response.json())
                return LimitOrder(dict_response['ticker'], dict_response['qty'], dict_response['price'], dict_response['creator'], dict_response['id'])
    
    async def get_best_ask(self, ticker:str) -> LimitOrder:
        """Returns the current best limit sell order

        Args:
            ticker (str): the ticker of the asset

        Returns:
            LimitOrder: the current best limit sell order
        """
        async with aiohttp.ClientSession() as session:
            url = f'http://localhost:5000/api/v1/get_best_ask?ticker={ticker}'
            async with session.get(url) as response:
                
                dict_response = await response.json()
                return LimitOrder(dict_response['ticker'], dict_response['qty'], dict_response['price'], dict_response['creator'], dict_response['id'])
          
    async def get_midprice(self, ticker:str) -> float:
        """Returns the current midprice of the best bid and ask orders in the orderbook of an asset

        Args:
            ticker (str): the ticker of the asset

        Returns:
            float: the current midprice
        """
        async with aiohttp.ClientSession() as session:
            url = f'http://localhost:5000/api/v1/get_midprice?ticker={ticker}'
            async with session.get(url) as response:    
                
                dict_response = await response.json()
                return dict_response['midprice']

    async def get_order_book(self,ticker:str) -> OrderBook:
        async with aiohttp.ClientSession() as session:
            url = f'http://localhost:5000/api/v1/get_order_book?ticker={ticker}'
            async with session.get(url) as response:
                dict_response = await response.json()
                return dict_response

    async def get_quotes(self,ticker):
        async with aiohttp.ClientSession() as session:
            url = f'http://localhost:5000/api/v1/get_quotes?ticker={ticker}'
            async with session.get(url) as response:
                dict_response = await response.json()
                return dict_response

    async def get_trades(self, ticker):
        async with aiohttp.ClientSession() as session:
            url = f'http://localhost:5000/api/v1/get_trades?ticker={ticker}'
            async with session.get(url) as response:
                dict_response = await response.json()
                return dict_response

    async def market_buy(self, ticker:str, qty:int, fee=0.0):
        """Places a market buy order. The order executes automatically at the best sell price if ask quotes are available.

        Args:
            ticker (str): the ticker of the asset.
            qty (int): the quantity of the asset to be acquired (in units)

        """
        async with aiohttp.ClientSession() as session:
            post_url = f'http://localhost:5000/api/v1/market_buy'
            data = {'ticker': ticker, 'qty': qty, 'buyer': self.name, 'fee': fee}
            async with session.post(post_url, json=data) as response:
                response = post(post_url, data)
                dict_response = await response.json()
                return dict_response
    
    async def market_sell(self, ticker:str, qty:int, fee=0.0):
        """Places a market sell order. The order executes automatically at the best buy price if bid quotes are available.

        Args:
            ticker (str): the ticker of the asset.
            qty (int): the quantity of the asset to be sold (in units)

        """
        post_url = f'http://localhost:5000/api/v1/market_sell'
        data = {'ticker': ticker, 'qty': qty, 'seller': self.name, 'fee': fee}
        response = post(post_url, json=data)
        dict_response = await response.json()
        return dict_response

    async def limit_buy(self, ticker:str, price:float, qty:int, fee=0.0) -> LimitOrder:
        """Creates a limit buy order for a given asset and quantity at a certain price.

        Args:
            ticker (str): the ticker of the asset
            price (float): the limit price
            qty (int): the quantity to be acquired

        Returns:
            LimitOrder
        """
        post_url = f'http://localhost:5000/api/v1/limit_buy'
        data = {'ticker': ticker, 'price': price, 'qty': qty, 'creator': self.name, 'fee': fee}
        response = post(post_url, json=data)
        dict_response = await response.json()
        return LimitOrder(dict_response['ticker'], dict_response['qty'], dict_response['price'], dict_response['creator'], dict_response['id'])

    async def limit_sell(self, ticker:str, price:float, qty:int, fee=0.0) -> LimitOrder:
        """Creates a limit sell order for a given asset and quantity at a certain price.

        Args:
            ticker (str): the ticker of the asset
            price (float): the limit price
            qty (int): the quantity to be sold

        Returns:
            LimitOrder
        """
        post_url = f'http://localhost:5000/api/v1/limit_sell'
        data = {'ticker': ticker, 'price': price, 'qty': qty, 'creator': self.name, 'fee': fee}
        response = post(post_url, json=data)
        dict_response = await response.json()
        return LimitOrder(dict_response['ticker'], dict_response['qty'], dict_response['price'], dict_response['creator'], dict_response['id'])
    
    async def get_position(self,ticker):
        return sum(t['qty'] for t in self._transactions if t['ticker'] == ticker)

    async def get_cash_history(self):
        return pd.DataFrame(self.__cash_history).set_index('dt')

    @property
    def trades(self):
        trades = self.exchange.trades
        trades = trades[trades[['buyer','seller']].isin([self.name]).any(axis=1)]
        return trades

    async def _set_exchange(self,exchange):
        self.exchange = exchange

    async def cancel_order(self, id:str) -> Union[LimitOrder,None]:
        """Cancels the order with a given id (if it exists)

        Args:
            id (str): the id of the limit order

        Returns:
            Union[LimitOrder,None]: the cancelled order if it is still pending. None if it does not exists or has already been filled/cancelled
        """
        post_url = f'http://localhost:5000/api/v1/cancel_order'
        data = {'id': id}
        response = post(post_url, json=data)
        dict_response = await response.json()
        return LimitOrder(dict_response['ticker'], dict_response['qty'], dict_response['price'], dict_response['creator'], dict_response['id'])

    async def cancel_all_orders(self, ticker:str):
        """Cancels all remaining orders that the agent has on an asset.

        Args:
            ticker (str): the ticker of the asset.
        """
        post_url = f'http://localhost:5000/api/v1/cancel_all_orders'
        data = {'agent': self.name, 'ticker': ticker}
        response = post(post_url, json=data)
        dict_response = await response.json()
        return dict_response

    async def get_price_bars(self, ticker, bar_size='1D', limit=20):
        url = f'http://localhost:5000/api/v1/candles?ticker={ticker}&interval={bar_size}&limit={limit}'
        
        dict_response = await response.json()
        return dict_response
    
    def next(self):  
        pass
