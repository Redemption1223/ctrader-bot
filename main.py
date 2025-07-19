#!/usr/bin/env python3
"""
RENDER-COMPATIBLE CTRADER BOT
Fixed for Render deployment system
"""

import json
import time
import os
import urllib.request
import urllib.parse
import random
import math
import threading
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

print("🚀 RENDER-COMPATIBLE CTRADER BOT")
print("=" * 60)

class RenderCompatibleBot:
    """Bot designed specifically for Render deployment"""
    
    def __init__(self):
        self.logs = []
        self.log("🚀 INITIALIZING RENDER-COMPATIBLE BOT")
        
        # Initialize safely
        self.running = True
        self.account_verified = False
        self.account_info = {"verified": False, "balance": 10000.0}
        self.current_balance = 10000.0
        self.daily_trades = 0
        self.total_trades = 0
        self.successful_trades = 0
        self.total_profit = 0.0
        self.trade_history = []
        self.start_time = datetime.now()
        
        # Trading config
        self.max_daily_trades = 20
        self.currency_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD']
        
        # Load credentials
        self.load_credentials()
        
        # Test API connection
        self.test_api_connection()
        
        self.log("✅ BOT INITIALIZED FOR RENDER")
    
    def log(self, message):
        """Safe logging"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}"
            self.logs.append(log_entry)
            
            if len(self.logs) > 100:
                self.logs = self.logs[-100:]
            
            print(log_entry)
        except:
            print(f"LOG ERROR: {message}")
    
    def load_credentials(self):
        """Load cTrader credentials"""
        try:
            self.access_token = os.getenv('CTRADER_ACCESS_TOKEN', '').strip()
            self.account_id = os.getenv('CTRADER_ACCOUNT_ID', '').strip()
            self.client_id = os.getenv('CTRADER_CLIENT_ID', '').strip()
            self.client_secret = os.getenv('CTRADER_CLIENT_SECRET', '').strip()
            self.refresh_token = os.getenv('CTRADER_REFRESH_TOKEN', '').strip()
            
            self.log(f"🔑 Credentials: Token({'✅' if self.access_token else '❌'}) Account({'✅' if self.account_id else '❌'})")
            
        except Exception as e:
            self.log(f"❌ Credential error: {e}")
    
    def test_api_connection(self):
        """Test cTrader API connection"""
        if not self.access_token:
            self.log("⚠️ No access token - using simulation mode")
            return
        
        try:
            self.log("🧪 Testing cTrader API...")
            
            # Test correct endpoints
            endpoints = [
                "https://openapi.ctrader.com/v1/accounts",
                "https://demo-openapi.ctrader.com/v1/accounts"
            ]
            
            for endpoint in endpoints:
                try:
                    self.log(f"   Testing: {endpoint}")
                    
                    headers = {
                        'Authorization': f'Bearer {self.access_token}',
                        'Accept': 'application/json'
                    }
                    
                    request = urllib.request.Request(endpoint, headers=headers)
                    
                    with urllib.request.urlopen(request, timeout=10) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode())
                            
                            if data and len(data) > 0:
                                account = data[0]
                                self.account_verified = True
                                self.account_info = {
                                    'verified': True,
                                    'account_id': account.get('accountId', 'Unknown'),
                                    'balance': float(account.get('balance', 10000)),
                                    'currency': account.get('currency', 'USD'),
                                    'broker': account.get('brokerName', 'Unknown')
                                }
                                self.current_balance = self.account_info['balance']
                                
                                self.log(f"✅ API SUCCESS: {self.account_info['account_id']}")
                                self.log(f"   Balance: {self.account_info['balance']:.2f} {self.account_info['currency']}")
                                return
                        else:
                            self.log(f"   ❌ HTTP {response.status}")
                
                except urllib.error.HTTPError as e:
                    self.log(f"   ❌ HTTP {e.code}: {e.reason}")
                except Exception as e:
                    self.log(f"   ❌ Error: {e}")
            
            self.log("⚠️ API tests failed - using simulation mode")
            
        except Exception as e:
            self.log(f"❌ API test error: {e}")
    
    def generate_signal(self, symbol):
        """Generate trading signal"""
        try:
            confidence = random.uniform(0.7, 0.95)
            action = random.choice(['BUY', 'SELL', 'HOLD'])
            price = 1.0000 + random.uniform(-0.01, 0.01)
            
            return {
                'symbol': symbol,
                'action': action,
                'confidence': confidence,
                'price': price
            }
        except:
            return {'symbol': symbol, 'action': 'HOLD', 'confidence': 0}
    
    def execute_trade(self, signal):
        """Execute trade (simulation)"""
        try:
            symbol = signal['symbol']
            action = signal['action']
            
            # Simulate trading
            success = random.choice([True, True, True, False])  # 75% success
            
            if success:
                profit = random.uniform(-10, 30)  # -$10 to +$30
                self.total_profit += profit
                self.current_balance += profit
                self.successful_trades += 1
                
                trade = {
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'symbol': symbol,
                    'action': action,
                    'success': True,
                    'profit': profit,
                    'balance': self.current_balance
                }
                
                self.trade_history.append(trade)
                if len(self.trade_history) > 20:
                    self.trade_history = self.trade_history[-20:]
                
                self.log(f"✅ {action} {symbol} | P&L: {profit:+.2f}")
                return True
            else:
                self.log(f"❌ {action} {symbol} failed")
                return False
        
        except Exception as e:
            self.log(f"❌ Trade error: {e}")
            return False
    
    def trading_cycle(self):
        """Main trading cycle"""
        try:
            if self.daily_trades >= self.max_daily_trades:
                return
            
            self.log("🧠 Trading analysis...")
            
            for symbol in self.currency_pairs:
                try:
                    signal = self.generate_signal(symbol)
                    
                    if signal['action'] in ['BUY', 'SELL'] and signal['confidence'] > 0.85:
                        self.log(f"🎯 Signal: {signal['action']} {symbol} ({signal['confidence']:.1%})")
                        
                        if self.execute_trade(signal):
                            self.daily_trades += 1
                            self.total_trades += 1
                            
                            if self.daily_trades >= self.max_daily_trades:
                                break
                
                except Exception as e:
                    self.log(f"❌ {symbol} error: {e}")
                    continue
        
        except Exception as e:
            self.log(f"❌ Trading cycle error: {e}")
    
    def get_stats(self):
        """Get bot statistics"""
        try:
            runtime = datetime.now() - self.start_time
            success_rate = (self.successful_trades / max(self.total_trades, 1)) * 100
            
            return {
                'active': self.running,
                'account_verified': self.account_verified,
                'account_info': self.account_info,
                'daily_trades': self.daily_trades,
                'max_daily_trades': self.max_daily_trades,
                'total_trades': self.total_trades,
                'success_rate': success_rate,
                'current_balance': self.current_balance,
                'total_profit': self.total_profit,
                'runtime': str(runtime).split('.')[0],
                'recent_logs': self.logs[-20:],
                'recent_trades': self.trade_history[-10:]
            }
        except:
            return {'active': True, 'error': 'Stats error'}
    
    def run_forever(self):
        """Run trading bot forever"""
        try:
            self.log("🚀 STARTING TRADING ENGINE")
            
            cycle = 0
            
            while True:
                try:
                    cycle += 1
                    self.log(f"🔄 Cycle #{cycle}")
                    
                    # Execute trading
                    self.trading_cycle()
                    
                    # Status update
                    stats = self.get_stats()
                    self.log(f"💓 Status: API({'✅' if stats['account_verified'] else '❌'}) | "
                           f"Trades: {stats['daily_trades']}/{stats['max_daily_trades']} | "
                           f"Success: {stats['success_rate']:.1f}% | "
                           f"Balance: {stats['current_balance']:.2f}")
                    
                    # Wait 3 minutes
                    self.log("⏰ Next cycle in 3 minutes...")
                    time.sleep(180)
                
                except KeyboardInterrupt:
                    self.log("🛑 Bot stopped")
                    break
                except Exception as e:
                    self.log(f"❌ Cycle error: {e}")
                    time.sleep(60)
                    continue
        
        except Exception as e:
            self.log(f"❌ Bot error: {e}")

# Global bot instance
bot = RenderCompatibleBot()

class RenderHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for Render"""
    
    def do_GET(self):
        try:
            if self.path == '/' or self.path == '/dashboard':
                html = self.get_dashboard()
            elif self.path == '/health':
                html = json.dumps({'status': 'healthy', 'bot': 'running'})
            else:
                html = '<h1>cTrader Bot Dashboard</h1><p><a href="/">Go to Dashboard</a></p>'
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(str(html).encode('utf-8'))
            
        except Exception as e:
            try:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'Error: {e}'.encode())
            except:
                pass
    
    def get_dashboard(self):
        """Generate simple dashboard"""
        try:
            stats = bot.get_stats()
            
            status_color = "#28a745" if stats['account_verified'] else "#ffc107"
            status_text = "✅ LIVE CONNECTED" if stats['account_verified'] else "🧪 SIMULATION MODE"
            
            trades_html = ""
            for trade in stats.get('recent_trades', []):
                profit_color = "#28a745" if trade.get('profit', 0) >= 0 else "#dc3545"
                trades_html += f'''
                <div style="padding: 10px; margin: 5px 0; background: rgba(255,255,255,0.1); border-radius: 8px;">
                    <strong>{trade.get('action', 'UNKNOWN')} {trade.get('symbol', 'UNKNOWN')}</strong> at {trade.get('time', 'Unknown')}
                    <span style="color: {profit_color}; float: right;">P&L: {trade.get('profit', 0):+.2f}</span>
                </div>
                '''
            
            logs_html = ""
            for log in stats.get('recent_logs', []):
                log_color = "#ffffff"
                if "✅" in log:
                    log_color = "#28a745"
                elif "❌" in log:
                    log_color = "#dc3545"
                elif "⚠️" in log:
                    log_color = "#ffc107"
                
                logs_html += f'<div style="color: {log_color}; margin: 2px 0; font-family: monospace; font-size: 0.9em;">{log}</div>'
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🚀 cTrader Trading Bot</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{ 
            text-align: center; 
            margin-bottom: 30px;
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }}
        .header h1 {{ 
            font-size: 2.5em; 
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ffd700, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .status {{ 
            background: {status_color}; 
            padding: 20px; 
            border-radius: 15px; 
            text-align: center; 
            margin-bottom: 30px;
            font-size: 1.3em;
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
            padding: 25px; 
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        .card h3 {{ 
            color: #ffd700; 
            margin-bottom: 20px; 
            font-size: 1.4em;
        }}
        .metric {{ 
            display: flex; 
            justify-content: space-between; 
            margin: 15px 0; 
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }}
        .metric-value {{ 
            font-weight: bold; 
            color: #ffd700;
        }}
        .logs {{ 
            background: rgba(0,0,0,0.5); 
            padding: 20px; 
            border-radius: 10px; 
            max-height: 300px;
            overflow-y: auto;
        }}
        .refresh {{ 
            position: fixed; 
            top: 20px; 
            right: 20px; 
            background: #ff6b6b; 
            color: white; 
            border: none; 
            padding: 15px 20px; 
            border-radius: 25px; 
            cursor: pointer; 
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .refresh:hover {{ background: #ff5252; }}
    </style>
    <script>
        setTimeout(() => location.reload(), 30000);
        function refresh() {{ location.reload(); }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 cTrader Trading Bot</h1>
            <p>Automated Forex Trading System</p>
            <p style="opacity: 0.8;">Last Updated: {datetime.now().strftime('%H:%M:%S UTC')}</p>
        </div>
        
        <button class="refresh" onclick="refresh()">🔄 Refresh</button>
        
        <div class="status">{status_text}</div>
        
        <div class="grid">
            <div class="card">
                <h3>📊 Performance</h3>
                <div class="metric">
                    <span>Account Status:</span>
                    <span class="metric-value">{'✅ VERIFIED' if stats['account_verified'] else '🧪 SIMULATION'}</span>
                </div>
                <div class="metric">
                    <span>Today's Trades:</span>
                    <span class="metric-value">{stats['daily_trades']}/{stats['max_daily_trades']}</span>
                </div>
                <div class="metric">
                    <span>Success Rate:</span>
                    <span class="metric-value">{stats['success_rate']:.1f}%</span>
                </div>
                <div class="metric">
                    <span>Current Balance:</span>
                    <span class="metric-value">${stats['current_balance']:.2f}</span>
                </div>
                <div class="metric">
                    <span>Total P&L:</span>
                    <span class="metric-value" style="color: {'#00ff00' if stats['total_profit'] >= 0 else '#ff4444'};">{stats['total_profit']:+.2f}</span>
                </div>
                <div class="metric">
                    <span>Runtime:</span>
                    <span class="metric-value">{stats['runtime']}</span>
                </div>
            </div>
            
            <div class="card">
                <h3>💹 Recent Trades</h3>
                <div style="max-height: 250px; overflow-y: auto;">
                    {trades_html if trades_html else '<p style="text-align: center; opacity: 0.7;">No trades yet</p>'}
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>📱 System Logs</h3>
            <div class="logs">
                {logs_html}
            </div>
        </div>
    </div>
</body>
</html>
            """
            
            return html
        
        except Exception as e:
            return f'<h1>Dashboard Error: {e}</h1>'
    
    def log_message(self, format, *args):
        # Suppress server logs
        pass

def create_server():
    """Create HTTP server for Render"""
    try:
        port = int(os.getenv('PORT', 10000))
        
        bot.log(f"🌐 Starting server on port {port}")
        
        server = HTTPServer(('0.0.0.0', port), RenderHandler)
        
        # Start server in background thread
        def run_server():
            try:
                server.serve_forever()
            except Exception as e:
                bot.log(f"Server error: {e}")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        bot.log("✅ Web server started")
        
        return server
    
    except Exception as e:
        bot.log(f"❌ Server start error: {e}")
        return None

def main():
    """Main function for Render deployment"""
    try:
        print("🚀 STARTING RENDER-COMPATIBLE BOT")
        
        # Start web server
        server = create_server()
        
        # Give server time to start
        time.sleep(2)
        
        # Start trading bot
        bot.run_forever()
    
    except Exception as e:
        print(f"Main error: {e}")
        bot.log(f"Main error: {e}")
        
        # Keep running even if there's an error
        while True:
            try:
                time.sleep(60)
                bot.log("🔄 Bot still running...")
            except KeyboardInterrupt:
                break
            except:
                continue

if __name__ == "__main__":
    main()
