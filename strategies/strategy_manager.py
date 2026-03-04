import asyncio

from utils.file_io import FileIO


from .macd.macd import Macd
from .macd.signal_1s import MacdSignals1s
from .macd.signal_1m import MacdSignals1m
from .heikin_ashin.heikin_ashin import HeikinAshin

from .price_change.price_change import PriceChange
from .order_book.order_book import OrderBook


from bot.states.macd_state import macd_states

class StratedyManager:
    def __init__(self):
        self.file_io = FileIO()
        self.macd_states = macd_states

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
            await self._order_book_handler(data, bound_loads)
        elif event_type == "price_change":
            await self._price_change_handler(data, bound_loads)
        elif event_type == "last_trade_price":
            pass
        


#--------------------------------Helping Handlers---------------------------#
    async def _price_change_handler(self, data, bound_loads):

        price_change = PriceChange(data, bound_loads)
        
        try:
            await asyncio.gather(
                # Current Window Updates
                price_change.current_yes_ask_price(),
                price_change.current_no_ask_price(),
                # price_change.current_yes_bid_price(),
                # price_change.current_no_bid_price(),

                # Next Window Updates
                # price_change.next_yes_ask_price(),
                # price_change.next_no_ask_price(),
                # price_change.next_yes_bid_price(),
                # price_change.next_no_bid_price()
            )

        except Exception as e:
            print(f"❌ Error in PriceChange gather: {e}")

    
    async def _order_book_handler(self, data, bound_loads):
        
        order_book = OrderBook(data, bound_loads)

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
            
            macd_1m_signals = None
            macd_1s_signals = None

            if interval == '1s':
                # 1s signals
                macd_signals1s = MacdSignals1s(df,interval,label)
                hist = macd_signals1s.define_no_bull_bear_in_60s()
                # hist_velocity = macd_signals1s.define_macd_hist_velocity(period=5)
                # slope = macd_signals1s.get_1s_trend_slope(lookback=60)

                macd_1s_signals = {
                    'bull_weight': hist['bull_weight'],
                    'bear_weight': hist['bear_weight'],
                    'net_bias': hist['net_bias'],
                    'elapsed': hist['elapsed']
                }

                self.macd_states.set_macd_1s(macd_1s_signals)
            
            if interval == "1m":
                # 1m signals
                macd_signals1m = MacdSignals1m(df,interval,label)
                macd_h_exhaustion = macd_signals1m.define_histogram_exhaustion(periods=6)
                macd_h_momentum = macd_signals1m.define_histogram_momentum(periods=4)
                macd_h_side = macd_signals1m.define_histogram_side(periods=6)
                macd_h_squeeze = macd_signals1m.define_histogram_squeeze(periods=6,volatility_periods=24)
                macd_h_zeroline_reject = macd_signals1m.define_zero_line_reject(periods=3, volatility_periods=24)
                macd_h_slope = macd_signals1m.define_histogram_slope(periods=6)

                macd_1m_signals = {
                    'h_exhaustion':macd_h_exhaustion,
                    'h_momentum':macd_h_momentum,
                    'h_side':macd_h_side,
                    'h_squeeze':macd_h_squeeze,
                    'h_zeroline_reject':macd_h_zeroline_reject,
                    'h_slope':macd_h_slope
                }

                self.macd_states.set_macd_1m(macd_1m_signals)

                print(f"macd_1m_states: {self.macd_states.macd_1m}")

            return macd_1m_signals, macd_1s_signals
            
        except Exception as e:
            
            print(f"❌ Critical Exception in indicator chain: {e}")
            return None
        
