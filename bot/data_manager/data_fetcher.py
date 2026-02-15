import asyncio
import json
import time

from api.binance.binance_rest import BinanceRest
from api.binance.binance_wss import BinanceWss
from api.binance.binance_config import INTERVAL_MS
from api.clob.clob_wss import ClobWss
from api.clob.clob_rest import ClobRest
from api.gamma.gamma_rest import GammaRest

from utils.time import get_binance_time_range_in_mins



class DataFetcher:
    def __init__(self):
       
        self.binance_rest = None
        self.binance_wss = None
        self.binance_interval_ms = INTERVAL_MS

        self.clob_wss_tasks = {}
        
    # --- BINANCE LOGIC ---    
    async def fetch_binance_rest(self, mins, interval, symbol): 
        all_candles = []
        start_time, end_time = get_binance_time_range_in_mins(mins)
        current_start = start_time

        step_ms = self.binance_interval_ms.get(interval, 60000)

        while current_start < end_time:
            params = {
                "symbol":symbol,
                "interval":interval,
                "startTime":current_start,
                "limit": 1000
            }
            
            self.binance_rest = BinanceRest(params)
            data = await self.binance_rest.fetch_binance_rest_data()

            if not data: return

            all_candles.extend(data)
            last_open_time = data[-1][0]
            if last_open_time < current_start:
                break
            current_start = last_open_time + step_ms
            await asyncio.sleep(0.1)

        return all_candles

    async def open_binance_wss(self, params, binance_callback):
        if self.binance_wss is None:
            self.binance_wss = BinanceWss(params, binance_callback)
            return await self.binance_wss.connect_binance_wss()
            
    async def close_binance_wss(self):
        if self.binance_wss is None: return
        
        await self.binance_wss.disconnect_binance_wss()
        self.binance_wss = None

    async def wait_for_binance_wss(self):
        if self.binance_wss and self.binance_wss.service:
            await self.binance_wss.service.connected_event.wait()


    # --- CLOB LOGIC ---
    async def open_clob_wss(self, channel_type, sub_msg, clob_rest, clob_callback):

        condition_id = sub_msg['condition_id']
        stream_key = f"{channel_type}_{condition_id}"

        if stream_key in self.clob_wss_tasks:
            print(f"⚠️ Stream {stream_key} already exists in registry.")
            return

        auth_params = clob_rest.get_l2_creds()
        if channel_type == 'user':
            payload = {
                "type":"subscribe",
                "channel":"user",
                "markets": [condition_id],
                "auth": {
                    "apiKey" : auth_params['api_key'],
                    "secret" : auth_params['api_secret'],
                    "passphrase" : auth_params['api_passphrase']
                }
            }
        else:
            payload = {
                "type": "subscribe",
                "assets_ids": json.loads(sub_msg['clob_ids']),
                "channels": sub_msg['channels']
             }
        clob_wss = ClobWss(channel_type, payload, condition_id, clob_callback)
        self.clob_wss_tasks[stream_key] = clob_wss
        
        return await clob_wss.connect_clob_wss()

    async def close_clob_wss(self, channel_type, condition_id):
        stream_key = f"{channel_type}_{condition_id}"
        clob_wss = self.clob_wss_tasks.get(stream_key)
        if clob_wss:
            await clob_wss.disconnect_clob_wss()
            del self.clob_wss_tasks[stream_key]
        else:
            print(f"❌ No active stream found for {stream_key}")


    # --- HELPERS ---
    async def fetch_submsg_clobwss(self, timestamp, channels):
        if timestamp is None: return
        params = {
            "active": str(True).lower(),
            "closed": str(False).lower()
        }
        gamma_rest = GammaRest(params, timestamp)
        event_slug = await gamma_rest.fetch_slug_event()
        event_market = event_slug['markets'][0]
        
        return {
            'clob_ids':event_market['clobTokenIds'],
            'condition_id':event_market['conditionId'],
            'channels':channels
        }


            


   

if __name__ == "__main__":

    first_data_received = asyncio.Event()
    async def binance_callback(msg):
        if not first_data_received.is_set():
            first_data_received.set()
            print("📥 First Binance WSS message received! Triggering REST fetch...")
        # print("binance_streaming here baby.......................................")
        
    
    async def clob_callback(msg):
        pass
        # print("clob_streaming here baby.......................................")
        

    async def main(clob_callback, binance_callback):
        timestamps = ["1770895800", "1770896700"]
        channels = ["book", "price_change", "last_trade_price", "best_bid_ask"]
        binance_params = ["btcusdt@kline_1m", "btcusdt@kline_1s"]
        binance_rest_cfg = {"mins": 15, "interval": "1s", "label": "1hr_1s", "symbol": "BTCUSDT"}

        clob_rest = ClobRest()
        await clob_rest.authenticate()
        data_fetcher = DataFetcher()

        # 1. Start Binance WSS in the background
        binance_task = asyncio.create_task(
            data_fetcher.open_binance_wss(binance_params, binance_callback)
        )

        # 2. WAIT for the event signal before moving forward
        print("⏳ Waiting for first live WSS message...")
        await first_data_received.wait()
        print("🚀 Binance WSS Connected. Proceeding to REST fetch.")

        # 3. Fetch REST data now that the socket is alive
        data = await data_fetcher.fetch_binance_rest(
            binance_rest_cfg['mins'], 
            binance_rest_cfg['interval'], 
            binance_rest_cfg["symbol"]
        )
        print(f"✅ REST Data synchronized: {len(data)} candles.")

        # 4. Launch CLOB tasks
        clob_tasks = []
        initial_msg = await data_fetcher.fetch_submsg_clobwss(timestamps[0], channels)
        
        # Start User Channel
        clob_tasks.append(asyncio.create_task(
            data_fetcher.open_clob_wss('user', initial_msg, clob_rest, clob_callback)
        ))

        # Start Market Channels
        for ts in timestamps:
            sub_msg = await data_fetcher.fetch_submsg_clobwss(ts, channels)
            clob_tasks.append(asyncio.create_task(
                data_fetcher.open_clob_wss('market', sub_msg, clob_rest, clob_callback)
            ))

        # 5. Gather all persistent tasks to keep the loop alive
        await asyncio.gather(binance_task, *clob_tasks)  
            
        
        
    
    asyncio.run(main(clob_callback, binance_callback))
