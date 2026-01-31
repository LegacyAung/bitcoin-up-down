import asyncio

from api.binance.binance_rest import BinanceRest
from api.binance.binance_wss import BinanceWss
from api.clob.clob_rest import ClobRest
from api.clob.clob_wss import ClobWss

class DataFetcher:
    def __init__(self):
        self.binance_rest = BinanceRest()
        self.binance_wss = BinanceWss()
        self.clob_rest = ClobRest()
        self.clob_wss = ClobWss()

    async def fetch_binance_rest(self, min, interval, symbol): 
        return await self.binance_rest.get_binance_rest_data(min, interval, symbol)

    async def fetch_binance_wss(self, params, callback):
        return await self.binance_wss.stream_binance_data(params, callback)

    async def fetch_clob_rest(self):
        pass

    async def fetch_clob_wss(self,callback):
        return await self.clob_wss.stream_market_data(callback)

def main():
    pass

if __name__ == "__main__":
    main()
