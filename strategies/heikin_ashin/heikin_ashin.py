import pandas as pd


class HeikinAshin:
    def __init__(self, df):
        self.df = df

    def calculate_heikin_ashin(self):
        if self.df is None or self.df.empty: return None

        ha_df = self.df.copy()

        ha_df['ha_close'] = (ha_df['open'] + ha_df['high'] + ha_df['low'] + ha_df['close']) / 4

        ha_open = [(ha_df['open'].iloc[0] + ha_df['close'].iloc[0]) / 2]

        for i in range(1, len(ha_df)):
            ha_open.append((ha_open[i-1] + ha_df['ha_close'].iloc[i-1]) / 2)
        
        ha_df['ha_open'] = ha_open

        ha_df['ha_high'] = ha_df[['high', 'ha_open', 'ha_close']].max(axis=1)
        ha_df['ha_low'] = ha_df[['low', 'ha_open', 'ha_close']].min(axis=1)
    
        return ha_df  
