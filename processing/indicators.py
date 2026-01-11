import pandas as pd
import os

def calculate_rsi(df, period=14):

    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))

    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    
    rs = avg_gain / (avg_loss + 1e-10) # 1e-10 prevents division by zero
    rsi = 100 - (100 / (1 + rs))
    return rsi.dropna()


def calculate_ema(df, period=9):
    ema = df['close'].ewm(span=period, adjust=False).mean()
    return ema.dropna()


def calculate_macd(df, fast=12, slow=26, signal=9):
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    macd_hist = macd_line - signal_line
    return macd_line, signal_line, macd_hist

def calculate_bollinger_bands(df, period=20, std_dev=2):
    """Bollinger Bands (Upper, Middle, Lower)."""
    middle_band = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    return upper_band, middle_band, lower_band

def calculate_volume_change(df, period=5):
    """Percentage change in volume over X periods."""
    return df['volume'].pct_change(periods=period)

def apply_all_indicators(df):
    """
    Orchestrator function to apply all indicators to the main dataframe.
    """
    df = df.copy()
    
    # Trend & Momentum
    df['rsi'] = calculate_rsi(df)
    df['ema_9'] = calculate_ema(df, 9)
    df['ema_21'] = calculate_ema(df, 21)
    
    # MACD
    df['macd'], df['macd_signal'], df['macd_hist'] = calculate_macd(df)
    
    # Volatility
    df['bb_upper'], df['bb_mid'], df['bb_lower'] = calculate_bollinger_bands(df)
    
    # Volume
    df['vol_change_5'] = calculate_volume_change(df)
    
    # Clean up (remove the first few rows that have NaN from calculations)
    drop_nan = df.dropna()
    output_path = os.path.join("data", "btcusdt_with_indicators.csv")
    export_csv = drop_nan.to_csv(output_path, index=False)

    
    return export_csv

file_path = os.path.join("data", "btcusdt_history.csv")
my_btc_data = pd.read_csv(file_path)
apply_all_indicators(my_btc_data)
