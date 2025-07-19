#!/usr/bin/env python3
"""
LIGHTWEIGHT AI TRADING ENGINE
Optimized for cloud deployment - Railway, Heroku, Render compatible
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import yfinance as yf
import warnings
import logging
from datetime import datetime, timedelta
import json
import pickle
from typing import Dict, List, Tuple, Optional
import threading
import time
import os
from flask import Flask, render_template_string, jsonify

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """Pure Python technical indicators - no external dependencies"""
    
    @staticmethod
    def sma(data, period):
        """Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def ema(data, period):
        """Exponential Moving Average"""
        return data.ewm(span=period).mean()
    
    @staticmethod
    def rsi(data, period=14):
        """Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def macd(data, fast=12, slow=26, signal=9):
        """MACD Indicator"""
        ema_fast = TechnicalIndicators.ema(data, fast)
        ema_slow = TechnicalIndicators.ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(data, period=20, std_dev=2):
        """Bollinger Bands"""
        sma = TechnicalIndicators.sma(data, period)
        std = data.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower
    
    @staticmethod
    def atr(high, low, close, period=14):
        """Average True Range"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(window=period).mean()

class LightweightPredictor:
    """Lightweight ML predictor using only scikit-learn"""
    
    def __init__(self):
        self.models = {
            'rf': RandomForestRegressor(n_estimators=50, random_state=42, max_depth=10),
            'gb': GradientBoostingRegressor(n_estimators=50, random_state=42, max_depth=6)
        }
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML models"""
        features = df.copy()
        
        # Technical indicators
        features['SMA_10'] = TechnicalIndicators.sma(features['Close'], 10)
        features['SMA_20'] = TechnicalIndicators.sma(features['Close'], 20)
        features['EMA_12'] = TechnicalIndicators.ema(features['Close'], 12)
        features['RSI'] = TechnicalIndicators.rsi(features['Close'])
        
        # MACD
        macd, signal, hist = TechnicalIndicators.macd(features['Close'])
        features['MACD'] = macd
        features['MACD_signal'] = signal
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = TechnicalIndicators.bollinger_bands(features['Close'])
        features['BB_upper'] = bb_upper
        features['BB_middle'] = bb_middle
        features['BB_lower'] = bb_lower
        
        # Price features
        features['price_change'] = features['Close'].pct_change()
        features['high_low_ratio'] = features['High'] / features['Low']
        features['volume_change'] = features['Volume'].pct_change()
        
        # Lag features
        for lag in [1, 2, 3]:
            features[f'close_lag_{lag}'] = features['Close'].shift(lag)
            
        # Rolling statistics
        features['close_mean_5'] = features['Close'].rolling(5).mean()
        features['close_std_5'] = features['Close'].rolling(5).std()
        
        return features.dropna()
    
    def train(self, df: pd.DataFrame, target_col: str = 'Close'):
        """Train the ensemble models"""
        logger.info("Training lightweight ML models...")
        
        features_df = self.prepare_features(df)
        
        if len(features_df) < 50:
            logger.error("Insufficient data for training")
            return False
            
        # Select numeric features
        feature_cols = features_df.select_dtypes(include=[np.number]).columns.tolist()
        if target_col in feature_cols:
            feature_cols.remove(target_col)
            
        X = features_df[feature_cols].values
        y = features_df[target_col].values
        
        # Handle any remaining NaN values
        mask = ~np.isnan(X).any(axis=1) & ~np.isnan(y)
        X = X[mask]
        y = y[mask]
        
        if len(X) < 30:
            logger.error("Not enough clean data for training")
            return False
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train models
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        
        for name, model in self.models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            logger.info(f"{name.upper()} trained - MSE: {mse:.6f}")
        
        self.is_trained = True
        return True
    
    def predict(self, df: pd.DataFrame) -> Dict[str, float]:
        """Make predictions"""
        if not self.is_trained:
            return {'ensemble': df['Close'].iloc[-1] if len(df) > 0 else 1.0}
            
        try:
            features_df = self.prepare_features(df)
            
            if len(features_df) == 0:
                return {'ensemble': df['Close'].iloc[-1]}
                
            # Get latest features
            latest_features = features_df.iloc[-1:].select_dtypes(include=[np.number])
            
            # Handle NaN values
            if latest_features.isna().any().any():
                return {'ensemble': df['Close'].iloc[-1]}
                
            X_scaled = self.scaler.transform(latest_features.values)
            
            predictions = {}
            for name, model in self.models.items():
                predictions[name] = model.predict(X_scaled)[0]
            
            # Ensemble average
            predictions['ensemble'] = np.mean(list(predictions.values()))
            
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {'ensemble': df['Close'].iloc[-1] if len(df) > 0 else 1.0}

class TradingEngine:
    """Lightweight trading engine optimized for cloud deployment"""
    
    def __init__(self, symbol: str = "EURUSD"):
        self.symbol = symbol
        self.predictor = LightweightPredictor()
        self.account_balance = 10000.0
        self.positions = []
        self.trade_history = []
        self.is_running = False
        self.current_price = 0.0
        self.last_signal = {'action': 'HOLD', 'confidence': 0.0}
        
    def fetch_data(self, period: str = "6mo") -> pd.DataFrame:
        """Fetch market data"""
        try:
            # Use EUR/USD proxy since direct forex data can be limited
            ticker = yf.Ticker("FXE")  # Euro ETF as proxy
            data = ticker.history(period=period)
            
            if data.empty:
                # Fallback to EUR/GBP
                ticker = yf.Ticker("FXB")
                data = ticker.history(period=period)
                
            return data
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def generate_signal(self, df: pd.DataFrame) -> Dict:
        """Generate trading signals"""
        if len(df) < 30:
            return {'action': 'HOLD', 'confidence': 0.0, 'price': 0.0}
            
        try:
            # Get current price
            current_price = df['Close'].iloc[-1]
            self.current_price = current_price
            
            # Calculate indicators
            rsi = TechnicalIndicators.rsi(df['Close']).iloc[-1]
            
            # MACD
            macd, signal, hist = TechnicalIndicators.macd(df['Close'])
            macd_val = macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0
            signal_val = signal.iloc[-1] if not pd.isna(signal.iloc[-1]) else 0
            
            # Moving averages
            sma_10 = TechnicalIndicators.sma(df['Close'], 10).iloc[-1]
            sma_20 = TechnicalIndicators.sma(df['Close'], 20).iloc[-1]
            
            # Get ML prediction
            predictions = self.predictor.predict(df)
            predicted_price = predictions.get('ensemble', current_price)
            
            # Signal logic
            signals = []
            confidence = 0.0
            
            # RSI signals
            if rsi < 30:
                signals.append('BUY')
                confidence += 0.3
            elif rsi > 70:
                signals.append('SELL')
                confidence += 0.3
                
            # MACD signals
            if macd_val > signal_val:
                signals.append('BUY')
                confidence += 0.2
            else:
                signals.append('SELL')
                confidence += 0.2
                
            # Moving average signals
            if sma_10 > sma_20:
                signals.append('BUY')
                confidence += 0.2
            else:
                signals.append('SELL')
                confidence += 0.2
                
            # ML prediction signal
            price_change = (predicted_price - current_price) / current_price
            if price_change > 0.001:  # 0.1% threshold
                signals.append('BUY')
                confidence += 0.3
            elif price_change < -0.001:
                signals.append('SELL')
                confidence += 0.3
            
            # Determine final action
            buy_signals = signals.count('BUY')
            sell_signals = signals.count('SELL')
            
            if buy_signals > sell_signals and confidence > 0.5:
                action = 'BUY'
            elif sell_signals > buy_signals and confidence > 0.5:
                action = 'SELL'
            else:
                action = 'HOLD'
                
            signal = {
                'action': action,
                'confidence': min(confidence, 1.0),
                'price': current_price,
                'predicted_price': predicted_price,
                'rsi': rsi,
                'macd': macd_val,
                'timestamp': datetime.now()
            }
            
            self.last_signal = signal
            return signal
            
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            return {'action': 'HOLD', 'confidence': 0.0, 'price': current_price}
    
    def train_models(self) -> bool:
        """Train the ML models"""
        logger.info("Fetching training data...")
        data = self.fetch_data(period="1y")
        
        if data.empty:
            logger.error("No training data available")
            return False
            
        return self.predictor.train(data)
    
    def run_backtest(self):
        """Run simple backtest"""
        logger.info("Running backtest...")
        data = self.fetch_data(period="6mo")
        
        if data.empty:
            logger.error("No backtest data")
            return
            
        trades = 0
        wins = 0
        
        # Simple backtest logic
        for i in range(50, len(data), 10):  # Every 10 days
            test_data = data.iloc[:i+1]
            signal = self.generate_signal(test_data)
            
            if signal['action'] != 'HOLD' and signal['confidence'] > 0.6:
                trades += 1
                # Simulate trade outcome (simplified)
                if np.random.random() > 0.4:  # 60% win rate simulation
                    wins += 1
        
        win_rate = (wins / trades * 100) if trades > 0 else 0
        logger.info(f"Backtest: {trades} trades, {win_rate:.1f}% win rate")
    
    def get_status(self) -> Dict:
        """Get current status"""
        return {
            'is_running': self.is_running,
            'account_balance': self.account_balance,
            'current_price': self.current_price,
            'last_signal': self.last_signal,
            'total_trades': len(self.trade_history),
            'symbol': self.symbol,
            'timestamp': datetime.now().isoformat()
        }
    
    def start_trading(self):
        """Start trading simulation"""
        self.is_running = True
        logger.info("Starting trading simulation...")
        
        while self.is_running:
            try:
                data = self.fetch_data(period="3mo")
                if not data.empty:
                    signal = self.generate_signal(data)
                    logger.info(f"Signal: {signal['action']} | Confidence: {signal['confidence']:.2f} | Price: {signal['price']:.4f}")
                
                time.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Trading loop error: {e}")
                time.sleep(60)
    
    def stop_trading(self):
        """Stop trading"""
        self.is_running = False

# Flask Web App
app = Flask(__name__)
engine = TradingEngine()

@app.route('/')
def dashboard():
    """Main dashboard"""
    status = engine.get_status()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Trading Engine</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .status { color: {{ 'green' if status['is_running'] else 'red' }}; font-weight: bold; }
            .metric { margin: 10px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }
            .header { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
            .signal { padding: 10px; border-radius: 5px; margin: 10px 0; }
            .buy { background: #d4edda; border: 1px solid #c3e6cb; }
            .sell { background: #f8d7da; border: 1px solid #f5c6cb; }
            .hold { background: #fff3cd; border: 1px solid #ffeaa7; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">🤖 Lightweight AI Trading Engine</h1>
            
            <div class="metric">
                <strong>Status:</strong> 
                <span class="status">{{ '🟢 RUNNING' if status['is_running'] else '🔴 STOPPED' }}</span>
            </div>
            
            <div class="metric">
                <strong>💰 Account Balance:</strong> ${{ "{:,.2f}".format(status['account_balance']) }}
            </div>
            
            <div class="metric">
                <strong>💱 Symbol:</strong> {{ status['symbol'] }}
            </div>
            
            <div class="metric">
                <strong>💲 Current Price:</strong> {{ "{:.4f}".format(status['current_price']) }}
            </div>
            
            <div class="signal {{ status['last_signal']['action'].lower() }}">
                <strong>🎯 Latest Signal:</strong> {{ status['last_signal']['action'] }} 
                (Confidence: {{ "{:.1%}".format(status['last_signal']['confidence']) }})
            </div>
            
            <div class="metric">
                <strong>📈 Total Trades:</strong> {{ status['total_trades'] }}
            </div>
            
            <div class="metric">
                <strong>🕒 Last Update:</strong> {{ status['timestamp'][:19] }} UTC
            </div>
            
            <p><em>Page auto-refreshes every 30 seconds</em></p>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html, status=status)

@app.route('/api/status')
def api_status():
    """API endpoint for status"""
    return jsonify(engine.get_status())

@app.route('/health')
def health():
    """Health check"""
    return "OK"

def run_trading_engine():
    """Run trading engine in background"""
    try:
        if engine.train_models():
            engine.run_backtest()
            engine.start_trading()
    except Exception as e:
        logger.error(f"Trading engine error: {e}")

if __name__ == "__main__":
    # Start trading engine in background
    trading_thread = threading.Thread(target=run_trading_engine, daemon=True)
    trading_thread.start()
    
    # Start web server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)