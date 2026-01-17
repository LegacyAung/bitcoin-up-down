import pandas as pd
import os

def calculate_rsi(df, period=15):

    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))

    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    
    rs = avg_gain / (avg_loss + 1e-10) # 1e-10 prevents division by zero
    rsi = 100 - (100 / (1 + rs))
    return rsi.dropna()


def calculate_rsi_divergence(df, window=15):
    # Identifies Bullish (1) and Bearish (-1) Divergence.
    # can calculate both regular and hidden divergence.

    # 1. Get current and previous peak/trench
    df['p_high'] = df['close'].rolling(window=window).max()
    df['p_low'] = df['close'].rolling(window=window).min()
    df['r_high'] = df['rsi'].rolling(window=window).max()
    df['r_low'] = df['rsi'].rolling(window=window).min()

    # Previous peaks (shifted by window)
    df['prev_p_high'] = df['p_high'].shift(window)
    df['prev_p_low'] = df['p_low'].shift(window)
    df['prev_r_high'] = df['r_high'].shift(window)
    df['prev_r_low'] = df['r_low'].shift(window)

    # 2. Bullish Scenerios
    # Regular Bullish: Price LL / RSI HL
    reg_bull = (df['p_low'] < df['prev_p_high']) & (df['r_low'] > df['prev_r_low'])
    # Hidden Bullish: Price HL / RSI LL
    hid_bull = (df['p_low'] > df['prev_p_low']) & (df['r_low'] < df['prev_r_low'])


    # 3. Bearish Scenarios
    # Regular Bearish: Price HH / RSI LH
    reg_bear = (df['p_high'] > df['prev_p_high']) & (df['r_high'] < df['prev_r_high'])
    # Hidden Bearish: Price LH / RSI HH
    hid_bear = (df['p_high'] < df['prev_p_high']) & (df['r_high'] > df['prev_r_high']) 

    # 4. Map to a single feature or multiple
    df['bull_div'] = 0
    df.loc[reg_bull, 'bull_div'] = 1
    df.loc[hid_bull, 'bull_div'] = 2 # Distinct value for hidden

    df['bear_div'] = 0
    df.loc[reg_bear, 'bear_div'] = -1
    df.loc[hid_bear, 'bear_div'] = -2 # Distinct value for hidden

    # 5. RESOLVE OVERLAPS (The "Squeeze" Fix)
    # Identify rows where both Bull and Bear are active
    overlap = (df['bull_div'] != 0) & (df['bear_div'] != 0)
    
    # Create a new feature: div_squeeze (1 if conflicting, 0 if clear)
    df['div_squeeze'] = 0
    df.loc[overlap, 'div_squeeze'] = 1

    # In case of overlap, we clear the specific div signals 
    # so the model isn't confused by conflicting directions
    df.loc[overlap, ['bull_div', 'bear_div']] = 0

    return df[['bull_div', 'bear_div', 'div_squeeze']]

    


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

def calculate_bollinger_bands(df, period=15, std_dev=2):
    """Bollinger Bands (Upper, Middle, Lower)."""
    middle_band = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    return upper_band, middle_band, lower_band

def calculate_volume_change(df, period=15):
    """Percentage change in volume over X periods."""
    return df['volume'].pct_change(periods=period)


def calculate_dynamic_thresholds(df, horizon=15):
    # 1. Calculate the 15-min percentage change across the whole dataset
    future_change = (df['close'].shift(-horizon)-df['close'])/ df['close']
    future_change = future_change.dropna()

    # 2. Calculate Rolling standard deviation (volatility of last 24 hours)
    std_dev = future_change.rolling(window=1440).std()
    
    # 3. Define noise filter
    min_vol_threshold = std_dev * 0.5
    


    return std_dev, min_vol_threshold


def calculate_target(df, horizon=15):
    # Calculates the future price and the binary target using dynamic thresholds.#
    # 1. Create future_close (Look ahead 15 rows)
    df['future_close'] = df['close'].shift(-horizon)

    # 2. Calculate the percentage return for that future window
    df['future_pct_change'] = (df['future_close']- df['close'])/ df['close']

    # 3. Get dynamic limits from calculate_dynamic_thresholds
    # get target_labels

    def get_binary_label(row):
        change = row['future_pct_change']
        limit = row['min_vol_threshold']

        if pd.isna(change) or pd.isna(limit):
            return None

        if abs(change) < limit:
            return None
        # Binary Logic
        if change > 0:
            return 1
        else: 
            return 0

    return df['future_close'], df.apply(get_binary_label, axis=1)


def calculate_natr(df, period=14):
    # Average True Range (ATR) - Measures market volatility.

    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()

    # True Range is the maximum of the three ranges
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)

    # ATR is the rolling average of the True Range
    atr = true_range.rolling(window=period).mean()
    natr = (atr / df['close']) * 100
    return natr.dropna()

def apply_all_indicators(df):
    """
    Orchestrator function to apply all indicators to the main dataframe.
    """
    df = df.copy()
    
    # 1. basic indicators
    df['rsi'] = calculate_rsi(df)
    df['ema_9'] = calculate_ema(df, 9)
    df['ema_21'] = calculate_ema(df, 21)
    # MACD
    df['macd'], df['macd_signal'], df['macd_hist'] = calculate_macd(df)
    # Volatility
    df['bb_upper'], df['bb_mid'], df['bb_lower'] = calculate_bollinger_bands(df)
    # Volume
    df['vol_change_5'] = calculate_volume_change(df)
    # Average True Range
    df['natr'] = calculate_natr(df, period=14)

    # RSI Divergence
    # Values: 1=Reg Bull, 2=Hidden Bull, -1=Reg Bear, -2=Hidden Bear
    divergence_df = calculate_rsi_divergence(df, window=14)
    df['bull_div'] = divergence_df['bull_div']
    df['bear_div'] = divergence_df['bear_div']
    df['div_squeeze'] = divergence_df['div_squeeze']
    
    # Aggressive Features to Kill "Neutral" Bias
    # RSI Velocity (Speed of momentum change)
    df['rsi_velocity'] = df['rsi'].diff(3)

    # BB Bandwidth (Detecting the 'Squeeze' before volatility)
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_mid']
    
    # EMA Gap (Distance from mean - helps identify overextension)
    df['ema_gap'] = (df['close'] - df['ema_21']) / df['ema_21']
    
    # dynamic threshold & Target
    std_dev, min_vol_threshold = calculate_dynamic_thresholds(df)
    df['volatility_std'] = std_dev
    df['min_vol_threshold'] = min_vol_threshold
    df['future_close'], df['target'] = calculate_target(df)

    # --- 4. Final Cleanup ---
    # We drop NaNs from both the start (indicators/rolling) and end (future shift)
    # df.dropna(subset=['target', 'rsi', 'macd'])

    df = df.dropna(subset=['target'])
    
    # Clean up (remove the first few rows that have NaN from calculations)
    drop_nan = df.dropna()
    output_path = os.path.join("data", "btcusdt_with_indicators.csv")
    export_csv = drop_nan.to_csv(output_path, index=False)

    
    return export_csv



if __name__ == "__main__":

    file_path = os.path.join("data", "btcusdt_history.csv")
    my_btc_data = pd.read_csv(file_path)
    apply_all_indicators(my_btc_data)