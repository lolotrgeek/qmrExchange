from Messaging import Pusher, Puller, Requester, Responder, Router, Broker
import signal

interrupted = False

def signal_handler(signum, frame):
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, signal_handler)
def test():
    try:
        requester = Requester()

        while True:
            requester.request("test")
            if interrupted:
                print ("W: interrupt received, killing server…")
                break
    except KeyboardInterrupt:
        requester.close()
        return None

if __name__ == "__main__":
    test()