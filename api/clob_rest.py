import requests
import json
import time
from config import CLOB_ENDPOINT
from .gamma import fetch_current_event_slug

TOKEN_IDS = fetch_current_event_slug(active=True, closed=False)
CLOB_IDS = TOKEN_IDS.get('clob_token_ids')
CONDITION_ID = TOKEN_IDS.get('condition_id')



def get_market_snapshot(token_id: str):
    """
    Fetches the full order book, current price, and midpoint in one go.
    """
    endpoints = {
        "book": f"{CLOB_ENDPOINT}/book",
        "price": f"{CLOB_ENDPOINT}/price",
        "midpoint": f"{CLOB_ENDPOINT}/midpoint"
    }
    
    snapshot = {}
    
    try:
        # 1. Get Price
        p_res = requests.get(endpoints["price"], params={"token_id": token_id, "side": "buy"})
        snapshot["last_buy_price"] = p_res.json().get("price")

        # 2. Get Midpoint
        m_res = requests.get(endpoints["midpoint"], params={"token_id": token_id})
        snapshot["midpoint"] = m_res.json().get("mid")

        # 3. Get Full Book
        b_res = requests.get(endpoints["book"], params={"token_id": token_id})
        snapshot["order_book"] = b_res.json()
        
        return snapshot
    except Exception as e:
        print(f"Error fetching CLOB REST data: {e}")
        return None
    



def get_clob_rest():
    price_url = f"{CLOB_ENDPOINT}/book"
    res = requests.get(price_url, params={"token_id": CLOB_IDS[1], "side":"buy"})
    res.raise_for_status()
    
    data = res.json()
    return data


# Get past 3days bitcoin data from polymarket
def get_clob_btc_3_days():
    # Calculate timestamps for the last 3 days
    end_time = int(time.time())
    start_time = end_time - (3 * 24 * 60 * 60)

    url = "https://clob.polymarket.com/prices-history"
    params = {
        "market": "YOUR_TOKEN_ID", # Replace with actual token ID
        "startTs": start_time,
        "endTs": end_time,
        "interval": "1m",
        "fidelity": 1
    }

    response = requests.get(url, params=params)
    data = response.json()

    print(data)

    
get_clob_btc_3_days()