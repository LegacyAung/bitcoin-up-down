import numpy as np

from utils.time import get_no_1s_behind_current_time

class MacdSignals1s:
    def __init__(self,df,interval,label):
        self.df = df
        self.interval = interval
        self.label = label
    
    def define_momentum_on_10s(self, periods=4):
        if self.df is None or len(self.df) < (periods * 10):
            return None
        
        raw_hist = self.df['histogram'].tail(periods*10).values

        period_sums = [np.sum(raw_hist[i:i+10]) for i in range(0, len(raw_hist), 10)]

        slopes = np.diff(period_sums)

        is_consistently_growing = np.all(slopes > 0)
        is_consistently_falling = np.all(slopes < 0)

        curr_10s = period_sums[-1]  
        prev_10s = period_sums[-2] 

        momentum = "NEUTRAL"
        if curr_10s > 0:
            if is_consistently_growing:
                momentum = "STRONG_BULLISH_STAIRCASE"
            else:
                momentum = "BULLISH_EXPANDING" if curr_10s > prev_10s else "BULLISH_EXHAUSTING"

        elif curr_10s < 0:
            if is_consistently_falling:
                momentum = "STRONG_BEARISH_STAIRCASE"
            else:
                momentum = "BEARISH_EXPANDING" if curr_10s < prev_10s else "BEARISH_EXHAUSTING"

        return {
            "current_10s_sum": curr_10s,
            "period_sums": period_sums, # [T-30s, T-20s, T-10s, Now]
            "momentum_10s": momentum,
            "is_consistent": is_consistently_growing or is_consistently_falling
        }


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
        
    
    def define_macd_hist_zero_crossover(self):
        if len(self.df) < 2 : return

        prev = self.df['histogram'].iloc[-2]
        curr = self.df['histogram'].iloc[-1]

        if prev < 0 and curr > 0 :
            print("BULLISH_CROSS")
            return "BULLISH_CROSS"
        if prev > 0 and curr < 0 :
            print("BEARISH_CROSS")
            return "BEARISH_CROSS"

        
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
    

    def _get_macd_10s_hist(self):
        if self.df is None or len(self.df) < 10 : return 

        hist_10s_sum = np.sum(self.df['histogram'].tail(10).values)

        return hist_10s_sum