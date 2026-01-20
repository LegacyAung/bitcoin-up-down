import asyncio
import json
import time

from utils.time import get_binance_time_range
from .binance_service import BinanceService
from config import BINANCE_ENDPOINT


class BinanceRest:
    def __init__(self):
        self.binance_service = BinanceService()
        self.binance_url = BINANCE_ENDPOINT
        
    async def get_binance_rest_data(self,days=int,interval=str,symbol=str):
        all_candles = []
        start_time, end_time = get_binance_time_range(days)
        current_start = start_time

        while current_start < end_time:
            # symbol="BTCUSDT", interval="1m"
            params = {
                "symbol":symbol,
                "interval":interval,
                "startTime":current_start,
                "limit": 1000 # Max limit per request
            }
            data = await self.binance_service.get_binance_rest(self.binance_url, params,10)
            if not data:
                break
            all_candles.extend(data)

            current_start = data[-1][6] + 1
            time.sleep(0.1)
        return all_candles        



async def main():
    # 1. Initialize the class
    binance_rest = BinanceRest()
    
    # 2. Define how to handle the data
    data = await binance_rest.get_binance_rest_data(1,"1m","BTCUSDT")
    print(data)

if __name__ == "__main__":
     asyncio.run(main())

        
