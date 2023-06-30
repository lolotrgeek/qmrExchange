from random import randint
import traceback
from source.Messaging import Requester
from source.API import API
from rich import print
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def run_api(exchange_channel = 5570):
    try:
        requester = Requester(exchange_channel)
        await requester.connect()
        api = API(requester)
        api.run()
    except Exception as e:
        print("[API Error] ", e)
        return None
    except  KeyboardInterrupt:
        print("attempting to close api..." )
        return None
    

if __name__ == '__main__':
    try:
        print('starting api')
        asyncio.run(run_api())
    except Exception as e:
        print("[API Error] ", e)
        traceback.print_exc()
        exit()