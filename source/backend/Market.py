import pandas as pd
from typing import List
from .OrderBook import OrderBook
from .Trade import Trade
from .LimitOrder import LimitOrder
from .OrderSide import OrderSide

class Market():
    def __init__(self, datetime= None):
        self.datetime = datetime
        self.books = {}
        self.trades = None
        self.trades_log: List[Trade] = []

    def __str__(self):
        return ', '.join(ob for ob in self.books)

    def run(self):
        market = {}
        for ticker in self.books:
            market[ticker]["books"] = self.get_order_book(ticker)
            market[ticker]["latest_trade"] = self.get_latest_trade(ticker)
            market[ticker]["quotes"] = self.get_quotes(ticker)
            market[ticker]["best_bid"] = self.get_best_bid(ticker)
            market[ticker]["best_ask"] = self.get_best_ask(ticker)
            market[ticker]["midprice"] = self.get_midprice(ticker)
        return market

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
        return next(trade for trade in self.trade_log[::-1] if trade.ticker == ticker)

    def get_quotes(self, ticker):
        try:
            # TODO: if more than one order has the best price, add the quantities.
            # TODO: check if corresponding quotes exist in order to avoid exceptions
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

    def get_best_bid(self, ticker:str) -> LimitOrder:
        """retrieves the current best bid in the orderbook of an asset

        Args:
            ticker (str): the ticker of the asset.

        Returns:
            LimitOrder
        """
        if self.books[ticker].bids:
            return self.books[ticker].bids[0]

    def get_best_ask(self, ticker:str) -> LimitOrder:
        """retrieves the current best ask in the orderbook of an asset

        Args:
            ticker (str): the ticker of the asset.

        Returns:
            LimitOrder
        """
        if self.books[ticker].asks:
            return self.books[ticker].asks[0]

    def get_midprice(self, ticker:str) -> float:
        """Returns the current midprice of the best bid and ask quotes.

        Args:
            ticker (str): the ticker of the asset

        Returns:
            float: the current midprice
        """
        quotes = self.get_quotes(ticker)
        return (quotes['bid_p'] + quotes['ask_p']) / 2

    def get_trades(self, ticker:str, limit=20) -> pd.DataFrame:
        """Retrieves all past trades of a given asset

        Args:
            ticker (str): the ticker of the asset

        Returns:
            pd.DataFrame: a dataframe containing all trades
        """
        return pd.DataFrame.from_records([t.to_dict() for t in self.trade_log if t.ticker == ticker]).set_index('dt').sort_index().head(limit)
    
    def get_price_bars(self, ticker, limit=20, bar_size='1D'):
        trades = self.trades
        trades = trades[trades['ticker']== ticker]
        df = trades.resample(bar_size).agg({'price': 'ohlc', 'qty': 'sum'})
        df.columns = df.columns.droplevel()
        df.rename(columns={'qty':'volume'},inplace=True)
        return df.head(limit)
    