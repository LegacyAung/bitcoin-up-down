import asyncio
import json

class DataManager:
    def __init__(self, clob_wss):
        
        self.clob_wss = clob_wss
        self.wss_market_data = None

    async def handle_wss_data(self,msg):
        event_type = msg.get("event_type")
        self.wss_market_data = msg
        print(f"📊 DataManager updated: {event_type}")


    





