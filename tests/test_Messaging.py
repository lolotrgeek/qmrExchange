import unittest
import sys
import os
import threading
import time
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from source.Messaging import Requester, Responder, Broker, Pusher, Puller, Router

#TODO: combo these tests, [requesters,responders,broker] and [pusher, puller, router] need to be tested together
class TestRequester(unittest.TestCase):
    def test_request_success(self):
        channel = '5556'
        requester = Requester(channel)
        response = requester.request("test message")
        requester.close()
        self.assertIsNotNone(response)

    def test_request_failure(self):
        channel = '5556'
        requester = Requester(channel)
        with self.assertRaises(Exception):
            requester.request(None)
        requester.close()

class TestResponder(unittest.TestCase):
    def test_respond_success(self):
        channel = '5557'
        responder = Responder(channel)
        response = responder.respond(lambda msg: "response")
        self.assertEqual(response, "response")

    def test_respond_failure(self):
        channel = '5557'
        responder = Responder(channel)
        with self.assertRaises(Exception):
            responder.respond(None)

class TestBroker(unittest.TestCase):
    def test_broker(self):
        request_side = '5556'
        response_side = '5557'
        broker = Broker(request_side, response_side)
        broker_thread = threading.Thread(target=broker.route)
        broker_thread.start()
        time.sleep(1)

        pusher = Pusher('5558')
        pusher.push("test message")
        time.sleep(1)

        puller = Puller('5556')
        response = puller.pull()

        broker_thread.join()
        puller.close()
        self.assertIsNotNone(response)

class TestPusher(unittest.TestCase):
    def test_push_success(self):
        channel = '5558'
        pusher = Pusher(channel)
        result = pusher.push("test message")
        self.assertTrue(result)

    def test_push_failure(self):
        channel = '5558'
        pusher = Pusher(channel)
        with self.assertRaises(Exception):
            pusher.push(None)

class TestPuller(unittest.TestCase):
    def test_pull_success(self):
        channel = '5556'
        puller = Puller(channel)
        result = puller.pull()
        self.assertIsNotNone(result)

    def test_pull_failure(self):
        channel = '5556'
        puller = Puller(channel)
        with self.assertRaises(Exception):
            puller.pull()

class TestRouter(unittest.TestCase):
    def test_route(self):
        producer = '5558'
        consumer = '5556'
        router = Router(producer, consumer)
        router_thread = threading.Thread(target=router.route)
        router_thread.start()
        time.sleep(1)

        pusher = Pusher('5558')
        pusher.push("test message")
        time.sleep(1)

        puller = Puller('5556')
        response = puller.pull()

        router_thread.join()
        puller.close()
        self.assertIsNotNone(response)

if __name__ == '__main__':
    unittest.main()
