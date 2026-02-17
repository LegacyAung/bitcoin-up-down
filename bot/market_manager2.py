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
        self.user_channel_ts = None
        self.rolling_timestamps = {'current': "", 'next': ""}
        self.is_pricediff_finished = False
        

    async def market_starter(self):
        if self.is_initialized:
            return
        
        self.is_initialized = True
        self.is_running = True
        print("🔐 Initializing L1/L2 Authentication...")

        try:
            # 1. Authenticate with CLOB
            await self.clob_rest.authenticate()

            print("🚀 Starting Binance WSS Stream...")
            asyncio.create_task(self.data_manager.handle_binance_wss_pipeline())
            
            print("🚀 Step 2: Fetching Binance Rest data...")
            await self.data_manager.handle_binance_rest_data()

            self.user_channel_ts = self._get_curr_res_ts()
            print("🚀 Step 3: Starting CLOB User Channel...")
            asyncio.create_task(self.data_manager.handle_clob_wss_pipeline(self.user_channel_ts, 'user', self.clob_rest))

            print("🚀 Step 3 1/2: Starting CLOB Market Channels...")
            asyncio.create_task(self._dynamic_clob_wss_monitor())

        
            print("🚀 Step 4: Starting 15m binance_rest...")
            asyncio.create_task(self._monitor_binance_rest_15m_persistance())
            

            if not self.is_pricediff_finished:
                print("🚀 Step 5: Starting persistance price diff...")
                asyncio.create_task(self._monitor_price_diff_persistance())
            
        except Exception as e:
            self.is_initialized = False
            print(f"🛑 Failed to start market analyzer: {e}")

        

    async def market_disconnector(self):
        if not self.is_initialized: return
        
        print("\n🛑 Initiating Shutdown...")
        self.is_running = False
        
        try: 
            await self.data_manager.handle_disconnect_binance_wss()
        except Exception as e:
            print(f"⚠️ Binance disconnect error: {e}")

        for ts in list(self.active_clob_streams):
            try:
                await self.data_manager.handle_disconnect_clob_wss(ts,'market')
            except Exception as e:
                print(f"⚠️ CLOB Market ({ts}) disconnect error: {e}")

        if self.user_channel_ts:
            try:
                await self.data_manager.handle_disconnect_clob_wss(self.user_channel_ts, 'user')
            except Exception as e:
                print(f"⚠️ CLOB User ({ts}) disconnect error: {e}")

        self.is_initialized = False






#----------------------------------Monitors-------------------------------------#

    async def _dynamic_clob_wss_monitor(self):
        if self.res_count == 0 :
                self.rolling_timestamps['current'] = self._get_curr_res_ts()
                self.rolling_timestamps['next'] = self._get_next_res_ts()
        
        while self.is_running:
            try: 
                self.delta_sec = self._get_delta_sec()
                if self.delta_sec >= 900:
                    old_next = self.rolling_timestamps['next']
                    self.rolling_timestamps['current'] = old_next
                    self.rolling_timestamps['next'] = self._get_next_res_ts()
                    self.res_count += 1
                    print(f"✅ Timestamps Rotated: {self.rolling_timestamps}")
                    await asyncio.sleep(1)
                    continue
                
                if self.delta_sec <= 30:
                    await self._manage_clob_wss(action='stop', slug_timestamp=self.rolling_timestamps.get('current'), status="current")
                elif self.delta_sec <= 300:
                    await self._manage_clob_wss(action='start', slug_timestamp=self.rolling_timestamps.get('next'), status="next")
                else:
                    await self._manage_clob_wss(action='start', slug_timestamp=self.rolling_timestamps.get('current'), status="current" )
                
                await asyncio.sleep(1)

            except Exception as e:
                print(f"⚠️ Monitor Error: {e}")
                await asyncio.sleep(5)

    async def _manage_clob_wss(self, action, slug_timestamp, status):
        
        if action == "start":
            if slug_timestamp not in self.active_clob_streams:
                self.active_clob_streams.add(slug_timestamp)
                asyncio.create_task(
                    self.data_manager.handle_clob_wss_pipeline(slug_timestamp, "market", self.clob_rest)
                )
                print(f"starting clob wss:  {status} and slug_timestamp  {slug_timestamp}")

        if action == "stop":
            if slug_timestamp in self.active_clob_streams:
                self.active_clob_streams.remove(slug_timestamp)
                asyncio.create_task(
                    self.data_manager.handle_disconnect_clob_wss(slug_timestamp, "market")
                )
                print(f"stopping clob wss: {status} and slug_timestamp: {slug_timestamp}")

    async def _monitor_binance_rest_15m_persistance(self):
        while self.is_running:
            try:
                if self.delta_sec >= 899:
                    await self.data_manager.handle_persistant_15m_binance_rest(self.delta_sec)
                    await asyncio.sleep(5)
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"⚠️ Binance REST Error: {e}")
                await asyncio.sleep(5)

    async def _monitor_price_diff_persistance(self):
        while self.is_running:
            try:
                if self.delta_sec == 0:
                    print("📊 Resolution Hit: Performing fresh Price Diff sync...")
                    await self.data_manager.handle_persistant_price_diff()
                    self.is_pricediff_finished = True
                    await asyncio.sleep(1) 
                else:
                    self.is_pricediff_finished = False
                    await self.data_manager.handle_persistant_price_diff()
                    await asyncio.sleep(1) 
                    
            except Exception as e:
                print(f"⚠️ Price Diff Error: {e}")
                await asyncio.sleep(5)

#-------------------------------HELPERS-----------------------------------#

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

