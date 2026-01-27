import numpy as np


class MacdSignals1m:
    def __init__(self,df,interval,label):
        self.df = df
        self.interval = interval
        self.label = label

    def define_histogram_momentum(self, periods=3):
        if self.df is None or len(self.df) < periods : return

        recent_hist = self.df['histogram'].tail(periods).values
        diffs = np.diff(recent_hist)
        if all(d > 0 for d in diffs):
        # Even if values are -0.2, if they are rising, it's 
            print("----------------------------------------------1m-------------------------------------------------")
            print("------------BULLISH-----------")
            print("----------------------------------------------1m-------------------------------------------------")
            return "BULLISH"
    
        elif all(d < 0 for d in diffs):
        # Even if values are +0.5, if they are falling, it's BEARISH
            print("----------------------------------------------1m-------------------------------------------------")
            print("-----------BEARISH------------")
            print("----------------------------------------------1m-------------------------------------------------")
            return "BEARISH"
        
        print("----------------------------------------------1m-------------------------------------------------")
        print("-----------NEUTRAL------------")
        print("----------------------------------------------1m-------------------------------------------------")
        return "NEUTRAL"
    
    # def define_macd_divergence(self, periods=20):
    #     if self.df is None or len(self.df) < periods: 
    #         return "NEUTRAL"

    #     # Get the recent slice
    #     recent_data = self.df.tail(periods)
        
    #     # 1. Find the current and previous "Local Lows" for Price
    #     # We divide the periods in half to compare the 'now' vs the 'then'
    #     half = periods // 2
    #     first_half = recent_data.head(half)
    #     second_half = recent_data.tail(half)

    #     price_min_1 = first_half['close'].min()
    #     price_min_2 = second_half['close'].min()

    #     # 2. Find the corresponding MACD Histogram Lows
    #     hist_min_1 = first_half['histogram'].min()
    #     hist_min_2 = second_half['histogram'].min()

    #     # --- BULLISH DIVERGENCE ---
    #     # Price is making a Lower Low, but Histogram is making a Higher Low
    #     if price_min_2 < price_min_1 and hist_min_2 > hist_min_1:
    #         # Extra filter: Only call it if the histogram is still negative 
    #         # (catching the turn before the cross)
    #         if hist_min_2 < 0:
    #             print(f"[{self.label}] 🟢 BULLISH DIVERGENCE DETECTED 🟢")
    #             return "BULLISH_DIVERGENCE"

    #     # --- BEARISH DIVERGENCE ---
    #     # Price is making a Higher High, but Histogram is making a Lower High
    #     price_max_1 = first_half['close'].max()
    #     price_max_2 = second_half['close'].max()
    #     hist_max_1 = first_half['histogram'].max()
    #     hist_max_2 = second_half['histogram'].max()

    #     if price_max_2 > price_max_1 and hist_max_2 < hist_max_1:
    #         if hist_max_2 > 0:
    #             print(f"[{self.label}] 🔴 BEARISH DIVERGENCE DETECTED 🔴")
    #             return "BEARISH_DIVERGENCE"

    #     return "NEUTRAL"
    

    # def define_hidden_divergence(self, periods=20):
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
            print("----------------------------------------------1m-------------------------------------------------")
            print(f"[{self.label}] ⚠️ BULLISH EXHAUSTION (Momentum Peaking)")
            return "BULL_EXHAUSTION"
            
        # BEARISH EXHAUSTION (Bottom of a red move)
        # Prev bars were decreasing (more negative), but current is less negative
        if hist[-2] < 0 and hist[-1] > hist[-2] and hist[-2] < hist[-3]:
            print("----------------------------------------------1m-------------------------------------------------")
            print(f"[{self.label}] ⚠️ BEARISH EXHAUSTION (Sellers Exhausted)")
            return "BEAR_EXHAUSTION"

        return "NEUTRAL"





