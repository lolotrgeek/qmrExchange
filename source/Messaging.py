import traceback
import zmq
import zmq.asyncio
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Requester:
    def __init__(self, channel='5556'):
        self.channel = channel

    async def connect(self):
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f'tcp://127.0.0.1:{self.channel}')
        self.poller = zmq.asyncio.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

    async def request(self, msg):
        try:
            await self.socket.send_json(msg)
            return await self.socket.recv_json()
        except zmq.ZMQError as e:
            print("[Requester Error]", e, "Request:", msg)
            return None
        except Exception as e:
            print("[Requester Error]", e, "Request:", msg)
            print(traceback.format_exc())
            return None

    async def close(self):
        await self.socket.close()
        await self.context.term()

class Responder:
    def __init__(self, channel='5556'):
        self.channel = channel

    async def connect(self):
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f'tcp://127.0.0.1:{self.channel}')

    async def respond(self, callback=lambda msg: msg): 
        try:
            msg = await self.socket.recv_json()
            response = await callback(msg)
            await self.socket.send_json(response)
            return response
        except zmq.ZMQError as e:
            print("[Response Error]", e, "Request:", msg)
            return None
        except Exception as e:
            print("[Response Error]", e, "Request:", msg)
            print(traceback.format_exc())
            await self.socket.send_json(None)
            return None

class Broker:
    def __init__(self, request_side='5556', response_side='5557'):
        self.request_side = request_side
        self.response_side = response_side

    async def start(self):
        self.context = zmq.asyncio.Context()
        self.requests_socket = self.context.socket(zmq.ROUTER)
        self.requests_socket.bind(f"tcp://127.0.0.1:{self.request_side}")
        self.responses_socket = self.context.socket(zmq.DEALER)
        self.responses_socket.bind(f"tcp://127.0.0.1:{self.response_side}")
        self.mon_socket = self.context.socket(zmq.PUB)
        self.mon_socket.bind("tcp://127.0.0.1:6969")

    async def route(self, cb=None):
        try:
            await zmq.asyncio.proxy(self.requests_socket, self.responses_socket, self.mon_socket)
        except Exception as e:
            print("[Broker Error]", e)


class Pusher():
    def __init__(self, channel='5558'):
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

    def close(self):
        self.socket.close()
        self.context.term()

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