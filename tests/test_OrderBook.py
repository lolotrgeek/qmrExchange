import unittest
import pandas as pd
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from source.types.LimitOrder import LimitOrder
from source.types.OrderBook import OrderBook

class OrderBookTests(unittest.TestCase):

    def setUp(self):
        self.order_book = OrderBook("AAPL")

    def test_order_book_ticker(self):
        self.assertEqual(self.order_book.ticker, "AAPL")

    def test_order_book_repr(self):
        expected_repr = "<OrderBook: AAPL>"
        self.assertEqual(repr(self.order_book), expected_repr)

    def test_order_book_str(self):
        expected_str = "<OrderBook: AAPL>"
        self.assertEqual(str(self.order_book), expected_str)

    def test_order_book_df(self):
        self.order_book.bids = [
            LimitOrder("AAPL", 100, 150.0),
            LimitOrder("AAPL", 200, 140.0)
        ]
        self.order_book.asks = [
            LimitOrder("AAPL", 50, 160.0),
            LimitOrder("AAPL", 75, 170.0)
        ]
        expected_df = {
            'bids': pd.DataFrame({
                'ticker': ['AAPL', 'AAPL'],
                'qty': [100, 200],
                'price': [150.0, 140.0]
            }),
            'asks': pd.DataFrame({
                'ticker': ['AAPL', 'AAPL'],
                'qty': [50, 75],
                'price': [160.0, 170.0]
            })
        }
        self.assertEqual(self.order_book.df, expected_df)

    def test_order_book_to_dict(self):
        self.order_book.bids = [
            LimitOrder("AAPL", 100, 150.0),
            LimitOrder("AAPL", 200, 140.0)
        ]
        self.order_book.asks = [
            LimitOrder("AAPL", 50, 160.0),
            LimitOrder("AAPL", 75, 170.0)
        ]
        expected_dict = {
            "bids": [
                {'ticker': 'AAPL', 'qty': 100, 'price': 150.0},
                {'ticker': 'AAPL', 'qty': 200, 'price': 140.0}
            ],
            "asks": [
                {'ticker': 'AAPL', 'qty': 50, 'price': 160.0},
                {'ticker': 'AAPL', 'qty': 75, 'price': 170.0}
            ]
        }
        self.assertEqual(self.order_book.to_dict(), expected_dict)

if __name__ == '__main__':
    unittest.main()
