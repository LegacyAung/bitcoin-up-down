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



# get binance time range in millisecond timestamps
# default 3 days
def get_binance_time_range(days=3):
    end_time = int(time.time() * 1000)
    start_time = end_time - (days * 24 * 60 * 60 * 1000)
    
    return start_time, end_time


print("hello world")