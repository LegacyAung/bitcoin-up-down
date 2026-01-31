import numpy as np 


class MacdSignals15m:

    def __init__(self,df,interval,label):
        pass


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
