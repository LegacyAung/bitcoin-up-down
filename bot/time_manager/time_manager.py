from .time_persistance import TimePersistance
from utils.time import get_end_timestamp_bot_workhours, get_market_window_timestamps



class TimeManager:
    def __init__(self):
        self.time_persistance = TimePersistance()

    
    def handle_dynamic_clob_wss(self, delta_sec, timestamps, res_count):
              
        if delta_sec <= 300 :
            return
        elif delta_sec < 120 and res_count > 0:
            return
        else: 
            return

        
    def handle_time_persistance(self, res_sec):
        time_data_utc = self.time_persistance.persistantly_cal_time_delta_to_next_resolution(res_sec)
        return time_data_utc

    def get_current_ts_utc(self):
        current_ts_utc = self.time_persistance.persistantly_get_current_time_utc()
        return current_ts_utc
    
    def get_end_ts_utc(self,current_utc, hours):
        secs = hours * 3600
        end_ts_utc = get_end_timestamp_bot_workhours(current_utc, secs)
        return end_ts_utc
    
    def get_next_res_ts(self):
        tss = get_market_window_timestamps()
        next_res_ts = tss[2]
        return next_res_ts
    
    def get_curr_res_ts(self):
        tss = get_market_window_timestamps()
        curr_res_ts = tss[1]
        return curr_res_ts





def main():
    pass

if __name__ == "__main__":
    main()