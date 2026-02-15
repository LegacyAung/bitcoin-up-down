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
        

