import asyncio
import json
from config import CLOB_ENDPOINT, CLOB_WEBSOCKET
from .gamma_api import fetch_current_event_slug
from services.clob_service import ClobService 


class ClobApi:

    def __init__(self):
        # 1. Initialize Service and API Config
        self.clob_services = ClobService()
        self.clob_endpoint = CLOB_ENDPOINT
        self.wss_url = f"{CLOB_WEBSOCKET}/ws/market"

        # 2. Fetch and Store IDs as class-wide attributes
        current_event = fetch_current_event_slug()
        self.market = current_event['markets'][0]
        self.clob_ids = json.loads(self.market['clobTokenIds'])
        self.condition_id = self.market['conditionId']
        self.channels = [
            "book", 
            "price_change", 
            "last_trade_price", 
            "best_bid_ask", 
            "tick_size_change", 
            "new_market", 
            "market_resolved"
        ]

        print(f"✅ Market Initialized. UP: {self.clob_ids[0][:8]}... | DOWN: {self.clob_ids[1][:8]}...")

    # --- CLOB REST Data Fetchers ---
    async def fetch_order_book(self):
        """Returns the current buy/sell depth for a specific token"""
        url = f"{self.clob_endpoint}/book"
        return await self.clob_services.get_clob_rest(url,params={'token_id':self.clob_ids})

    async def fetch_last_price(self, side="buy"):
        """Returns the current market price for a side (buy/sell)"""

        url = f"{CLOB_ENDPOINT}/price"
        return await self.clob_services.get_clob_rest(url, params={
                "token_id":self.clob_ids, 
                "side":side
            })

    async def fetch_price_history(self, interval='1h', fidelity=1):
        """Returns the historical odds (probability) for the token"""
        
        url = f"{CLOB_ENDPOINT}/prices-history"
        return await self.clob_services.get_clob_rest(url, params={
            "market": self.clob_ids,
            "interval": interval,
            "fidelity": fidelity
        })
    

    # --- CLOB WSS Data Fetchers ---
    async def stream_market_data(self,callback): 
        """
        Generic method to stream any combination of public channels.
        Supported channels: ["book", "price_change", "last_trade_price", "best_bid_ask", "tick_size_change", "new_market", "market_resolved"]
        """
        subscribe_msg = {
            "type": "subscribe",
            "assets_ids": self.clob_ids,  # Subscribes to both Up and Down
            "channels": self.channels
        }

        print(f"🚀 Streaming Channels: {self.channels}")

        await self.clob_services.stream_clob_wss(
            url = self.wss_url,
            subscribe_msg=subscribe_msg,
            callback=callback
        )

    


async def my_callback(msg):
    # This captures every single raw JSON object from all channels
    print(f"Incoming {msg.get('event_type')} data...")
    # Add your logic to store in a DataFrame or send to model here

if __name__ == "__main__":
    api = ClobApi()
    
    # Define all public channels available
    all_channels = ["book", "price_change", "last_trade_price"]
    
    # Run the generic stream
    try:
        asyncio.run(api.stream_market_data(all_channels, my_callback))
    except KeyboardInterrupt:
        print("🛑 Stopped.")