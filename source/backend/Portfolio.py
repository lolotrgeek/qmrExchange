from .utils._utils import get_datetime_range, get_pandas_time
import pandas as pd
from datetime import datetime, timedelta

class Portfolio():
    def __init__(self, from_date=None, end_time=None) -> None:
        self._time_unit = 'day'
        self._from_date = from_date
        self._end_time = end_time
        pass       
        
    def get_portfolio_history(self, agent):
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