import requests
import time
from typing import Optional

EVENTS_GAMMA_ENDPOINT = "https://gamma-api.polymarket.com/events/slug/"
BTC_UPDOWN_15M = "btc-updown-15m"




def fetch_current_event_slug(active=True, closed=False):
    slug_timestamp = '1767596400'
    params = {
        "active":str(active).lower(),
        "closed":str(closed).lower()
    }
    res = requests.get(EVENTS_GAMMA_ENDPOINT + BTC_UPDOWN_15M + f"-{slug_timestamp}",params=params, timeout=10)

    res.raise_for_status()
    event = res.json()

    print(event)


fetch_current_event_slug(active=True, closed=False)



# def fetch_all_events(limit=100, closed=False, active=True):
#     EVENTS_GAMMA_ENDPOINT = "https://gamma-api.polymarket.com/events"
#     all_events = []
#     offset = 0

#     start_time = time.perf_counter() # starttime
    
#     while True:

#         params = {
#             "limit":limit,
#             "offset":offset,
#             "active":str(active).lower(),
#             "closed":str(closed).lower()
#         }

#         res = requests.get(EVENTS_GAMMA_ENDPOINT, params=params, timeout=10)

#         res.raise_for_status()

#         events = res.json()

#         # no events left, break
#         if not events:
#             break

#         # if event that start with slug "btc-updown-15m", then extend to the array 
#         for event in events:
#             slug = event.get("slug","")
#             if slug.startswith("btc-updown-15m"):
#                 all_events.append(event)
#         offset += limit

#     elapsed = time.perf_counter() - start_time #endtime
#     print(f"⏱ Time taken: {elapsed:.2f} seconds")
#     print(f"\n✅ Total btc-updown-15m events found: {len(all_events)}")

#     return all_events


# btc_15m_events = fetch_all_events()

# for e in btc_15m_events[:10]:
#     print(e["slug"], "| event_id:", e["id"])







