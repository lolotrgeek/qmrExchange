from flask import Flask, jsonify, request
from ._utils import format_dataframe_rows_to_dict

def API(sim):
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "hello"
    
    @app.route('/api/v1/sim_time', methods=['GET'])
    def get_sim_time():
        return jsonify({'sim_time': sim.dt, 'episode': sim.episode, 'episodes': sim._episodes})

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
        candles = sim.get_price_bars(ticker, bar_size=interval).head(limit).to_json()
        if candles:
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
        trades = sim.trades.head(limit).to_json()
        if trades:
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
        sim.exchange.create_asset(ticker, seed_price, seed_bid, seed_ask)
        return jsonify({'message': 'Asset created successfully.'})

    @app.route('/api/v1/crypto/get_mempool', methods=['GET'])
    def get_mempool():
        limit = request.args.get('limit', type=int)
        ticker = request.args.get('ticker') # NOTE: this would typically be a hash of a contract address
        if(ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        if(limit is None):
            limit = 20
        mempool = sim.exchange.blockchain.mempool.transaction_log
        return mempool.head(limit).to_json()

    @app.route('/api/v1/get_order_book', methods=['GET'])
    def get_order_book():
        ticker = request.args.get('ticker')
        if(ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        order_book = sim.exchange.get_order_book(ticker)
        if order_book:
            return jsonify({"bids": format_dataframe_rows_to_dict(order_book.df['bids']), "asks":  format_dataframe_rows_to_dict(order_book.df['asks'])})
        else:
            return jsonify({'message': 'Order book not found.'})

    @app.route('/api/v1/get_latest_trade', methods=['GET'])
    def get_latest_trade():
        ticker = request.args.get('ticker')
        if(ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        latest_trade = sim.exchange.get_latest_trade(ticker)
        if latest_trade:
            return jsonify(latest_trade.to_dict())
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
        trades = sim.exchange.get_trades(ticker).head(limit)
        format_trades = format_dataframe_rows_to_dict(trades)
        if not trades.empty:
            return jsonify(format_trades)
        else:
            return jsonify({'message': 'No trades available.'})

    @app.route('/api/v1/get_quotes', methods=['GET'])
    def get_quotes():
        ticker = request.args.get('ticker')
        if(ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        quotes = sim.exchange.get_quotes(ticker)
        if quotes:
            return jsonify(quotes)
        else:
            return jsonify({'message': 'No quotes available.'})

    @app.route('/api/v1/get_best_bid', methods=['GET'])
    def get_best_bid():
        ticker = request.args.get('ticker')
        if(ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        best_bid = sim.exchange.get_best_bid(ticker)
        if best_bid:
            return jsonify(best_bid.to_dict())
        else:
            return jsonify({'message': 'No bids available.'})

    @app.route('/api/v1/get_best_ask', methods=['GET'])
    def get_best_ask():
        ticker = request.args.get('ticker')
        if(ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        best_ask = sim.exchange.get_best_ask(ticker)
        if best_ask:
            return jsonify(best_ask.to_dict())
        else:
            return jsonify({'message': 'No asks available.'})

    @app.route('/api/v1/get_midprice', methods=['GET'])
    def get_midprice():
        ticker = request.args.get('ticker')
        if(ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        midprice = sim.exchange.get_midprice(ticker)
        return jsonify({'midprice': midprice})

    @app.route('/api/v1/limit_buy', methods=['POST'])
    def limit_buy():
        data = request.get_json()
        ticker = data['ticker']
        price = data['price']
        qty = data['qty']
        creator = data['creator']
        fee = data['fee']
        order = sim.exchange.limit_buy(ticker, price, qty, creator, fee)
        return jsonify(order.to_dict())

    @app.route('/api/v1/limit_sell', methods=['POST'])
    def limit_sell():
        data = request.get_json()
        ticker = data['ticker']
        price = data['price']
        qty = data['qty']
        creator = data['creator']
        fee = data['fee']
        order = sim.exchange.limit_sell(ticker, price, qty, creator, fee)
        return jsonify(order.to_dict())

    @app.route('/api/v1/cancel_order', methods=['POST'])
    def cancel_order():
        data = request.get_json()
        order_id = data['id']
        cancelled_order = sim.exchange.cancel_order(order_id)
        if cancelled_order:
            return jsonify(cancelled_order.to_dict())
        else:
            return jsonify({'message': 'Order not found.'})

    @app.route('/api/v1/cancel_all_orders', methods=['POST'])
    def cancel_all_orders():
        data = request.get_json()
        agent = data['agent']
        ticker = data['ticker']
        sim.exchange.cancel_all_orders(agent, ticker)
        return jsonify({'message': 'All orders cancelled successfully.'})

    @app.route('/api/v1/market_buy', methods=['POST'])
    def market_buy():
        data = request.get_json()
        ticker = data['ticker']
        qty = data['qty']
        buyer = data['buyer']
        fee = data['fee']
        sim.exchange.market_buy(ticker, qty, buyer, fee)
        return jsonify({'message': 'Market buy order executed successfully.'})

    @app.route('/api/v1/market_sell', methods=['POST'])
    def market_sell():
        data = request.get_json()
        ticker = data['ticker']
        qty = data['qty']
        seller = data['seller']
        fee = data['fee']
        sim.exchange.market_sell(ticker, qty, seller, fee)
        return jsonify({'message': 'Market sell order executed successfully.'})

    return app

