import asyncio
import json
import time

from utils.time import get_binance_time_range, get_binance_time_range_in_hours, get_binance_time_range_in_mins
from .binance_service import BinanceService
from config import BINANCE_ENDPOINT
from utils.interval import INTERVAL_MS


class BinanceRest:
    def __init__(self):
        self.binance_service = BinanceService()
        self.binance_url = BINANCE_ENDPOINT
        self.interval_ms = INTERVAL_MS
        
    async def get_binance_rest_data(self,mins=int,interval=str,symbol=str): #24,"1m","BTCUSDT" #1440,"1m","BTCUSDT"
        all_candles = []
        start_time, end_time = get_binance_time_range_in_mins(mins)
        current_start = start_time


        step_ms = self.interval_ms.get(interval, 60000)

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
            last_open_time = data[-1][0]

            if last_open_time < current_start:
                break
            current_start = last_open_time + step_ms
            #current_start = data[-1][6] + 1  #for 1s data[-1][0] + 1000
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

        
