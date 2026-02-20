import asyncio
import json
from utils.file_io import FileIO


from .macd.macd import Macd
from .macd.signal_1s import MacdSignals1s
from .macd.signal_1m import MacdSignals1m
from .heikin_ashin.heikin_ashin import HeikinAshin

from .price_change.price_change import PriceChange
from .order_book.order_book import OrderBook

class StratedyManager:
    def __init__(self):
        self.file_io = FileIO()
        

    async def handle_rest_from_distributor(self, buffers, interval, label):
        
        buffer = buffers.get(label)

        if buffer is None or buffer.empty:
            print(f"❌ Error: No buffer data found for {label}")
            return
        
        processed_df = await self._calculate_all_indicators(buffer, interval)

        if processed_df is not None:
            processed_df = processed_df.dropna().copy()
            return processed_df
        
        return None

    async def handle_wss_from_distributor(self, buffers, interval, label):
        buffer = buffers[label]

        if buffer is None or buffer.empty : return None
        
        processed_df = await self._calculate_all_indicators(buffer, interval)

        if processed_df is not None and not processed_df.empty:
            new_row = processed_df.iloc[-1].to_dict()
            await self._all_signals(processed_df, interval, label)

            return new_row

        return None

    async def handle_clob_wss_from_distributor(self, data, event_type, bound_loads):
        if data is None :return 

        if event_type == "book":
            pass
        elif event_type == "price_change":
            await self._price_change_handler(data, bound_loads)
        elif event_type == "last_trade_price":
            pass
        


#--------------------------------Helping Handlers---------------------------#
    async def _price_change_handler(self, data, bound_loads):

        price_change = PriceChange(data, bound_loads)
        
        return await price_change.current_no_ask_price()

    
    async def _order_book_handler(self, data, bound_loads):
        pass


#----------------------------------HELPERS----------------------------------#    
    async def _calculate_all_indicators(self, df, interval):
        try:
            if df is None or df.empty:
                print("❌ Error: Input DF to indicators is empty.")
                return None
            
            processed_df = Macd(df).calculate_macd()
            
            if processed_df is None:
                print("❌ Error: MACD calculation returned None")
                return None
            
            if interval == "1s":
                ha_df = HeikinAshin(processed_df).calculate_heikin_ashin()
                if ha_df is not None:
                    processed_df = ha_df    
                else:
                    print("⚠️ Warning: HA failed, falling back to standard MACD df")    
            
            return processed_df
        
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
        
