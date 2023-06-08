from time import sleep
from multiprocessing import Process
from Messaging import Pusher, Puller, Router
from Clock import Clock

def push():
    try:
        p = Pusher(5115)
        clock = Clock()
        while True:
            clock.tick()
            msg = p.push({"time": str(clock.dt)})
    
    except KeyboardInterrupt:
        return

def pull(channel):
    try:
        s = Puller(channel)
        sleep(.5)
        while True:
            msg = s.pull()
            print(msg)
    except Exception as e:
        print(e)
        return None

def route(channel):
    try:
        r = Router(5115, channel )
        r.route()
    except Exception as e:
        print(e)
        return None    


if __name__ == '__main__':
    try:

        channel = 5114
        pusher = Process(target=push)
        puller = Process(target=pull , args=(channel,))
        router = Process(target=route , args=(channel,))

        pusher.start()
        puller.start()
        router.start()

        while True:
            sleep(.1)

    except KeyboardInterrupt:
        print("attempting to close processes..." )
        pusher.terminate()
        puller.terminate()
        router.terminate()
        pusher.join()
        puller.join()
        router.join()
        print("processes successfully closed")

    finally:
        exit(0)