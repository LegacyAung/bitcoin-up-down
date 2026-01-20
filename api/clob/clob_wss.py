import asyncio
import json
from config import CLOB_WEBSOCKET
from services.clob_service import ClobService 
from ..gamma.gamma_rest import fetch_current_event_slug

class ClobWss:
    def __init__(self):
        # 1. Initialize Service and API Config
        self.clob_services = ClobService()
        self.wss_url = f"{CLOB_WEBSOCKET}/ws/market"
        

        self._current_event = self._get_current_event_slug()
        self.current_market = self._current_event['markets'][0]
        self.clob_ids = json.loads(self.current_market['clobTokenIds'])
        self.condition_id = self.current_market['conditionId']
        self.channels = [
            "book", 
            "price_change", 
            "last_trade_price", 
            "best_bid_ask", 
            "tick_size_change", 
            "new_market", 
            "market_resolved"
        ]

        # state management
        self.is_running = False
        self.last_callback = None


    def _get_current_event_slug(self):
        return fetch_current_event_slug()


    async def reconnect(self):
        """
        Closes existing connection and restarts the stream 
        using the previously saved callback.
        """
        print("🔄 Connection lost or stale. Attempting to reconnect...")
        # 1. Clean up (The service layer should handle closing the actual socket)
        self.is_running = False
        await asyncio.sleep(2) # Short buffer to avoid rapid-fire looping
        # 2. Restart the stream
        if self.last_callback:
            await self.stream_market_data(self.last_callback)

    async def disconnect(self):
        """
        Gracefully stops the stream and prevents automatic reconnection.
        """
        print("🔌 Disconnecting WebSocket...")
        self.is_running = False  # Critical: stops the reconnect loop
        try:
            await self.clob_services.close_clob_wss()
        except Exception as e:
            print(f"⚠️ Error during disconnect: {e}")
        print("✅ WebSocket disconnected.")

# --- CLOB WSS Data Streaming Starter ---
    async def stream_market_data(self,callback):
        self.last_callback = callback
        self.is_running = True

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

        try:
            await self.clob_services.stream_clob_wss(
                url = self.wss_url,
                subscribe_msg=subscribe_msg,
                callback=callback
            )
        except Exception as e:
            if self.is_running:
                await self.reconnect()

        


if __name__ == "__main__":
    pass