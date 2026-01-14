import tensorflow as tf
from keras import Sequential
from keras.layers import LSTM, Dense, Dropout, Input
import os

class LSTMNetwork:
    def __init__(self, input_shape):
        """
        input_shape: (window_size, num_features) 
        Example: (60, 21) if you have 60 mins of history and 21 indicators.
        """
        self.input_shape = input_shape
        self.model = self._build_model()

    """Defines the layers of the Neural Network."""
    def _build_model(self):
        model = Sequential([
            # Input Layer: Tells the model what shape to expect
            Input(shape = self.input_shape),

            # Layer 1: LSTM with 64 neurons or nodes
            LSTM(units=64, return_sequences=True ),
            Dropout(0.2),

            # Layer 2: LSTM with 32 neurons or nodes
            LSTM(units=32, return_sequences=False),
            Dropout(0.2),

            # Layer 3: Dense layer for interpretation
            Dense(units=16, activation='relu'),
            
            # Final Layer: Output 
            # Sigmoid squashes the result between 0 and 1 (Probability)
            Dense(units=1, activation='sigmoid')
        ])

        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',  # Standard for 1/0 classification
            metrics=['accuracy']
        )

        return model
    
    def train(self, x_train, y_train, epochs=50, batch_size=32):
        """Trains the model on the 3D window data."""
        print(f"🚀 Training LSTM on {len(x_train)} samples...")
        
        history = self.model.fit(
            x_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2, # Uses the last 20% of data to test itself
            verbose=1
        )
        return history
    def save(self, folder_path="models", filename="lstm_model.h5"):
        """Saves the trained model to the models/ folder."""
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        save_path = os.path.join(folder_path, filename)
        self.model.save(save_path)
        print(f"💾 LSTM Model saved to: {save_path}")