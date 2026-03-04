import numpy as np



class MacdSignals1m:
    def __init__(self,df,interval,label):
        self.df = df
        self.interval = interval
        self.label = label

    def define_current_hist(self):
        if self.df is None: return
        current_val = self.df['histogram'].iloc[-1]
        return current_val
    

    def define_histogram_slope(self, periods=3):
        if self.df is None or len(self.df) < periods: return

        y = self.df['histogram'].tail(periods).values
        x = np.arange(len(y))
        slope, _ = np.polyfit(x, y, 1)
        slope = float(slope)
        print(f"slope: {slope}")

        return slope

    def define_histogram_squeeze(self, periods=3, volatility_periods=24):
        if self.df is None: return

        threshold = self._get_dynamic_threshold(volatility_periods)

        recent_abs_hist = np.abs(self.df['histogram'].tail(periods).values)

        if all(val < threshold for val in recent_abs_hist):
            return "SQUEEZE_ACTIVE"
        
        return "NEUTRAL"

    def define_zero_line_reject(self, periods=3, volatility_periods=24):
        if self.df is None: return

        threshold = self._get_dynamic_threshold(volatility_periods)

        hist = self.df['histogram'].tail(periods).values

        if all( v > 0 for v in hist):
            if hist[-1] > hist[-2] and hist[-2] < hist[-3]:
                if hist[-2] < threshold:
                    return "BULL_ZERO_REJECT"
                
        if all(v < 0 for v in hist):
            if hist[-1] < hist[-2] and hist[-2] > hist[-3]:
                if hist[-2] > -threshold:
                    return "BEAR_ZERO_REJECT"

        return "NEUTRAL"


    def define_histogram_side(self, periods=3):
        if self.df is None or len(self.df) < periods : return

        recent_hist = self.df['histogram'].tail(periods).values
        if periods <= 3:
            avg_hist = np.mean(recent_hist)
        else:
            weights = np.arange(1, periods + 1) # e.g., [1, 2, 3, 4, 5]
            avg_hist = np.dot(recent_hist, weights) / weights.sum()

        if avg_hist > 0:
            return "OVERALL_BULLSIDE"
        if avg_hist < 0:
            return "OVERALL_BEARSIDE"
        else:
            return "NEUTRAL"


    def define_histogram_momentum(self, periods=3):
        if self.df is None or len(self.df) < periods : return

        recent_hist = self.df['histogram'].tail(periods).values
        diffs = np.diff(recent_hist)
        if all(d > 0 for d in diffs):
        # Even if values are -0.2, if they are rising, it's 
            # print("----------------------------------------------1m-------------------------------------------------")
            # print("------------BULLISH-----------")
            # print("----------------------------------------------1m-------------------------------------------------")
            return "BULLISH"
    
        if all(d < 0 for d in diffs):
        # Even if values are +0.5, if they are falling, it's BEARISH
            # print("----------------------------------------------1m-------------------------------------------------")
            # print("-----------BEARISH------------")
            # print("----------------------------------------------1m-------------------------------------------------")
            return "BEARISH"
        
        # print("----------------------------------------------1m-------------------------------------------------")
        # print("-----------NEUTRAL------------")
        # print("----------------------------------------------1m-------------------------------------------------")
        return "NEUTRAL"
    
    def define_macd_divergence(self, periods=20):
        if self.df is None or len(self.df) < periods: 
            return "NEUTRAL"

        # Get the recent slice
        recent_data = self.df.tail(periods)
        
        # 1. Find the current and previous "Local Lows" for Price
        # We divide the periods in half to compare the 'now' vs the 'then'
        half = periods // 2
        first_half = recent_data.head(half)
        second_half = recent_data.tail(half)

        price_min_1 = first_half['close'].min()
        price_min_2 = second_half['close'].min()

        # 2. Find the corresponding MACD Histogram Lows
        hist_min_1 = first_half['histogram'].min()
        hist_min_2 = second_half['histogram'].min()

        # --- BULLISH DIVERGENCE ---
        # Price is making a Lower Low, but Histogram is making a Higher Low
        if price_min_2 < price_min_1 and hist_min_2 > hist_min_1:
            # Extra filter: Only call it if the histogram is still negative 
            # (catching the turn before the cross)
            if hist_min_2 < 0:
                print(f"[{self.label}] 🟢 BULLISH DIVERGENCE DETECTED 🟢")
                return "BULLISH_DIVERGENCE"

        # --- BEARISH DIVERGENCE ---
        # Price is making a Higher High, but Histogram is making a Lower High
        price_max_1 = first_half['close'].max()
        price_max_2 = second_half['close'].max()
        hist_max_1 = first_half['histogram'].max()
        hist_max_2 = second_half['histogram'].max()

        if price_max_2 > price_max_1 and hist_max_2 < hist_max_1:
            if hist_max_2 > 0:
                print(f"[{self.label}] 🔴 BEARISH DIVERGENCE DETECTED 🔴")
                return "BEARISH_DIVERGENCE"

        return "NEUTRAL"
    

    def define_hidden_divergence(self, periods=20):
        if self.df is None or len(self.df) < periods: 
            return "NEUTRAL"

        recent_data = self.df.tail(periods)
        half = periods // 2
        first_half = recent_data.head(half)
        second_half = recent_data.tail(half)

        # --- BULLISH HIDDEN DIVERGENCE (Continuation) ---
        # Price: Higher Low | MACD: Lower Low
        price_low_1 = first_half['close'].min()
        price_low_2 = second_half['close'].min()
        
        hist_low_1 = first_half['histogram'].min()
        hist_low_2 = second_half['histogram'].min()

        if price_low_2 > price_low_1 and hist_low_2 < hist_low_1:
            print(f"[{self.label}] 🟢 BULLISH HIDDEN DIVERGENCE (Trend Reload) 🟢")
            return "HIDDEN_BULLISH"

        # --- BEARISH HIDDEN DIVERGENCE (Continuation) ---
        # Price: Lower High | MACD: Higher High
        price_high_1 = first_half['max'].max()
        price_high_2 = second_half['max'].max()
        
        hist_high_1 = first_half['histogram'].max()
        hist_high_2 = second_half['histogram'].max()

        if price_high_2 < price_high_1 and hist_high_2 > hist_high_1:
            print(f"[{self.label}] 🔴 BEARISH HIDDEN DIVERGENCE (Trend Reload) 🔴")
            return "HIDDEN_BEARISH"

        return "NEUTRAL"


    def define_histogram_exhaustion(self, periods=3):
        if self.df is None or len(self.df) < periods + 1:return
        
        hist = self.df['histogram'].tail(periods + 1).values
        
        # BULLISH EXHAUSTION (Top of a green move)
        # Prev bars were increasing, but current bar is smaller
        if hist[-2] > 0 and hist[-1] < hist[-2] and hist[-2] > hist[-3]:
            # print("----------------------------------------------1m-------------------------------------------------")
            # print(f"[{self.label}] ⚠️ BULLISH EXHAUSTION (Momentum Peaking)")
            return "BULL_EXHAUSTION"
            
        # BEARISH EXHAUSTION (Bottom of a red move)
        # Prev bars were decreasing (more negative), but current is less negative
        if hist[-2] < 0 and hist[-1] > hist[-2] and hist[-2] < hist[-3]:
            # print("----------------------------------------------1m-------------------------------------------------")
            # print(f"[{self.label}] ⚠️ BEARISH EXHAUSTION (Sellers Exhausted)")
            return "BEAR_EXHAUSTION"

        return "NEUTRAL"





#-------------------------------------------HELPERS----------------------------------------------#
    def _get_dynamic_threshold(self, periods=24, multiplier=0.5, min_val=2, max_val=4):
        """
        Calculates a threshold based on the volatility of the histogram.
        multiplier: 0.5 means the squeeze is active if bars are 50% smaller 
        than the recent average volatility.
        """  

        if self.df is None or len(self.df) < periods:
            return 2
        
        hist_volatility = self.df['histogram'].tail(periods).std()

        cal_threshold = hist_volatility * multiplier
        
        dynamic_threshold = np.clip(cal_threshold, min_val, max_val)

        return dynamic_threshold


            



