#!/usr/bin/env python3
"""
BULLETPROOF TRADING ENGINE
Pure Python - Zero ML dependencies - Guaranteed to work everywhere
"""

import requests
import json
import time
import os
import threading
import random
import math
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify

def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

class PurePythonIndicators:
    """Pure Python technical indicators - no external libraries"""
    
    @staticmethod
    def sma(prices, period):
        """Simple Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        return sum(prices[-period:]) / period
    
    @staticmethod
    def ema(prices, period):
        """Exponential Moving Average"""
        if len(prices) < 2:
            return prices[-1] if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    @staticmethod
    def rsi(prices, period=14):
        """Relative Strength Index"""
        if len(prices) < period + 1:
            return 50
        
        changes = []
        for i in range(1, len(prices)):
            changes.append(prices[i] - prices[i-1])
        
        if len(changes) < period:
            return 50
        
        gains = [max(0, change) for change in changes[-period:]]
        losses = [max(0, -change) for change in changes[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def macd(prices, fast=12, slow=26):
        """MACD Indicator"""
        if len(prices) < slow:
            return 0, 0
        
        ema_fast = PurePythonIndicators.ema(prices, fast)
        ema_slow = PurePythonIndicators.ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        
        # Simple signal line (could be improved)
        signal_line = macd_line * 0.9  # Simplified
        
        return macd_line, signal_line

class MarketDataSimulator:
    """Simulate realistic market data without external APIs"""
    
    def __init__(self):
        self.base_price = 1.0850  # EUR/USD base
        self.price_history = []
        self.last_update = time.time()
        
    def get_current_price(self):
        """Generate realistic price movement"""
        now = time.time()
        
        # Time-based volatility
        hour = datetime.now().hour
        if 8 <= hour <= 16:  # London session
            volatility = 0.0015
        elif 13 <= hour <= 21:  # NY session  
            volatility = 0.0012
        else:  # Asian/quiet
            volatility = 0.0008
        
        # Price movement simulation
        time_diff = now - self.last_update
        if time_diff > 60:  # Update every minute
            
            # Trend component (daily cycle)
            trend = math.sin((now % 86400) / 86400 * 2 * math.pi) * 0.002
            
            # Random walk
            random_move = random.uniform(-volatility, volatility)
            
            # News events (rare spikes)
            if random.random() < 0.01:  # 1% chance
                news_spike = random.uniform(-0.003, 0.003)
            else:
                news_spike = 0
            
            # Update price
            price_change = trend + random_move + news_spike
            self.base_price += price_change
            
            # Keep price in reasonable range
            if self.base_price < 1.0500:
                self.base_price = 1.0500
            elif self.base_price > 1.1200:
                self.base_price = 1.1200
            
            self.last_update = now
        
        return round(self.base_price, 5)
    
    def get_price_history(self, periods=100):
        """Get historical prices for analysis"""
        if len(self.price_history) < periods:
            # Generate initial history
            base = 1.0850
            for i in range(periods):
                change = random.uniform(-0.001, 0.001)
                base += change
                self.price_history.append(round(base, 5))
        
        # Add current price
        current = self.get_current_price()
        self.price_history.append(current)
        
        # Keep last 200 prices
        if len(self.price_history) > 200:
            self.price_history = self.price_history[-200:]
        
        return self.price_history.copy()

class SimpleTradingEngine:
    """Ultra-simple trading engine with pure Python logic"""
    
    def __init__(self):
        self.symbol = "EURUSD"
        self.account_balance = 10000.0
        self.positions = []
        self.trade_history = []
        self.is_running = False
        
        self.market_data = MarketDataSimulator()
        self.indicators = PurePythonIndicators()
        
        self.current_price = 0.0
        self.last_signal = {
            'action': 'HOLD',
            'confidence': 0.0,
            'price': 0.0,
            'rsi': 50,
            'macd': 0,
            'timestamp': datetime.now()
        }
        
        log("🚀 Simple Trading Engine initialized")
    
    def analyze_market(self):
        """Analyze market and generate signals"""
        try:
            # Get price data
            prices = self.market_data.get_price_history()
            current_price = prices[-1]
            self.current_price = current_price
            
            # Calculate indicators
            rsi = self.indicators.rsi(prices)
            sma_10 = self.indicators.sma(prices, 10)
            sma_20 = self.indicators.sma(prices, 20)
            macd_line, macd_signal = self.indicators.macd(prices)
            
            # Generate signals
            signals = []
            confidence = 0.0
            
            # RSI signals (mean reversion)
            if rsi < 30:
                signals.append('BUY')
                confidence += 0.4
            elif rsi > 70:
                signals.append('SELL')
                confidence += 0.4
            elif rsi < 40:
                signals.append('BUY')
                confidence += 0.2
            elif rsi > 60:
                signals.append('SELL')
                confidence += 0.2
            
            # Moving average signals (trend following)
            if sma_10 > sma_20:
                signals.append('BUY')
                confidence += 0.3
            else:
                signals.append('SELL')
                confidence += 0.3
            
            # MACD signals
            if macd_line > macd_signal:
                signals.append('BUY')
                confidence += 0.2
            else:
                signals.append('SELL')
                confidence += 0.2
            
            # Price momentum
            if len(prices) >= 5:
                recent_change = (prices[-1] - prices[-5]) / prices[-5]
                if recent_change > 0.001:  # 0.1% up
                    signals.append('BUY')
                    confidence += 0.1
                elif recent_change < -0.001:  # 0.1% down
                    signals.append('SELL')
                    confidence += 0.1
            
            # Determine final action
            buy_count = signals.count('BUY')
            sell_count = signals.count('SELL')
            
            if buy_count > sell_count and confidence > 0.5:
                action = 'BUY'
            elif sell_count > buy_count and confidence > 0.5:
                action = 'SELL'
            else:
                action = 'HOLD'
            
            # Create signal
            signal = {
                'action': action,
                'confidence': min(confidence, 1.0),
                'price': current_price,
                'rsi': rsi,
                'macd': macd_line,
                'sma_10': sma_10,
                'sma_20': sma_20,
                'timestamp': datetime.now()
            }
            
            self.last_signal = signal
            return signal
            
        except Exception as e:
            log(f"❌ Analysis error: {e}")
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'price': self.current_price,
                'rsi': 50,
                'macd': 0,
                'timestamp': datetime.now()
            }
    
    def execute_trade(self, signal):
        """Execute trades based on signals"""
        if signal['action'] == 'HOLD' or signal['confidence'] < 0.6:
            return
        
        # Simple position sizing
        risk_amount = self.account_balance * 0.02  # 2% risk
        position_size = int(risk_amount * 100)  # Convert to units
        
        trade = {
            'id': len(self.trade_history) + 1,
            'action': signal['action'],
            'price': signal['price'],
            'size': position_size,
            'confidence': signal['confidence'],
            'timestamp': datetime.now(),
            'status': 'OPEN'
        }
        
        self.positions.append(trade)
        self.trade_history.append(trade)
        
        log(f"📈 Trade: {signal['action']} {position_size} units at {signal['price']:.5f} (Confidence: {signal['confidence']:.2f})")
    
    def manage_positions(self):
        """Manage open positions"""
        current_price = self.current_price
        
        for position in self.positions[:]:
            if position['status'] != 'OPEN':
                continue
            
            # Simple profit/loss calculation
            if position['action'] == 'BUY':
                pnl = (current_price - position['price']) * position['size']
            else:  # SELL
                pnl = (position['price'] - current_price) * position['size']
            
            # Close position conditions
            should_close = False
            close_reason = ""
            
            # Take profit (2% gain)
            if pnl > position['size'] * 0.02:
                should_close = True
                close_reason = "TAKE_PROFIT"
            
            # Stop loss (1% loss)
            elif pnl < -position['size'] * 0.01:
                should_close = True
                close_reason = "STOP_LOSS"
            
            # Time-based exit (hold for max 1 hour in simulation)
            elif (datetime.now() - position['timestamp']).seconds > 3600:
                should_close = True
                close_reason = "TIME_EXIT"
            
            if should_close:
                position['status'] = 'CLOSED'
                position['exit_price'] = current_price
                position['pnl'] = pnl
                position['close_reason'] = close_reason
                
                self.account_balance += pnl
                self.positions.remove(position)
                
                log(f"💰 Position closed: {close_reason} - P&L: ${pnl:.2f}")
    
    def get_status(self):
        """Get current engine status"""
        return {
            'is_running': self.is_running,
            'account_balance': round(self.account_balance, 2),
            'current_price': self.current_price,
            'open_positions': len(self.positions),
            'total_trades': len(self.trade_history),
            'last_signal': {
                'action': self.last_signal['action'],
                'confidence': round(self.last_signal['confidence'], 3),
                'rsi': round(self.last_signal.get('rsi', 50), 1),
                'price': self.last_signal.get('price', 0)
            },
            'symbol': self.symbol,
            'timestamp': datetime.now().isoformat()
        }
    
    def start_trading(self):
        """Start the trading loop"""
        self.is_running = True
        log("🚀 Starting trading simulation...")
        
        while self.is_running:
            try:
                # Analyze market
                signal = self.analyze_market()
                
                # Manage existing positions
                self.manage_positions()
                
                # Execute new trades
                if len(self.positions) < 3:  # Max 3 concurrent positions
                    self.execute_trade(signal)
                
                # Log status
                log(f"💹 Price: {self.current_price:.5f} | Signal: {signal['action']} | "
                    f"Confidence: {signal['confidence']:.2f} | RSI: {signal['rsi']:.1f} | "
                    f"Balance: ${self.account_balance:.2f}")
                
                # Wait before next iteration
                time.sleep(30)  # 30 seconds
                
            except Exception as e:
                log(f"❌ Trading loop error: {e}")
                time.sleep(60)
    
    def stop_trading(self):
        """Stop trading"""
        self.is_running = False
        log("🛑 Trading stopped")

# Flask Web Application
app = Flask(__name__)
trading_engine = SimpleTradingEngine()

@app.route('/')
def dashboard():
    """Trading dashboard"""
    status = trading_engine.get_status()
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pure Python Trading Engine</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
            }
            .container { 
                max-width: 1200px;
                margin: 0 auto;
                background: white; 
                padding: 30px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .header { 
                text-align: center;
                color: #2c3e50; 
                border-bottom: 3px solid #3498db; 
                padding-bottom: 20px;
                margin-bottom: 30px;
            }
            .metrics {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .metric { 
                padding: 20px; 
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 10px;
                border-left: 5px solid #007bff;
                transition: transform 0.2s;
            }
            .metric:hover {
                transform: translateY(-2px);
            }
            .metric-value {
                font-size: 1.5em;
                font-weight: bold;
                color: #2c3e50;
            }
            .metric-label {
                color: #6c757d;
                font-size: 0.9em;
                margin-bottom: 5px;
            }
            .status-running { color: #28a745; }
            .status-stopped { color: #dc3545; }
            .signal { 
                padding: 20px; 
                border-radius: 10px; 
                margin: 20px 0;
                text-align: center;
                font-size: 1.2em;
                font-weight: bold;
            }
            .signal-buy { 
                background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                border: 2px solid #28a745;
                color: #155724;
            }
            .signal-sell { 
                background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
                border: 2px solid #dc3545;
                color: #721c24;
            }
            .signal-hold { 
                background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
                border: 2px solid #ffc107;
                color: #856404;
            }
            .footer {
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #dee2e6;
                color: #6c757d;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">🤖 Pure Python Trading Engine</h1>
            
            <div class="metrics">
                <div class="metric">
                    <div class="metric-label">Engine Status</div>
                    <div class="metric-value {{ 'status-running' if status['is_running'] else 'status-stopped' }}">
                        {{ '🟢 RUNNING' if status['is_running'] else '🔴 STOPPED' }}
                    </div>
                </div>
                
                <div class="metric">
                    <div class="metric-label">Account Balance</div>
                    <div class="metric-value">${{ "{:,.2f}".format(status['account_balance']) }}</div>
                </div>
                
                <div class="metric">
                    <div class="metric-label">Current Price ({{ status['symbol'] }})</div>
                    <div class="metric-value">{{ "{:.5f}".format(status['current_price']) }}</div>
                </div>
                
                <div class="metric">
                    <div class="metric-label">Open Positions</div>
                    <div class="metric-value">{{ status['open_positions'] }}</div>
                </div>
                
                <div class="metric">
                    <div class="metric-label">Total Trades</div>
                    <div class="metric-value">{{ status['total_trades'] }}</div>
                </div>
                
                <div class="metric">
                    <div class="metric-label">RSI Indicator</div>
                    <div class="metric-value">{{ "{:.1f}".format(status['last_signal']['rsi']) }}</div>
                </div>
            </div>
            
            <div class="signal signal-{{ status['last_signal']['action'].lower() }}">
                🎯 Latest Signal: {{ status['last_signal']['action'] }} 
                (Confidence: {{ "{:.1%}".format(status['last_signal']['confidence']) }})
            </div>
            
            <div class="footer">
                <p>🕒 Last Update: {{ status['timestamp'][:19] }} UTC</p>
                <p><em>Pure Python • Zero ML Dependencies • Bulletproof Deployment</em></p>
                <p><em>Page auto-refreshes every 30 seconds</em></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html_template, status=status)

@app.route('/api/status')
def api_status():
    """API endpoint"""
    return jsonify(trading_engine.get_status())

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return "OK", 200

def start_trading_background():
    """Start trading in background thread"""
    try:
        trading_engine.start_trading()
    except Exception as e:
        log(f"❌ Trading engine error: {e}")

if __name__ == "__main__":
    log("🚀 Starting Pure Python Trading Engine")
    
    # Start trading engine in background
    trading_thread = threading.Thread(target=start_trading_background, daemon=True)
    trading_thread.start()
    
    # Start Flask web server
    port = int(os.environ.get('PORT', 5000))
    log(f"🌐 Web server starting on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)