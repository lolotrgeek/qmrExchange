from flask import Flask, jsonify, request
from .Requests import Requests
import flask_monitoringdashboard as dashboard
from time import sleep


def handle_call(call, name="", to_json=True):
    try:
        if call is None:
            print(name, call)
            # TODO: the dict is being generated but this gets recieved as None...
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

    timeout = 5
    max_tries = 5

    def make_request(request, key:str, tries=0):
        if tries >= max_tries:
            error = {}
            error[key] = {'error': 'Max tries reached.'}
            return error
        conn.send(request)
        if(conn.poll(timeout)):
            try:
                msg = conn.recv()
                if msg is None or 'error' in msg:
                    print('None', msg)
                    raise Exception('Error.')
                elif msg[key] is None or 'error' in msg[key]:
                    print('None', msg[key])
                    raise Exception('Error.')
                else:
                    print(f'key {key} found.')
                    return msg[key]
            except:
                tries += 1
                sleep(0.1)
                return make_request(request, key, tries)
        else:
            error = {}
            error[key] = {'error': 'Timeout.'}
            return error

    @app.route('/')
    def index():
        return "hello"

    @app.route('/api/v1/sim_time', methods=['GET'])
    def get_sim_time():
        return make_request({'get_sim_time': True}, 'sim_time')

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
        return make_request({'get_candles': {'ticker': ticker, 'interval': interval, 'limit': limit}}, 'candles')

    @app.route('/api/v1/create_asset', methods=['POST'])
    def create_asset():
        data = request.get_json()
        ticker = data['ticker']
        seed_price = data.get('seed_price', 100)
        seed_bid = data.get('seed_bid', 0.99)
        seed_ask = data.get('seed_ask', 1.01)
        return make_request({'create_asset': {'ticker': ticker, 'seed_price': seed_price, 'seed_bid': seed_bid, 'seed_ask': seed_ask}}, 'created_asset')


    @app.route('/api/v1/crypto/get_mempool', methods=['GET'])
    def get_mempool():
        limit = request.args.get('limit', type=int)
        if (limit is None):
            limit = 20
        mempool = reqs.get_mempool(limit)
        return make_request({'get_mempool': {'limit': limit}}, 'mempool')

    @app.route('/api/v1/get_order_book', methods=['GET'])
    def get_order_book():
        ticker = request.args.get('ticker')
        if (ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        return make_request({'get_order_book': {'ticker': ticker}}, 'order_book')


    @app.route('/api/v1/get_latest_trade', methods=['GET'])
    def get_latest_trade():
        ticker = request.args.get('ticker')
        if (ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        return make_request({'get_latest_trade': {'ticker': ticker}}, 'latest_trade')


    @app.route('/api/v1/get_trades', methods=['GET'])
    def get_trades():
        limit = request.args.get('limit', type=int)
        ticker = request.args.get('ticker')
        if (ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        if (limit is None):
            limit = 20
        return make_request({'get_trades': {'ticker': ticker, 'limit': limit}}, 'trades')


    @app.route('/api/v1/get_quotes', methods=['GET'])
    def get_quotes():
        ticker = request.args.get('ticker')
        if (ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        return make_request({'get_quotes': {'ticker': ticker}}, 'quotes')
        

    @app.route('/api/v1/get_best_bid', methods=['GET'])
    def get_best_bid():
        ticker = request.args.get('ticker')
        if (ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        return make_request({'get_best_bid': {'ticker': ticker}}, 'best_bid')


    @app.route('/api/v1/get_best_ask', methods=['GET'])
    def get_best_ask():
        ticker = request.args.get('ticker')
        if (ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        return make_request({'get_best_ask': {'ticker': ticker}}, 'best_ask')


    @app.route('/api/v1/get_midprice', methods=['GET'])
    def get_midprice():
        ticker = request.args.get('ticker')
        if (ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        return make_request({'get_midprice': {'ticker': ticker}}, 'midprice')

    @app.route('/api/v1/limit_buy', methods=['POST'])
    def limit_buy():
        data = request.get_json()
        ticker = data['ticker']
        price = data['price']
        qty = data['qty']
        creator = data['creator']
        fee = data['fee']
        return make_request({'limit_buy': {'ticker': ticker, 'price': price, 'qty': qty, 'creator': creator, 'fee': fee}}, 'limit_buy_placed') 


    @app.route('/api/v1/limit_sell', methods=['POST'])
    def limit_sell():
        data = request.get_json()
        ticker = data['ticker']
        price = data['price']
        qty = data['qty']
        creator = data['creator']
        fee = data['fee']
        return make_request({'limit_sell': {'ticker': ticker, 'price': price, 'qty': qty, 'creator': creator, 'fee': fee}}, 'limit_sell_placed')


    @app.route('/api/v1/cancel_order', methods=['POST'])
    def cancel_order():
        data = request.get_json()
        order_id = data['id']
        return make_request({'cancel_order': {'order_id': order_id}}, 'order_cancelled')


    @app.route('/api/v1/cancel_all_orders', methods=['POST'])
    def cancel_all_orders():
        data = request.get_json()
        agent = data['agent']
        ticker = data['ticker']
        return make_request({'cancel_all_orders': {'ticker': ticker, 'agent': agent}}, 'orders_cancelled')


    @app.route('/api/v1/market_buy', methods=['POST'])
    def market_buy():
        data = request.get_json()
        ticker = data['ticker']
        qty = data['qty']
        buyer = data['buyer']
        fee = data['fee']
        return make_request({'market_buy': {'ticker': ticker, 'qty': qty, 'buyer': buyer, 'fee': fee}}, 'market_buy_placed')


    @app.route('/api/v1/market_sell', methods=['POST'])
    def market_sell():
        data = request.get_json()
        ticker = data['ticker']
        qty = data['qty']
        seller = data['seller']
        fee = data['fee']
        return make_request({'market_sell': {'ticker': ticker, 'qty': qty, 'seller': seller, 'fee': fee}}, 'market_sell_placed')


    return app
