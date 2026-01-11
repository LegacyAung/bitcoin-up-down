import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import joblib
import os


class DataProcessor:
    def __init__(self, window_size=60, feature_range=(0,1)):
        self.window_size = window_size
        self.scaler = MinMaxScaler(feature_range=feature_range)
        self.features_df = None
        self.target_array = None
    
    """Step 1: Load the CSV from disk."""
    def load_data(self, csv_path):
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV not found at {csv_path}")
        return pd.read_csv(csv_path)
    
    """Step 2: Define what the model is trying to predict."""
    def create_target(self, df):
        # Target: 1 if the NEXT close is higher than current close
        # We use .shift(-1) to bring 'future' data into the 'current' row
        df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
        df.dropna(inplace=True)
        return df

    """Step 3: Separate the label from the input data."""
    def split_features_target(self, df):
        self.target_array = df['target'].values
        self.features_df = df.drop(['target'], axis=1)
        return self.target_array, self.features_df

    """Step 4: Normalize data to 0-1 range for the Neural Network."""
    def scale_features(self, features):
        return self.scaler.fit_transform(features)
    
    """Step 5: Transform 2D data into 3D sequences for LSTM."""
    def create_sliding_windows(self, scaled_data):
        x_lstm = []
        x_xgb = []
        y = []

        for i in range(self.window_size, len(scaled_data)):
            # The 'Window': Last N rows of data
            x_lstm.append(scaled_data[i - self.window_size:i])
            # The 'Snaphot': The single most recent row for XGBoost
            x_xgb.append(scaled_data[i - 1])
            # The Label: Did the price actually go up after this window?
            y.append(self.target_array[i - 1])

        return np.array(x_lstm), np.array(x_xgb), np.array(y)

    """Step 6: Persist the scaler for live trading use later."""
    def save_scaler(self,folder_name="models", filename="scaler.pkl"):
        project_root = os.path.dirname(os.path.abspath(__file__))
        target_dir = os.path.join(project_root, folder_name)

        # 2. Create the folder if it doesn't exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f"Created directory: {target_dir}")

        # 3. Save the scaler using joblib
        save_path = os.path.join(target_dir, filename)
        joblib.dump(self.scaler, save_path)
        print(f"Scaler successfully saved to: {save_path}")
    
    """Orchestrator method to run everything in order."""
    def run_full_pipeline(self, csv_path):
        
        raw_df = self.load_data(csv_path)
        df_with_target = self.create_target(raw_df)
        features, _ = self.split_features_target(df_with_target)
        scaled_features = self.scale_features(features)
        
        return self.create_sliding_windows(scaled_features)


if __name__ == "__main__":
    processor = DataProcessor(window_size=4) # Using 4 for easier printing
    input_path = os.path.join("data", "btcusdt_with_indicators.csv")
    
    # ... (Your previous loading/scaling code) ...
    dataframe = processor.load_data(input_path)
    target_dataframe = processor.create_target(dataframe)
    target, features = processor.split_features_target(target_dataframe)
    features_only_numeric = features.drop(columns=['timestamp'], errors='ignore')
    scaled_data = processor.scale_features(features_only_numeric) 

    # --- STEP 5: Call the sliding windows method ---
    X_lstm, X_xgb, y = processor.create_sliding_windows(scaled_data)

    print("\n" + "="*30)
    print("SLIDING WINDOWS OUTPUT")
    print("="*30)
    
    print(f"LSTM 3D Shape: {X_lstm.shape}") # (Samples, TimeSteps, Features)
    print(f"XGB 2D Shape:  {X_xgb.shape}")  # (Samples, Features)
    print(f"Target Shape:  {y.shape}")      # (Samples,)

    print("\n--- FIRST LSTM WINDOW (X_lstm[0]) ---")
    print("This is what the model sees for ONE prediction:")
    print(X_lstm[0])