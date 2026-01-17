import pandas as pd
import numpy as np
from processing.processor import DataProcessor
from training.lstm_network import LSTMNetwork
import os

def run_full_test():
    # 1. Load and Process Data
    print("📂 Loading processed CSV data...")
    processor = DataProcessor(window_size=60, feature_range=(0,1))
    input_csv_path = os.path.join("data", "btcusdt_with_indicators.csv")
    
    # This generates the (Samples, 60, 21) shape the LSTM expects
    x_lstm, x_xgb, y = processor.run_full_pipeline(input_csv_path)
    
    print(f"📊 Data Prepared: {x_lstm.shape[0]} windows found.")
    print(f"📐 Input Shape: {x_lstm.shape[1]} mins x {x_lstm.shape[2]} indicators.")

    # 2. Initialize the LSTM with the CORRECT input shape
    # X.shape[1:] gives us (60, 21)
    brain = LSTMNetwork(input_shape=x_lstm.shape[1:])

    # 3. Train the Model
    # We use a small epoch count (e.g., 10) just to verify it works
    print("\n🚀 Starting Training...")
    history = brain.train(x_lstm, y, epochs=10, batch_size=32)

    # 4. Save the trained brain
    brain.save()

    # 5. Quick Result Check
    final_acc = history.history['accuracy'][-1]
    print(f"\n✅ SUCCESS! Final Training Accuracy: {final_acc*100:.2f}%")

if __name__ == "__main__":
    run_full_test()