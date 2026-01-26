import pandas as pd


class Macd:
    def __init__(self, df, fast=12, slow=26, signal=9):
        self.df = df
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
   
    def calculate_macd(self, column='close'):
        if self.df is None or self.df.empty: return None
        
        # Ensure numeric to prevent calculation crashes
        close_vals = pd.to_numeric(self.df[column], errors='coerce')
        
        # Vectorized EMA math (adjust=False is standard for TradingView style MACD)
        ema_f = close_vals.ewm(span=self.fast, adjust=False).mean()
        ema_s = close_vals.ewm(span=self.slow, adjust=False).mean()
        
        self.df['macd_line'] = ema_f - ema_s
        self.df['signal_line'] = self.df['macd_line'].ewm(span=self.signal, adjust=False).mean()
        self.df['histogram'] = self.df['macd_line'] - self.df['signal_line']
        
        return self.df 
    
    



        



