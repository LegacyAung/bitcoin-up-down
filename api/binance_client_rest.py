import requests
import time
from utils.time import get_binance_time_range


#past 3 days
def get_binance_history():
    
    url = "https://api.binance.com/api/v3/klines"
    filename = "btc_1m_3days.csv"
    symbol="BTCUSDT"
    

    # Calculate timestamps in milliseconds
    start_time, end_time = get_binance_time_range()
    
    all_candles = []
    current_start = start_time
    print(f"Fetching {3} days of 1m data for {symbol}...")

    while current_start < end_time:

        params = {
            "symbol": symbol,
            "interval": "1m",
            "startTime": current_start,
            "limit": 1000 # Max limit per request
        }

        res = requests.get(url, params=params)
        data = res.json()

        if not data: 
            break

        all_candles.extend(data)
        # Move the start time to the last candle's close time + 1ms
        current_start = data[-1][6] + 1
        
        # Be polite to the API rate limit
        time.sleep(0.1)
    
    return all_candles
   
    


# Run and check results
if __name__ == "__main__":
    get_binance_history()