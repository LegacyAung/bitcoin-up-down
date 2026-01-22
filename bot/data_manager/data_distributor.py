import asyncio
import json

from utils.file_io import FileIO
from strategies.macd.macd_manager import MacdManager


class DataDistributor:
    
    def __init__(self):
        self.file_io = FileIO()
        self.macd_manager = MacdManager()
        

    async def distribute_binance_rest_to_macd(self, df, interval, label):
        if df.empty : return
        cleaned_df = df.iloc[:-1].copy()
        await self.macd_manager.get_df_from_data_distributor(
            df=cleaned_df, 
            interval=interval, 
            label=label
        )
        path = self.file_io.get_path(f"btc_candles_{label}.jsonl")
        self.file_io.export_full_df_to_jsonl(cleaned_df, path)
        print(f"📦 Label: {label} | Interval: {interval} | Saved to: {path}")
                
    
    async def distribute_binance_wss_to_macd(self, df):
        
        print(f"This is from data distributor: {df}")
        