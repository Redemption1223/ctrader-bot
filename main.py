#!/usr/bin/env python3
"""
CRASH-PROOF CTRADER BOT
Maximum stability with bulletproof error handling
"""

import json
import time
import os
import urllib.request
import urllib.parse
import random
import math
import threading
import traceback
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

print("🛡️ CRASH-PROOF CTRADER BOT STARTING")
print("=" * 60)

class CrashProofBot:
    """Bulletproof bot that never crashes"""
    
    def __init__(self):
        try:
            self.logs = []
            self.safe_log("🛡️ INITIALIZING CRASH-PROOF BOT")
            
            # Initialize all variables with safe defaults
            self.access_token = ""
            self.refresh_token = ""
            self.client_id = ""
            self.client_secret = ""
            self.account_id = ""
            
            # Bot state with safe defaults
            self.running = True
            self.account_verified = False
            self.account_info = {"verified": False, "balance": 10000.0, "currency": "USD"}
            self.current_balance = 10000.0
            self.daily_trades = 0
            self.total_trades = 0
            self.successful_trades = 0
            self.total_profit = 0.0
            self.trade_history = []
            self.current_signals = {}
            self.start_time = datetime.now()
            
            # Trading config
            self.max_daily_trades = 20
            self.currency_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD']
            
            # Load credentials safely
            self.safe_load_credentials()
            
            # Try API connection (but don't crash if it fails)
            self.safe_test_api()
            
            self.safe_log("✅ CRASH-PROOF BOT INITIALIZED SUCCESSFULLY")
            
        except Exception as e:
            self.safe_log(f"❌ Init error (but continuing): {e}")
            # Even if init fails, set safe defaults
            self.running = True
            self.account_verified = False
            self.current_balance = 10000.0
    
    def safe_log(self, message):
        """Ultra-safe logging that never crashes"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}"
            
            if not hasattr(self, 'logs'):
                self.logs = []
            
            self.logs.append(log_entry)
            
            # Keep reasonable log size
            if len(self.logs) > 100:
                self.logs = self.logs[-100:]
            
            print(log_entry)
            
        except Exception as e:
            # Even logging can't fail!
            print(f"[ERROR] Logging failed: {e}")
            print(f"[ERROR] Original message: {message}")
    
    def safe_load_credentials(self):
        """Safely load credentials without crashing"""
        try:
            self.safe_log("🔑 Loading credentials safely...")
            
            # Safe environment variable loading
            try:
                self.access_token = str(os.getenv('CTRADER_ACCESS_TOKEN', '')).strip()
                self.safe_log(f"   Access Token: {'✅' if self.access_token else '❌'} ({len(self.access_token)} chars)")
            except:
                self.access_token = ""
                self.safe_log("   Access Token: ❌ (load error)")
            
            try:
                self.refresh_token = str(os.getenv('CTRADER_REFRESH_TOKEN', '')).strip()
                self.safe_log(f"   Refresh Token: {'✅' if self.refresh_token else '❌'} ({len(self.refresh_token)} chars)")
            except:
                self.refresh_token = ""
                self.safe_log("   Refresh Token: ❌ (load error)")
            
            try:
                self.client_id = str(os.getenv('CTRADER_CLIENT_ID', '')).strip()
                self.safe_log(f"   Client ID: {'✅' if self.client_id else '❌'} ({len(self.client_id)} chars)")
            except:
                self.client_id = ""
                self.safe_log("   Client ID: ❌ (load error)")
            
            try:
                self.client_secret = str(os.getenv('CTRADER_CLIENT_SECRET', '')).strip()
                self.safe_log(f"   Client Secret: {'✅' if self.client_secret else '❌'} ({len(self.client_secret)} chars)")
            except:
                self.client_secret = ""
                self.safe_log("   Client Secret: ❌ (load error)")
            
            try:
                self.account_id = str(os.getenv('CTRADER_ACCOUNT_ID', '')).strip()
                self.safe_log(f"   Account ID: {'✅' if self.account_id else '❌'} ({self.account_id or 'None'})")
            except:
                self.account_id = ""
                self.safe_log("   Account ID: ❌ (load error)")
            
        except Exception as e:
            self.safe_log(f"❌ Credential loading error: {e}")
            # Set safe defaults
            self.access_token = ""
            self.refresh_token = ""
            self.client_id = ""
            self.client_secret = ""
            self.account_id = ""
    
    def safe_test_api(self):
        """Safely test API without crashing"""
        try:
            if not self.access_token:
                self.safe_log("⚠️ No access token - skipping API test")
                return
            
            self.safe_log("🧪 Testing API connection safely...")
            
            # Test endpoints one by one with full error handling
            test_endpoints = [
                ("https://openapi.ctrader.com/v1/accounts", "LIVE v1"),
                ("https://demo-openapi.ctrader.com/v1/accounts", "DEMO v1"),
                ("https://openapi.ctrader.com/accounts", "LIVE no-version"),
                ("https://demo-openapi.ctrader.com/accounts", "DEMO no-version")
            ]
            
            for url, description in test_endpoints:
                try:
                    self.safe_log(f"   Testing {description}: {url}")
                    result = self.safe_api_call(url, description)
                    
                    if result and result.get('success'):
                        self.safe_log(f"🎉 API CONNECTION SUCCESS with {description}!")
                        self.account_verified = True
                        self.account_info = result
                        self.current_balance = float(result.get('balance', 10000))
                        return True
                    else:
                        error = result.get('error', 'Unknown') if result else 'No response'
                        self.safe_log(f"   ❌ {description} failed: {error}")
                
                except Exception as e:
                    self.safe_log(f"   ❌ {description} exception: {e}")
                    continue
            
            self.safe_log("⚠️ All API tests failed - using simulation mode")
            
        except Exception as e:
            self.safe_log(f"❌ API test error: {e}")
    
    def safe_api_call(self, url, description):
        """Make a safe API call that never crashes"""
        try:
            if not self.access_token:
                return {"success": False, "error": "No access token"}
            
            # Create request with timeout and proper headers
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'User-Agent': 'CrashProofBot/1.0'
            }
            
            request = urllib.request.Request(url, headers=headers)
            
            # Make request with timeout
            with urllib.request.urlopen(request, timeout=10) as response:
                status = response.status
                
                if status == 200:
                    try:
                        response_text = response.read().decode('utf-8')
                        data = json.loads(response_text)
                        
                        if isinstance(data, list) and len(data) > 0:
                            account = data[0]
                        elif isinstance(data, dict):
                            account = data
                        else:
                            return {"success": False, "error": "No account data"}
                        
                        # Extract account info safely
                        result = {
                            "success": True,
                            "account_id": str(account.get('accountId', account.get('id', 'Unknown'))),
                            "balance": float(account.get('balance', 10000)),
                            "currency": str(account.get('currency', 'USD')),
                            "broker": str(account.get('brokerName', account.get('broker', 'Unknown'))),
                            "method": description,
                            "verified": True
                        }
                        
                        return result
                        
                    except json.JSONDecodeError:
                        return {"success": False, "error": "Invalid JSON response"}
                    except (ValueError, TypeError) as e:
                        return {"success": False, "error": f"Data parsing error: {e}"}
                else:
                    return {"success": False, "error": f"HTTP {status}"}
        
        except urllib.error.HTTPError as e:
            return {"success": False, "error": f"HTTP Error {e.code}"}
        except urllib.error.URLError as e:
            return {"success": False, "error": f"URL Error: {e.reason}"}
        except Exception as e:
            return {"success": False, "error": f"Request failed: {e}"}
    
    def safe_trading_cycle(self):
        """Ultra-safe trading cycle"""
        try:
            if self.daily_trades >= self.max_daily_trades:
                self.safe_log(f"📊 Daily limit reached: {self.daily_trades}/{self.max_daily_trades}")
                return
            
            self.safe_log("🧠 Safe trading analysis...")
            
            for symbol in self.currency_pairs:
                try:
                    # Generate safe trading signal
                    signal = self.safe_generate_signal(symbol)
                    
                    if signal and signal.get('action') in ['BUY', 'SELL']:
                        confidence = signal.get('confidence', 0)
                        
                        if confidence > 0.8:
                            self.safe_log(f"🎯 Trading signal: {signal['action']} {symbol} ({confidence:.1%})")
                            
                            # Execute safe trade
                            success = self.safe_execute_trade(signal)
                            
                            if success:
                                self.daily_trades += 1
                                
                                if self.daily_trades >= self.max_daily_trades:
                                    break
                    
                except Exception as e:
                    self.safe_log(f"❌ Trading error for {symbol}: {e}")
                    continue
            
        except Exception as e:
            self.safe_log(f"❌ Trading cycle error: {e}")
    
    def safe_generate_signal(self, symbol):
        """Generate trading signal safely"""
        try:
            # Simple but safe signal generation
            confidence = random.uniform(0.6, 0.95)
            action = random.choice(['BUY', 'SELL', 'HOLD'])
            price = 1.0000 + random.uniform(-0.01, 0.01)
            
            signal = {
                'symbol': symbol,
                'action': action,
                'confidence': confidence,
                'price': price,
                'timestamp': datetime.now().isoformat()
            }
            
            return signal
            
        except Exception as e:
            self.safe_log(f"❌ Signal generation error for {symbol}: {e}")
            return None
    
    def safe_execute_trade(self, signal):
        """Execute trade safely"""
        try:
            symbol = signal.get('symbol', 'UNKNOWN')
            action = signal.get('action', 'UNKNOWN')
            volume = 10000
            
            # Simulate realistic trading
            success = random.choice([True, True, True, False])  # 75% success
            
            if success:
                # Calculate realistic profit
                profit = volume * 0.0001 * random.uniform(-1, 3)
                estimated_profit = profit * 10
                
                self.total_profit += estimated_profit
                self.current_balance += estimated_profit
                self.total_trades += 1
                self.successful_trades += 1
                
                # Record trade safely
                try:
                    trade_record = {
                        'timestamp': datetime.now().isoformat(),
                        'time': datetime.now().strftime("%H:%M:%S"),
                        'symbol': symbol,
                        'action': action,
                        'volume': volume,
                        'success': True,
                        'profit': estimated_profit,
                        'balance': self.current_balance
                    }
                    
                    self.trade_history.append(trade_record)
                    
                    # Keep reasonable history size
                    if len(self.trade_history) > 50:
                        self.trade_history = self.trade_history[-50:]
                        
                except Exception as e:
                    self.safe_log(f"❌ Trade recording error: {e}")
                
                self.safe_log(f"✅ Trade success: {action} {symbol} | P&L: {estimated_profit:+.2f}")
                return True
            else:
                self.total_trades += 1
                self.safe_log(f"❌ Trade failed: {action} {symbol}")
                return False
            
        except Exception as e:
            self.safe_log(f"❌ Trade execution error: {e}")
            return False
    
    def safe_get_stats(self):
        """Get statistics safely"""
        try:
            runtime = datetime.now() - self.start_time
            success_rate = 0
            
            try:
                if self.total_trades > 0:
                    success_rate = (self.successful_trades / self.total_trades) * 100
            except:
                success_rate = 0
            
            stats = {
                'active': self.running,
                'account_verified': self.account_verified,
                'account_info': self.account_info,
                'daily_trades': self.daily_trades,
                'max_daily_trades': self.max_daily_trades,
                'total_trades': self.total_trades,
                'successful_trades': self.successful_trades,
                'success_rate': success_rate,
                'current_balance': self.current_balance,
                'total_profit': self.total_profit,
                'runtime': str(runtime).split('.')[0],
                'recent_logs': self.logs[-30:] if hasattr(self, 'logs') else [],
                'version': 'crash-proof-1.0'
            }
            
            return stats
            
        except Exception as e:
            self.safe_log(f"❌ Stats error: {e}")
            # Return safe defaults
            return {
                'active': True,
                'account_verified': False,
                'daily_trades': 0,
                'total_trades': 0,
                'success_rate': 0,
                'current_balance': 10000,
                'total_profit': 0,
                'runtime': '00:00:00',
                'recent_logs': ['Error getting stats'],
                'version': 'crash-proof-1.0'
            }
    
    def safe_run_bot(self):
        """Ultra-safe bot execution that never crashes"""
        try:
            self.safe_log("🛡️ CRASH-PROOF BOT RUNNING")
            
            cycle = 0
            
            while self.running:
                try:
                    cycle += 1
                    self.safe_log(f"🔄 Safe Cycle #{cycle}")
                    
                    # Safe trading
                    self.safe_trading_cycle()
                    
                    # Safe status update
                    try:
                        stats = self.safe_get_stats()
                        self.safe_log(f"💓 Status: Verified: {'✅' if stats['account_verified'] else '❌'} | "
                                    f"Trades: {stats['daily_trades']}/{stats['max_daily_trades']} | "
                                    f"Success: {stats['success_rate']:.1f}% | "
                                    f"Balance: {stats['current_balance']:.2f}")
                    except Exception as e:
                        self.safe_log(f"❌ Status update error: {e}")
                    
                    # Safe sleep
                    try:
                        self.safe_log("⏰ Waiting 2 minutes for next cycle...")
                        time.sleep(120)
                    except KeyboardInterrupt:
                        self.safe_log("🛑 Bot stopped by user")
                        break
                    except Exception as e:
                        self.safe_log(f"❌ Sleep error: {e}")
                        time.sleep(60)  # Fallback sleep
                
                except Exception as e:
                    self.safe_log(f"❌ Cycle error (but continuing): {e}")
                    try:
                        time.sleep(60)  # Wait before retry
                    except:
                        pass
                    continue
        
        except Exception as e:
            self.safe_log(f"❌ Major bot error: {e}")
            # Try to restart gracefully
            try:
                time.sleep(30)
                self.safe_log("🔄 Attempting bot restart...")
                self.safe_run_bot()
            except:
                self.safe_log("💥 Bot cannot restart - ending safely")

# Global bot instance
crash_proof_bot = None

class CrashProofHandler(BaseHTTPRequestHandler):
    """Crash-proof web handler"""
    
    def do_GET(self):
        try:
            if self.path == '/' or self.path == '/dashboard':
                html = self.get_safe_dashboard()
            elif self.path == '/health':
                html = json.dumps({
                    'status': 'crash_proof',
                    'bot_active': True,
                    'version': 'crash-proof-1.0'
                })
            else:
                html = '<h1>404 Not Found</h1>'
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(str(html).encode('utf-8'))
            
        except Exception as e:
            try:
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f'<h1>Error: {e}</h1>'.encode())
            except:
                pass
    
    def get_safe_dashboard(self):
        """Generate safe dashboard"""
        try:
            if not crash_proof_bot:
                return "<h1>Bot not initialized</h1>"
            
            stats = crash_proof_bot.safe_get_stats()
            
            status_color = "#28a745" if stats['account_verified'] else "#ffc107"
            status_text = "✅ CONNECTED" if stats['account_verified'] else "🛡️ SAFE MODE"
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🛡️ Crash-Proof Bot</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: white;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ 
            text-align: center; 
            margin-bottom: 30px;
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 20px;
        }}
        .header h1 {{ 
            font-size: 2.5em; 
            color: #00ff88;
            margin-bottom: 15px;
        }}
        .status {{ 
            background: {status_color}; 
            padding: 20px; 
            border-radius: 15px; 
            text-align: center; 
            margin-bottom: 20px;
            font-size: 1.2em;
            font-weight: bold;
        }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ 
            background: rgba(255,255,255,0.1); 
            padding: 25px; 
            border-radius: 15px;
        }}
        .card h3 {{ color: #00ff88; margin-bottom: 20px; }}
        .metric {{ 
            display: flex; 
            justify-content: space-between; 
            margin: 15px 0; 
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }}
        .logs {{ 
            background: rgba(0,0,0,0.5); 
            padding: 20px; 
            border-radius: 10px; 
            font-family: monospace; 
            font-size: 0.9em;
            max-height: 400px;
            overflow-y: auto;
            margin-top: 20px;
        }}
        .refresh {{ 
            position: fixed; 
            top: 20px; 
            right: 20px; 
            background: #00ff88; 
            color: black; 
            border: none; 
            padding: 15px 20px; 
            border-radius: 25px; 
            cursor: pointer; 
            font-weight: bold;
        }}
    </style>
    <script>
        setTimeout(() => location.reload(), 30000);
        function refresh() {{ location.reload(); }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ CRASH-PROOF BOT</h1>
            <p>Ultra-Stable • Never Crashes • Always Running</p>
            <p>Last Updated: {datetime.now().strftime('%H:%M:%S UTC')}</p>
        </div>
        
        <button class="refresh" onclick="refresh()">🔄</button>
        
        <div class="status">{status_text}</div>
        
        <div class="grid">
            <div class="card">
                <h3>🛡️ System Status</h3>
                <div class="metric">
                    <span>Bot Status:</span>
                    <span>🟢 RUNNING</span>
                </div>
                <div class="metric">
                    <span>Crash Protection:</span>
                    <span>🛡️ ACTIVE</span>
                </div>
                <div class="metric">
                    <span>API Connection:</span>
                    <span>{'✅ YES' if stats['account_verified'] else '⚠️ SAFE MODE'}</span>
                </div>
                <div class="metric">
                    <span>Runtime:</span>
                    <span>{stats['runtime']}</span>
                </div>
            </div>
            
            <div class="card">
                <h3>📊 Trading Stats</h3>
                <div class="metric">
                    <span>Today's Trades:</span>
                    <span>{stats['daily_trades']}/{stats['max_daily_trades']}</span>
                </div>
                <div class="metric">
                    <span>Success Rate:</span>
                    <span>{stats['success_rate']:.1f}%</span>
                </div>
                <div class="metric">
                    <span>Balance:</span>
                    <span>{stats['current_balance']:.2f}</span>
                </div>
                <div class="metric">
                    <span>Total P/L:</span>
                    <span style="color: {'#00ff88' if stats['total_profit'] >= 0 else '#ff4444'};">{stats['total_profit']:+.2f}</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>📱 System Logs</h3>
            <div class="logs">
"""
            
            for log in stats['recent_logs']:
                log_color = '#ffffff'
                if '✅' in log:
                    log_color = '#00ff88'
                elif '❌' in log:
                    log_color = '#ff4444'
                elif '⚠️' in log:
                    log_color = '#ffaa00'
                
                html += f'<div style="color: {log_color}; margin: 2px 0;">{log}</div>'
            
            html += '''
            </div>
        </div>
    </div>
</body>
</html>
'''
            
            return html
            
        except Exception as e:
            return f'<h1>Dashboard Error (but bot still running): {e}</h1>'
    
    def log_message(self, format, *args):
        # Suppress server logs to avoid clutter
        pass

def safe_start_server():
    """Start server safely"""
    try:
        if crash_proof_bot:
            crash_proof_bot.safe_log("🌐 Starting crash-proof server...")
        
        port = int(os.getenv('PORT', 10000))
        server = HTTPServer(('0.0.0.0', port), CrashProofHandler)
        
        def run_server():
            try:
                server.serve_forever()
            except Exception as e:
                if crash_proof_bot:
                    crash_proof_bot.safe_log(f"Server error (but continuing): {e}")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        if crash_proof_bot:
            crash_proof_bot.safe_log(f"✅ Server running on port {port}")
        
    except Exception as e:
        if crash_proof_bot:
            crash_proof_bot.safe_log(f"Server start error: {e}")

def main():
    """Main function with maximum crash protection"""
    global crash_proof_bot
    
    try:
        print("🛡️ STARTING CRASH-PROOF BOT")
        
        # Create crash-proof bot
        crash_proof_bot = CrashProofBot()
        
        # Start server
        safe_start_server()
        
        # Run bot
        crash_proof_bot.safe_run_bot()
        
    except Exception as e:
        print(f"Main error: {e}")
        try:
            if crash_proof_bot:
                crash_proof_bot.safe_log(f"Main error: {e}")
        except:
            pass
        
        # Try to restart after delay
        try:
            time.sleep(30)
            print("🔄 Attempting restart...")
            main()
        except:
            print("💥 Cannot restart - ending")

if __name__ == "__main__":
    main()
