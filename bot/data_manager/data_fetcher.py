import asyncio
import json

from api.binance.binance_rest import BinanceRest
from api.binance.binance_wss import BinanceWss
from api.clob.clob_rest import ClobRest
from api.clob.clob_wss import ClobWss2
from api.gamma.gamma_rest import fetch_event_slug

class DataFetcher:
    def __init__(self):
        self.binance_rest = BinanceRest()
        self.binance_wss = BinanceWss()
        self.clob_rest = ClobRest()
        
        

    async def fetch_binance_rest(self, min, interval, symbol): 
        return await self.binance_rest.get_binance_rest_data(min, interval, symbol)

    async def fetch_binance_wss(self, params, callback):
        return await self.binance_wss.stream_binance_data(params, callback)

    async def fetch_clob_rest(self):
        pass

    async def fetch_clob_wss(self,callback, sub_msg):

        clob_wss2 = ClobWss2(sub_msg['clob_ids'], sub_msg['condition_id'], sub_msg['channdels'])
        
        return await clob_wss2.stream_market_data(callback)
    
    async def fetch_submsg_clob_wss(self, timestamp:str, channels:list[str]):
        if timestamp is None: return

        
        event_slug = fetch_event_slug(active=True, closed=False, timestamp=timestamp)
        event_market = event_slug['markets'][0]
        clob_ids = json.load(event_market['clobTokenIds'])
        condition_id = event_market['conditionId']
        closed_time = event_market['closedTime']

        return {
            'clob_ids':clob_ids,
            'condition_id':condition_id,
            'channels':channels,
            'closed_time':closed_time
        }

            

async def callback(msg):
    print(msg)



async def main(callback):
    data_fetcher = DataFetcher()
    params = ['btcusdt@kline_1m', 'btcusdt@kline_1s']
    await data_fetcher.fetch_clob_wss(params = params, callback=callback)

    

if __name__ == "__main__":
    asyncio.run(main(callback))
