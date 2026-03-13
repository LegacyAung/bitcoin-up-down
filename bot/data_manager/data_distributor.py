import pandas as pd

from utils.file_io import FileIO
from strategies.strategy_manager import StratedyManager

from bot.states.portfolio_state import portfolio_states



class DataDistributor:
    
    def __init__(self):
        self.file_io = FileIO()
        self.stratedgy_manager = StratedyManager()

        self.pf_states = portfolio_states
        

        self.buffers = {
            '1day_1m': pd.DataFrame(),
            '1hr_1s': pd.DataFrame(),
            '1day_15m': pd.DataFrame()
        }

#-----------------------------Binance--------------------------#

    async def distribute_binance_wss(self, df, interval):
        if df.empty : return
        label = "1hr_1s" if interval == '1s' else "1day_1m"

        self.buffers[label] = pd.concat([self.buffers[label], df], ignore_index=True).tail(900)

        enriched_row = await self.stratedgy_manager.handle_wss_from_distributor(
                buffers = self.buffers,
                interval = interval,
                label = label
            )
        if enriched_row:
            filename = f"btc_candles_indications_{label}.jsonl"
            path = self.file_io.get_path(filename)
            await self.file_io.append_row_to_jsonl2(path,enriched_row)

    
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
            await self._distribute_as_jsonl(enriched_df, filename,interval,label)
            
    
    async def distribute_persistant_binance_rest(self, df, interval, label):
        if df.empty : return
        
        current_buffer_15m = self.buffers.get(label, pd.DataFrame())
        combined = pd.concat([current_buffer_15m, df], ignore_index=True)
        combined = combined.drop_duplicates(subset=['timestamp'], keep='last').sort_values('timestamp')
        self.buffers[label] = combined.tail(150)

        enriched_15m_df = await self.stratedgy_manager.handle_rest_from_distributor(
            buffers = self.buffers,
            interval = interval,
            label = label
        )

        if enriched_15m_df is not None:
            self.buffers[label] = enriched_15m_df
            filename = f"btc_candles_indications_{label}.jsonl"
            await self._distribute_as_jsonl(enriched_15m_df, filename,interval,label)


#-----------------------------Clob--------------------------#
    async def distribute_clob_wss(self, data, event_type, bound_loads):
        if data is None or (isinstance(data, dict) and not data): return
        
        if hasattr(data, 'empty') and data.empty: return
        

        if event_type == "trade":
            order_id = data.get('id')
            order_status = data.get('status')
            self.pf_states.set_active_trades(data) if order_status == "MATCHED" else print(f"{order_id} status is currently {order_status}")
            print(f"data_distributor_{event_type}: {self.pf_states.active_trades}")

        if event_type == "order":
            
            order_id = data.get('id')
            order_status = data.get('status')
            self.pf_states.set_open_orders(data) if order_status == "LIVE" else print(f"{order_id} status is currently {order_status}")
            print(f"data_distributor_{event_type}: {self.pf_states.open_orders}")

        await self.stratedgy_manager.handle_clob_wss_from_distributor(
            data=data,
            event_type=event_type,
            bound_loads=bound_loads
        )
        
    
    


#-----------------------------Helpers--------------------------#
    async def _distribute_as_jsonl(self, df, filename, interval, label):
        path = self.file_io.get_path(filename)
        await self.file_io.export_full_df_to_jsonl2(df,path)
        print(f"📦 Label: {label} | Interval: {interval} | Saved to: {path}")


   

        

        