import asyncio
import time


from api.clob.clob_rest import ClobRest
from .data_manager.data_manager import DataManager



class MarketManager:
    def __init__(self):
        self.clob_rest = ClobRest()
        self.data_manager = DataManager()
        self.last_msg_time = time.time()
        self.is_running = True

    async def market_starter(self):

        print("🔐 Initializing L1/L2 Authentication...")

        try:
            # This enables both L1 (local signing) and L2 (API access)
            await self.clob_rest.authenticate()
            print("✅ Authentication Successful. Signer ready for L1.")

            print("🚀 Starting PolyMarket Data Stream...")
            print("🚀 Starting Binance Market Data Stream...")
            wss_task = asyncio.create_task(self.data_manager.handle_wss_pipeline())
            
            print("🚀 fetching Binance Rest data...")
            asyncio.create_task(self.data_manager.handle_binance_rest_data())

            print("🔄 Starting Persistent 15m Heartbeat...")
            asyncio.create_task(self.data_manager.handle_persistant_15m_binance_rest())

            await wss_task

        except Exception as e:
            print(f"🛑 Failed to start market analyzer: {e}")



if __name__ == "__main__":
    market_manager = MarketManager()
    asyncio.run(market_manager.market_starter())