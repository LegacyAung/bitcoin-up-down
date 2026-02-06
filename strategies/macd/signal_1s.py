import numpy as np


from utils.time import get_no_1s_behind_current_time

class MacdSignals1s:
    def __init__(self,df,interval,label):
        self.df = df
        self.interval = interval
        self.label = label
    
        

    def define_no_bull_bear_in_60s(self):
        _, elapsed, _ = self._get_no_1s_behind_current_time()
        if len(self.df) < 2: return
        hist = self.df['histogram'].tail(elapsed).values

        bull_secs_count = np.sum(hist > 0)
        bear_secs_count = np.sum(hist < 0)

        bull_weight = abs(np.sum(hist[hist > 0])) if bull_secs_count > 0 else 0
        bear_weight = abs(np.sum(hist[hist < 0])) if bear_secs_count > 0 else 0 

        net_bias = bull_weight - bear_weight
        
        # print(f"[{self.label}] Elapsed: {elapsed}s")
        # print("hist_1s: ", self.df['histogram'].iloc[-1])
        # print(f"Bullish: {bull_secs_count}s (Weight: {bull_weight:.4f})")
        # print(f"Bearish: {bear_secs_count}s (Weight: {bear_weight:.4f})")
        # print(f"Net Bias: {net_bias:.4f}")

        return {
            "bull_weight": bull_weight,
            "bear_weight": bear_weight,
            "net_bias": net_bias,
            "elapsed": elapsed
        }
        
    
    # def define_macd_hist_zero_crossover(self):
    #     if len(self.df) < 2 : return

    #     prev = self.df['histogram'].iloc[-2]
    #     curr = self.df['histogram'].iloc[-1]

    #     if prev < 0 and curr > 0 :
    #         print("BULLISH_CROSS")
    #         return "BULLISH_CROSS"
    #     if prev > 0 and curr < 0 :
    #         print("BEARISH_CROSS")
    #         return "BEARISH_CROSS"

        
    def define_macd_hist_velocity(self, period=3):

        if self.df is None or len(self.df) < period:
            return
        
        recent_hist = self.df['histogram'].tail(period).values
        diffs = np.diff(recent_hist)

        velocity = np.diff(diffs)
        if all(v > 0 for v in velocity):
            # print("ACCELERATING_UP") 
            return "ACCELERATING_UP"
        if all(v < 0 for v in velocity):
            # print("ACCELERATING_DOWN") 
            return "ACCELERATING_DOWN"
        # print("STABLE")
        return "STABLE"


   
    

    def _get_no_1s_behind_current_time(self):

        return get_no_1s_behind_current_time()
    