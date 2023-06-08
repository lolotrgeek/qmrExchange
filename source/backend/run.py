
from .Agents import NaiveMarketMaker, RandomMarketTaker
from .Exchange import Exchange
from time import sleep
from multiprocessing import Process
from .Clock import Clock
from .API import API
from .Market import Market
from .Messaging import Pusher, Puller, Responder, Router
from .Requests import Requests
from .Responses import Responses
from .Portfolio import Portfolio
from datetime import datetime
from random import randint
from ._utils import dumps, format_dataframe_rows_to_dict

tickers = ['XYZ']
agents = []
num_agents = 1
start_time = datetime(1700,1,1)

def run_clock():
    try:
        p = Pusher(5115)
        clock = Clock()
        while True:
            clock.tick()
            msg = p.push({"time": str(clock.dt)})
    
    except KeyboardInterrupt:
        return

def get_clock(time_channel):
    try:
        s = Puller(time_channel)
        sleep(.5)
        while True:
            msg = s.pull()
            # print(msg)
    except Exception as e:
        print(e)
        return None

def route_clock(time_channel):
    try:
        r = Router(5115, time_channel )
        r.route()
    except Exception as e:
        print(e)
        return None  

def run_exchange(time_channel, exchange_channel):
    try: 
        exchange = Exchange(datetime=start_time)
        time_puller = Puller(time_channel)
        exchange.datetime = time_puller.pull()
        exchange.create_asset(tickers[0])
        exchange_listener = Responder(exchange_channel)
        responses = Responses(exchange, exchange_listener)

        while True:
            # listen for orders and cancellations here on the exchange channel...
            # when a message is received, call the appropriate exchange method
            exchange.datetime = time_puller.pull()
            responses.listen()
            pass
    except Exception as e:
        print(e)
        return None  


def run_agent(time_channel, exchange_channel):
    try:
        agent = None
        if randint(0,1) == 0:
            agent =  NaiveMarketMaker(name='market_maker', tickers=tickers, aum=1_000, spread_pct=0.005, qty_per_order=4, requester=Requests(exchange_channel, market_channel, candle_channel, trades_channel))
        else:
            agent = RandomMarketTaker(name='market_taker', tickers=tickers, aum=1_000, prob_buy=.2, prob_sell=.2, qty_per_order=1, requester=Requests(exchange_channel, market_channel, candle_channel, trades_channel) )

        while True:
            agent.next()
    except Exception as e:
        print(e)
        return None

def agent_episodes(time_channel, exchange_channel):
    try:
        episodes = 1000
        maker =  NaiveMarketMaker(name='market_maker', tickers=tickers, aum=1_000, spread_pct=0.005, qty_per_order=4, requester=Requests(exchange_channel))
        taker = RandomMarketTaker(name='market_taker', tickers=tickers, aum=1_000, prob_buy=.2, prob_sell=.2, qty_per_order=1, requester=Requests(exchange_channel) )
        for i in range(0, episodes):
            maker.next()
            taker.next()
            print(f'episode {i} complete')

        time_puller = Puller(time_channel)
        end_time = time_puller.pull()
        # portfolio=Portfolio(from_date=start_time)


        # mt_holdings = portfolio.get_portfolio_history('market_taker')
        # mm_holdings = portfolio.get_portfolio_history('market_maker')
    except Exception as e:
        print(e)
        return None

def main():
    try:
        time_channel = 5114
        exchange_channel = 5570

        clock_process = Process(target=run_clock)
        clock_router = Process(target=route_clock, args=(time_channel, ))
        clock_getter = Process(target=get_clock, args=(time_channel, ))
        exchange_process = Process(target=run_exchange, args=(time_channel, exchange_channel ))

        clock_router.start()
        clock_process.start()
        clock_getter.start()
        exchange_process.start()

        for i in range(0,num_agents):
            agent_process = Process(target=agent_episodes, args=(time_channel, exchange_channel ))
            agent_process.start()

        while True:
            sleep(.1)

    except KeyboardInterrupt:
        print("attempting to close processes..." )
        for agent in agents:
            agent.terminate()
            agent.join()
        clock_process.terminate()
        clock_router.terminate()
        clock_getter.terminate()
        exchange_process.terminate()
        clock_process.join()
        exchange_process.join()

        print("processes successfully closed")

    finally:
        exit(0)