from flask import jsonify
from flask_socketio import SocketIO, emit
from time import sleep

#TODO: for this to work we need to push data from the exchange and pull it to here then re-broadcast via websocket
def WebSockets(app, sim):
    socketio = SocketIO(app, cors_allowed_origins="*")

    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        # Send initial order book data to the client
        # emit('order_book', sim.exchange.get_order_book())


    @socketio.on('/ws/v1/get_order_book')
    def handle_get_order_book(data):
        ticker = data['ticker'] 
        if(ticker is None or ticker == ""):
            return jsonify({'message': 'Ticker not found.'})
        order_book = sim.exchange.get_order_book(ticker)
        if order_book:
            emit('order_book', jsonify({"bids": order_book.df['bids'].to_dict(), "asks": order_book.df['asks'].to_dict()}))
        else:
            emit('order_book', jsonify({'message': 'Order book not found.'}))
        sleep(1)

    return socketio