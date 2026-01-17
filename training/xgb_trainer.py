import pandas as pd
import numpy as np 
import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

class XGBoostTrainer:
    def __init__(self, data_path, model_dir='models'):
        self.data_path = data_path
        self.model_dir = model_dir
        self.model = None

        self.params = {
            'objective': 'binary:logistic',
            'n_estimators': 300,
            'max_depth': 3,
            'learning_rate': 0.02,
            'eval_metric': 'logloss',
            'random_state': 42,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 30,
            'gamma': 5,
            # We will add scale_pos_weight dynamically in xgb_train
        }

    def load_and_preprocess(self):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Data file not found at {self.data_path}")
        
        df = pd.read_csv(self.data_path)
        features = ['rsi', 'ema_9', 'ema_21', 'macd', 'macd_signal', 'macd_hist', 
                    'bb_upper', 'bb_mid', 'bb_lower', 'vol_change_5', 'natr',
                    'bull_div', 'bear_div', 'div_squeeze', 
                    'rsi_velocity', 'bb_width', 'ema_gap']

        x = df[features]
        y = df['target']

        split_idx = int(len(x) * 0.8)
        self.x_train, self.x_test = x.iloc[:split_idx], x.iloc[split_idx:]
        self.y_train, self.y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        print(f"✅ Data Loaded: {len(self.x_train)} training rows, {len(self.x_test)} test rows.")

    def xgb_dynamic_threshold(self, current_natr):
        # Increased thresholds to protect your $0.95 hedge
        if current_natr < 0.15:
            return 0.72 # Very strict in low vol
        elif current_natr > 0.40:
            return 0.60 # More aggressive in high vol
        else:
            return 0.65 

    def xgb_train(self):
        print("🚀 Training with Balanced Time-Decay...")

        # 1. FIX CLASS IMBALANCE (The 0.00 Precision Fix)
        # Calculates ratio of Bearish to Bullish to force model to care about both
        num_neg = (self.y_train == 0).sum()
        num_pos = (self.y_train == 1).sum()
        self.params['scale_pos_weight'] = num_neg / num_pos

        # 2. SOFTEN TIME DECAY (Recent Bias Fix)
        # Using 2.0x instead of 5.0x so it doesn't "forget" older bullish patterns
        n_rows = len(self.y_train)
        time_weights = np.linspace(1.0, 2.0, n_rows)

        self.model = xgb.XGBClassifier(**self.params)
        self.model.fit(
            self.x_train, self.y_train,
            sample_weight=time_weights,
            eval_set=[(self.x_test, self.y_test)],
            verbose=False
        )

        if not os.path.exists(self.model_dir): os.makedirs(self.model_dir)
        model_path = os.path.join(self.model_dir, 'xgb_momentum_model.pkl')
        joblib.dump(self.model, model_path)
        print(f"💾 Model trained with ScalePosWeight: {self.params['scale_pos_weight']:.2f}")

    def xgb_evaluate(self):
        if self.model is None: return
        
        y_proba = self.model.predict_proba(self.x_test)[:,1]
        
        # DEBUG: See if the model is even capable of hitting your thresholds
        print(f"Probabilities - Max: {y_proba.max():.4f}, Min: {y_proba.min():.4f}, Mean: {y_proba.mean():.4f}")

        natr_values = self.x_test['natr'].values
        y_pred_strict = []

        for p, natr in zip(y_proba, natr_values):
            t = self.xgb_dynamic_threshold(natr)
            if p > t:
                y_pred_strict.append(1)
            elif p < (1 - t):
                y_pred_strict.append(0)
            else:
                y_pred_strict.append(-1)

        results = pd.DataFrame({'actual': self.y_test.values, 'pred': y_pred_strict})
        trades_only = results[results['pred'] != -1]

        print("\n" + "="*30)
        print(f"📊 DYNAMIC HEDGE PERFORMANCE")
        print(f"Total Test Candles: {len(results)} | Trades Taken: {len(trades_only)}")
        print("="*30)

        if not trades_only.empty:
            target_names = ['Bearish (No)', 'Bullish (Yes)']
            print(classification_report(trades_only['actual'], trades_only['pred'], 
                                        target_names=target_names, labels=[0, 1]))
            
            cm = confusion_matrix(trades_only['actual'], trades_only['pred'], labels=[0, 1])
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                        xticklabels=target_names, yticklabels=target_names)
            plt.title('Dynamic Decision Matrix')
            plt.show()
        else:
            print("⚠️ No trades met the threshold. Try lowering the base threshold (0.65).")

if __name__ == "__main__":
    trainer = XGBoostTrainer('data/btcusdt_with_indicators.csv')
    trainer.load_and_preprocess()
    trainer.xgb_train()
    trainer.xgb_evaluate()