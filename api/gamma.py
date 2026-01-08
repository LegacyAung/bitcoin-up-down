import requests
import json
from config import EVENTS_GAMMA_ENDPOINT
from utils.time import get_market_window_timestamps

BTC_UPDOWN_15M = "btc-updown-15m"


def fetch_current_event_slug(active=True, closed=False):

    #getting current timestamp
    market_win_timestamps = get_market_window_timestamps()
    
    current_timestamps = market_win_timestamps[1]
    
    params = {
        "active":str(active).lower(),
        "closed":str(closed).lower()
    }
    res = requests.get(EVENTS_GAMMA_ENDPOINT + BTC_UPDOWN_15M + f"-{current_timestamps}",params=params, timeout=10)

    res.raise_for_status()
    event = res.json()

    for market in event.get('markets', []):
        clob_token_ids = market.get('clobTokenIds')
        condition_id = market.get('conditionId')


        if isinstance(clob_token_ids, str):
            clob_token_ids = json.loads(clob_token_ids)  
        else:
            clob_token_ids = clob_token_ids      
        
        clob_rest_ids = {
            "clob_token_ids": clob_token_ids,
            "condition_id": condition_id
        }
        return clob_rest_ids

    

