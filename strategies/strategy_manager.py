import pandas as pd
import numpy as np
import asyncio
import json
from utils.file_io import FileIO
from .macd.macd import Macd
from .macd.signal_1s import MacdSignals1s
from .macd.signal_1m import MacdSignals1m
# from .macd.signal_15m import MacdSignals15m




class StratedyManager:
    def __init__(self):
        self.file_io = FileIO()
        self.buffers = {
            '1day_1m': pd.DataFrame(),
            '1hr_1s': pd.DataFrame(),
            '1day_15m': pd.DataFrame()
        }
        

    async def handle_rest_df_from_data_distributor(self, df, interval, label):
        if df.empty: return
        
        combined_df = await self._calculate_all_indicators(df)
        
        combined_df = combined_df.dropna().copy()
        max_rows = 900 if interval == '1s' else 1500
        self.buffers[label] = combined_df.tail(max_rows).copy()

        target_path = self.file_io.get_path(filename=f"btc_strategy_{label}.jsonl")
        self.file_io.export_full_df_to_jsonl(combined_df,target_path)


    async def handle_wss_df_from_data_distributor(self,df, interval):
        
        if df.empty: return
        
        label = "1hr_1s" if interval == '1s' else "1day_1m" if interval == '1m' else "1day_15m"
        max_rows = 900 if interval == '1s' else 1500
        buffer = self.buffers.get(label, pd.DataFrame())

        if not buffer.empty:
            last_ts = float(buffer.iloc[-1]['timestamp'])
            curr_ts = float(df.iloc[0]['timestamp'])
            step = 1000.0 if interval == '1s' else 60000.0
            gap = curr_ts - last_ts
            if (step * 1.5) < gap < (step * 30):
                num_missing = int(round(gap / step)) - 1
                if num_missing > 0:
                    last_price = buffer.iloc[-1]['close']
                    patch_ts = np.arange(last_ts + step, curr_ts, step)
                    patch_df = pd.DataFrame({
                        'timestamp': patch_ts,
                        'close': last_price
                    })
                    buffer = pd.concat([buffer, patch_df], ignore_index=True)
        combined = pd.concat([buffer, df], ignore_index=True).tail(max_rows).copy()
        self.buffers[label] = combined

        if len(combined) < 50: return

        result_df = await self._calculate_all_indicators(combined)
        if result_df is not None and not result_df.empty:
            # Extract the most recent row as a dictionary
            new_row = result_df.iloc[-1].to_dict()

            # Clean up floats for faster I/O and smaller file size
            new_row = {k: round(v, 4) if isinstance(v, float) else v for k, v in new_row.items()}
            await self._all_signals(self.buffers[label],interval,label)

            # --- 4. ASYNC PERSISTENCE ---
            target_path = self.file_io.get_path(filename=f"btc_strategy_{label}.jsonl")
            asyncio.create_task(self._async_save(target_path, new_row))

  

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
                hist_zero_crossover = macd_signals1s.define_macd_hist_zero_crossover()
                hist_velocity = macd_signals1s.define_macd_hist_velocity(period=5)
                # slope = macd_signals1s.get_1s_trend_slope(lookback=60)
            
            if interval == "1m":
                # 1m signals
                macd_signals1m = MacdSignals1m(df,interval,label)
                hist_momentum = macd_signals1m.define_histogram_momentum()
                # macd_divergence = macd_signals1m.define_macd_divergence(periods=20)
                # macd_hid_divergence = macd_signals1m.define_hidden_divergence(periods=20)
                macd_hist_exhaustion = macd_signals1m.define_histogram_exhaustion(periods=3)

            return hist_momentum, macd_hist_exhaustion, hist, hist_zero_crossover, hist_velocity
            
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