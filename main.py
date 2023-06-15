from source.backend.types.OrderSide import OrderSide
from source.backend.types.LimitOrder import LimitOrder
from source.backend.types.OrderBook import OrderBook
from source.backend.Exchange import Exchange
from source.backend.AgentRemote import AgentRemote
from source.backend.Agents import RandomMarketTaker, NaiveMarketMaker, CryptoMarketMaker, CryptoMarketTaker, RemoteTrader
from source.backend.run import main
import sys
import traceback

if __name__ == '__main__':
    try:
        main()        
        print('done...')
        exit(0)
    except:
        # print(sys.exc_info()[2])
        # print(traceback.format_exc())
        exit(0)
        

# export all imports
__all__ = [
    'OrderSide',
    'LimitOrder',
    'OrderBook',
    'Exchange',
    'AgentRemote',
    'RandomMarketTaker',
    'NaiveMarketMaker',
    'CryptoMarketMaker',
    'CryptoMarketTaker',
    'RemoteTrader',
    'plot_bars',
]