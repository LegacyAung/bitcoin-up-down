import asyncio
import websockets
import json
from config import CLOB_WEBSOCKET
from .gamma import fetch_current_event_slug


async def stream_polymarket_data():
    websocket_url = f"{CLOB_WEBSOCKET}/ws/market"

    market_data = fetch_current_event_slug()
    asset_ids = market_data.get('clob_token_ids')


    async with websockets.connect(websocket_url) as websocket:

        subscribe_msg = {
            "type": "market",
            "assets_ids":asset_ids
        }

        await websocket.send(json.dumps(subscribe_msg))


        async for message in websocket:
            # Parse the JSON message
            raw_data = json.loads(message)
            
            # Ensure raw_data is a list so we can loop through it
            # If it's a single dict, wrap it in a list to use the same logic
            messages = raw_data if isinstance(raw_data, list) else [raw_data]

            for data in messages:

                print(data)
                # Now data is a dictionary, so .get() will work
                # if data.get("event_type") == "book":
                #     asset = data.get("asset_id")
                #     bids = data.get("bids", [])
                #     asks = data.get("asks", [])

                #     print("-" * 30)
                #     print(f"ORDERBOOK | Asset: {asset[:8]}...")
                    
                #     # Show top 3 Bids (Buyers)
                #     print("BIDS (Buyers):")
                #     for b in bids[:3]:
                #         print(f"  Price: {b['price']} | Size: {b['size']}")
                    
                #     # Show top 3 Asks (Sellers)
                #     print("ASKS (Sellers):")
                #     for a in asks[:3]:
                #         print(f"  Price: {a['price']} | Size: {a['size']}")
                #     print("-" * 30)




# Run the stream
if __name__ == "__main__":
    asyncio.run(stream_polymarket_data())


