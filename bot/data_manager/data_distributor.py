import asyncio
import json
import os

from utils.file_io import FileIO
from strategies.macd.macd_manager import MacdManager


class DataDistributor:
    
    def __init__(self):
        self.file_io = FileIO()
        self.macd_manager = MacdManager()
        

    async def distribute_binance_rest_to_macd(self, df, interval, label):
        if df.empty : return
        cleaned_df = df.iloc[:-1].copy()
        await self.macd_manager.handle_rest_df_from_data_distributor(
            df=cleaned_df, 
            interval=interval, 
            label=label
        )
        path = self.file_io.get_path(f"btc_candles_{label}.jsonl")
        self.file_io.export_full_df_to_jsonl(cleaned_df, path)
        print(f"📦 Label: {label} | Interval: {interval} | Saved to: {path}")
                
    # persistently updating the most recent binance kline data
    async def distribute_binance_wss_to_macd(self, df, interval):
        if df.empty : return
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        label_1m=f"btc_candles_1day_{interval}.jsonl"
        label_1s=f"btc_candles_6hr_{interval}.jsonl"
        path_1m = os.path.join(data_dir,label_1m)
        path_1s=os.path.join(data_dir,label_1s)
        candle_dict = df.to_dict(orient='records')[0]
        await self.macd_manager.handle_wss_df_from_data_distributor(df,interval)
        
        if interval == '1m':
           self.file_io.append_row_to_jsonl(path_1m,candle_dict)
        if interval == '1s':
            self.file_io.append_row_to_jsonl(path_1s,candle_dict)        
        print(f"This is from data distributor: {df}")
        