from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TODAY_UNIX_TIMESTAMPS_BTC = []

def get_current_time_et():
    et = ZoneInfo("America/New_York")
    now_et = datetime.now(et)
    time_format = {
        "default": now_et,
        "hour_min_sec": now_et.strftime("%H:%M:%S")
    }
    return time_format


def get_aroundup_unix_timestamps():
    current_time_dict = get_current_time_et()
    
    # Extract the actual datetime object from the dictionary
    current_et = current_time_dict.get('default')

    # 1. Calculate how many minutes to add to reach the next 15m mark
    # (If it's already exactly on a 15m mark, this logic adds 15 mins)
    mins_to_add = 15 - (current_et.minute % 15)

    # 2. Create the start time (Add minutes to the DATETIME object, not the dict)
    start_time = current_et + timedelta(minutes=mins_to_add)
    start_time = start_time.replace(second=0, microsecond=0)
    
    # 3. Loop and append timestamps
    current_step = start_time
    timestamps = []
    
    # Loop until the day changes
    while current_step.day == current_et.day:
        int_current_step = int(current_step.timestamp())
        str_current_step = str(int_current_step)
        timestamps.append(str_current_step)
        current_step += timedelta(minutes=15)
        
    return timestamps


def get_prev_15m_timestamp():
    current_time_dict = get_current_time_et()
    current_et = current_time_dict.get('default')

    # 1. Floor to the current 15m mark (e.g., 10:38 -> 10:30)
    floored_time = current_et.replace(
        minute=(current_et.minute // 15) * 15, 
        second=0, 
        microsecond=0
    )

    prev_interval = floored_time - timedelta(minutes=15)

    return str(int(prev_interval.timestamp()))

def get_all_relevant_timestamps():
    current_time_dict = get_current_time_et()
    current_et = current_time_dict.get('default')

    # 1. Start exactly at the current 15m floor (e.g., 10:30)
    start_time = current_et.replace(
        minute=(current_et.minute // 15) * 15, 
        second=0, 
        microsecond=0
    )
    
    # 2. To get the "Previous" resolution as well, subtract 15 once
    previous_resolution = start_time - timedelta(minutes=15)
    
    # 3. Generate the rest (Current + Future)
    timestamps = [str(int(previous_resolution.timestamp()))]
    current_step = start_time
    
    while current_step.day == current_et.day:
        timestamps.append(str(int(current_step.timestamp())))
        current_step += timedelta(minutes=15)
        
    return timestamps

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





