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
        self.is_initialized = False
        self.delta_sec = 0
        self.res_count = 0
        
        self.active_clob_streams = set()
        self.rolling_timestamps = {'current': "", 'next': ""}
        

    async def market_starter(self):
        if self.is_initialized:
            return
        
        self.is_initialized = True
        self.is_running = True
        print("🔐 Initializing L1/L2 Authentication...")

        try:
            # This enables both L1 (local signing) and L2 (API access)
            await self.clob_rest.authenticate()
            print("✅ Authentication Successful. Signer ready for L1.")

            print("🚀 Starting Binance WSS Stream...")
            binance_task = asyncio.create_task(self.data_manager.handle_binance_wss_pipeline())
            #clob_task = asyncio.create_task(self.data_manager.handle_clob_wss_pipeline())

            # print("🚀 Starting PolyMarket Data Stream...")
            # wss_task = asyncio.create_task(self.data_manager.handle_wss_pipeline())
            
            print("🚀 fetching Binance Rest data...")
            asyncio.create_task(self.data_manager.handle_binance_rest_data())

            print("🔄 Starting Persistent 15m Heartbeat...")
            asyncio.create_task(self.data_manager.handle_persistant_15m_binance_rest())

            print("🔄 Starting Persistent Price Difference (Price to beat)")
            asyncio.create_task(self.data_manager.handle_persistant_price_diff())

            await binance_task
        except Exception as e:
            self.is_initialized = False
            print(f"🛑 Failed to start market analyzer: {e}")

        

    async def market_disconnector(self):
        print("\n🛑 Initiating Shutdown...")

        
    async def _dynamic_clob_wss_monitor(self):
        self.rolling_timestamps['current'] = self._get_curr_res_ts()
        self.rolling_timestamps['next'] = self._get_next_res_ts()

        while True:
            try: 
                self.delta_sec = self._get_delta_sec()
                if self.delta_sec == 0:
                    self.rolling_timestamps['current'] = self._get_curr_res_ts()
                    self.rolling_timestamps['next'] = self._get_next_res_ts()    

                if self.delta_sec <= 30:
                    await self._manage_clob_wss(action='stop', slug_timestamp=self.rolling_timestamps.get('current'), status="current")
                elif self.delta_sec <= 300:
                    await self._manage_clob_wss(action='start', slug_timestamp=self.rolling_timestamps.get('next'), status="next")
                else:
                    await self._manage_clob_wss(action='start', slug_timestamp=self.rolling_timestamps.get('current'), status="current" )
 
            except Exception as e:
                print(f"⚠️ Monitor Error: {e}")
                await asyncio.sleep(5)

    async def _manage_clob_wss(self, action, slug_timestamp, status):
        
        if action == "start":
            if slug_timestamp not in self.active_clob_streams:
                self.active_clob_streams.add(slug_timestamp)
                asyncio.create_task(
                    self.data_manager.handle_clob_wss_pipeline(slug_timestamp=slug_timestamp)
                )
                print(f"starting clob wss:  {status} and slug_timestamp  {slug_timestamp}")

        if action == "stop":
            if slug_timestamp in self.active_clob_streams:
                self.active_clob_streams.remove(slug_timestamp)
                print(f"stopping clob wss: {status} and slug_timestamp: {slug_timestamp}")

    def _get_delta_sec(self):
        countdown_15m = self.time_manager.handle_time_persistance(res_sec=900) 
        return countdown_15m.get('delta_sec')

    def _get_next_res_ts(self):
        next_res_ts = self.time_manager.get_next_res_ts()
        return next_res_ts
    
    def _get_curr_res_ts(self):
        curr_res_ts = self.time_manager.get_curr_res_ts()
        return curr_res_ts



if __name__ == "__main__":
    market_manager = MarketManager()
    asyncio.run(market_manager.market_starter())

