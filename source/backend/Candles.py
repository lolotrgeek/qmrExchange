    def get_price_bars(self, ticker, limit=20, bar_size='1D'):
        trades = self.trades
        trades = trades[trades['ticker']== ticker]
        df = trades.resample(bar_size).agg({'price': 'ohlc', 'qty': 'sum'})
        df.columns = df.columns.droplevel()
        df.rename(columns={'qty':'volume'},inplace=True)
        return df.head(limit)