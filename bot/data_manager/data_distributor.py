import pandas as pd

from utils.file_io import FileIO
from strategies.strategy_manager import StratedyManager



class DataDistributor:
    
    def __init__(self):
        self.file_io = FileIO()
        self.stratedgy_manager = StratedyManager()
        

        self.buffers = {
            '1day_1m': pd.DataFrame(),
            '1hr_1s': pd.DataFrame(),
            '1day_15m': pd.DataFrame()
        }

    async def distribute_binance_wss(self, df, interval):
        if df.empty : return
        label = "1hr_1s" if interval == '1s' else "1day_1m"

        self.buffers[label] = pd.concat([self.buffers[label], df], ignore_index=True).tail(900)

        if 'macd_line' in self.buffers[label].columns:
            enriched_row = await self.stratedgy_manager.handle_wss_from_distributor(
                buffers = self.buffers,
                interval = interval,
                label = label
            )

            if enriched_row:
                filename = f"btc_candles_indications_{label}.jsonl"
                path = self.file_io.get_path(filename)
                self.file_io.append_row_to_jsonl(path,enriched_row)

        
    async def distribute_binance_rest(self, df, interval, label):
        if df.empty : return
        new_history = df.iloc[:-1].copy()
        combined = pd.concat([new_history, self.buffers[label]], ignore_index=True)
        combined = combined.drop_duplicates(subset=['timestamp'], keep="last")
        combined = combined.sort_values('timestamp').reset_index(drop=True)

        max_rows = 900 if interval == '1s' else 1500
        self.buffers[label] = new_history.tail(max_rows).copy()

        enriched_df = await self.stratedgy_manager.handle_rest_from_distributor(
            buffers = self.buffers,
            interval = interval,
            label = label
        )

        if enriched_df is not None:
            self.buffers[label] = enriched_df
            filename = f"btc_candles_indications_{label}.jsonl"
            self._distribute_as_jsonl(enriched_df, filename,interval,label)
            
                
    def _distribute_as_jsonl(self, df, filename, interval, label):
        path = self.file_io.get_path(filename)
        self.file_io.export_full_df_to_jsonl(df,path)
        print(f"📦 Label: {label} | Interval: {interval} | Saved to: {path}")


   

        

        