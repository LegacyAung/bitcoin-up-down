import time
from datetime import timedelta
from utils.time import get_market_window_timestamps, get_current_time_et, get_current_time_utc

class TimePersistance:
    def __init__(self):
        self.get_current_time_et = None
        self.get_current_time_utc = None
        self.time_data = {}

    def persistantly_cal_time_delta_to_next_resolution(self, res_sec=900): #default is 15 min so res_sec is 900
        self.get_current_time_utc = get_current_time_utc()
        seconds_past_start = self.get_current_time_utc % res_sec
        delta_seconds = res_sec - seconds_past_start
        self.time_data = {
            "utc_unix" : self.get_current_time_utc,
            "delta_sec" : delta_seconds,
            "readable" : str(timedelta(seconds=delta_seconds))[2:],
            "res_name": f"{res_sec // 60}min"
        }
        print(f"\r🕒 UTC: {self.time_data['utc_unix']} | ⏳ Next 15m in: {self.time_data['readable']} ({self.time_data['delta_sec']}s) \033[K", end="", flush=True)
        return self.time_data
         
        
    def persistantly_get_current_time_utc(self):
        """persistant calculation utc timestamp in unix"""
        self.get_current_time_utc = get_current_time_utc()
        print(f"\rCurrent UTC: {self.get_current_time_utc}", end="", flush=True)
        return self.get_current_time_utc
        
        

    def persistantly_get_current_time_et(self):
        """persistant calculation et timestamp in unix"""
        
        self.get_current_time_et = get_current_time_et()
        print(f"\rCurrent ET: {self.get_current_time_et}", end="", flush=True)
        return self.get_current_time_et

        
            
        
def main():
    time_persistance = TimePersistance()
    while True:
        time_persistance.persistantly_cal_time_delta_to_next_resolution(res_sec=900)
        time.sleep(0.5)
if __name__ == "__main__":
    main()