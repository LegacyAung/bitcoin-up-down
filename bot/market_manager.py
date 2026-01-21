import asyncio
import json
import time

from api.clob.clob_wss import ClobWss
from api.clob.clob_rest import ClobRest
from api.binance.binance_wss import BinanceWss
from .data_manager.data_manager import DataManager


class MarketManager:
    def __init__(self):
        self.clob_wss = ClobWss()
        self.clob_rest = ClobRest()
        self.binance_wss = BinanceWss()
        self.data_manager = DataManager(
            self.clob_wss,
            self.binance_wss
        )
        self.last_msg_time = time.time()
        self.is_running = True
    
    async def market_starter(self):
        params = ["btcusdt@kline_1m", "btcusdt@kline_1s"]
        """
        Leg 3: Initialize Authentication and Start Stream
        """
        print("🔐 Initializing L1/L2 Authentication...")
        try:
            # This enables both L1 (local signing) and L2 (API access)
            await self.clob_rest.authenticate()
            print("✅ Authentication Successful. Signer ready for L1.")

            # start clob websocket stream
            print("🚀 Starting PolyMarket Data Stream...")
            print("🚀 Starting Binance Market Data Stream...")
            await asyncio.gather(
                self.clob_wss.stream_market_data(self.data_manager.handle_clob_wss_data),
                self.binance_wss.stream_binance_data(params, self.data_manager.handle_binance_wss_data)
            )
        except Exception as e:
            print(f"🛑 Failed to start market analyzer: {e}")

    async def market_disconnector(self):
        print("\n🛑 Initiating Shutdown...")

        try:
            await self.clob_rest.cancel_all()
            print("✅ All orders cancelled.")

            await self.clob_wss.disconnect()
            print("🔌 websocket disconnected")

        except Exception as e:
            print(f"⚠️ Error during safe shutdown: {e}")
        finally:
            asyncio.get_event_loop().stop()

    async def update_heartbeat(self, msg):
        """Callback to update the clock every time data arrives"""
        self.last_msg_time = time.time()
    
    async def check_heartbeat(self, msg):
        while self.is_running:
            await asyncio.sleep(10)
            elapsed = time.time() - self.last_msg_time

            if elapsed > 30:
                print(f"⚠️ Connection stale ({int(elapsed)}s since last msg). Reconnecting...")
                await self.reconnect()


    async def reconnect(self):
        print("🔄 Performing soft reset of services...")
        await self.clob_wss.disconnect()
        await asyncio.sleep(2)


     
if __name__ == "__main__":
    analyzer = MarketManager()
    asyncio.run(analyzer.market_starter())