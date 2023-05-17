from datetime import datetime
from decimal import Decimal
from .OrderSide import OrderSide
from ._utils import get_random_string

class LimitOrder():

    def __init__(self, ticker, price, qty, creator, side, dt=None):
        self.id = get_random_string()
        self.ticker: str = ticker
        self.price: Decimal = price
        self.type: OrderSide = side
        self.qty: int = qty
        self.creator: str = creator
        self.dt: datetime = dt if dt else datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'price': self.price,
            'qty': self.qty,
            'creator': self.creator,
            'dt': self.dt
        }

    def __repr__(self):
        return f'<LimitOrder: {self.ticker} {self.qty}@{self.price}>'

    def __str__(self):
        return f'<LimitOrder: {self.ticker} {self.qty}@{self.price}>'
