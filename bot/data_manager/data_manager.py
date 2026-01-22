import asyncio
import json

from api.binance.binance_rest import BinanceRest
from api.clob.clob_rest import ClobRest
from api.clob.clob_wss import ClobWss
from api.clob.clob_rest import ClobRest
from api.binance.binance_wss import BinanceWss
from api.gamma.gamma_rest import fetch_event_slug, fetch_current_event_slug
from utils.time import get_market_window_timestamps
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

    async def handle_clob_wss_data(self,msg):
        self.clob_wss_market_data = msg
        
        

    async def handle_binance_wss_data(self,msg):
        if 'result' in msg:
            print("⚠️ Received empty or malformed message from WebSocket.")
            return
        else:
            self.binance_wss_market_data = msg
            await asyncio.gather(
                self._handle_1s_binance_wss_data(),
                self._handle_1min_binance_wss_date()
            )
            print("✅binance wss is passing down data stream")


    async def handle_binance_rest_data(self):
        await asyncio.gather(
            self._handle_6hrs_1s_binance_rest_data(),
            self._handle_1day_1m_binance_rest_data(),
            self._handle_1day_15m_binanace_rest_data()
        )
        
    async def handle_current_event_snapshot(self):
        data = await asyncio.gather(
           self.clob_rest.fetch_order_book(),
           self.clob_rest.fetch_last_price(),
           self.clob_rest.fetch_price_history()
        )
        return data
    
    async def handle_current_slug(self):
        return fetch_current_event_slug(active=True, closed=False)
    
    async def handle_previous_slug(self):
        timestamps = get_market_window_timestamps()
        prev_timestamp = timestamps[0]
        return fetch_event_slug(active=False,closed=True,timestamp=prev_timestamp)


    # for MACD data
    async def _handle_1day_1m_binance_rest_data(self):
        raw_data_list = await self.binance_rest.get_binance_rest_data(24,"1m","BTCUSDT")
        df = await self.data_synthesizer.synthesize_raw_binance_rest_data(raw_data_list=raw_data_list)
        await self.data_distributor.distribute_binance_rest_to_macd(df=df, interval='1m', label='1day_1m')
    
    
    async def _handle_1day_15m_binanace_rest_data(self):
        raw_data_list = await self.binance_rest.get_binance_rest_data(24,"15m","BTCUSDT")
        df = await self.data_synthesizer.synthesize_raw_binance_rest_data(raw_data_list=raw_data_list)
        await self.data_distributor.distribute_binance_rest_to_macd(df=df, interval='15m', label='1day_15m')
    
    async def _handle_6hrs_1s_binance_rest_data(self):
        raw_data_list = await self.binance_rest.get_binance_rest_data(6,"1s","BTCUSDT")
        df = await self.data_synthesizer.synthesize_raw_binance_rest_data(raw_data_list=raw_data_list)
        await self.data_distributor.distribute_binance_rest_to_macd(df=df, interval='6hr', label='6hr_1s')
    
    async def _handle_1min_binance_wss_date(self):
        while self.binance_wss_market_data is None:
            print("⏳ Waiting for first Binance WSS message...")
            await asyncio.sleep(0.5)
        kline = self.binance_wss_market_data.get('k')
        if kline['T'] - kline['t'] == 5999 and kline['x'] == True:
            df = self.data_synthesizer.synthesize_raw_binance_wss_data(self.binance_wss_market_data)
            await self.data_distributor.distribute_binance_wss_to_macd(df=df)
        
    async def _handle_1s_binance_wss_data(self):
        while self.binance_wss_market_data is None:
            print("⏳ Waiting for first Binance WSS message...")
            await asyncio.sleep(0.5)
        kline = self.binance_wss_market_data.get('k')
        if kline['T'] - kline['t'] == 999 and kline['x'] == True:
            df = self.data_synthesizer.synthesize_raw_binance_wss_data(self.binance_wss_market_data)
            await self.data_distributor.distribute_binance_wss_to_macd(df=df)
        
    

    
    
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





