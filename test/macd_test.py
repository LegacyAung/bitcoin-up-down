import asyncio
import pandas as pd
import numpy as np
import os
import json

from api.binance.binance_rest import BinanceRest
from api.binance.binance_wss import BinanceWss
from strategies.macd.macd import Macd
from utils.file_io import FileIO


binance_rest = BinanceRest()
binance_wss = BinanceWss()
# macd = Macd()
fileio = FileIO()



DATA_FOLDER = r"E:\bitcoin_up_down\data"
DATA_FILE_NAME = "btc_candles_1m.jsonl"
FULL_PATH = os.path.join(DATA_FOLDER, DATA_FILE_NAME)

async def handle_binance_wss_data(msg):
        # msg['k'] contains the kline data
    print(msg)
    kline = msg.get('k')
    
    # Check if 'x' (is_candle_closed) is True
    #kline['x'] == True
    if kline and kline['x'] == True: 
        # Format the data to match your REST export exactly
        new_row = {
            "timestamp": kline['t'],
            "open": float(kline['o']),
            "high": float(kline['h']),
            "low": float(kline['l']),
            "close": float(kline['c']),
            "volume": float(kline['v'])
        }
        # Append to the JSONL file
        # 2. Append to Raw File (btc_candles_1m.jsonl)
        fileio.append_row_to_jsonl(fileio.raw_data_path, new_row)
        print(f"📁 Raw data saved: {new_row['timestamp']}")

        await persistantly_calculate_macd()
    # Format the data to match your REST export exactly
    

async def run_binance_wss(callback):
    return await binance_wss.stream_binance_data(callback=callback)
    


async def run_binance_rest():
    return await  binance_rest.get_binance_rest_data(24, "1m", "BTCUSDT")


async def export_to_jsonl(data_list):
    # 1. Define the columns based on Binance REST response structure
    columns = [
        "timestamp", "open", "high", "low", "close", "volume", 
        "close_time", "quote_asset_volume", "number_of_trades", 
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ]

    # 2. Create DataFrame
    df = pd.DataFrame(data_list, columns=columns)

    df = df.iloc[:-1].copy()

    # 3. Select only the columns you want and convert types to float
    target_cols = ["timestamp", "open", "high", "low", "close", "volume"]
    df = df[target_cols].astype({
        "open": float, 
        "high": float, 
        "low": float, 
        "close": float, 
        "volume": float
    })

    # 4. Export using Pandas (orient='records' and lines=True creates JSONL)
    # Use mode='a' if you want to append, or 'w' to overwrite
    df.to_json(FULL_PATH, orient='records', lines=True)
    
    print(f"✅ Exported {len(df)} candles to {FULL_PATH}")

async def calculate_macd_history():
    """Wipes the old MACD file and creates a new one from full history."""
    df_raw = fileio.load_jsonl_to_df(fileio.raw_data_path)
    if not df_raw.empty:
        macd_engine = Macd(df_raw)
        df_macd = macd_engine.calculate_macd() # returns df with indicators
        
        # Target: btc_macd_1m.jsonl
        macd_path = fileio.get_path('btc_macd_1m.jsonl')
        fileio.export_full_df_to_jsonl(df_macd, macd_path)
        print(f"📊 Historical MACD file created at {macd_path}")

async def persistantly_calculate_macd():
    """Appends only the latest indicator row to the MACD file."""
    # Load raw candles to get full history (required for accurate EMA)
    df_raw = fileio.load_jsonl_to_df(fileio.raw_data_path)
    if len(df_raw) >= 26:
        macd_engine = Macd(df_raw)
        df_processed = macd_engine.calculate_macd()
        df_processed['timestamp'] = df_processed['timestamp'].astype(int)
        # Get only the newest row of indicators
        latest_macd = df_processed.iloc[-1:].to_dict(orient='records')[0]
        
        # Append to separate MACD file
        macd_path = fileio.get_path('btc_macd_1m.jsonl')
        fileio.append_row_to_jsonl(macd_path, latest_macd)
        print(f"📈 MACD entry appended to {macd_path}")


   

async def main():
    historical_candles = await run_binance_rest()

    if historical_candles:
        print("REST Data Loaded.")
        await export_to_jsonl(historical_candles)
        await calculate_macd_history()
    else:
        print("No data received from REST API.")

    print("Starting Live Stream Persistence...")
    await run_binance_wss(handle_binance_wss_data)


    



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot Stopped.")