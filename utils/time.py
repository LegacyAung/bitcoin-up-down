import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


#current time in Unix timestamp and et time
def get_current_time_et():
    et = ZoneInfo("America/New_York")
    now_et = datetime.now(et)
    time_format = {
        "default": now_et,
        "hour_min_sec": now_et.strftime("%H:%M:%S")
    }
    return time_format

# will get unix timestamps of current [previous_resolution, live_resolution, future_resolution]
def get_market_window_timestamps():
    current_time_dict = get_current_time_et()
    current_et = current_time_dict.get('default')

    # 1. Calculate the "Middle" (Current Active Interval)
    # Example: 12:48 becomes 12:45
    middle_step = current_et.replace(
        minute=(current_et.minute // 15) * 15, 
        second=0, 
        microsecond=0
    )

    # 2. Calculate the "Previous" (15 mins before middle)
    prev_step = middle_step - timedelta(minutes=15)

    # 3. Calculate the "Next" (15 mins after middle)
    next_step = middle_step + timedelta(minutes=15)

    # Convert all to string UNIX timestamps
    return [
        str(int(prev_step.timestamp())),   # Previous
        str(int(middle_step.timestamp())), # Current (Middle)
        str(int(next_step.timestamp()))    # Next
    ]


# will get unix timestamps of previous 24 hr starting from current timestamp 15min window
def get_prev_24hr_timestamps():
    market_window_timestamps = get_market_window_timestamps()
    current_market_timestamp = int(market_window_timestamps[1])
    prev_24hr_timestamps = []

    for i in range(96):
        past_ts_sec = current_market_timestamp - (i * 15 * 60)
        prev_24hr_timestamps.append(str(past_ts_sec))

    return prev_24hr_timestamps


# get binance time range in millisecond timestamps
def get_binance_time_range(days):
    end_time = int(time.time() * 1000)
    start_time = end_time - (days * 24 * 60 * 60 * 1000)
    
    return start_time, end_time


def get_binance_time_range_in_hours(hrs):
    end_time = int(time.time() * 1000)
    start_time = end_time - (hrs * 60 * 60 * 1000)
    return start_time, end_time





