import asyncio
import os

from utils.file_io import FileIO
from strategies.strategy_manager import StratedyManager
from .data_persistance import DataPersistance


class DataDistributor:
    
    def __init__(self):
        self.file_io = FileIO()
        self.stratedgy_manager = StratedyManager()
        self.data_persistance = DataPersistance()
       
        
    async def distribute_binance_rest(self, df, interval, label):
        if df.empty : return
        cleaned_df = df.iloc[:-1].copy()
        await asyncio.gather(
            self.stratedgy_manager.handle_rest_df_from_data_distributor(
                df=cleaned_df,
                interval=interval,
                label=label
            ),
            
        )
        filename = f"btc_candles_{label}.jsonl"
        self._distribute_as_jsonl(cleaned_df,filename,interval,label)
                
    # persistently updating the most recent binance kline data
    async def distribute_binance_wss(self, df, interval):
        if df.empty : return

        prefix = "1hr" if interval == "1s" else "1day"
        filename = f"btc_candles_{prefix}_{interval}.jsonl"

        path = self.file_io.get_path(filename)
        candle_dict = df.to_dict(orient='records')[0]
        
        await self.stratedgy_manager.handle_wss_df_from_data_distributor(df,interval)
        self.file_io.append_row_to_jsonl(path, candle_dict)

    
    async def distribute_persistant_binance_rest(self, df, interval, label):
        pass


    def _distribute_as_jsonl(self, df, filename, interval, label):
        path = self.file_io.get_path(filename)
        self.file_io.export_full_df_to_jsonl(df,path)
        print(f"📦 Label: {label} | Interval: {interval} | Saved to: {path}")


   

        

        