import asyncio
import websockets
import httpx
import json

class BinanceService:
    def __init__(self):
        self.http_client = httpx.AsyncClient()
        self.active_ws = None
        self.should_run = True

    async def get_binance_rest(self, url, params=None, timeout=10):
        """Async REST request that won't block the event loop."""
        try: 
            res= await self.http_client.get(url,params=params,timeout=timeout)
            res.raise_for_status()
            return res.json() 

        except httpx.RequestError as e:
            print(f"❌ Binance API Error: {e}")
            return None
        

    async def stream_binance_wss(self, url, subscribe_msg, callback):
        """
        Reusable WebSocket streamer. 
        Pass a 'callback' function to handle data as it arrives.
        """

        while self.should_run:
            try:
                async with websockets.connect(url) as ws:
                    print("ws stuff: ", ws)
                    self.active_ws = ws # Save reference for manual closing
                    await ws.send(json.dumps(subscribe_msg))
                    print(f"✅ Connected to {url}")
                    while self.should_run:
                        message = await ws.recv()
                        data = json.loads(message)
                        await callback(data)
            except Exception as e:
                if self.should_run:
                    print(f"🔄 WSS Connection lost: {e}. Reconnecting in 5s...")
                    await asyncio.sleep(5)
                else:
                    print("🔌 Stream stopped by user.")


    async def close_binance_wss(self):
        print("🛑 Initiating ClobService Shutdown...")
        self.should_run = False 
        
        if self.active_ws:
            try:
                await self.active_ws.close()
                self.active_ws = None
                print("✅ WebSocket closed.")
            except Exception as e:
                print(f"⚠️ Error closing WebSocket: {e}")

        # 2. Close the HTTP client
        try:
            await self.http_client.aclose()
            print("✅ HTTP Client closed.")
        except Exception as e:
            print(f"⚠️ Error closing HTTP client: {e}")