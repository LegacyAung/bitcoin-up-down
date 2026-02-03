import asyncio

from ..time_manager.time_manager import TimeManager
from .data_fetcher import DataFetcher
from .data_synthesizer import DataSynthesizer
from .data_distributor import DataDistributor

class DataPersistance:
    def __init__(self):
        self.time_manager = TimeManager()
        self.data_fetcher = DataFetcher()
        self.data_synthesizer = DataSynthesizer()
        self.data_distributor = DataDistributor()

    async def persistantly_get_binance_rest(self,mins,interval,symbol):
        min_to_sec = mins * 60
        min_for_binance_rest = mins * 2
        time_data = self.time_manager.handle_time_persistance(min_to_sec)

        delta = time_data.get('delta_sec')
        if delta == 0 or delta >= (min_to_sec - 1):
            raw_data = await self.data_fetcher.fetch_binance_rest(min_for_binance_rest,interval,symbol)
            return await self.data_synthesizer.synthesize_raw_binance_rest_data(raw_data)

        return None
    
    async def persistantly_get_price_diff(self, df_1s, df_15, mins):
        min_to_sec = mins * 60
        time_data = self.time_manager.handle_time_persistance(min_to_sec)
        delta = time_data.get('delta_sec')

        if df_1s or df_15 is None: return None





        


    










async def main():
    dp = DataPersistance()
    print("⏳ Watching clock for new candle...")
    
    while True:
        # Test with 1 minute (60s) for faster verification
        result = await dp.persistantly_get_binance_rest(15, "15m", "BTCUSDT")
        
        if result is not None:
            print(f"✅ Success! New Row Fetched: {result.tail(1)}")
            break # Exit after successful test
            
        await asyncio.sleep(0.5) # Check twice per second
if __name__ == "__main__":
    asyncio.run(main())