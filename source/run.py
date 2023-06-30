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
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

tickers = ['XYZ']
agents = []
num_agents = 1

start_time = datetime(1700,1,1)

async def run_exchange(exchange_channel = 5570):
    try: 
        exchange = Exchange(datetime=start_time)
        await exchange.create_asset(tickers[0]) 
        responder = Responder(exchange_channel)

        await responder.connect()

        async def get_time():
            clock = Clock()
            get_time = clock.tick()
            if get_time == None: 
                return None
            elif not isinstance(get_time, datetime):
                return None
            else: 
                exchange.datetime = get_time          
                return get_time

        async def callback(msg):
            if msg['topic'] == 'create_asset': return await dumps(exchange.create_asset(msg['ticker'],msg['qty'], msg['seed_price'], msg['seed_bid'], msg['seed_ask']).to_dict())
            elif msg['topic'] == 'limit_buy': return await dumps(exchange.limit_buy(msg['ticker'], msg['price'], msg['qty'], msg['creator'], msg['fee']).to_dict())
            elif msg['topic'] == 'limit_sell': return await dumps(exchange.limit_sell(msg['ticker'], msg['price'], msg['qty'], msg['creator'], msg['fee']).to_dict())
            elif msg['topic'] == 'market_buy': return await exchange.market_buy(msg['ticker'], msg['qty'], msg['buyer'], msg['fee'])
            elif msg['topic'] == 'market_sell': return await exchange.market_sell(msg['ticker'], msg['qty'], msg['seller'], msg['fee'])
            elif msg['topic'] == 'cancel_order': return await exchange.cancel_order(msg['order_id'])
            elif msg['topic'] == 'cancel_all_orders': return await exchange.cancel_all_orders(msg['agent'], msg['ticker'])
            elif msg['topic'] == 'candles': return await exchange.get_price_bars(ticker=msg['ticker'], bar_size=msg['interval'], limit=msg['limit'])
            # elif msg['topic'] == 'mempool': return await exchange.mempool(msg['limit'])
            elif msg['topic'] == 'order_book': return await dumps(exchange.get_order_book(msg['ticker']).to_dict())
            elif msg['topic'] == 'latest_trade': return await dumps(exchange.get_latest_trade(msg['ticker']))
            elif msg['topic'] == 'trades': return await dumps(exchange.get_trades(msg['ticker']))
            elif msg['topic'] == 'quotes': return await exchange.get_quotes(msg['ticker'])
            elif msg['topic'] == 'best_bid': return await dumps(exchange.get_best_bid(msg['ticker']).to_dict())
            elif msg['topic'] == 'best_ask': return await dumps(exchange.get_best_ask(msg['ticker']).to_dict())
            elif msg['topic'] == 'midprice': return await exchange.get_midprice(msg['ticker'])
            elif msg['topic'] == 'cash': return await exchange.get_cash(msg['agent'])
            elif msg['topic'] == 'assets': return await exchange.get_assets(msg['agent'])
            elif msg['topic'] == 'register_agent': return await exchange.register_agent(msg['name'], msg['initial_cash'])
            elif msg['topic'] == 'get_agent': return await dumps(exchange.get_agent(msg['name']))
            elif msg['topic'] == 'get_agents': return await dumps(exchange.get_agents())
            elif msg['topic'] == 'add_cash': return await dumps(exchange.add_cash(msg['agent'], msg['amount']))
            #TODO: exchange topic to get general exchange data
            else: return f'unknown topic {msg["topic"]}'

        last_latest_trade = None
        while True:
            await get_time()
            print (exchange.datetime)
            msg = await responder.respond(callback)
            if msg == None:
                continue
            latest_trade = await exchange.get_latest_trade('XYZ')
            if(last_latest_trade != latest_trade):
                last_latest_trade = latest_trade
                print(latest_trade)

                # print("UnBought Supply: ", exchange.get_assets('run_seed'), "Total Cash", exchange.agents_cash())
                # print(exchange.get_order_book('XYZ').to_dict())
    except Exception as e:
        print("[Exchange Error] ", e)
        print(traceback.print_exc())
        return None  
    except KeyboardInterrupt:
        print("attempting to close exchange..." )
        return None

async def run_agent(exchange_channel = 5570):
    try:
        print("running agent")
        agent = None
        picker = randint(0,3)
        requester = Requester(channel=exchange_channel)
        await requester.connect()
        print(f"Agent {picker} connected")
        if picker == 0:
            agent =  NaiveMarketMaker(name='market_maker', tickers=tickers, aum=1_000, spread_pct=0.005, qty_per_order=4, requester=Requests(requester))
        elif picker == 1:
            agent = RandomMarketTaker(name='market_taker', tickers=tickers, aum=1_000, prob_buy=.2, prob_sell=.2, qty_per_order=1, requester=Requests(requester))
        else:
            agent = LowBidder(name='low_bidder', tickers=tickers, aum=1_000, requester=Requests(requester))
        registered = await agent.register()
        if registered is None:
            raise Exception("Agent not registered")
        while True:
            next = await agent.next()
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

async def run_api(exchange_channel = 5570):
    try:
        requester = Requester(exchange_channel)
        await requester.connect()
        api = API(requester)
        api.run()
    except Exception as e:
        print("[API Error] ", e)
        return None
    except  KeyboardInterrupt:
        print("attempting to close api..." )
        return None

async def main():
    try:
        exchange_process = Process(target=asyncio.run, args=(run_exchange(), ))


        exchange_process.start()

        
        for i in range(0,num_agents):
            print(f"starting agent {i}")
            agent_process = Process(target=asyncio.run, args=(run_agent(), ))
            agents.append(agent_process)
            agent_process.start()

        while True:
            sleep(.1)

    except KeyboardInterrupt:
        print("attempting to close processes..." )
        exchange_process.terminate()

        exchange_process.join()


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
