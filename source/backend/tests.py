from time import sleep, time
from multiprocessing import Process
from Messaging import Requester, Responder, Broker

def request(topic, message):
    try:
        r = Requester()
        nones = 0
        wrong = 0
        messages = 0
        start = time()
        max_count = 10
        while True:
            if(time()-start >= max_count):
                print(messages / max_count, "worlds received per second and ", nones, "nones", wrong, "wrong")
                break
            msg = r.request(topic, message)
            if msg == None:
                nones += 1
            elif msg == "world":
                messages += 1
            else:
                wrong += 1
    except Exception as e:
        print(e)
        return None

def creul_request(topic, message):
    try:
        r = Requester()
        nones = 0
        wrong = 0
        messages = 0
        start = time()
        max_count = 10
        while True:
            if(time()-start >= max_count):
                print(messages / max_count, "cruel_worlds received per second and ", nones, "nones", wrong, "wrong")
                break
            msg = r.request(topic, message)
            if msg == None:
                nones += 1
            elif msg == "cruel_world":
                messages += 1
            else:
                wrong += 1
    except Exception as e:
        print(e)
        return None

def responding(msg):
    if(msg['topic'] == 'hello'): return "world"
    elif(msg['topic'] == 'goodbye'): return "cruel_world"
    else: return None

def respond():
    try:
        s = Responder()
        nones = 0
        messages = 0
        start = time()
        max_count = 11        
        while True:
            if(time()-start >= max_count):
                print(messages / max_count, "messages responded per second and ", nones, "nones")
                break
            response = s.respond(responding)
            if response == None:
                nones += 1
            elif response == "world":
                messages += 1
            elif response == "cruel_world":
                messages += 1    
                    
    except Exception as e:
        print(e)
        return None

def route():
    try:
        r = Broker()
        r.route()
    except Exception as e:
        print(e)
        return None    


if __name__ == '__main__':

    router = Process(target=route)
    responder = Process(target=respond)
    requester = Process(target=request, args=("hello", {"world": "world"}))
    requester_bye = Process(target=creul_request, args=("goodbye", {"cruel_world": "cruel_world"}))

    router.start()
    responder.start()
    requester.start()
    requester_bye.start()
    try:
        while True:
            sleep(.1)

    except KeyboardInterrupt:
        print("attempting to close processes..." )
        responder.terminate()
        requester.terminate()
        requester_bye.terminate()
        router.terminate()
        router.join()
        responder.join()
        requester.join()
        requester_bye.join()
        print("processes successfully closed")

    finally:
        exit(0)
