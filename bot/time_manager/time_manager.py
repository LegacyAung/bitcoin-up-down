from .time_persistance import TimePersistance



class TimeManager:
    def __init__(self):
        self.time_persistance = TimePersistance()

        
    def handle_time_persistance(self, res_sec):
        time_data_utc = self.time_persistance.persistantly_cal_time_delta_to_next_resolution(res_sec)
        return time_data_utc

    def handle_time_analyzer(self):
        return






def main():
    pass

if __name__ == "__main__":
    main()