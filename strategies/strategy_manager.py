import pandas as pd
import numpy as np
import asyncio
import json
from utils.file_io import FileIO


from .macd.macd import Macd
from .macd.signal_1s import MacdSignals1s
from .macd.signal_1m import MacdSignals1m


class StratedyManager:
    def __init__(self):
        self.file_io = FileIO()
        

    async def handle_rest_from_distributor(self, buffers, interval, label):
        
        buffer = buffers.get(label)

        if buffer is None or buffer.empty:
            print(f"❌ Error: No buffer data found for {label}")
            return
        
        combined_df = await self._calculate_all_indicators(buffer)

        if combined_df is not None:
            combined_df = combined_df.dropna().copy()
            return combined_df
        
        return None

    async def handle_wss_from_distributor(self, buffers, interval, label):
        buffer = buffers[label]

        if buffer is None or buffer.empty : return None
        
        df_with_indicators = await self._calculate_all_indicators(buffer)

        if df_with_indicators is not None and not df_with_indicators.empty:

            new_row = df_with_indicators.iloc[-1].to_dict()

            await self._all_signals(df_with_indicators, interval, label)

            return new_row
        
        return None


    async def _calculate_all_indicators(self, df):
        try:
            if df is None or df.empty:
                print("❌ Error: Input DF to indicators is empty.")
                return None
            df = Macd(df).calculate_macd()
            if df is None:
                print("❌ Error: MACD calculation returned None")
                return None
            return df
        except Exception as e:
            print(f"❌ Critical Exception in indicator chain: {e}")
            return None
        
    async def _all_signals(self,df,interval,label):
        try:
            if df is None or df.empty:
                print("❌ Error: Input DF to indicators is empty.")
                return None
            
            if interval == '1s':
                # 1s signals
                macd_signals1s = MacdSignals1s(df,interval,label)
                hist = macd_signals1s.define_no_bull_bear_in_60s()
                hist_velocity = macd_signals1s.define_macd_hist_velocity(period=5)
                # slope = macd_signals1s.get_1s_trend_slope(lookback=60)
            
            if interval == "1m":
                # 1m signals
                macd_signals1m = MacdSignals1m(df,interval,label)
                hist_momentum = macd_signals1m.define_histogram_momentum()
                macd_hist_exhaustion = macd_signals1m.define_histogram_exhaustion(periods=3)

            return hist_momentum, macd_hist_exhaustion, hist, hist_velocity
            
        except Exception as e:
            
            #print(f"❌ Critical Exception in indicator chain: {e}")
            return None
        
    async def _async_save(self, file_path, data):
        """Non-blocking background save to JSONL."""
        try:
            # Offload blocking I/O to a background thread
            await asyncio.to_thread(self._sync_append_jsonl, file_path, data)
        except Exception as e:
            print(f"❌ Async Save Error: {e}")

    def _sync_append_jsonl(self, file_path, data):
        """Synchronous file append operation."""
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data) + '\n')