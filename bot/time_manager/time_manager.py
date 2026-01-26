import time
from utils.time import get_market_window_timestamps, get_current_time_et

class time_manager:
    def __init__(self):
        self.market_window_timestamps = get_market_window_timestamps()
        self.get_current_time_et = get_current_time_et()

    async def persistantly_cal_time_delta_of_next_resolution(self):
        pass


    async def persistantly_cal_current_time(self):
        pass

