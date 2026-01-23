import pandas as pd
from dataclasses import asdict
from ..utils.schemas import Candle



class DataSynthesizer:
    def __init__(self) :
        self.candle : None 

    # changing raw data from binance wss to panda dataframe
    async def synthesize_raw_binance_wss_data(self,raw_data):
        k = raw_data.get('k')
        if not k:
            return None
        self.candle = Candle(
            timestamp=int(k['t']),
            open=float(k['o']),
            high=float(k['h']),
            low=float(k['l']),
            close=float(k['c']),
            volume=float(k['v'])
        )

        df = pd.DataFrame([asdict(self.candle)]) 
        return df
    
    # changing raw data from binance rest to panda dataframe
    async def synthesize_raw_binance_rest_data(self, raw_data_list):
        if not raw_data_list:
            return pd.DataFrame()
        
        candles = []
        for item in raw_data_list:
            self.candle = Candle(
                timestamp=int(item[0]),
                open=float(item[1]),
                high=float(item[2]),
                low=float(item[3]),
                close=float(item[4]),
                volume=float(item[5])
            )
            candles.append(asdict(self.candle))
        
        return pd.DataFrame(candles)



    