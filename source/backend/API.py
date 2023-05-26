from flask import Flask, jsonify, request
from .Requests import Requests
import flask_monitoringdashboard as dashboard


def handle_call(call, to_json=True):
    try:
        if call is None:
            return jsonify({'message': 'Call not found.'})
        elif 'error' in call:
            return jsonify({'message': 'Error.'})
        elif to_json == True:
            return jsonify(call)
    except:
        return False


def API(conn):
    app = Flask(__name__)
    dashboard.bind(app)
    reqs = Requests(conn)

    @app.route('/')
    def index():
        return "hello"

    @app.route('/api/v1/sim_time', methods=['GET'])
    def get_sim_time():
        sim_time = reqs.get_sim_time()
        return handle_call(sim_time)

    @app.route('/api/v1/candles', methods=['GET'])
    def candles():
        interval = request.args.get('interval')
        limit = request.args.get('limit', type=int)
        ticker = request.args.get('ticker')
        if (interval is None):
            interval = '15Min'
        if (limit is None):
            limit = 20
        if (ticker is None or ticker == ""):
            ticker = 'XYZ'
        candles = reqs.get_candles(ticker, interval, limit)
        return handle_call(candles)

    @app.route('/api/v1/trades', methods=['GET'])
    def trades():
        limit = request.args.get('limit', type=int)
        ticker = request.args.get('ticker')
        if (limit is None):
            limit = 20
        if (ticker is None or ticker == ""):
            ticker = 'XYZ'
        trades = reqs.get_trades(ticker, limit)
        return handle_call(trades)

    @app.route('/api/v1/create_asset', methods=['POST'])
    def create_asset():
        data = request.get_json()
        ticker = data['ticker']
        seed_price = data.get('seed_price', 100)
        seed_bid = data.get('seed_bid', 0.99)
        seed_ask = data.get('seed_ask', 1.01)
        created_asset = reqs.create_asset(
            ticker, seed_price, seed_bid, seed_ask)
        return handle_call(created_asset)

    @app.route('/api/v1/crypto/get_mempool', methods=['GET'])
    def get_mempool():
        limit = request.args.get('limit', type=int)
        if (limit is None):
            limit = 20
        mempool = reqs.get_mempool(limit)
        return handle_call(mempool, to_json=False)

    @app.route('/api/v1/get_order_book', methods=['GET'])
    def get_order_book():
        ticker = request.args.get('ticker')
        if (ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        order_book = reqs.get_order_book(ticker)
        return handle_call(order_book)

    @app.route('/api/v1/get_latest_trade', methods=['GET'])
    def get_latest_trade():
        ticker = request.args.get('ticker')
        if (ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        latest_trade = reqs.get_latest_trade(ticker)
        return handle_call(latest_trade)

    @app.route('/api/v1/get_trades', methods=['GET'])
    def get_trades():
        limit = request.args.get('limit', type=int)
        ticker = request.args.get('ticker')
        if (ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        if (limit is None):
            limit = 20
        trades = reqs.get_trades(ticker, limit)
        return handle_call(trades)

    @app.route('/api/v1/get_quotes', methods=['GET'])
    def get_quotes():
        ticker = request.args.get('ticker')
        if (ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        quotes = reqs.get_quotes(ticker)
        return handle_call(quotes)

    @app.route('/api/v1/get_best_bid', methods=['GET'])
    def get_best_bid():
        ticker = request.args.get('ticker')
        if (ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        best_bid = reqs.get_best_bid(ticker)
        return handle_call(best_bid)

    @app.route('/api/v1/get_best_ask', methods=['GET'])
    def get_best_ask():
        ticker = request.args.get('ticker')
        if (ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        best_ask = reqs.get_best_ask(ticker)
        return handle_call(best_ask)

    @app.route('/api/v1/get_midprice', methods=['GET'])
    def get_midprice():
        ticker = request.args.get('ticker')
        if (ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        midprice = reqs.get_midprice(ticker)
        return handle_call(midprice)

    @app.route('/api/v1/limit_buy', methods=['POST'])
    def limit_buy():
        data = request.get_json()
        ticker = data['ticker']
        price = data['price']
        qty = data['qty']
        creator = data['creator']
        fee = data['fee']
        order = reqs.limit_buy(ticker, price, qty, creator, fee)
        return handle_call(order)

    @app.route('/api/v1/limit_sell', methods=['POST'])
    def limit_sell():
        data = request.get_json()
        ticker = data['ticker']
        price = data['price']
        qty = data['qty']
        creator = data['creator']
        fee = data['fee']
        order = reqs.limit_sell(ticker, price, qty, creator, fee)
        return handle_call(order)

    @app.route('/api/v1/cancel_order', methods=['POST'])
    def cancel_order():
        data = request.get_json()
        order_id = data['id']
        cancelled_order = reqs.cancel_order(order_id)
        return handle_call(cancelled_order)

    @app.route('/api/v1/cancel_all_orders', methods=['POST'])
    def cancel_all_orders():
        data = request.get_json()
        agent = data['agent']
        ticker = data['ticker']
        cancelled_orders = reqs.cancel_all_orders(agent, ticker)
        return handle_call(cancelled_orders)

    @app.route('/api/v1/market_buy', methods=['POST'])
    def market_buy():
        data = request.get_json()
        ticker = data['ticker']
        qty = data['qty']
        buyer = data['buyer']
        fee = data['fee']
        place_market_buy = reqs.market_buy(ticker, qty, buyer, fee)
        return handle_call(place_market_buy)

    @app.route('/api/v1/market_sell', methods=['POST'])
    def market_sell():
        data = request.get_json()
        ticker = data['ticker']
        qty = data['qty']
        seller = data['seller']
        fee = data['fee']
        place_market_sell = reqs.market_sell(ticker, qty, seller, fee)
        return handle_call(place_market_sell)

    return app
