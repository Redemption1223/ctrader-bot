#!/usr/bin/env python3
"""
ADVANCED AI TRADING ENGINE
Multi-model machine learning system for cTrader
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import yfinance as yf
import talib
import warnings
import logging
from datetime import datetime, timedelta
import json
import pickle
from typing import Dict, List, Tuple, Optional
import asyncio
import websocket
import threading
import time

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """Technical analysis indicators calculator"""
    
    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive technical indicators"""
        data = df.copy()
        
        # Price-based indicators
        data['SMA_10'] = talib.SMA(data['Close'], timeperiod=10)
        data['SMA_20'] = talib.SMA(data['Close'], timeperiod=20)
        data['SMA_50'] = talib.SMA(data['Close'], timeperiod=50)
        data['EMA_12'] = talib.EMA(data['Close'], timeperiod=12)
        data['EMA_26'] = talib.EMA(data['Close'], timeperiod=26)
        
        # MACD
        data['MACD'], data['MACD_signal'], data['MACD_hist'] = talib.MACD(data['Close'])
        
        # RSI
        data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
        
        # Bollinger Bands
        data['BB_upper'], data['BB_middle'], data['BB_lower'] = talib.BBANDS(data['Close'])
        
        # Stochastic
        data['STOCH_K'], data['STOCH_D'] = talib.STOCH(data['High'], data['Low'], data['Close'])
        
        # ATR
        data['ATR'] = talib.ATR(data['High'], data['Low'], data['Close'])
        
        # Volume indicators
        data['OBV'] = talib.OBV(data['Close'], data['Volume'])
        data['AD'] = talib.AD(data['High'], data['Low'], data['Close'], data['Volume'])
        
        # Price patterns
        data['DOJI'] = talib.CDLDOJI(data['Open'], data['High'], data['Low'], data['Close'])
        data['HAMMER'] = talib.CDLHAMMER(data['Open'], data['High'], data['Low'], data['Close'])
        
        return data

class LSTMModel:
    """LSTM Neural Network for price prediction"""
    
    def __init__(self, sequence_length: int = 60):
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = MinMaxScaler()
        
    def build_model(self, input_shape: Tuple[int, int]) -> tf.keras.Model:
        """Build LSTM model architecture"""
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(50, return_sequences=True, input_shape=input_shape),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.LSTM(50, return_sequences=True),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.LSTM(50),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(25),
            tf.keras.layers.Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
    
    def prepare_data(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequences for LSTM training"""
        scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))
        
        X, y = [], []
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i, 0])
            y.append(scaled_data[i, 0])
            
        return np.array(X), np.array(y)
    
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 100):
        """Train the LSTM model"""
        X = X.reshape((X.shape[0], X.shape[1], 1))
        
        if self.model is None:
            self.model = self.build_model((X.shape[1], 1))
            
        self.model.fit(X, y, epochs=epochs, batch_size=32, verbose=0)
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        X = X.reshape((X.shape[0], X.shape[1], 1))
        predictions = self.model.predict(X)
        return self.scaler.inverse_transform(predictions)

class EnsemblePredictor:
    """Ensemble of multiple ML models"""
    
    def __init__(self):
        self.models = {
            'rf': RandomForestRegressor(n_estimators=100, random_state=42),
            'gb': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'lstm': LSTMModel()
        }
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML models"""
        features = df.copy()
        
        # Price-based features
        features['price_change'] = features['Close'].pct_change()
        features['high_low_ratio'] = features['High'] / features['Low']
        features['volume_change'] = features['Volume'].pct_change()
        
        # Lag features
        for lag in [1, 2, 3, 5]:
            features[f'close_lag_{lag}'] = features['Close'].shift(lag)
            features[f'volume_lag_{lag}'] = features['Volume'].shift(lag)
            
        # Rolling statistics
        for window in [5, 10, 20]:
            features[f'close_mean_{window}'] = features['Close'].rolling(window).mean()
            features[f'close_std_{window}'] = features['Close'].rolling(window).std()
            features[f'volume_mean_{window}'] = features['Volume'].rolling(window).mean()
            
        return features.dropna()
    
    def train(self, df: pd.DataFrame, target_col: str = 'Close'):
        """Train all models in the ensemble"""
        logger.info("Training ensemble models...")
        
        # Prepare features
        features_df = self.prepare_features(df)
        
        # Select feature columns (exclude target and non-numeric)
        feature_cols = features_df.select_dtypes(include=[np.number]).columns.tolist()
        if target_col in feature_cols:
            feature_cols.remove(target_col)
            
        X = features_df[feature_cols].values
        y = features_df[target_col].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train traditional ML models
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        
        self.models['rf'].fit(X_train, y_train)
        self.models['gb'].fit(X_train, y_train)
        
        # Train LSTM
        lstm_X, lstm_y = self.models['lstm'].prepare_data(y)
        if len(lstm_X) > 0:
            self.models['lstm'].train(lstm_X, lstm_y, epochs=50)
        
        self.is_trained = True
        logger.info("Ensemble training completed")
        
        # Evaluate models
        self._evaluate_models(X_test, y_test)
        
    def _evaluate_models(self, X_test: np.ndarray, y_test: np.ndarray):
        """Evaluate model performance"""
        for name, model in self.models.items():
            if name == 'lstm':
                continue  # Skip LSTM evaluation for now
                
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            logger.info(f"{name.upper()} - MSE: {mse:.4f}, MAE: {mae:.4f}")
    
    def predict(self, df: pd.DataFrame) -> Dict[str, float]:
        """Make ensemble predictions"""
        if not self.is_trained:
            raise ValueError("Models must be trained before prediction")
            
        features_df = self.prepare_features(df)
        
        # Get latest features
        latest_features = features_df.iloc[-1:].select_dtypes(include=[np.number])
        X_scaled = self.scaler.transform(latest_features.values)
        
        predictions = {}
        
        # Traditional ML predictions
        predictions['rf'] = self.models['rf'].predict(X_scaled)[0]
        predictions['gb'] = self.models['gb'].predict(X_scaled)[0]
        
        # LSTM prediction
        if len(df) >= self.models['lstm'].sequence_length:
            recent_prices = df['Close'].tail(self.models['lstm'].sequence_length).values
            lstm_X, _ = self.models['lstm'].prepare_data(recent_prices)
            if len(lstm_X) > 0:
                predictions['lstm'] = self.models['lstm'].predict(lstm_X[-1:].reshape(1, -1))[0][0]
        
        # Ensemble average
        predictions['ensemble'] = np.mean(list(predictions.values()))
        
        return predictions

class RiskManager:
    """Risk management and position sizing"""
    
    def __init__(self, max_risk_per_trade: float = 0.02, max_portfolio_risk: float = 0.1):
        self.max_risk_per_trade = max_risk_per_trade
        self.max_portfolio_risk = max_portfolio_risk
        
    def calculate_position_size(self, account_balance: float, entry_price: float, 
                              stop_loss: float, confidence: float) -> float:
        """Calculate position size based on risk management"""
        risk_amount = account_balance * self.max_risk_per_trade
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0
            
        base_position_size = risk_amount / price_risk
        
        # Adjust based on confidence
        adjusted_size = base_position_size * confidence
        
        return min(adjusted_size, account_balance * 0.1)  # Max 10% of balance per trade
    
    def should_enter_trade(self, current_positions: int, confidence: float) -> bool:
        """Determine if we should enter a new trade"""
        max_positions = 5  # Maximum concurrent positions
        min_confidence = 0.6  # Minimum confidence threshold
        
        return current_positions < max_positions and confidence >= min_confidence

class AITradingEngine:
    """Main AI Trading Engine"""
    
    def __init__(self, symbol: str = "EURUSD", timeframe: str = "1h"):
        self.symbol = symbol
        self.timeframe = timeframe
        self.predictor = EnsemblePredictor()
        self.risk_manager = RiskManager()
        self.technical_indicators = TechnicalIndicators()
        
        self.account_balance = 10000.0  # Starting balance
        self.positions = []
        self.trade_history = []
        self.is_running = False
        
    def fetch_data(self, period: str = "1y") -> pd.DataFrame:
        """Fetch market data"""
        try:
            # For demo purposes, using stock data (replace with forex data source)
            ticker = yf.Ticker("EURUSD=X")
            data = ticker.history(period=period)
            
            if data.empty:
                # Fallback to EUR/USD proxy
                ticker = yf.Ticker("FXE")  # Euro ETF
                data = ticker.history(period=period)
                
            return data
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess market data with technical indicators"""
        if df.empty:
            return df
            
        # Add technical indicators
        processed_data = self.technical_indicators.calculate_indicators(df)
        
        # Clean data
        processed_data = processed_data.dropna()
        
        return processed_data
    
    def generate_signals(self, df: pd.DataFrame) -> Dict:
        """Generate trading signals"""
        if len(df) < 50:  # Need sufficient data
            return {'action': 'HOLD', 'confidence': 0.0}
            
        try:
            # Get predictions
            predictions = self.predictor.predict(df)
            
            current_price = df['Close'].iloc[-1]
            predicted_price = predictions['ensemble']
            
            # Calculate signal strength
            price_change_pct = (predicted_price - current_price) / current_price
            
            # Technical analysis signals
            latest = df.iloc[-1]
            
            # RSI signal
            rsi_signal = 0
            if latest['RSI'] < 30:
                rsi_signal = 1  # Oversold - buy signal
            elif latest['RSI'] > 70:
                rsi_signal = -1  # Overbought - sell signal
                
            # MACD signal
            macd_signal = 0
            if latest['MACD'] > latest['MACD_signal']:
                macd_signal = 1
            else:
                macd_signal = -1
                
            # Moving average signal
            ma_signal = 0
            if latest['Close'] > latest['SMA_20']:
                ma_signal = 1
            else:
                ma_signal = -1
                
            # Combine signals
            technical_score = (rsi_signal + macd_signal + ma_signal) / 3
            price_score = np.tanh(price_change_pct * 10)  # Normalize
            
            combined_score = (technical_score + price_score) / 2
            confidence = abs(combined_score)
            
            # Determine action
            if combined_score > 0.3:
                action = 'BUY'
            elif combined_score < -0.3:
                action = 'SELL'
            else:
                action = 'HOLD'
                
            return {
                'action': action,
                'confidence': confidence,
                'predicted_price': predicted_price,
                'current_price': current_price,
                'technical_score': technical_score,
                'price_score': price_score,
                'predictions': predictions
            }
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return {'action': 'HOLD', 'confidence': 0.0}
    
    def execute_trade(self, signal: Dict, df: pd.DataFrame):
        """Execute trade based on signal"""
        if signal['action'] == 'HOLD':
            return
            
        current_price = signal['current_price']
        confidence = signal['confidence']
        
        # Calculate stop loss and take profit
        atr = df['ATR'].iloc[-1]
        
        if signal['action'] == 'BUY':
            stop_loss = current_price - (2 * atr)
            take_profit = current_price + (3 * atr)
        else:  # SELL
            stop_loss = current_price + (2 * atr)
            take_profit = current_price - (3 * atr)
            
        # Check if we should enter trade
        if not self.risk_manager.should_enter_trade(len(self.positions), confidence):
            logger.info(f"Trade rejected - Risk management criteria not met")
            return
            
        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            self.account_balance, current_price, stop_loss, confidence
        )
        
        if position_size > 0:
            trade = {
                'id': len(self.trade_history) + 1,
                'symbol': self.symbol,
                'action': signal['action'],
                'entry_price': current_price,
                'position_size': position_size,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': confidence,
                'timestamp': datetime.now(),
                'status': 'OPEN'
            }
            
            self.positions.append(trade)
            self.trade_history.append(trade)
            
            logger.info(f"Trade executed: {signal['action']} {position_size:.2f} units at {current_price:.5f}")
    
    def manage_positions(self, current_price: float):
        """Manage open positions"""
        for position in self.positions[:]:  # Copy list to avoid modification during iteration
            if position['status'] != 'OPEN':
                continue
                
            # Check stop loss and take profit
            if position['action'] == 'BUY':
                if current_price <= position['stop_loss']:
                    self._close_position(position, current_price, 'STOP_LOSS')
                elif current_price >= position['take_profit']:
                    self._close_position(position, current_price, 'TAKE_PROFIT')
            else:  # SELL
                if current_price >= position['stop_loss']:
                    self._close_position(position, current_price, 'STOP_LOSS')
                elif current_price <= position['take_profit']:
                    self._close_position(position, current_price, 'TAKE_PROFIT')
    
    def _close_position(self, position: Dict, exit_price: float, reason: str):
        """Close a position"""
        position['exit_price'] = exit_price
        position['exit_time'] = datetime.now()
        position['status'] = 'CLOSED'
        position['close_reason'] = reason
        
        # Calculate P&L
        if position['action'] == 'BUY':
            pnl = (exit_price - position['entry_price']) * position['position_size']
        else:
            pnl = (position['entry_price'] - exit_price) * position['position_size']
            
        position['pnl'] = pnl
        self.account_balance += pnl
        
        # Remove from active positions
        if position in self.positions:
            self.positions.remove(position)
            
        logger.info(f"Position closed: {reason} - P&L: {pnl:.2f}")
    
    def train_models(self):
        """Train the AI models"""
        logger.info("Fetching training data...")
        data = self.fetch_data(period="2y")
        
        if data.empty:
            logger.error("No data available for training")
            return False
            
        processed_data = self.preprocess_data(data)
        
        if len(processed_data) < 100:
            logger.error("Insufficient data for training")
            return False
            
        self.predictor.train(processed_data)
        logger.info("Model training completed")
        return True
    
    def run_backtest(self, start_date: str = None, end_date: str = None):
        """Run backtesting"""
        logger.info("Starting backtest...")
        
        data = self.fetch_data(period="1y")
        if data.empty:
            logger.error("No data for backtesting")
            return
            
        processed_data = self.preprocess_data(data)
        
        # Reset for backtest
        self.account_balance = 10000.0
        self.positions = []
        self.trade_history = []
        
        # Run through historical data
        for i in range(100, len(processed_data)):  # Start after sufficient data
            current_data = processed_data.iloc[:i+1]
            current_price = current_data['Close'].iloc[-1]
            
            # Generate signal
            signal = self.generate_signals(current_data)
            
            # Manage existing positions
            self.manage_positions(current_price)
            
            # Execute new trades
            self.execute_trade(signal, current_data)
            
        # Close remaining positions
        final_price = processed_data['Close'].iloc[-1]
        for position in self.positions[:]:
            self._close_position(position, final_price, 'BACKTEST_END')
            
        self._print_backtest_results()
    
    def _print_backtest_results(self):
        """Print backtest results"""
        total_trades = len(self.trade_history)
        winning_trades = len([t for t in self.trade_history if t.get('pnl', 0) > 0])
        
        if total_trades > 0:
            win_rate = winning_trades / total_trades * 100
            total_pnl = sum([t.get('pnl', 0) for t in self.trade_history])
            
            logger.info("=== BACKTEST RESULTS ===")
            logger.info(f"Total Trades: {total_trades}")
            logger.info(f"Winning Trades: {winning_trades}")
            logger.info(f"Win Rate: {win_rate:.2f}%")
            logger.info(f"Total P&L: {total_pnl:.2f}")
            logger.info(f"Final Balance: {self.account_balance:.2f}")
            logger.info(f"Return: {((self.account_balance - 10000) / 10000 * 100):.2f}%")
    
    def start_live_trading(self):
        """Start live trading (demo mode)"""
        logger.info("Starting live trading engine...")
        self.is_running = True
        
        while self.is_running:
            try:
                # Fetch latest data
                data = self.fetch_data(period="3mo")
                if data.empty:
                    time.sleep(60)
                    continue
                    
                processed_data = self.preprocess_data(data)
                current_price = processed_data['Close'].iloc[-1]
                
                # Generate signals
                signal = self.generate_signals(processed_data)
                
                # Manage positions
                self.manage_positions(current_price)
                
                # Execute trades
                self.execute_trade(signal, processed_data)
                
                # Log status
                logger.info(f"Price: {current_price:.5f}, Signal: {signal['action']}, "
                          f"Confidence: {signal['confidence']:.3f}, "
                          f"Positions: {len(self.positions)}, Balance: {self.account_balance:.2f}")
                
                # Wait before next iteration
                time.sleep(300)  # 5 minutes
                
            except KeyboardInterrupt:
                logger.info("Stopping trading engine...")
                self.is_running = False
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                time.sleep(60)
    
    def stop_trading(self):
        """Stop the trading engine"""
        self.is_running = False
        logger.info("Trading engine stopped")
    
    def get_status(self) -> Dict:
        """Get current engine status"""
        return {
            'is_running': self.is_running,
            'account_balance': self.account_balance,
            'open_positions': len(self.positions),
            'total_trades': len(self.trade_history),
            'symbol': self.symbol,
            'timeframe': self.timeframe
        }
    
    def save_model(self, filepath: str):
        """Save trained models"""
        try:
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'predictor': self.predictor,
                    'scaler': self.predictor.scaler
                }, f)
            logger.info(f"Model saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_model(self, filepath: str):
        """Load trained models"""
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.predictor = data['predictor']
            logger.info(f"Model loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")

class TradingWebServer:
    """Web server for Render deployment"""
    
    def __init__(self, engine):
        self.engine = engine
        
    def create_app(self):
        """Create Flask-like web app for status monitoring"""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json
        import threading
        
        class TradingHandler(BaseHTTPRequestHandler):
            def __init__(self, engine, *args, **kwargs):
                self.engine = engine
                super().__init__(*args, **kwargs)
                
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    status = self.engine.get_status()
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>AI Trading Engine</title>
                        <meta http-equiv="refresh" content="30">
                        <style>
                            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                            .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                            .status {{ color: {'green' if status['is_running'] else 'red'}; font-weight: bold; }}
                            .metric {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
                            .header {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1 class="header">🤖 AI Trading Engine Dashboard</h1>
                            <div class="metric">
                                <strong>Status:</strong> 
                                <span class="status">{'🟢 RUNNING' if status['is_running'] else '🔴 STOPPED'}</span>
                            </div>
                            <div class="metric">
                                <strong>💰 Account Balance:</strong> ${status['account_balance']:,.2f}
                            </div>
                            <div class="metric">
                                <strong>📊 Open Positions:</strong> {status['open_positions']}
                            </div>
                            <div class="metric">
                                <strong>📈 Total Trades:</strong> {status['total_trades']}
                            </div>
                            <div class="metric">
                                <strong>💱 Trading Pair:</strong> {status['symbol']}
                            </div>
                            <div class="metric">
                                <strong>⏰ Timeframe:</strong> {status['timeframe']}
                            </div>
                            <div class="metric">
                                <strong>🕒 Last Update:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
                            </div>
                            <p><em>Page auto-refreshes every 30 seconds</em></p>
                        </div>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
                    
                elif self.path == '/status':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    status = self.engine.get_status()
                    self.wfile.write(json.dumps(status, default=str).encode())
                    
                elif self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'OK')
                    
                else:
                    self.send_response(404)
                    self.end_headers()
                    
            def log_message(self, format, *args):
                # Suppress default HTTP logging
                pass
        
        def handler(*args, **kwargs):
            TradingHandler(self.engine, *args, **kwargs)
            
        return handler
    
    def start_server(self, port=8080):
        """Start web server for Render"""
        handler = self.create_app()
        server = HTTPServer(('0.0.0.0', port), handler)
        
        logger.info(f"🌐 Web server starting on port {port}")
        logger.info(f"📊 Dashboard: http://localhost:{port}")
        logger.info(f"🔍 Status API: http://localhost:{port}/status")
        
        # Start trading engine in background thread
        trading_thread = threading.Thread(target=self.run_trading_engine, daemon=True)
        trading_thread.start()
        
        # Start web server (blocking)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down server...")
            self.engine.stop_trading()
            server.shutdown()
    
    def run_trading_engine(self):
        """Run the trading engine in background"""
        try:
            # Train models first
            if self.engine.train_models():
                logger.info("✅ Models trained successfully")
                
                # Run backtest
                self.engine.run_backtest()
                
                # Start live trading simulation
                logger.info("🚀 Starting live trading simulation...")
                self.engine.start_live_trading()
            else:
                logger.error("❌ Failed to train models")
                
        except Exception as e:
            logger.error(f"❌ Trading engine error: {e}")

if __name__ == "__main__":
    import os
    import threading
    
    # Get port from environment (Render sets this)
    port = int(os.environ.get('PORT', 8080))
    
    # Initialize trading engine
    logger.info("🚀 Initializing AI Trading Engine for Render deployment...")
    engine = AITradingEngine(symbol="EURUSD", timeframe="1h")
    
    # Create and start web server
    web_server = TradingWebServer(engine)
    web_server.start_server(port=port)