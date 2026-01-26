import pandas as pd
import numpy as np

class BB:
    def __init__(self,df, period=20, std_dev=2):
        self.df = df.copy()
        self.period = period
        self.std_dev = std_dev

    def calculate_bb(self, column='close'):
        if self.df is None or self.df.empty: return None
        
        # Vectorized Rolling Math
        ma = self.df[column].rolling(window=self.period, min_periods=1).mean()
        std = self.df[column].rolling(window=self.period, min_periods=1).std()
        
        # Append new columns to the EXISTING dataframe
        self.df['bb_middle'] = ma
        self.df['bb_upper'] = ma + (std * self.std_dev)
        self.df['bb_lower'] = ma - (std * self.std_dev)
        self.df['bb_bandwidth'] = (self.df['bb_upper'] - self.df['bb_lower']) / ma
        self.df['bb_pct'] = (self.df[column] - self.df['bb_lower']) / (self.df['bb_upper'] - self.df['bb_lower'])
        
        return self.df