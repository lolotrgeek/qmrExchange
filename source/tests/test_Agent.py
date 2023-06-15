import unittest
from unittest.mock import MagicMock
from datetime import datetime
import pandas as pd
from ..Agent import Agent, Exchange, Trade, LimitOrder

class TestAgent(unittest.TestCase):
    def setUp(self):
        self.agent_name = "TestAgent"
        self.tickers = ["AAPL", "GOOGL", "MSFT"]
        self.aum = 10000
        self.agent = Agent(self.agent_name, self.tickers, self.aum)
        self.exchange = MagicMock(spec=Exchange)
        self.agent._set_exchange(self.exchange)

    def test_init(self):
        self.assertEqual(self.agent.name, self.agent_name)
        self.assertIsInstance(self.agent.id, str)
        self.assertEqual(self.agent.tickers, self.tickers)
        self.assertIsNone(self.agent.exchange)
        self.assertEqual(self.agent.cash, self.aum)
        self.assertEqual(self.agent.initial_cash, self.aum)
        self.assertListEqual(self.agent._transactions, [])

    def test_get_latest_trade(self):
        ticker = "AAPL"
        latest_trade = Trade(...)
        self.exchange.get_latest_trade.return_value = latest_trade
        result = self.agent.get_latest_trade(ticker)
        self.assertEqual(result, latest_trade)
        self.exchange.get_latest_trade.assert_called_once_with(ticker)

    def test_get_best_bid(self):
        ticker = "AAPL"
        best_bid = LimitOrder(...)
        self.exchange.get_best_bid.return_value = best_bid
        result = self.agent.get_best_bid(ticker)
        self.assertEqual(result, best_bid)
        self.exchange.get_best_bid.assert_called_once_with(ticker)

    # Add more test methods for the other methods in the Agent class

if __name__ == '__main__':
    unittest.main()
