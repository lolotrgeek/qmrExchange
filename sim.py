
from main import *
import time
import threading
from API import API
# from WebSockets import WebSockets

time_interval = 'minute'
tickers = ['XYZ']
sim = Simulator(time_unit=time_interval)
sim.exchange.create_asset(tickers[0])

#TODO: have agents run in separate processes and connect via API
mm = NaiveMarketMaker(name='market_maker', tickers=tickers, aum=1_000, spread_pct=0.005, qty_per_order=4)
sim.add_agent(mm)

mt = RandomMarketTaker(name='market_taker', tickers=tickers, aum=1_000, prob_buy=.2, prob_sell=.2, qty_per_order=1,seed=42)
sim.add_agent(mt)

app = API(sim)
# ws = WebSockets(app, sim)

def run_loop(run_event):
    sim.run(run_event)

def main():
    run_event = threading.Event()
    run_event.set()
    t1 = threading.Thread(target=run_loop, args=[run_event])
    t1.start()

    # ws.run(app)
    app.run()
    

    try:
        while 1:
            time.sleep(.1)
    except KeyboardInterrupt:
        print("attempting to close threads..." )
        run_event.clear()
        t1.join()
        print("threads successfully closed")


if __name__ == '__main__':
    main()
