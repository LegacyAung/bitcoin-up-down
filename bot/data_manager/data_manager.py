import asyncio
import json

from api.binance.binance_rest import BinanceRest
from api.clob.clob_rest import ClobClient
from api.gamma.gamma_rest import fetch_event_slug

class DataManager:
    def __init__(self, clob_wss, binance_wss):
        
        self.clob_wss = clob_wss
        self.clob_wss_market_data = None
        self.binance_wss = binance_wss
        self.binance_wss_market_data = None

    async def handle_clob_wss_data(self,msg):
        self.clob_wss_market_data = msg
        print("✅clob wss is passing down data stream")
        

    async def handle_binance_wss_data(self,msg):
        self.binance_wss_market_data = msg
        print("✅binance wss is passing down data stream")
        
    





