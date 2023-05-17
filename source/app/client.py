import socketio

# Connect to the server
sio = socketio.Client()
sio.connect('http://localhost:5000')


@sio.on('connect')
def on_connect():
    print('Connected to the server')

@sio.on('order_book')
def on_order_book(data):
    print('Received order book data:')
    print(data)

# Send a request to get the order book
sio.emit('/ws/v1/get_order_book', {'ticker': 'XYZ'})

# Keep the script running to continue receiving events
sio.wait()