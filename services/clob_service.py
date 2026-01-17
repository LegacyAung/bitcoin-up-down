import asyncio
import json
import httpx  # Better for async REST than requests
import websockets

class ClobService:
    def __init__(self):
        self.http_client = httpx.AsyncClient()

    async def get_clob_rest(self, url, params=None, timeout=10):
        """Async REST request that won't block the event loop."""
        try:
            res = await self.http_client.get(url, params=params, timeout=timeout)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            print(f"❌ REST Error: {e}")
            return None

    async def stream_clob_wss(self, url, subscribe_msg, callback):
        """
        Reusable WebSocket streamer. 
        Pass a 'callback' function to handle data as it arrives.
        """
        while True:  # Auto-reconnect loop
            try:
                async with websockets.connect(url) as ws:
                    await ws.send(json.dumps(subscribe_msg))
                    print(f"✅ Connected to {url}")
                    
                    async for message in ws:
                        data = json.loads(message)
                        # Ensure we always deal with a list
                        messages = data if isinstance(data, list) else [data]
                        
                        for msg in messages:
                            await callback(msg) # Send data to your logic
                            
            except Exception as e:
                print(f"🔄 WSS Connection lost: {e}. Reconnecting in 5s...")
                await asyncio.sleep(5)

