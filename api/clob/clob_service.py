import asyncio
import json
import httpx  # Better for async REST than requests
import websockets

class ClobService:
    def __init__(self):
        self.http_client = httpx.AsyncClient()
        self.active_ws = None
        self.should_run = True

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
        while self.should_run:  # Auto-reconnect loop
            try:
                async with websockets.connect(url) as ws:
                    self.active_ws = ws # Save reference for manual closing
                    await ws.send(json.dumps(subscribe_msg))
                    print(f"✅ Connected to {url}")
                    
                    async for message in ws:
                        if not self.should_run:
                            break

                        data = json.loads(message)
                        # Ensure we always deal with a list
                        messages = data if isinstance(data, list) else [data]
                        
                        for msg in messages:
                            await callback(msg) # Send data to your logic
                            
            except Exception as e:
                if self.should_run:
                    print(f"🔄 WSS Connection lost: {e}. Reconnecting in 5s...")
                    await asyncio.sleep(5)
                else:
                    print("🔌 Stream stopped by user.")
    
    async def close_clob_wss(self):
        """
        Signals the loop to stop and closes the active WebSocket.
        Also cleans up the HTTP client.
        """
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

    async def simulate_clob_failure(self):
        """Forcibly closes the socket to trigger an exception in the stream loop."""
        if self.active_ws:
            print("🔌 [TEST] Forcing a network failure...")
            # Closing with a non-standard code (like 1006) simulates an abnormal drop
            await self.active_ws.close(code=1006)
        else:
            print("❌ [TEST] No active connection to kill.")