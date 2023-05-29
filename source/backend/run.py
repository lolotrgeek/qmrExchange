
from .Agents import NaiveMarketMaker, RandomMarketTaker
from .Simulator import Simulator
import time
import multiprocessing as mp
from .API import API
# from WebSockets import WebSockets

time_interval = 'minute'
tickers = ['XYZ']
sim = Simulator(time_unit=time_interval)
sim.exchange.crypto = True
sim.exchange.create_asset(tickers[0])

mm = NaiveMarketMaker(name='market_maker', tickers=tickers, aum=1_000, spread_pct=0.005, qty_per_order=4)
sim.add_agent(mm)

mt = RandomMarketTaker(name='market_taker', tickers=tickers, aum=1_000, prob_buy=.2, prob_sell=.2, qty_per_order=1,seed=42)
sim.add_agent(mt)

# ws = WebSockets(app, sim)

def run_app(conn):
    # on api request gets the specific data from the main process and sends to client
    app = API(conn)
    app.run()

def run_loop(conn):
    # at each iter of loop writes entire state to queue
    sim.run(conn)

def main():
    ctx = mp.get_context('spawn')
    state = ctx.Queue()

    p1 = ctx.Process(target=run_loop, args=(state, ))
    p2 = ctx.Process(target=run_app, args=(state, ))

    p1.start()
    p2.start()

    # ws.run(app)

    try:
        while 1:
            time.sleep(.1)
    except KeyboardInterrupt:
        print("attempting to close processes..." )
        p1.join()
        p2.join()
        print("processes successfully closed")



