import pandas as pd
import numpy as np
from scipy.signal import argrelextrema


"""
Parameter,1s Leg (Scalping),1m Leg (Trend Following)
RSI Period,21 (Higher = Less Noise),14 (Standard)
Divergence order,15 to 30,5 to 7
Divergence lookback,300 (5 mins of data),60 (1 hour of data)
MACD Fast/Slow,12 / 26,12 / 26
Buffer Size,1000 candles,500 candles
"""

class Rsi:
    def __init__(self, df, period=14, ma_period=14, window=50):
        self.df = df.copy()
        self.period = period
        self.ma_period = ma_period
        self.window = window

    def calculate_rsi(self, column="close"):
        if self.df is None or self.df.empty:
            return
        
        delta = self.df[column].diff()
        gain = (delta.where(delta > 0, 0))
        loss = (-delta.where(delta < 0, 0))

        avg_gain = gain.ewm(alpha=1/self.period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/self.period, adjust=False).mean()

        rs = avg_gain / avg_loss
        self.df['rsi'] = 100 - (100 / (1 + rs))

        # 2. RSI-Based Moving Average (Signal Line)
        # Using SMA for the RSI-MA is standard, but you can use EMA as well
        
        # EMA  
        self.df['rsi_ma'] = self.df['rsi'].ewm(span=self.ma_period, adjust=False).mean()
        
        # SMA
        # self.df['rsi_ma'] = self.df['rsi'].rolling(window=self.ma_period).mean()

        # 3. Z-Score Calculation (Statistical Probability)
        # Measures how many standard deviations price is from the 20-period mean
        rolling_mean = self.df[column].rolling(window=self.window).mean()
        rolling_std = self.df[column].rolling(window=self.window).std()
        self.df['z_score'] = (self.df[column] - rolling_mean) / rolling_std

        
        return self.df
    

    def calculate_rsi_divergence(self, order=7, lookback=60):
        """
        Detects Bullish and Bearish Divergence.
        order: How many candles to the left/right to confirm a pivot (higher = more stable).
        lookback: How far back to look for the previous pivot.
        """

        if 'rsi' not in self.df.colunms:
            self.calculate_rsi()

        df = self.df.tail(lookback + order).copy()

        # 1. Find Local Extrema (Pivots)
        # argrelextrema finds indices where value is > or < its neighbors
        hh_idx = argrelextrema(df['close'].values, np.greater, order=order)[0]
        ll_idx = argrelextrema(df['close'].values, np.less, order=order)[0]

        signals = []

        # 2. BULLISH CHECKS (Using Lows)
        if len(ll_idx) >= 2:
            p2, p1 = ll_idx[-1], ll_idx[-2]
            # --- Regular Bullish (Reversal) ---
            if df['close'].iloc[p2] < df['close'].iloc[p1] and df['rsi'].iloc[p2] > df['rsi'].iloc[p1]:
                signals.append("regular_bullish")
            
            # --- Hidden Bullish (Continuation) ---
            elif df['close'].iloc[p2] > df['close'].iloc[p1] and df['rsi'].iloc[p2] < df['rsi'].iloc[p1]:
                signals.append("hidden_bullish")

        # 3. BEARISH CHECKS (Using Highs)
        if len(hh_idx) >= 2:
            p2, p1 = hh_idx[-1], hh_idx[-2]
            # --- Regular Bearish (Reversal) ---
            if df['close'].iloc[p2] > df['close'].iloc[p1] and df['rsi'].iloc[p2] < df['rsi'].iloc[p1]:
                signals.append("regular_bearish")
            
            # --- Hidden Bearish (Continuation) ---
            elif df['close'].iloc[p2] < df['close'].iloc[p1] and df['rsi'].iloc[p2] > df['rsi'].iloc[p1]:
                signals.append("hidden_bearish")
        

        if signals:
            return {
                "type": signals[-1],
                "rsi_value": float(df['rsi'].iloc[p2]),
                "price": float(df['close'].iloc[p2]),
                "timestamp": df['timestamp'].iloc[p2]
            }
        return None

    
