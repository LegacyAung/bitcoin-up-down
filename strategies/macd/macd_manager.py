import pandas as pd
from utils.file_io import FileIO
from .macd import Macd

class MacdManager:
    def __init__(self):
        self.file_io = FileIO()
        self.buffers = {
            '1day_1m': pd.DataFrame(),
            '6hr_1s': pd.DataFrame(),
            '1day_15m': pd.DataFrame()
        }
        
    async def handle_rest_df_from_data_distributor(self, df, interval, label):
        if df.empty : return
        cols_to_fix = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        for col in cols_to_fix:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['timestamp', 'close'])
        macd_df = await self._calculate_macd(df)
        # 2. Update the BUFFER so the WSS logic has history to work with
        # We keep the last 1000 rows to ensure MACD accuracy
        self.buffers[label] = macd_df.tail(1000).copy()

        target_path = self.file_io.get_path(filename=f"btc_macd_{label}.jsonl")
        self.file_io.export_full_df_to_jsonl(macd_df,target_path)
        
        print(f"📊 MACD history for {label} saved to btc_macd_{label}.jsonl")

    async def handle_wss_df_from_data_distributor(self,df, interval):
        if df.empty : return
        label = None
        if interval == '1s':
            label = "6hr_1s"
        elif interval == '1m':
            label = "1day_1m"
        else:
            label = "1day_15m"
        buffer = self.buffers.get(label, pd.DataFrame())
        combined = pd.concat([buffer, df], ignore_index=True)
        # 3. ROLLING WINDOW: Keep only the last 1000 rows in RAM
        # This prevents the bot from slowing down over 20 hours
        if len(combined) > 1000:
            combined = combined.tail(1000)
        
        self.buffers[label] = combined

        # 4. Calculate MACD on just this lean buffer
        macd_df = await self._calculate_macd(combined)
        new_row = macd_df.iloc[-1].to_dict() # The latest calculated values

        # 5. PERSIST TO DISK (Append mode)
        # This saves the MACD result to the file without re-writing the whole file
        target_path = self.file_io.get_path(filename=f"btc_macd_{label}.jsonl")
        self.file_io.append_row_to_jsonl(target_path, new_row)

    
    async def _calculate_macd(self,df):
       if not df.empty:
        macd = Macd(df).calculate_macd()
        return macd
        

    