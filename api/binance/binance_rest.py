import asyncio
import time

from utils.time import get_binance_time_range_in_mins
from .binance_service import BinanceService

from ..restful_services import RestfulServices
from config import BINANCE_ENDPOINT




class BinanceRest:
    def __init__(self, params, timeout=10):
        self.url = BINANCE_ENDPOINT
        self.params = params
        self.timeout = timeout

        self.service = RestfulServices(self.url,self.params,self.timeout)


    async def fetch_binance_rest_data(self):
        return await self.service.get()


   

async def main():
    # 1. Initialize the class
    binance_rest = BinanceRest()
    
    # 2. Define how to handle the data
    data = await binance_rest.get_binance_rest_data(1,"1m","BTCUSDT")
    print(data)

if __name__ == "__main__":
     asyncio.run(main())

        
