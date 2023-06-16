import unittest
from datetime import datetime
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from source.Exchange import Exchange
from source.types.LimitOrder import LimitOrder
from source.types.OrderSide import OrderSide

class ExchangeTestCase(unittest.TestCase):
    def setUp(self):
        self.exchange = Exchange(datetime=datetime(2023, 1, 1))
        self.exchange.create_asset("AAPL", seed_price=150, seed_bid=0.99, seed_ask=1.01)
    
    def tearDown(self):
        self.exchange = None

    def test_create_asset(self):
        asset = self.exchange.create_asset("BTC", seed_price=50000)
        self.assertEqual(asset.ticker, "BTC")
        self.assertEqual(asset.bids[0].price, 49500)
        self.assertEqual(asset.asks[0].price, 50500)

    def test_get_order_book(self):
        order_book = self.exchange.get_order_book("AAPL")
        self.assertEqual(order_book.ticker, "AAPL")
        self.assertEqual(len(order_book.bids), 1)
        self.assertEqual(len(order_book.asks), 1)

    def test_cancel_order(self):
        # self.exchange.books["AAPL"].bids.clear()
        order = self.exchange.limit_buy("AAPL", price=149, qty=2, creator="buyer1")
        self.assertEqual(len(self.exchange.books["AAPL"].bids), 2)
        self.exchange.cancel_order(order.id)
        self.assertEqual(len(self.exchange.books["AAPL"].bids), 1)
        self.assertEqual(self.exchange.get_order(order.id), None)

    def test_get_latest_trade(self):
        latest_trade = self.exchange.get_latest_trade("AAPL")
        self.assertEqual(latest_trade["ticker"], "AAPL")
        self.assertEqual(latest_trade["price"], 150)
        self.assertEqual(latest_trade["buyer"], "init_seed")
        self.assertEqual(latest_trade["seller"], "init_seed")

    def test_get_quotes(self):
        quotes = self.exchange.get_quotes("AAPL")
        self.assertEqual(quotes["ticker"], "AAPL")
        self.assertEqual(quotes["bid_qty"], 1)
        self.assertEqual(quotes["bid_p"], 148.5)
        self.assertEqual(quotes["ask_qty"], 1)
        self.assertEqual(quotes["ask_p"], 151.5)

    def test_get_midprice(self):
        midprice = self.exchange.get_midprice("AAPL")
        self.assertEqual(midprice["midprice"], 150)

    def test_get_trades(self):
        trades = self.exchange.get_trades("AAPL", limit=10)
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0]["ticker"], "AAPL")

    def test_get_price_bars(self):
        price_bars = self.exchange.get_price_bars("AAPL", limit=10)
        self.assertEqual(len(price_bars), 1)
        self.assertEqual(price_bars[0], {'open': 150, 'high': 150, 'low': 150, 'close': 150, 'volume': 1, 'dt': '01/01/2023, 00:00:00'})

    def test_get_best_ask(self):
        best_ask = self.exchange.get_best_ask("AAPL")
        self.assertIsInstance(best_ask, LimitOrder)
        self.assertEqual(best_ask.type, OrderSide.SELL)

    def test_get_best_bid(self):
        best_bid = self.exchange.get_best_bid("AAPL")
        self.assertIsInstance(best_bid, LimitOrder)
        self.assertEqual(best_bid.type, OrderSide.BUY)

    def test_limit_buy(self):
        order = self.exchange.limit_buy("AAPL", price=149, qty=2, creator="buyer1")
        self.assertIsInstance(order, LimitOrder)
        self.assertEqual(order.type, OrderSide.BUY)
        self.assertEqual(order.price, 149)
        self.assertEqual(order.qty, 2)

    def test_limit_sell(self):
        order = self.exchange.limit_sell("AAPL", price=151, qty=3, creator="seller1")
        self.assertIsInstance(order, LimitOrder)
        self.assertEqual(order.type, OrderSide.SELL)
        self.assertEqual(order.price, 151)
        self.assertEqual(order.qty, 3)
        
    def test_get_order(self):
        self.exchange.limit_buy("AAPL", price=150, qty=2, creator="buyer1")
        self.exchange.limit_sell("AAPL", price=155, qty=3, creator="seller1")

        order_id = self.exchange.books["AAPL"].bids[0].id
        result = self.exchange.get_order(order_id)
        expected = [0, self.exchange.books["AAPL"].bids[0]]

        self.assertEqual(result, expected)

        order_id = "invalid_id"
        result = self.exchange.get_order(order_id)

        self.assertIsNone(result)
        

def test_cancel_all_orders(self):
    self.exchange.limit_buy("AAPL", price=150, qty=2, creator="buyer1")
    self.exchange.limit_sell("AAPL", price=155, qty=3, creator="seller1")
    self.exchange.limit_buy("AAPL", price=152, qty=1, creator="buyer2")
    self.exchange.limit_sell("AAPL", price=160, qty=4, creator="seller2")

    self.assertEqual(len(self.exchange.books["AAPL"].bids), 2)
    self.assertEqual(len(self.exchange.books["AAPL"].asks), 2)

    self.exchange.cancel_all_orders("buyer1", "AAPL")

    self.assertEqual(len(self.exchange.books["AAPL"].bids), 1)
    self.assertEqual(len(self.exchange.books["AAPL"].asks), 2)

def test_market_buy(self):
    self.exchange.limit_sell("AAPL", price=155, qty=3, creator="seller1")
    self.exchange.limit_sell("AAPL", price=160, qty=2, creator="seller2")

    result = self.exchange.market_buy("AAPL", qty=4, buyer="buyer1", fee=0.01)

    self.assertEqual(result, {"market_buy": "AAPL"})
    self.assertEqual(len(self.exchange.books["AAPL"].asks), 1)
    self.assertEqual(self.exchange.books["AAPL"].asks[0].qty, 1)

def test_market_sell(self):
    self.exchange.limit_buy("AAPL", price=150, qty=2, creator="buyer1")
    self.exchange.limit_buy("AAPL", price=152, qty=1, creator="buyer2")

    result = self.exchange.market_sell("AAPL", qty=3, seller="seller1", fee=0.02)

    self.assertEqual(result, {"market_sell": "AAPL"})
    self.assertEqual(len(self.exchange.books["AAPL"].bids), 1)
    self.assertEqual(self.exchange.books["AAPL"].bids[0].qty, 0)

def test_trades(self):
    self.exchange.limit_buy("AAPL", price=150, qty=2, creator="buyer1")
    self.exchange.limit_sell("AAPL", price=155, qty=3, creator="seller1")
    self.exchange.limit_buy("AAPL", price=152, qty=1, creator="buyer2")

    trades = self.exchange.trades

    self.assertEqual(len(trades), 3)
    self.assertIn("buyer1", trades['buyer'])
    self.assertIn("seller1", trades['seller'])
    self.assertIn("buyer2", trades['buyer'])

def test_register_agent(self):
    result = self.exchange.register_agent("agent1", initial_cash=10000)

    self.assertEqual(result, {"registered_agent": "agent1"})
    self.assertEqual(len(self.exchange.agents), 1)
    self.assertEqual(self.exchange.agents[0]['name'], "agent1")
    self.assertEqual(self.exchange.agents[0]['cash'], 10000)
    self.assertEqual(len(self.exchange.agents[0]['_transactions']), 0)

def test_get_cash(self):
    self.exchange.register_agent("agent1", initial_cash=10000)

    result = self.exchange.get_cash("agent1")

    self.assertEqual(result, {"cash": 10000})

def test_get_assets(self):
    self.exchange.register_agent("agent1", initial_cash=10000)
    self.exchange.limit_buy("AAPL", price=150, qty=2, creator="agent1")
    self.exchange.limit_sell("AAPL", price=155, qty=3, creator="agent1")

    result = self.exchange.get_assets("agent1")

    self.assertEqual(result, {"assets": [{'dt': self.exchange.datetime, 'cash_flow': -300, 'ticker': 'AAPL', 'qty': 2},
                                          {'dt': self.exchange.datetime, 'cash_flow': 465, 'ticker': 'AAPL', 'qty': 3}]})

def test_get_agent(self):
    self.exchange.register_agent("agent1", initial_cash=10000)

    result = self.exchange.get_agent("agent1")

    self.assertEqual(result, {'name': 'agent1', 'cash': 10000, '_transactions': []})

def test_get_agent_index(self):
    self.exchange.register_agent("agent1", initial_cash=10000)
    self.exchange.register_agent("agent2", initial_cash=20000)

    index = self.exchange._Exchange__get_agent_index("agent2")

    self.assertEqual(index, 1)


if __name__ == '__main__':
    unittest.main()

