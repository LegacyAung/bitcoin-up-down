import pandas as pd
import numpy as np

class Macd:
    def __init__(self, df, fast=12, slow=26, signal=9):
        self.df = df
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
   
    def calculate_macd(self, column='close'):
        """Initial calculation for the whole history."""
        if self.df is None or self.df.empty: return None
        
        # EMAs and MACD
         
        self.df['ema_fast'] = self.df[column].ewm(span=self.fast, adjust=False).mean()
        self.df['ema_slow'] = self.df[column].ewm(span=self.slow, adjust=False).mean()
        self.df['macd_line'] = self.df['ema_fast'] - self.df['ema_slow']
        self.df['signal_line'] = self.df['macd_line'].ewm(span=self.signal, adjust=False).mean()
        self.df['histogram'] = self.df['macd_line'] - self.df['signal_line']
        
        output_cols = ['timestamp', 'close', 'macd_line', 'signal_line', 'histogram']
        return self.df[output_cols]
    
    



        



