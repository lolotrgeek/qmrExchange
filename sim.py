from datetime import datetime
from flask import Flask, jsonify, request
from main import *
import time
import threading



time_interval = 'minute'
tickers = ['XYZ']
sim = Simulator(time_unit=time_interval)
sim.exchange.create_asset(tickers[0])

#TODO: have agents run in separate processes and connect via API
mm = NaiveMarketMaker(name='market_maker', tickers=tickers, aum=1_000, spread_pct=0.005, qty_per_order=4)
sim.add_agent(mm)

mt = RandomMarketTaker(name='market_taker', tickers=tickers, aum=1_000, prob_buy=.2, prob_sell=.2, qty_per_order=1,seed=42)
sim.add_agent(mt)

app = Flask(__name__)
@app.route('/')
def index():
    return "hello"

@app.route('/api/v1/candles')
def candles():
    interval=request.args.get('interval')
    limit=request.args.get('limit', type=int)
    ticker=request.args.get('ticker')
    if(interval is None):
        interval = '15Min'
    if(limit is None):
        limit = 20
    if(ticker is None):
        ticker = 'XYZ'

    print(interval, limit, ticker)
    df_candles = sim.get_price_bars(ticker, bar_size=interval)
    return jsonify(df_candles.head(limit).to_json())

@app.route('/api/v1/portfolio')
def portfolio():
    mt_holdings = sim.get_portfolio_history('market_taker')
    mm_holdings = sim.get_portfolio_history('market_maker')
    return jsonify({'market_taker': mt_holdings.to_json(), 'market_maker': mm_holdings.to_json()})

@app.route('/api/v1/trades')
def trades():
    return jsonify(sim.trades.to_json())

def run_loop(run_event):
    sim.run(run_event)

def main():
    run_event = threading.Event()
    run_event.set()
    t1 = threading.Thread(target=run_loop, args=[run_event])
    t1.start()

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
