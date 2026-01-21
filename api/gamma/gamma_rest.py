from config import EVENTS_GAMMA_ENDPOINT
from utils.time import get_market_window_timestamps, get_prev_24hr_timestamps
from .gamma_service import get_gamma_rest

BTC_UPDOWN_15M = "btc-updown-15m"
EVENTS_GAMMA_ENDPOINT = EVENTS_GAMMA_ENDPOINT
TIMEOUT = 10


def fetch_event_slug(active=bool,closed=str,timestamp=str):
    url = EVENTS_GAMMA_ENDPOINT + BTC_UPDOWN_15M + f"-{timestamp}"
    params = {
        "active":str(active).lower(),
        "closed":str(closed).lower()
    }
    res = get_gamma_rest(url,params,timeout=TIMEOUT)
    return res

def fetch_current_event_slug(active=True, closed=False):

    # parameters and endpoints
    market_win_timestamps = get_market_window_timestamps()
    current_timestamps = market_win_timestamps[1]
    params = {
        "active":str(active).lower(),
        "closed":str(closed).lower()
    }
    url = EVENTS_GAMMA_ENDPOINT + BTC_UPDOWN_15M + f"-{current_timestamps}"
    timeout=10 
    res = get_gamma_rest(url,params,timeout) 
    
    return res


def fetch_all_event_slug_24hr():
    timestamps_24hr = get_prev_24hr_timestamps()
    events = []

    for timestamp in timestamps_24hr:
        #parameters and endpoints
        params = None
        url = EVENTS_GAMMA_ENDPOINT + BTC_UPDOWN_15M + f"-{timestamp}"
        timeout=10

        res = get_gamma_rest(url,params,timeout)
        events.append(res)

    return events


if __name__ == "__main__":
    pass

    

    




