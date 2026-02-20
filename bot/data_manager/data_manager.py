import asyncio

from .data_fetcher import DataFetcher
from .data_persistance import DataPersistance
from .data_synthesizer import DataSynthesizer
from .data_distributor import DataDistributor
from .data_config import MarketConfig

from functools import partial

class DataManager:

    def __init__(self):

        self.data_config = MarketConfig()
        self.binance_rest_configs = self.data_config.binance_rest 
        self.binance_wss_params = self.data_config.binance_wss
        self.clob_wss_channels = self.data_config.clob_wss   


        self.data_fetcher = DataFetcher()
        self.data_persistance = DataPersistance()
        self.data_synthesizer = DataSynthesizer()
        self.data_distributor = DataDistributor()
        
        self.first_data_received = asyncio.Event()

        
        
        
#------------------------ BINANCE--------------------------#
    async def handle_binance_rest_data(self):
        for config in self.binance_rest_configs:
            print(config)
            raw_data = await self.data_fetcher.fetch_binance_rest(
                config.mins, config.interval, config.symbol
            )

            df = await self.data_synthesizer.synthesize_raw_binance_rest_data(raw_data)
            await self.data_distributor.distribute_binance_rest(
                df, config.interval, config.label 
            )
    
    async def handle_binance_wss_pipeline(self):
        await self.data_fetcher.open_binance_wss(self.data_config.binance_wss, self._handle_binance_wss_data)
        
    async def handle_disconnect_binance_wss(self):
        await self.data_fetcher.close_binance_wss()


#--------------------------CLOB_WSS---------------------------#
    async def handle_clob_wss_pipeline(self, slug_timestamp, channel_type, clob_rest):
        sub_msg = await self._handle_gamma_rest_submsg(slug_timestamp=slug_timestamp)
        bound_loads = {
            "slug_timestamp": slug_timestamp,
            "channel_type": channel_type,
            "sub_msg":sub_msg
        }
        bound_handler = partial(self._handle_clob_wss_data, bound_loads=bound_loads)
        await self.data_fetcher.open_clob_wss(channel_type, sub_msg, clob_rest, bound_handler)
        
    async def handle_disconnect_clob_wss(self, slug_timestamp, channel_type):
        sub_msg = await self._handle_gamma_rest_submsg(slug_timestamp=slug_timestamp)
        condition_id = sub_msg['condition_id']
        await self.data_fetcher.close_clob_wss(channel_type, condition_id)
        


#--------------------------PERSISTANCE_HANDLERS---------------------------#
    async def handle_persistant_15m_binance_rest(self, delta_sec):
        config = self.binance_rest_configs[2]

        
        df = await self.data_persistance.persistantly_get_binance_rest(15, config.interval, config.symbol, delta_sec)
            
        if df is not None and not df.empty:

            closed_df = df.iloc[[0]] #taking the first row of the persistant df
                
                
            await self.data_distributor.distribute_persistant_binance_rest(closed_df, config.interval, config.label)
            print(f"🔄 Boss Updated: {config.label} sync complete.")

        await asyncio.sleep(1)

    async def handle_persistant_price_diff(self):
        
            
        current_buffers = self.data_distributor.buffers

        price_gap = await self.data_persistance.persistantly_get_price_diff(
            buffers = current_buffers,
            label_1s = self.binance_rest_configs[0].label,
            label_15m = self.binance_rest_configs[2].label,
        ) 
            
        if price_gap is not None:
            print(f"📊 Live Gap: {price_gap}")
        await asyncio.sleep(1)

    

#--------------------------HELPERS---------------------------#
    async def _handle_binance_wss_data(self, msg):
        if not self.first_data_received.is_set():
            self.first_data_received.set()
            print("📥 First Binance WSS message received! Triggering REST fetch...")
        
        if 'k' not in msg:
            if 'result' in msg:
                print("🚀 Subscription successful, waiting for first candle...")
            return 
        kline = msg['k']
        if kline.get('x'): 
            df = await self.data_synthesizer.synthesize_raw_binance_wss_data(msg)
            
            if df is not None:
                interval = kline.get('i')
                await self.data_distributor.distribute_binance_wss(df=df, interval=interval)
                
    async def _handle_clob_wss_data(self, msg, bound_loads=None):

        events = msg if isinstance(msg, list) else [msg]

        for event in events:
            e_type = event.get("event_type")

            if not e_type: continue

            method_name = f"synthesize_raw_clob_wss_{e_type}"
            handler = getattr(self.data_synthesizer, method_name)
            
            data = await handler(event)
            
            await self.data_distributor.distribute_clob_wss(data, e_type, bound_loads)
            
    async def _handle_gamma_rest_submsg(self, slug_timestamp):
        return await self.data_fetcher.fetch_submsg_clobwss(timestamp=slug_timestamp, channels=self.clob_wss_channels)







async def main():
    data_manager = DataManager()
    await data_manager._handle_gamma_rest_submsg()

if __name__ == "__main__":
    asyncio.run(main())

