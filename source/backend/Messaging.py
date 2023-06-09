import zmq

class Requester():
    def __init__(self, channel='5556'):
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect(f'tcp://127.0.0.1:{channel}')

    def request(self, topic, args=None):
        try:
            self.socket.send_json({'topic': topic, 'args': args})
            return self.socket.recv_json()
        except Exception as e:
            print(e)
            return None

class Responder():
    def __init__(self, channel='5557', topics ={}):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.connect(f'tcp://127.0.0.1:{channel}')
        self.topics = topics

    def respond(self):
        try:
            msg = self.socket.recv_json()
            if msg["topic"] in self.topics.keys():
                response = self.topics[msg['topic']](msg['args'])
                self.socket.send_json(response)
                return response
            else:
                self.socket.send_json(None)
                return None
        except Exception as e:
            # print("Response Error", e)
            self.socket.close()
            return None

class Broker():
    def __init__(self, request_side='5556', response_side='5557'):
        self.context = zmq.Context()
        self.requests_socket = self.context.socket(zmq.ROUTER)
        self.requests_socket.bind(f"tcp://127.0.0.1:{request_side}")
        self.responses_socket = self.context.socket(zmq.DEALER)
        self.responses_socket.bind(f"tcp://127.0.0.1:{response_side}")
        self.poller = zmq.Poller()
        self.poller.register(self.requests_socket, zmq.POLLIN)
        self.poller.register(self.responses_socket, zmq.POLLIN)

    def route(self, cb=None):
            try:
                zmq.proxy(self.requests_socket, self.responses_socket)
            except Exception as e:
                print("[Broker Error]", e)

class Pusher():
    def __init__(self, channel='5558'):
        self.highwatermark = 3 # how many messages to keep in , reduce the throughput but decreases a pull returning None
        self.lowwatermark = 1
        self.context = zmq.Context()
        self.zmq_socket = self.context.socket(zmq.PUSH)
        self.address = f"tcp://127.0.0.1:{channel}"
        self.zmq_socket.connect(self.address)
        

    def push(self, message):
        try:
            self.zmq_socket.send_json(message)
            return True
        except Exception as e:
            print(e)
            return None


class Puller():
    def __init__(self, channel='5556'):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.address = f"tcp://127.0.0.1:{channel}"
        self.socket.connect(self.address)

    def pull(self):
        try:
            msg = self.socket.recv_json()
            return msg
        except Exception as e:
            print(e)
            return None
        
    def request(self, topic, args=None):
        return self.pull()


class Router():
    def __init__(self, producer='5558', consumer='5556'):
        self.context = zmq.Context()
        self.producer_socket = self.context.socket(zmq.PULL)
        self.producer_socket.bind(f"tcp://127.0.0.1:{producer}")
        self.consumer_socket = self.context.socket(zmq.PUSH)
        self.consumer_socket.bind(f"tcp://127.0.0.1:{consumer}")
        self.poller = zmq.Poller()
        self.poller.register(self.producer_socket, zmq.POLLIN)

    def route(self, cb=None):
        last_msg = {}
        while True:
            try:
                evts = dict(self.poller.poll(.5))
                if self.producer_socket in evts:
                    msg = self.producer_socket.recv_json(zmq.DONTWAIT)
                    if msg is not None and msg != last_msg and msg != {}:
                        last_msg = msg
                # print("last", last_msg)
                self.consumer_socket.send_json(last_msg)
            except Exception as e:
                print(e)
                continue  