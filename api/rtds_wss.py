import asyncio
import websockets
import json

from config import RTDS_WEBSOCKET



#get current btc price from data chainlink
async def stream_btcusdt_price_chainlink():
    websocket_url = RTDS_WEBSOCKET

    
    async with websockets.connect(websocket_url, ping_interval=5, ping_timeout=10) as websocket:
        print(f"Connected to RTDS: {websocket_url}")

        # Subscription for Chainlink BTC/USD
        subscribe_msg = {
            "action": "subscribe",
            "subscriptions": [
                {
                    "topic": "crypto_prices_chainlink",
                    "type": "*",
                    "filters": json.dumps({"symbol": "btc/usd"})  # Chainlink uses slash format
                }
            ]
        }

        await websocket.send(json.dumps(subscribe_msg))

        async for message in websocket:
            if not message or not message.strip():
                continue

            try:
                # 2. Now it's safe to parse
                data = json.loads(message)
                payload = data.get('payload', {})

                if 'data' in payload and isinstance(payload['data'], list):
                    print(f"\n--- Historical Data for {payload.get('symbol')} ---")
                    for entry in payload['data']:
                        ts = entry.get('timestamp')
                        val = entry.get('value')
                        print(f"timestamp: {ts} || value: {val}")
                    print("--- End of History ---\n")
                
                # Check for single live updates (sent after the initial dump)
                elif data.get("type") == "update":
                    ts = payload.get('timestamp')
                    val = payload.get('value')
                    print(f"timestamp: {ts} || value: {val}")
                
            except json.JSONDecodeError:
                print(f"Received non-JSON message: {message}")



    websocket_url = RTDS_WEBSOCKET

    async with websockets.connect(websocket_url, ping_interval=5, ping_timeout=10) as websocket:
        print(f"Connected to RTDS: {websocket_url}")

        subscribe_msg = {
            "action": "subscribe", 
            "subscriptions": [
                {
                "topic": "crypto_prices",
                "type": "update",
                "filters": json.dumps({"symbol": "btcusdt"})
                }
            ]
        }

        await websocket.send(json.dumps(subscribe_msg))

        async for message in websocket:
            if not message or not message.strip():
                continue
            try:
                data = json.loads(message)
                payload_data = data.get('payload', {})
                
                # Filter for the continuous Binance price updates
                print(payload_data)
            except json.JSONDecodeError:
                pass
             
if __name__ == "__main__":
    try:
        asyncio.run(stream_btcusdt_price_chainlink())
    except KeyboardInterrupt:
        print("Stream stopped by user.")
