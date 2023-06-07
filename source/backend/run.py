
from .Agents import NaiveMarketMaker, RandomMarketTaker
from .Exchange import Exchange
import time
from multiprocessing import Process
from .Clock import Clock
from .API import API
from .Market import Market
from .Messaging import Pusher, Puller, Responder, Router
from .Requests import Requests
from random import randint
from .helpers import dumps

tickers = ['XYZ']
agents = []
num_agents = 5

def run_clock(time_channel):
    clock = Clock()
    time_pusher = Pusher(time_channel)
    while True:
        clock.tick()
        time_pusher.push(dumps(clock.dt))

def get_time(time_channel):
    '''
    call this to get the current simulation time, good for timestamps
    '''
    time_puller = Puller(time_channel)
    return time_puller.pull()

def route_exchange(exchange_producer, exchange_consumer):
    router = Router(exchange_producer, exchange_consumer)
    router.route()

def run_exchange(time_channel, exchange_producer, order_channel):
    exchange = Exchange()
    exchange.datetime = get_time(time_channel)
    exchange.create_asset(tickers[0])
    order_listen = Responder(order_channel)
    books_trades = Pusher(exchange_producer)

    while True:
        # listen for orders and cancellations here on the exchange channel...
        # when a message is received, call the appropriate exchange method
        exchange.datetime = get_time(time_channel)
        books_trades.push({"books": exchange.books, "trades": exchange.trades, "trade_log": exchange.trade_log})
        order_listen.respond('limit_buy', exchange.limit_buy)
        order_listen.respond('limit_sell', exchange.limit_sell)
        order_listen.respond('cancel_order', exchange.cancel_order)
        order_listen.respond('cancel_all_orders', exchange.cancel_all_orders)
        order_listen.respond('market_buy', exchange.market_buy)
        order_listen.respond('market_sell', exchange.market_sell)
        order_listen.respond('get_cash', exchange.get_cash)
        order_listen.respond('get_assets', exchange.get_assets)
        order_listen.respond('get_transactions', exchange.get_transactions)
        order_listen.respond('register_agent', exchange.register_agent)
        pass

def run_market(time_channel, market_channel, exchange_consumer, candle_channel, trades_channel ):
    market = Market()
    exchange_puller = Puller(exchange_consumer)
    market_pusher = Pusher(market_channel)

    while True:
        market.datetime = get_time(time_channel)
        exchange_data = exchange_puller.pull()
        if exchange_data:
            market.books = exchange_data['books']
            market.trades = exchange_data['trades']
            market.trades_log = exchange_data['trade_log']

        market_data = market.run()
        market_pusher.push(market_data)

        candle_responder = Responder(candle_channel)
        candle_responder.respond('candles', market.get_price_bars)

        trades_responder = Responder(trades_channel)
        trades_responder.respond('trades', market.get_trades)

def run_agent(market_channel, candle_channel, trades_channel, order_channel):
    agent = None
    if randint(0,1) == 0:
        agent =  NaiveMarketMaker(name='market_maker',  tickers=tickers, aum=1_000, spread_pct=0.005, qty_per_order=4, seed=42, requester=Requests(order_channel, market_channel, candle_channel, trades_channel) )
    else:
        agent = RandomMarketTaker(name='market_taker', tickers=tickers, aum=1_000, prob_buy=.2, prob_sell=.2, qty_per_order=1,seed=42, requester=Requests(order_channel, market_channel, candle_channel, trades_channel) )

    while True:
        agent.next()

def main():

    time_channel = 51143
    order_channel = 55570
    exchange_producer = 55550
    exchange_consumer = 55551
    market_channel = 55560
    candle_channel = 55561
    trades_channel = 55562

    clock_process = Process(target=run_clock, args=(time_channel, ))
    exchange_router = Process(target=route_exchange, args=(exchange_producer, exchange_consumer ))
    exchange_process = Process(target=run_exchange, args=(time_channel, exchange_producer, order_channel ))
    market_process = Process(target=run_market, args=(time_channel, market_channel, exchange_consumer, candle_channel, trades_channel ))

    clock_process.start()
    exchange_router.start()
    exchange_process.start()
    market_process.start()

    for i in range(0,num_agents):
        agent_process = Process(target=run_agent, args=(market_channel, candle_channel, trades_channel, order_channel ))
        agent_process.start()

    try:
        while 1:
            time.sleep(.1)
    except KeyboardInterrupt:
        print("attempting to close processes..." )
        for agent in agents:
            agent.terminate()
            agent.join()
        clock_process.join()
        exchange_router.join()
        exchange_process.join()
        market_process.join()
        print("processes successfully closed")

