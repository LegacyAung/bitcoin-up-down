import asyncio
import json

from api.binance.binance_rest import BinanceRest
from api.clob.clob_rest import ClobRest
from api.clob.clob_wss import ClobWss
from api.clob.clob_rest import ClobRest
from api.binance.binance_wss import BinanceWss
from .data_synthesizer import DataSynthesizer
from .data_distributor import DataDistributor

class DataManager:
    def __init__(self, clob_wss, binance_wss):
        self.clob_wss = clob_wss
        self.clob_wss_market_data = None
        self.binance_wss = binance_wss
        self.binance_wss_market_data = None

        self.clob_rest = ClobRest()
        self.binance_rest = BinanceRest()
        self.data_synthesizer = DataSynthesizer()
        self.data_distributor = DataDistributor()

        # Configuration for your 3 legs
        self.rest_configs = [
            {"mins": 15,  "interval": "1s",  "label": "1hr_1s"},
            {"mins": 1440, "interval": "1m",  "label": "1day_1m"},
            {"mins": 1440, "interval": "15m", "label": "1day_15m"}
        ]

    async def handle_clob_wss_data(self,msg):
        self.clob_wss_market_data = msg
        
    async def handle_binance_wss_data(self, msg):
        """Processes all 2 legs of WSS data dynamically."""
        if 'k' not in msg:
            if 'result' in msg:
                print("🚀 Subscription successful, waiting for first candle...")
            return 
        
        # 2. DATA PROCESSING
        kline = msg['k']
        if kline.get('x'):  # Only process when candle is closed
            # Send to synthesizer
            df = await self.data_synthesizer.synthesize_raw_binance_wss_data(msg)
            if df is not None:
                interval = kline.get('i')
                await self.data_distributor.distribute_binance_wss(df=df, interval=interval)

    async def handle_binance_rest_data(self):
        """Processes all 3 legs of REST data dynamically."""
        tasks = []
        for config in self.rest_configs:
            tasks.append(self._fetch_and_distribute_rest(config))
        await asyncio.gather(*tasks)
        
    async def handle_current_event_snapshot(self):
        data = await asyncio.gather(
           self.clob_rest.fetch_order_book(),
           self.clob_rest.fetch_last_price(),
           self.clob_rest.fetch_price_history()
        )
        return data
    
    


    
    async def _fetch_and_distribute_rest(self, config):
        """Single helper for all REST calls."""
        raw = await self.binance_rest.get_binance_rest_data(config['mins'], config['interval'], "BTCUSDT")
        df = await self.data_synthesizer.synthesize_raw_binance_rest_data(raw)
        await self.data_distributor.distribute_binance_rest(
            df=df, interval=config['interval'], label=config['label']
        )
   
    
        
    

    
    
async def main():
    # 1. Initialize the components
    clob_wss = ClobWss()
    binance_wss = BinanceWss()
    
    # 2. Initialize DataManager
    data_manager = DataManager(clob_wss, binance_wss)
    
    # 3. CALL the async method using await
    print("🚀 Triggering market snapshot...")
    data = await data_manager.handle_1day_1m_binance_rest_data()
    print(data)

if __name__ == "__main__":
    # Start the asyncio event loop
    asyncio.run(main())





