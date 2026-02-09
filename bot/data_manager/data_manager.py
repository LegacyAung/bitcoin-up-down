import asyncio

from .data_fetcher import DataFetcher
from .data_persistance import DataPersistance
from .data_synthesizer import DataSynthesizer
from .data_distributor import DataDistributor
from .data_config import MarketConfig


class DataManager:

    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.data_persistance = DataPersistance()
        self.data_synthesizer = DataSynthesizer()
        self.data_distributor = DataDistributor()
        self.data_config = MarketConfig()


        self.binance_rest_configs = self.data_config.binance_rest 
        self.binance_wss_params = self.data_config.binance_wss
        self.clob_wss_channels = self.data_config.clob_wss   
        
        

    async def handle_binance_rest_data(self):
        for config in self.binance_rest_configs:
            raw_data = await self.data_fetcher.fetch_binance_rest(
                config['mins'], config['interval'], config['symbol']
            )
            df = await self.data_synthesizer.synthesize_raw_binance_rest_data(raw_data)
            await self.data_distributor.distribute_binance_rest(
                df, config['interval'], config['label'] 
            )
    
    async def handle_wss_pipeline(self):
        await asyncio.gather(
            self.data_fetcher.fetch_binance_wss(
                self.binance_wss_params, self._handle_binance_wss_data
            ),
            self.data_fetcher.fetch_clob_wss(self._handle_clob_wss_data)
        )
    
    async def handle_binance_wss_pipeline(self):
        await self.data_fetcher.fetch_binance_wss(
            self.binance_wss_params, self._handle_clob_wss_data
        )

    async def handle_clob_wss_pipeline(self, slug_timestamp):
        sub_msg = await self._handle_gamma_rest_submsg(slug_timestamp=slug_timestamp)
        await self.data_fetcher.fetch_clob_wss(self._handle_clob_wss_data, sub_msg=sub_msg)

    async def handle_persistant_15m_binance_rest(self):
        config = self.binance_rest_configs[2]

        while True:
            df = await self.data_persistance.persistantly_get_binance_rest(15, config['interval'], config['symbol'])
            
            if df is not None and not df.empty:

                closed_df = df.iloc[[0]] #taking the first row of the persistant df
                
                
                await self.data_distributor.distribute_persistant_binance_rest(closed_df, config['interval'], config['label'])
                print(f"🔄 Boss Updated: {config['label']} sync complete.")

            await asyncio.sleep(1)

    async def handle_persistant_price_diff(self):
        while True:
            
            current_buffers = self.data_distributor.buffers

            price_gap = await self.data_persistance.persistantly_get_price_diff(
                buffers = current_buffers,
                label_1s = self.binance_rest_configs[0]['label'],
                label_15m = self.binance_rest_configs[2]['label'],
                mins = 15
            ) 
            
            if price_gap is not None:
                print(f"📊 Live Gap: {price_gap}")
            await asyncio.sleep(1)




    async def _handle_binance_wss_data(self, msg):
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

    async def _handle_clob_wss_data(self, msg):
        
        events = msg if isinstance(msg, list) else [msg]

        for event in events:
            e_type = event.get("event_type")
            if not e_type: continue

            method_name = f"synthesize_raw_clob_wss_{e_type}"
            handler = getattr(self.data_synthesizer, method_name)

            if not handler: return

            if e_type == "new_market":
                df = await handler(event)
                print("🆕new market scouter: ",df)

    async def _handle_gamma_rest_submsg(self, slug_timestamp):
        return await self.data_fetcher.fetch_submsg_clob_wss(timestamp=slug_timestamp, channels=self.clob_wss_channels)
        





async def main():
    pass

if __name__ == "__main__":
    asyncio.run(main())

