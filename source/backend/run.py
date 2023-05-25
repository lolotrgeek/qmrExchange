
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

def run_app(queue, conn):
    msg = conn.recv()
    app = API(queue, conn) 
    app.run()

def run_loop(queue, conn):
    msg = conn.recv()
    sim.run(queue, queue)

def main():
    ctx = mp.get_context('spawn')
    q = ctx.Queue()
    p1_conn, p2_conn = mp.Pipe(duplex=True)
    p1 = ctx.Process(target=run_loop, args=(q,p1_conn))
    p2 = ctx.Process(target=run_app, args=(q,p2_conn))

    p1.start()
    p2.start()

    # ws.run(app)

    try:
        while 1:
            time.sleep(.1)
    except KeyboardInterrupt:
        print("attempting to close processes..." )
        p1_conn.close()
        p2_conn.close()
        p1.join()
        p2.join()
        print("processes successfully closed")



