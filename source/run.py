from time import sleep
from datetime import datetime
from random import randint
import traceback
from multiprocessing import Process
from .Clock import Clock
from .API import API
from .Messaging import Pusher, Puller, Requester, Responder, Router, Broker
from .Requests import Requests
from .Agents import NaiveMarketMaker, RandomMarketTaker, TestAgent, LowBidder
from .Exchange import Exchange
from .utils._utils import dumps
from rich import print, inspect
from rich.live import Live
from rich.table import Table

tickers = ['XYZ']
agents = []
num_agents = 20
start_time = datetime(1700,1,1)

def run_clock():
    try:
        p = Pusher(5115)
        clock = Clock()
        while True:
            clock.tick()
            msg = p.push({"time": str(clock.dt)})
    
    except KeyboardInterrupt:
        print("attempting to close clock..." )
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
    except KeyboardInterrupt:
        print("attempting to close clock router..." )
        return None  

def run_broker(agent_channel, exchange_channel):
    try:
        broker = Broker(agent_channel, exchange_channel)
        broker.route()
        pass
    except Exception as e:
        print("[Broker Error] ", e)
        return None
    except KeyboardInterrupt:
        print("attempting to close broker..." )
        return None

def run_exchange(time_channel, exchange_channel):
    try: 
        exchange = Exchange(datetime=start_time)
        time_puller = Puller(time_channel)
        exchange.create_asset(tickers[0]) 
        responder = Responder(exchange_channel)
            
        def get_time():
            get_time = time_puller.pull()
            if get_time == None: 
                pass
            elif type(get_time) is dict and 'time' not in get_time:
                pass
            elif type(get_time['time']) is dict:
                pass
            else: 
                exchange.datetime = get_time['time']            

        def callback(msg):
            if msg['topic'] == 'create_asset': return dumps(exchange.create_asset(msg['ticker'],msg['qty'], msg['seed_price'], msg['seed_bid'], msg['seed_ask']).to_dict())
            elif msg['topic'] == 'limit_buy': return dumps(exchange.limit_buy(msg['ticker'], msg['price'], msg['qty'], msg['creator'], msg['fee']).to_dict())
            elif msg['topic'] == 'limit_sell': return dumps(exchange.limit_sell(msg['ticker'], msg['price'], msg['qty'], msg['creator'], msg['fee']).to_dict())
            elif msg['topic'] == 'market_buy': return exchange.market_buy(msg['ticker'], msg['qty'], msg['buyer'], msg['fee'])
            elif msg['topic'] == 'market_sell': return exchange.market_sell(msg['ticker'], msg['qty'], msg['seller'], msg['fee'])
            elif msg['topic'] == 'cancel_order': return exchange.cancel_order(msg['order_id'])
            elif msg['topic'] == 'cancel_all_orders': return exchange.cancel_all_orders(msg['agent'], msg['ticker'])
            elif msg['topic'] == 'candles': return exchange.get_price_bars(ticker=msg['ticker'], bar_size=msg['interval'], limit=msg['limit'])
            # elif msg['topic'] == 'mempool': return exchange.mempool(msg['limit'])
            elif msg['topic'] == 'order_book': return dumps(exchange.get_order_book(msg['ticker']).to_dict())
            elif msg['topic'] == 'latest_trade': return dumps(exchange.get_latest_trade(msg['ticker']))
            elif msg['topic'] == 'trades': return dumps(exchange.get_trades(msg['ticker']))
            elif msg['topic'] == 'quotes': return exchange.get_quotes(msg['ticker'])
            elif msg['topic'] == 'best_bid': return dumps(exchange.get_best_bid(msg['ticker']).to_dict())
            elif msg['topic'] == 'best_ask': return dumps(exchange.get_best_ask(msg['ticker']).to_dict())
            elif msg['topic'] == 'midprice': return exchange.get_midprice(msg['ticker'])
            elif msg['topic'] == 'cash': return exchange.get_cash(msg['agent'])
            elif msg['topic'] == 'assets': return exchange.get_assets(msg['agent'])
            elif msg['topic'] == 'register_agent': return exchange.register_agent(msg['name'], msg['initial_cash'])
            elif msg['topic'] == 'get_agent': return dumps(exchange.get_agent(msg['name']))
            elif msg['topic'] == 'get_agents': return dumps(exchange.get_agents())
            elif msg['topic'] == 'add_cash': return dumps(exchange.add_cash(msg['agent'], msg['amount']))
            #TODO: exchange topic to get general exchange data
            else: return f'unknown topic {msg["topic"]}'

        last_latest_trade = None
        while True:
            get_time()
            msg = responder.respond(callback)
            latest_trade =exchange.get_latest_trade('XYZ')
            if(last_latest_trade != latest_trade):
                last_latest_trade = latest_trade
                # print(latest_trade)

                # print("UnBought Supply: ", exchange.get_assets('init_seed'), "Total Cash", exchange.agents_cash())
                # print(exchange.get_order_book('XYZ').to_dict())
            if(msg == None):
                print("exchange closed") 
                break
        
    except Exception as e:
        print("[Exchange Error] ", e)
        print(traceback.print_exc())
        return None  
    except KeyboardInterrupt:
        print("attempting to close exchange..." )
        return None

def run_agent(time_channel, agent_channel):
    try:
        agent = None
        picker = randint(0,3)
        if picker == 0:
            agent =  NaiveMarketMaker(name='market_maker', tickers=tickers, aum=1_000, spread_pct=0.005, qty_per_order=4, requester=Requests(Requester(channel=agent_channel)))
        elif picker == 1:
            agent = RandomMarketTaker(name='market_taker', tickers=tickers, aum=1_000, prob_buy=.2, prob_sell=.2, qty_per_order=1, requester=Requests(Requester(channel=agent_channel)))
        else:
            agent = LowBidder(name='low_bidder', tickers=tickers, aum=1_000, requester=Requests(Requester(channel=agent_channel)))
        registered = agent.register()
        if registered is None:
            raise Exception("Agent not registered")
        while True:
            next = agent.next()
            if not next:
                break
    except Exception as e:
        print("[Agent Error] ", e)
        traceback.print_exc()
        return None
    except KeyboardInterrupt:
        print("attempting to close agent..." )
        agent.requests.requester.close()
        return None

def agent_episodes(time_channel, agent_channel):
    try:
        episodes = 1000
        maker =  NaiveMarketMaker(name='market_maker', tickers=tickers, aum=1_000, spread_pct=0.005, qty_per_order=4, requester=Requests(Requester(channel=agent_channel)))
        taker = RandomMarketTaker(name='market_taker', tickers=tickers, aum=1_000, prob_buy=.2, prob_sell=.2, qty_per_order=1, requester=Requests(Requester(channel=agent_channel)))
        maker_registered = maker.register()
        taker_registered = taker.register()
        if not maker_registered or not taker_registered:
            print('agent registration failed')
            return None
        sleep(.5)
        for i in range(0, episodes):
            maker.next()
            taker.next()
            # print(f'episode {i} complete')


        time_puller = Puller(time_channel)
        end_time = time_puller.pull()
        print("episodes complete", end_time)
        # portfolio=Portfolio(from_date=start_time)
        # mt_holdings = portfolio.get_portfolio_history('market_taker')
        # mm_holdings = portfolio.get_portfolio_history('market_maker')
    except Exception as e:
        print("[Agent Error] ", e)
        traceback.print_exc()
        return None
    except KeyboardInterrupt:
        return None

def agent_test(time_channel, agent_channel):
    try:
        requester = Requests(Requester(channel=agent_channel))
        agent = TestAgent(requester=requester)
        registered = agent.register()
        if registered is None:
            raise Exception("Agent not registered")
        agent.next()
    except KeyboardInterrupt:
        return None

def run_api(agent_channel):
    try:
        requester = Requester(agent_channel)
        api = API(requester)
        api.run()
    except Exception as e:
        print("[API Error] ", e)
        return None
    except  KeyboardInterrupt:
        print("attempting to close api..." )
        return None

def main():
    try:
        time_channel = 5114
        exchange_channel = 5570
        agent_channel = 5571

        clock_process = Process(target=run_clock)
        clock_router = Process(target=route_clock, args=(time_channel, ))
        broker_process = Process(target=run_broker, args=(agent_channel, exchange_channel ))
        exchange_process = Process(target=run_exchange, args=(time_channel, exchange_channel ))
        api_process = Process(target=run_api, args=(agent_channel,))

        clock_router.start()
        clock_process.start()
        broker_process.start()
        exchange_process.start()
        api_process.start()
        
        for i in range(0,num_agents):
            agent_process = Process(target=run_agent, args=(time_channel, agent_channel ))
            agents.append(agent_process)
            agent_process.start()

        while True:
            sleep(.1)

    except KeyboardInterrupt:
        print("attempting to close processes..." )
        clock_process.terminate()
        clock_router.terminate()
        exchange_process.terminate()
        api_process.terminate()
        broker_process.terminate()
        clock_process.join()
        clock_router.join()
        exchange_process.join()
        api_process.join()
        broker_process.join()

        while True:
            if(len(agents) == 0): break
            for agent in agents:
                print(f"waiting for {len(agents)} agents to close...")
                print(f"closing agent {agent.name}")
                agent.join()
                agents.remove(agent) 
            sleep(.1)

        print("processes successfully closed")

    finally:
        exit(0)