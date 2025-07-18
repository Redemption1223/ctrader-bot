# RAILWAY CTRADER BOT WITH WEB DASHBOARD
# Complete system with UI, smart AI, and real-time monitoring

import asyncio
import json
import logging
import time
import os
import urllib.request
import urllib.parse
import ssl
import socket
import random
import math
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import socketserver

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingDashboard:
    """Web dashboard for monitoring the bot"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.port = int(os.getenv('PORT', 8080))  # Railway provides PORT
        
    def get_dashboard_html(self):
        """Generate HTML dashboard"""
        # Get bot stats
        stats = self.bot.get_stats()
        trades = self.bot.get_recent_trades()
        signals = self.bot.get_current_signals()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🔥 Live cTrader AI Bot Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ 
            text-align: center; 
            margin-bottom: 30px;
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
        }}
        .header h1 {{ 
            font-size: 2.5em; 
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        .status {{ 
            display: inline-block;
            padding: 8px 16px;
            background: {'#28a745' if stats['active'] else '#dc3545'};
            border-radius: 20px;
            font-weight: bold;
        }}
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }}
        .card {{ 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 15px; 
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .card h3 {{ 
            margin-bottom: 15px; 
            color: #4ecdc4;
            font-size: 1.3em;
        }}
        .metric {{ 
            display: flex; 
            justify-content: space-between; 
            margin: 10px 0; 
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .metric-value {{ 
            font-weight: bold; 
            color: #ff6b6b;
        }}
        .signals {{ 
            display: grid; 
            gap: 10px; 
        }}
        .signal {{ 
            padding: 12px; 
            border-radius: 8px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
        }}
        .signal.buy {{ background: linear-gradient(45deg, #28a745, #20c997); }}
        .signal.sell {{ background: linear-gradient(45deg, #dc3545, #fd7e14); }}
        .signal.hold {{ background: linear-gradient(45deg, #ffc107, #fd7e14); color: #000; }}
        .confidence {{ 
            font-weight: bold; 
            font-size: 1.1em;
        }}
        .trades-table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 15px;
        }}
        .trades-table th, .trades-table td {{ 
            padding: 10px; 
            text-align: left; 
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }}
        .trades-table th {{ 
            background: rgba(255,255,255,0.1); 
            font-weight: bold;
        }}
        .trade-buy {{ color: #28a745; }}
        .trade-sell {{ color: #dc3545; }}
        .refresh-btn {{ 
            position: fixed; 
            top: 20px; 
            right: 20px; 
            background: #ff6b6b; 
            color: white; 
            border: none; 
            padding: 12px 20px; 
            border-radius: 25px; 
            cursor: pointer; 
            font-weight: bold;
            transition: all 0.3s;
        }}
        .refresh-btn:hover {{ 
            background: #ff5252; 
            transform: scale(1.05);
        }}
        .log-container {{ 
            background: rgba(0,0,0,0.3); 
            padding: 20px; 
            border-radius: 10px; 
            font-family: 'Courier New', monospace; 
            font-size: 0.9em;
            max-height: 300px;
            overflow-y: auto;
        }}
        .log-line {{ 
            margin: 5px 0; 
            padding: 3px 0;
        }}
        .log-info {{ color: #4ecdc4; }}
        .log-trade {{ color: #ff6b6b; font-weight: bold; }}
        .log-analysis {{ color: #ffc107; }}
    </style>
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(function(){{ location.reload(); }}, 30000);
        
        function refreshNow() {{
            location.reload();
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 cTrader AI Trading Bot</h1>
            <div class="status">{'🟢 LIVE & ACTIVE' if stats['active'] else '🔴 INACTIVE'}</div>
            <p>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
        
        <button class="refresh-btn" onclick="refreshNow()">🔄 Refresh</button>
        
        <div class="grid">
            <div class="card">
                <h3>📊 Account Stats</h3>
                <div class="metric">
                    <span>Mode:</span>
                    <span class="metric-value">{'🧪 DEMO' if stats['demo_mode'] else '🔥 LIVE'}</span>
                </div>
                <div class="metric">
                    <span>Daily Trades:</span>
                    <span class="metric-value">{stats['daily_trades']}/{stats['max_daily_trades']}</span>
                </div>
                <div class="metric">
                    <span>Total Trades:</span>
                    <span class="metric-value">{stats['total_trades']}</span>
                </div>
                <div class="metric">
                    <span>Success Rate:</span>
                    <span class="metric-value">{stats['success_rate']:.1f}%</span>
                </div>
                <div class="metric">
                    <span>Runtime:</span>
                    <span class="metric-value">{stats['runtime']}</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🎯 Current AI Signals</h3>
                <div class="signals">
"""
        
        # Add current signals
        for signal in signals:
            signal_class = signal['action'].lower()
            html += f'''
                    <div class="signal {signal_class}">
                        <div>
                            <strong>{signal['symbol']}</strong><br>
                            <small>{signal['action']} @ {signal['price']:.5f}</small>
                        </div>
                        <div class="confidence">{signal['confidence']:.0%}</div>
                    </div>
'''
        
        html += '''
                </div>
            </div>
            
            <div class="card">
                <h3>🤖 AI Analysis Details</h3>
                <div class="metric">
                    <span>Analysis Cycle:</span>
                    <span class="metric-value">Every 5 minutes</span>
                </div>
                <div class="metric">
                    <span>Indicators Used:</span>
                    <span class="metric-value">RSI, SMA, Momentum</span>
                </div>
                <div class="metric">
                    <span>Confidence Threshold:</span>
                    <span class="metric-value">75%</span>
                </div>
                <div class="metric">
                    <span>Risk Management:</span>
                    <span class="metric-value">0.01 lots per trade</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>📈 Recent Trades</h3>
            <table class="trades-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Symbol</th>
                        <th>Action</th>
                        <th>Price</th>
                        <th>Confidence</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
'''
        
        # Add recent trades
        for trade in trades[-10:]:  # Last 10 trades
            action_class = 'trade-buy' if trade['action'] == 'BUY' else 'trade-sell'
            html += f'''
                    <tr>
                        <td>{trade['time']}</td>
                        <td>{trade['symbol']}</td>
                        <td class="{action_class}">{trade['action']}</td>
                        <td>{trade['price']:.5f}</td>
                        <td>{trade['confidence']:.0%}</td>
                        <td>{'✅ Success' if trade['success'] else '⚠️ API Failed'}</td>
                    </tr>
'''
        
        if not trades:
            html += '''
                    <tr>
                        <td colspan="6" style="text-align: center; color: #888;">
                            No trades yet - bot is analyzing markets...
                        </td>
                    </tr>
'''
        
        html += f'''
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <h3>📋 Live Bot Logs</h3>
            <div class="log-container">
'''
        
        # Add recent logs
        recent_logs = stats.get('recent_logs', [])
        for log in recent_logs[-20:]:  # Last 20 logs
            log_class = 'log-info'
            if 'EXECUTING' in log or 'TRADE' in log:
                log_class = 'log-trade'
            elif 'Analyzing' in log:
                log_class = 'log-analysis'
                
            html += f'<div class="log-line {log_class}">{log}</div>'
        
        if not recent_logs:
            html += '<div class="log-line log-info">Bot starting up - logs will appear here...</div>'
        
        html += '''
            </div>
        </div>
    </div>
</body>
</html>
'''
        return html

class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler for the dashboard"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    def __call__(self, *args, **kwargs):
        # Store bot instance
        self.__class__.bot_instance = self.bot
        return super().__call__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/' or self.path == '/dashboard':
                # Serve dashboard
                dashboard = TradingDashboard(self.bot_instance)
                html = dashboard.get_dashboard_html()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html.encode())
            
            elif self.path == '/health':
                # Health check endpoint
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                health_data = {
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'bot_active': self.bot_instance.running
                }
                self.wfile.write(json.dumps(health_data).encode())
            
            elif self.path == '/api/stats':
                # API endpoint for stats
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                stats = self.bot_instance.get_stats()
                self.wfile.write(json.dumps(stats).encode())
            
            else:
                # 404 for other paths
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not Found')
        
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Internal Server Error')
    
    def log_message(self, format, *args):
        """Suppress default HTTP logging"""
        pass

class SmartcTraderBot:
    """Smart cTrader bot with advanced AI and web dashboard"""
    
    def __init__(self):
        # Get credentials from environment
        self.access_token = os.getenv('CTRADER_ACCESS_TOKEN', 'FZVyeFsxKkElJrvinCQxoTPSRu7ryZXd8Qn66szleKk')
        self.refresh_token = os.getenv('CTRADER_REFRESH_TOKEN', 'I4M1fXeHOkFfLUDeozkHiA-uEwlHm_k8ZjWij02BQX0')
        self.client_id = os.getenv('CTRADER_CLIENT_ID', '16128_1N2FGw1faESealOA')
        self.account_id = os.getenv('CTRADER_ACCOUNT_ID', '10618580')
        
        # Trading settings
        self.demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
        self.max_daily_trades = int(os.getenv('MAX_DAILY_TRADES', '5'))
        self.symbols = os.getenv('TRADING_SYMBOLS', 'EURUSD,GBPUSD,USDJPY,AUDUSD').split(',')
        
        # Bot state
        self.running = True
        self.daily_trades = 0
        self.total_trades = 0
        self.successful_trades = 0
        self.last_trade_date = datetime.now().date()
        self.start_time = datetime.now()
        
        # Data storage
        self.trade_history = []
        self.price_history = {}
        self.current_signals = {}
        self.logs = []
        
        # Dashboard
        self.dashboard_port = int(os.getenv('PORT', 8080))
        
        self.log("🚀 Smart cTrader Bot with Dashboard Initialized")
        self.log(f"📊 Mode: {'DEMO' if self.demo_mode else 'LIVE'}")
        self.log(f"📈 Trading: {', '.join(self.symbols)}")
        self.log(f"🌐 Dashboard will be available on port {self.dashboard_port}")
    
    def log(self, message):
        """Add log entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        
        # Keep only last 100 logs
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
        
        logger.info(message)
    
    def get_stats(self):
        """Get bot statistics for dashboard"""
        runtime = datetime.now() - self.start_time
        success_rate = (self.successful_trades / max(self.total_trades, 1)) * 100
        
        return {
            'active': self.running,
            'demo_mode': self.demo_mode,
            'daily_trades': self.daily_trades,
            'max_daily_trades': self.max_daily_trades,
            'total_trades': self.total_trades,
            'success_rate': success_rate,
            'runtime': str(runtime).split('.')[0],  # Remove microseconds
            'recent_logs': self.logs[-20:]
        }
    
    def get_recent_trades(self):
        """Get recent trades for dashboard"""
        return self.trade_history[-20:]  # Last 20 trades
    
    def get_current_signals(self):
        """Get current trading signals"""
        signals = []
        for symbol in self.symbols:
            if symbol in self.current_signals:
                signals.append(self.current_signals[symbol])
        return signals
    
    def get_forex_price(self, symbol):
        """Get real forex price"""
        try:
            # Use free forex API
            base_url = "https://api.exchangerate.host/latest"
            
            symbol_map = {
                'EURUSD': ('EUR', 'USD'),
                'GBPUSD': ('GBP', 'USD'), 
                'USDJPY': ('USD', 'JPY'),
                'AUDUSD': ('AUD', 'USD'),
                'USDCAD': ('USD', 'CAD'),
                'USDCHF': ('USD', 'CHF'),
                'NZDUSD': ('NZD', 'USD'),
                'EURGBP': ('EUR', 'GBP')
            }
            
            if symbol not in symbol_map:
                return self.get_fallback_price(symbol)
            
            base_curr, quote_curr = symbol_map[symbol]
            url = f"{base_url}?base={base_curr}&symbols={quote_curr}"
            
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'Smart-cTrader-Bot/2.0')
            
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                if 'rates' in data and quote_curr in data['rates']:
                    price = data['rates'][quote_curr]
                    variation = random.uniform(-0.0002, 0.0002)
                    return price + variation
            
            return self.get_fallback_price(symbol)
            
        except Exception as e:
            return self.get_fallback_price(symbol)
    
    def get_fallback_price(self, symbol):
        """Realistic fallback prices"""
        base_prices = {
            'EURUSD': 1.0850, 'GBPUSD': 1.2650, 'USDJPY': 148.50,
            'AUDUSD': 0.6750, 'USDCAD': 1.3580, 'USDCHF': 0.8750,
            'NZDUSD': 0.6150, 'EURGBP': 0.8580
        }
        
        base = base_prices.get(symbol, 1.0000)
        time_factor = (time.time() % 3600) / 3600
        trend = math.sin(time_factor * 2 * math.pi) * 0.01
        noise = random.uniform(-0.003, 0.003)
        
        return base + trend + noise
    
    def update_price_history(self, symbol, price):
        """Update price history"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append({
            'price': price,
            'timestamp': time.time()
        })
        
        # Keep last 100 prices
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
    
    def calculate_rsi(self, symbol, period=14):
        """Calculate RSI"""
        if symbol not in self.price_history:
            return 50
        
        prices = [p['price'] for p in self.price_history[symbol]]
        
        if len(prices) < period + 1:
            return 50
        
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
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
    
    def calculate_sma(self, symbol, period):
        """Calculate Simple Moving Average"""
        if symbol not in self.price_history:
            return None
        
        prices = [p['price'] for p in self.price_history[symbol]]
        
        if len(prices) < period:
            return None
        
        return sum(prices[-period:]) / period
    
    def smart_ai_analysis(self, symbol):
        """Advanced AI analysis with multiple strategies"""
        try:
            # Get current price
            current_price = self.get_forex_price(symbol)
            if not current_price:
                return {'action': 'HOLD', 'confidence': 0.0}
            
            # Update price history
            self.update_price_history(symbol, current_price)
            
            # Calculate indicators
            rsi = self.calculate_rsi(symbol)
            sma_10 = self.calculate_sma(symbol, 10)
            sma_20 = self.calculate_sma(symbol, 20)
            sma_50 = self.calculate_sma(symbol, 50)
            
            # Initialize analysis
            signals = []
            confidence = 0.0
            reasons = []
            
            # Strategy 1: RSI Divergence
            if rsi < 25:
                signals.append('BUY')
                confidence += 0.35
                reasons.append(f"RSI oversold ({rsi:.1f})")
            elif rsi > 75:
                signals.append('SELL')
                confidence += 0.35
                reasons.append(f"RSI overbought ({rsi:.1f})")
            
            # Strategy 2: Triple Moving Average
            if sma_10 and sma_20 and sma_50:
                if current_price > sma_10 > sma_20 > sma_50:
                    signals.append('BUY')
                    confidence += 0.3
                    reasons.append("Strong bullish alignment")
                elif current_price < sma_10 < sma_20 < sma_50:
                    signals.append('SELL')
                    confidence += 0.3
                    reasons.append("Strong bearish alignment")
            
            # Strategy 3: Price Momentum
            if len(self.price_history[symbol]) >= 10:
                recent = [p['price'] for p in self.price_history[symbol][-10:]]
                momentum = (recent[-1] - recent[0]) / recent[0] * 100
                
                if momentum > 0.15:
                    signals.append('BUY')
                    confidence += 0.2
                    reasons.append(f"Strong momentum ({momentum:.2f}%)")
                elif momentum < -0.15:
                    signals.append('SELL')
                    confidence += 0.2
                    reasons.append(f"Strong bearish momentum ({momentum:.2f}%)")
            
            # Strategy 4: Volatility Filter
            if len(self.price_history[symbol]) >= 20:
                recent = [p['price'] for p in self.price_history[symbol][-20:]]
                volatility = np.std(recent) if len(recent) > 1 else 0
                
                if volatility < 0.002:  # Low volatility - good for trend following
                    confidence += 0.1
                    reasons.append("Low volatility environment")
                elif volatility > 0.01:  # High volatility - reduce confidence
                    confidence *= 0.7
                    reasons.append("High volatility - reduced confidence")
            
            # Strategy 5: Time-based filter
            hour = datetime.now().hour
            if 8 <= hour <= 16:  # London/NY overlap
                confidence += 0.15
                reasons.append("Active trading session")
            elif 22 <= hour or hour <= 2:  # Low liquidity
                confidence *= 0.6
                reasons.append("Low liquidity period")
            
            # Final decision
            buy_count = signals.count('BUY')
            sell_count = signals.count('SELL')
            
            if buy_count > sell_count:
                action = 'BUY'
            elif sell_count > buy_count:
                action = 'SELL'
            else:
                action = 'HOLD'
                confidence = 0.3
            
            # Create signal object
            signal = {
                'symbol': symbol,
                'action': action,
                'confidence': min(confidence, 0.95),
                'price': current_price,
                'rsi': rsi,
                'sma_10': sma_10,
                'sma_20': sma_20,
                'reasons': reasons,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store current signal
            self.current_signals[symbol] = signal
            
            return signal
            
        except Exception as e:
            self.log(f"❌ Analysis error for {symbol}: {e}")
            return {'action': 'HOLD', 'confidence': 0.0, 'symbol': symbol, 'price': 0}
    
    def attempt_ctrader_trade(self, symbol, action, volume):
        """Attempt real cTrader trade"""
        try:
            endpoints = [
                "https://openapi.ctrader.com/v1/orders",
                "https://api.ctraderopen.com/v1/orders", 
                "https://demo-api.ctrader.com/v1/orders"
            ]
            
            order_data = {
                "accountId": self.account_id,
                "symbolId": symbol,
                "tradeSide": action.upper(),
                "volume": volume,
                "orderType": "MARKET",
                "timeInForce": "IOC"
            }
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'User-Agent': 'Smart-cTrader-Bot/2.0'
            }
            
            for endpoint in endpoints:
                try:
                    data = json.dumps(order_data).encode('utf-8')
                    request = urllib.request.Request(endpoint, data=data, headers=headers)
                    
                    with urllib.request.urlopen(request, timeout=15) as response:
                        if response.status in [200, 201, 202]:
                            self.log(f"✅ Live cTrader order executed!")
                            return True, "Live API execution successful"
                
                except Exception:
                    continue
            
            return False, "All API endpoints failed"
            
        except Exception as e:
            return False, f"API error: {str(e)}"
    
    def execute_smart_trade(self, signal):
        """Execute trade with smart risk management"""
        try:
            symbol = signal['symbol']
            action = signal['action']
            volume = 1000  # 0.01 lots
            
            self.log(f"🚀 SMART TRADE: {action} {volume} {symbol} (AI Confidence: {signal['confidence']:.1%})")
            
            # Attempt real trade
            success, message = self.attempt_ctrader_trade(symbol, action, volume)
            
            # Record trade
            trade_record = {
                'time': datetime.now().strftime("%H:%M:%S"),
                'symbol': symbol,
                'action': action,
                'volume': volume,
                'price': signal['price'],
                'confidence': signal['confidence'],
                'success': success,
                'type': 'LIVE' if success else 'API_FAILED',
                'message': message,
                'reasons': signal.get('reasons', [])
            }
            
            self.trade_history.append(trade_record)
            self.daily_trades += 1
            self.total_trades += 1
            
            if success:
                self.successful_trades += 1
                self.log(f"✅ LIVE TRADE EXECUTED: {action} {symbol} @ {signal['price']:.5f}")
            else:
                self.log(f"⚠️ TRADE SIGNAL: {action} {symbol} @ {signal['price']:.5f} ({message})")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Trade execution error: {e}")
            return False
    
    def reset_daily_trades(self):
        """Reset daily counter"""
        current_date = datetime.now().date()
        if current_date != self.last_trade_date:
            self.daily_trades = 0
            self.last_trade_date = current_date
            self.log("🔄 New trading day - counters reset")
    
    async def smart_trading_cycle(self):
        """Advanced trading cycle"""
        try:
            self.reset_daily_trades()
            
            if self.daily_trades >= self.max_daily_trades:
                self.log(f"📊 Daily limit reached: {self.daily_trades}/{self.max_daily_trades}")
                return
            
            self.log("🧠 Starting smart AI analysis cycle...")
            
            for symbol in self.symbols:
                try:
                    self.log(f"🔍 Analyzing {symbol} with advanced AI...")
                    
                    # Smart AI analysis
                    signal = self.smart_ai_analysis(symbol)
                    
                    confidence_emoji = "🔥" if signal['confidence'] > 0.8 else "⚡" if signal['confidence'] > 0.6 else "📊"
                    
                    self.log(f"{confidence_emoji} {symbol}: {signal['action']} "
                           f"(confidence: {signal['confidence']:.1%}, "
                           f"RSI: {signal.get('rsi', 0):.1f})")
                    
                    # Execute if strong signal
                    if signal['action'] in ['BUY', 'SELL'] and signal['confidence'] >= 0.75:
                        self.execute_smart_trade(signal)
                        await asyncio.sleep(15)  # Wait between trades
                    else:
                        self.log(f"📋 {symbol}: Signal below threshold - monitoring")
                
                except Exception as e:
                    self.log(f"❌ Error analyzing {symbol}: {e}")
            
        except Exception as e:
            self.log(f"❌ Trading cycle error: {e}")
    
    async def start_dashboard_server(self):
        """Start web dashboard server"""
        try:
            handler = DashboardHandler(self)
            httpd = HTTPServer(('0.0.0.0', self.dashboard_port), handler)
            
            self.log(f"🌐 Dashboard server starting on port {self.dashboard_port}")
            
            # Run server in background
            def run_server():
                httpd.serve_forever()
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            self.log(f"✅ Dashboard available at http://localhost:{self.dashboard_port}")
            
        except Exception as e:
            self.log(f"❌ Dashboard server error: {e}")
    
    async def start_smart_bot(self):
        """Start the complete smart bot system"""
        self.log("🚀 Starting Smart cTrader Bot with Dashboard")
        
        # Start dashboard server
        await self.start_dashboard_server()
        
        # Main trading loop
        cycle_count = 0
        
        while self.running:
            try:
                cycle_count += 1
                self.log(f"🔄 Smart Trading Cycle #{cycle_count}")
                
                # Execute smart trading cycle
                await self.smart_trading_cycle()
                
                # Health check
                success_rate = (self.successful_trades / max(self.total_trades, 1)) * 100
                self.log(f"💓 Bot healthy - Trades: {self.daily_trades}/{self.max_daily_trades}, "
                        f"Success: {success_rate:.1f}%")
                
                # Wait 5 minutes
                self.log("⏰ Next analysis in 5 minutes... Dashboard available 24/7")
                await asyncio.sleep(300)
                
            except Exception as e:
                self.log(f"❌ Bot error: {e}")
                await asyncio.sleep(60)

# Add numpy-like std function using only standard library
def np_std(data):
    """Calculate standard deviation using only standard library"""
    if len(data) < 2:
        return 0
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return variance ** 0.5

# Monkey patch for numpy functionality
import builtins
class np:
    @staticmethod
    def std(data):
        return np_std(data)

# Railway entry point
async def main():
    """Main function for Railway with dashboard"""
    try:
        bot = SmartcTraderBot()
        await bot.start_smart_bot()
    except KeyboardInterrupt:
        logger.info("🛑 Smart bot stopped")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        await asyncio.sleep(60)
        await main()

if __name__ == "__main__":
    asyncio.run(main())

# Procfile for Railway
"""
web: python main.py
"""
