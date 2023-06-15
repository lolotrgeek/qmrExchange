import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

import unittest
from unittest.mock import MagicMock
from source.Requests import Requests

class MockRequester:
    def request(self, message):
        return '{"key": "value"}'

class RequestsTests(unittest.TestCase):

    def setUp(self):
        self.mock_requester = MockRequester()
        self.requests = Requests(self.mock_requester)

    def test_make_request_returns_dict(self):
        topic = 'candles'
        message = {'ticker': 'BTC', 'interval': '1h', 'limit': 10}
        factory = self.mock_requester

        result = self.requests.make_request(topic, message, factory)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_get_price_bars(self):
        ticker = 'BTC'
        interval = '1h'
        limit = 10

        result = self.requests.get_price_bars(ticker, interval, limit)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_create_asset(self):
        ticker = 'BTC'
        seed_price = 10000
        seed_bid = 9900
        seed_ask = 10100

        result = self.requests.create_asset(ticker, seed_price, seed_bid, seed_ask)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_get_mempool(self):
        limit = 100

        result = self.requests.get_mempool(limit)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_get_order_book(self):
        ticker = 'BTC'

        result = self.requests.get_order_book(ticker)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_get_latest_trade(self):
        ticker = 'BTC'

        result = self.requests.get_latest_trade(ticker)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_get_trades(self):
        ticker = 'BTC'
        limit = 10

        result = self.requests.get_trades(ticker, limit)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_get_quotes(self):
        ticker = 'BTC'

        result = self.requests.get_quotes(ticker)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_get_best_bid(self):
        ticker = 'BTC'

        result = self.requests.get_best_bid(ticker)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_get_best_ask(self):
        ticker = 'BTC'

        result = self.requests.get_best_ask(ticker)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_get_midprice(self):
        ticker = 'BTC'

        result = self.requests.get_midprice(ticker)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_limit_buy(self):
        ticker = 'BTC'
        price = 10000
        quantity = 0.1
        creator = 'user1'
        fee = 0.001

        result = self.requests.limit_buy(ticker, price, quantity, creator, fee)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_limit_sell(self):
        ticker = 'BTC'
        price = 10000
        quantity = 0.1
        creator = 'user1'
        fee = 0.001

        result = self.requests.limit_sell(ticker, price, quantity, creator, fee)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_cancel_order(self):
        order_id = '12345'

        result = self.requests.cancel_order(order_id)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_cancel_all_orders(self):
        ticker = 'BTC'
        agent = 'user1'

        result = self.requests.cancel_all_orders(ticker, agent)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_market_buy(self):
        ticker = 'BTC'
        quantity = 0.1
        creator = 'user1'
        fee = 0.001

        result = self.requests.market_buy(ticker, quantity, creator, fee)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_market_sell(self):
        ticker = 'BTC'
        quantity = 0.1
        creator = 'user1'
        fee = 0.001

        result = self.requests.market_sell(ticker, quantity, creator, fee)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_get_cash(self):
        agent = 'user1'

        result = self.requests.get_cash(agent)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_get_assets(self):
        agent = 'user1'

        result = self.requests.get_assets(agent)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

    def test_register_agent(self):
        name = 'agent1'
        initial_cash = 10000

        result = self.requests.register_agent(name, initial_cash)

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'key': 'value'})

if __name__ == '__main__':
    unittest.main()