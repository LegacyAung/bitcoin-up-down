import asyncio
import websockets
import json
from datetime import datetime

# Use your config import
# from config import RTDS_WEBSOCKET 
RTDS_WEBSOCKET = "wss://ws-live-data.polymarket.com"

async def stream_btcusdt_price_chainlink():
    url = RTDS_WEBSOCKET
    
    while True:  # The persistence loop
        try:
            async with websockets.connect(url, ping_interval=5, ping_timeout=10) as ws:
                print(f"🚀 {datetime.now().strftime('%H:%M:%S')} - Connected to RTDS")

                subscribe_msg = {
                    "action": "subscribe",
                    "subscriptions": [{
                        "topic": "crypto_prices_chainlink",
                        "type": "*",
                        "filters": json.dumps({"symbol": "btc/usd"})
                    }]
                }
                await ws.send(json.dumps(subscribe_msg))

                # The listener loop
                async for message in ws:
                    if not message or not message.strip():
                        continue # Skip empty "Keep-Alive" messa
                    data = json.loads(message)
                    payload = data.get('payload', {})

                    # 1. Handle the Initial History Dump
                    if 'data' in payload and isinstance(payload['data'], list):
                        print(f"\n--- History Received ({len(payload['data'])} points) ---")
                        for entry in payload['data']:
                            print(f"Time: {entry.get('timestamp')} | Price: {entry.get('value')}")
                        
                        print("--- End of History: Reconnecting for fresh dump... ---\n")
                        # BREAK HERE to trigger the outer loop's reconnect
                        break 
                    
                    # 2. Handle Live Updates (if you want to stay connected, don't break above)
                    elif data.get("type") == "update":
                        print(f"LIVE: {payload.get('value')}")

                # Small delay to prevent spamming the server
                await asyncio.sleep(1) 

        except Exception as e:
            print(f"❌ Connection Error: {e}. Retrying in 5s...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(stream_btcusdt_price_chainlink())
    except KeyboardInterrupt:
        print("\n👋 Stream stopped by user.")