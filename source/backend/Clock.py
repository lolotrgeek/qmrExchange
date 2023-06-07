from ._utils import get_datetime_range, get_timedelta
from datetime import datetime, timedelta

class Clock():
    def __init__(self, time_unit='day') -> None:
        #NOTE: we are choosing the 1700 as year because it is the furthest year that pandas will resample
        self.dt = datetime(1700,1,1)
        self.timeDelta = get_timedelta(time_unit)
        
    def tick(self):
        if(type(self.dt) is str):
            print(f'dt is str')
            return False
        self.dt +=self.timeDelta

