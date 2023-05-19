import pandas as pd
from datetime import datetime
from .Exchange import Exchange
from .Agent import Agent
from ._utils import get_datetime_range, get_timedelta, get_pandas_time

class Simulator():
    def __init__(self, from_date=datetime(2022,1,1), time_unit='day', episodes=0):
        self.timeDelta = get_timedelta(time_unit)
        self.dt = from_date
        self.agents = []
        self.exchange = Exchange(datetime=from_date)
        self._from_date = from_date
        self._time_unit = time_unit
        self._episodes = episodes
        self.episode = 0
    
    def update_datetime(self):
        self.dt +=self.timeDelta
        self.exchange._set_datetime(self.dt)

    def add_agent(self,agent:Agent):
        # TODO: check that no existing agent already has the same name
        agent._set_exchange(self.exchange)
        self.agents.append(agent) 

    def next(self):
        try:
            if(self._episodes > 0 and self.episode >= self._episodes):
                return False
            if(type(self.dt) is str):
                print(f'dt is str')
                return False
            self.update_datetime()
            if(self.exchange.crypto):
                self.exchange.blockchain.process_transactions(self.dt)
            for agent in self.agents:
                agent.next()
            self.__update_agents_cash()
            if(self._episodes > 0):
                self.episode += 1
            return True
        except KeyboardInterrupt:
            return False
        
    def run(self, run_event=None):
        if(run_event == None):
            while True:
                if not self.next():
                    break
        else:
            while True and run_event.is_set():
                if not self.next():
                    break

    def get_price_bars(self, ticker, bar_size='1D'):
        return self.exchange.get_price_bars(ticker, bar_size)

    def get_portfolio_history(self, agent):
        agent = self.get_agent(agent)
        bar_size = get_pandas_time(self._time_unit)
        portfolio = pd.DataFrame(index=get_datetime_range(
            self._from_date, self.dt, self._time_unit))
        transactions = pd.DataFrame(agent._transactions).set_index('dt')
        for ticker in list(self.exchange.books.keys()):
            qty_asset = pd.DataFrame(
                transactions[transactions['ticker'] == ticker]['qty'])
            qty_asset = qty_asset.resample(bar_size).agg('sum').cumsum()
            price = pd.DataFrame(index=get_datetime_range(
                self._from_date, self.dt, self._time_unit))
            price = price.join(self.get_price_bars(
                ticker=ticker, bar_size=bar_size)['close']).ffill()
            price = price.join(qty_asset).ffill()
            portfolio[ticker] = (price['close'] * price['qty'])
        portfolio['cash'] = transactions['cash_flow'].resample(
            bar_size).agg('sum').ffill()
        portfolio.fillna(0, inplace=True)
        portfolio['cash'] = portfolio['cash'].cumsum()
        portfolio['aum'] = portfolio.sum(axis=1)
        return portfolio

    @property
    def trades(self):
        return self.exchange.trades
    
    @property
    def transactions(self):
        return self.exchange.blockchain.transactions

    # TODO: have cash update at the moment of the transaction
    def __update_agents_cash(self):
        for update in self.exchange.agents_cash_updates:
            agent_idx = self.__get_agent_index(update['agent'])
            # Check if not None because initial seed is not an agent
            if agent_idx is not None:
                self.agents[agent_idx].cash += update['cash_flow']
                self.agents[agent_idx]._transactions.append({'dt':self.dt,'cash_flow':update['cash_flow'],'ticker':update['ticker'],'qty':update['qty']})
        self.exchange.agents_cash_updates = []
        # look for confirmed transactions in the MemPool and update the agents' cash
        for transaction in self.exchange.blockchain.chain:
            if transaction.confirmed:
                buyer_idx = self.__get_agent_index(transaction.recipient)
                seller_idx = self.__get_agent_index(transaction.sender)
                if(buyer_idx is None or seller_idx is None):
                    continue
                buyer = self.agents[buyer_idx]
                seller = self.agents[seller_idx]
                buyer.cash -= transaction.amount + transaction.fee
                seller.cash += transaction.amount
                buyer._transactions.append({'dt':self.dt,'cash_flow':-(transaction.amount+transaction.fee),'ticker':transaction.ticker,'qty':transaction.amount})
                seller._transactions.append({'dt':self.dt,'cash_flow':transaction.amount,'ticker':transaction.ticker,'qty':transaction.amount})

    def get_agent(self, agent_name):
        return next((d for (index, d) in enumerate(self.agents) if d.name == agent_name), None)

    def __get_agent_index(self,agent_name):
        return next((index for (index, d) in enumerate(self.agents) if d.name == agent_name), None)