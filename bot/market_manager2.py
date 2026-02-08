import asyncio

from api.clob.clob_rest import ClobRest
from .data_manager.data_manager import DataManager
from .time_manager.time_manager import TimeManager



class MarketManager:
    def __init__(self):
        self.clob_rest = ClobRest()
        self.data_manager = DataManager()
        self.time_manager = TimeManager()
        

        self.is_running = False
        self.delta_sec = None
        self.is_initialized = False
        self.res_count = 0

    async def market_starter(self):
        if self.is_initialized:
            return
        
        self.is_initialized = True
        print("🔐 Initializing L1/L2 Authentication...")

        try:
            # This enables both L1 (local signing) and L2 (API access)
            await self.clob_rest.authenticate()
            print("✅ Authentication Successful. Signer ready for L1.")

            # print("🚀 Starting Binance & PolyMarket WSS Streams...")
            # binance_task = asyncio.create_task(self.data_manager.handle_binance_wss_pipeline())
            # clob_task = asyncio.create_task(self.data_manager.handle_clob_wss_pipeline())

            print("🚀 Starting PolyMarket Data Stream...")
            print("🚀 Starting Binance Market Data Stream...")
            wss_task = asyncio.create_task(self.data_manager.handle_wss_pipeline())
            
            print("🚀 fetching Binance Rest data...")
            asyncio.create_task(self.data_manager.handle_binance_rest_data())

            print("🔄 Starting Persistent 15m Heartbeat...")
            asyncio.create_task(self.data_manager.handle_persistant_15m_binance_rest())

            print("🔄 Starting Persistent Price Difference (Price to beat)")
            asyncio.create_task(self.data_manager.handle_persistant_price_diff())

            await wss_task
        except Exception as e:
            self.is_initialized = False
            print(f"🛑 Failed to start market analyzer: {e}")

        self.is_running = True

    async def market_disconnector(self):
        print("\n🛑 Initiating Shutdown...")


    
    
    
    async def _dya_clob_wss_monitor(self):
        while self.is_running:
            self.delta_sec = self._get_delta_sec()

            pass


    
    def _get_delta_sec(self):
        countdown_15m = self.time_manager.handle_time_persistance(res_sec=900) 
        return countdown_15m.get('delta_sec')

    def _get_next_resolution_timestamp(self):
        next_res_ts = self.time_manager.get_next_res_ts()
        return next_res_ts




if __name__ == "__main__":
    market_manager = MarketManager()
    asyncio.run(market_manager.market_starter())