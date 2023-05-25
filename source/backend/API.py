from flask import Flask, jsonify, request
from .Requests import Requests
import flask_monitoringdashboard as dashboard

def API(conn):
    app = Flask(__name__)
    dashboard.bind(app)
    reqs = Requests(conn)

    @app.route('/')
    def index():
        return "hello"
    
    @app.route('/api/v1/sim_time', methods=['GET'])
    def get_sim_time():
        return jsonify(reqs.get_sim_time())

    @app.route('/api/v1/candles', methods=['GET'])
    def candles():
        interval=request.args.get('interval')
        limit=request.args.get('limit', type=int)
        ticker=request.args.get('ticker')
        if(interval is None):
            interval = '15Min'
        if(limit is None):
            limit = 20
        if(ticker is None or ticker == ""):
            ticker = 'XYZ'
        candles = reqs.get_candles(ticker, interval, limit)
        if 'error' not in candles:
            return candles
        else:
            return jsonify({'message': 'No candles available.'})

    @app.route('/api/v1/trades', methods=['GET'])
    def trades():
        limit=request.args.get('limit', type=int)
        ticker=request.args.get('ticker')
        if(limit is None):
            limit = 20
        if(ticker is None or ticker == ""):
            ticker = 'XYZ'
        trades = reqs.get_trades(ticker, limit)
        if 'error' not in trades:
            return trades
        else:
            return jsonify({'message': 'No trades available.'})

    @app.route('/api/v1/create_asset', methods=['POST'])
    def create_asset():
        data = request.get_json()
        ticker = data['ticker']
        seed_price = data.get('seed_price', 100)
        seed_bid = data.get('seed_bid', 0.99)
        seed_ask = data.get('seed_ask', 1.01)
        return jsonify(reqs.create_asset(ticker, seed_price, seed_bid, seed_ask))

    @app.route('/api/v1/crypto/get_mempool', methods=['GET'])
    def get_mempool():
        limit = request.args.get('limit', type=int)
        if(limit is None):
            limit = 20
        mempool = reqs.get_mempool(limit)
        if 'error' not in mempool:
            return mempool
        else:
            return jsonify({'message': 'No mempool available.'})

    @app.route('/api/v1/get_order_book', methods=['GET'])
    def get_order_book():
        ticker = request.args.get('ticker')
        if(ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        order_book = reqs.get_order_book(ticker)
        if 'error' not in order_book:
            return jsonify(order_book)
        else:
            return jsonify({'message': 'Order book not found.'})

    @app.route('/api/v1/get_latest_trade', methods=['GET'])
    def get_latest_trade():
        ticker = request.args.get('ticker')
        if(ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        latest_trade = reqs.get_latest_trade(ticker)
        if 'error' not in latest_trade:
            return jsonify(latest_trade)
        else:
            return jsonify({'message': 'No trades available.'})

    @app.route('/api/v1/get_trades', methods=['GET'])
    def get_trades():
        limit = request.args.get('limit', type=int)
        ticker = request.args.get('ticker')
        if(ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        if(limit is None):
            limit = 20
        trades = reqs.get_trades(ticker, limit)
        if 'error' not in trades:
            return jsonify(trades)
        else:
            return jsonify({'message': 'No trades available.'})

    @app.route('/api/v1/get_quotes', methods=['GET'])
    def get_quotes():
        ticker = request.args.get('ticker')
        if(ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        quotes = reqs.get_quotes(ticker)
        if 'error' not in quotes:
            return jsonify(quotes)
        else:
            return jsonify({'message': 'No quotes available.'})

    @app.route('/api/v1/get_best_bid', methods=['GET'])
    def get_best_bid():
        ticker = request.args.get('ticker')
        if(ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        best_bid = reqs.get_best_bid(ticker)
        if 'error' not in best_bid:
            return jsonify(best_bid)
        else:
            return jsonify({'message': 'No bids available.'})

    @app.route('/api/v1/get_best_ask', methods=['GET'])
    def get_best_ask():
        ticker = request.args.get('ticker')
        if(ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        best_ask = reqs.get_best_ask(ticker)
        if 'error' not in best_ask:
            return jsonify(best_ask)
        else:
            return jsonify({'message': 'No asks available.'})

    @app.route('/api/v1/get_midprice', methods=['GET'])
    def get_midprice():
        ticker = request.args.get('ticker')
        if(ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        midprice = reqs.get_midprice(ticker)
        if 'error' not in midprice:
            return jsonify(midprice)
        else:
            return jsonify({'message': 'No midprice available.'})

    @app.route('/api/v1/limit_buy', methods=['POST'])
    def limit_buy():
        data = request.get_json()
        ticker = data['ticker']
        price = data['price']
        qty = data['qty']
        creator = data['creator']
        fee = data['fee']
        order = reqs.limit_buy(ticker, price, qty, creator, fee)
        if 'error' not in order:
            return jsonify(order)
        else:
            return jsonify({'message': 'Order not placed.'})

    @app.route('/api/v1/limit_sell', methods=['POST'])
    def limit_sell():
        data = request.get_json()
        ticker = data['ticker']
        price = data['price']
        qty = data['qty']
        creator = data['creator']
        fee = data['fee']
        order = reqs.limit_sell(ticker, price, qty, creator, fee)
        if 'error' not in order:
            return jsonify(order)
        else:
            return jsonify({'message': 'Order not placed.'})

    @app.route('/api/v1/cancel_order', methods=['POST'])
    def cancel_order():
        data = request.get_json()
        order_id = data['id']
        cancelled_order = reqs.cancel_order(order_id)
        if 'error' not in cancelled_order:
            return jsonify()
        else:
            return jsonify({'message': 'Order not found.'})

    @app.route('/api/v1/cancel_all_orders', methods=['POST'])
    def cancel_all_orders():
        data = request.get_json()
        agent = data['agent']
        ticker = data['ticker']
        cancelled_orders = reqs.cancel_all_orders(agent, ticker)
        if 'error' not in cancelled_orders:
            return jsonify(cancelled_orders)
        else:
            return jsonify({'message': 'Orders not found.'})

    @app.route('/api/v1/market_buy', methods=['POST'])
    def market_buy():
        data = request.get_json()
        ticker = data['ticker']
        qty = data['qty']
        buyer = data['buyer']
        fee = data['fee']
        place_market_buy = reqs.market_buy(ticker, qty, buyer, fee)
        if 'error' not in place_market_buy:
            return jsonify(place_market_buy)
        else:
            return jsonify({'message': 'Market buy order not placed.'})

    @app.route('/api/v1/market_sell', methods=['POST'])
    def market_sell():
        data = request.get_json()
        ticker = data['ticker']
        qty = data['qty']
        seller = data['seller']
        fee = data['fee']
        place_market_sell = reqs.market_sell(ticker, qty, seller, fee)
        if 'error' not in place_market_sell:
            return jsonify(place_market_sell)
        else:
            return jsonify({'message': 'Market sell order not placed.'})
        
    return app

