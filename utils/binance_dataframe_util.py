import pandas as pd
import os

#formatting binanace raw data to readable format and export as csv file
def format_binance_data(raw_candles_data):
    """Converts raw list from Binance into a cleaned DataFrame."""
    columns = [
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades', 
        'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
    ]

    df = pd.DataFrame(raw_candles_data, columns=columns)
    
    # Convert types
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)
    return df

# save binance raw data and export as csv file
def save_to_csv(df, symbol, folder="data"):
    # 1. Build the full path (e.g., 'data/btcusdt_history.csv')
    filename = f"{symbol.lower()}_history.csv"
    filepath = os.path.join(folder, filename)
    
    # 2. Save the file
    df.to_csv(filepath, index=False)
    
    # 3. Print the confirmation message
    print(f"✅ Saved {len(df)} rows to {filepath}.")
    return filepath