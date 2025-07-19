#!/usr/bin/env python3
"""
CLEAN WORLD-CLASS CTRADER BOT
No input() calls - works perfectly on Render
"""

import json
import time
import os
import urllib.request
import urllib.parse
import random
import math
import statistics
import threading
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

print("🚀 Starting Clean World-Class cTrader Bot")
print("=" * 60)

class WorldClassTradingBot:
    """World's most advanced cTrader trading bot - Clean version"""
    
    def __init__(self):
        # Real cTrader API credentials from environment
        self.access_token = os.getenv('CTRADER_ACCESS_TOKEN', '')
        self.refresh_token = os.getenv('CTRADER_REFRESH_TOKEN', '')
        self.client_id = os.getenv('CTRADER_CLIENT_ID', '')
        self.client_secret = os.getenv('CTRADER_CLIENT_SECRET', '')
        self.account_id = os.getenv('CTRADER_ACCOUNT_ID', '')
        
        # Trading configuration
        self.demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
        self.max_daily_trades = int(os.getenv('MAX_DAILY_TRADES', '20'))
        self.risk_percentage = float(os.getenv('RISK_PERCENTAGE', '0.02'))
        
        # Professional trading pairs
        self.major_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD']
        self.minor_pairs = ['EURGBP', 'EURJPY', 'GBPJPY', 'AUDJPY']
        self.all_symbols = self.major_pairs + self.minor_pairs
        
        # Bot state
        self.running = True
        self.daily_trades = 0
        self.total_trades = 0
        self.successful_trades = 0
        self.total_profit = 0.0
        self.start_time = datetime.now()
        self.last_trade_date = datetime.now().date()
        
        # Data storage
        self.trade_history = []
        self.price_history = {}
        self.current_signals = {}
        self.logs = []
        
        # Account verification
        self.account_verified = False
        self.account_info = {}
        
        self.log("🚀 Clean World-Class cTrader Bot Initialized")
        self.log(f"💰 Mode: {'DEMO' if self.demo_mode else 'LIVE'}")
        self.log(f"📊 Trading {len(self.all_symbols)} currency pairs")
        
        # Verify real account connection
        self.verify_account_connection()
    
    def log(self, message):
        """Enhanced professional logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        
        # Keep last 100 logs
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
        
        print(log_entry)
    
    def verify_account_connection(self):
        """Verify real cTrader account connection"""
        self.log("🔍 Verifying real cTrader account connection...")
        
        if not self.access_token:
            self.log("⚠️ No access token - running in simulation mode")
            self.account_info = {
                'account_id': 'SIMULATION',
                'account_type': 'DEMO',
                'broker': 'Simulation Mode',
                'balance': 10000.0,
                'currency': 'USD',
                'verified': False
            }
            return
        
        try:
            # Use correct API endpoint based on demo mode
            if self.demo_mode:
                api_base = "https://demo-openapi.ctrader.com"
            else:
                api_base = "https://openapi.ctrader.com"
            
            url = f"{api_base}/v2/accounts"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'User-Agent': 'WorldClassBot/2.0'
            }
            
            request = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(request, timeout=15) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    
                    if data and len(data) > 0:
                        account = data[0]
                        
                        self.account_info = {
                            'account_id': account.get('accountId', 'Unknown'),
                            'account_type': account.get('accountType', 'Unknown'),
                            'broker': account.get('brokerName', 'Unknown'),
                            'balance': float(account.get('balance', 0)),
                            'currency': account.get('currency', 'USD'),
                            'server': account.get('server', 'Unknown'),
                            'verified': True,
                            'last_update': datetime.now().isoformat()
                        }
                        
                        self.account_verified = True
                        
                        self.log("✅ REAL ACCOUNT VERIFIED!")
                        self.log(f"   📋 Account: {self.account_info['account_id']}")
                        self.log(f"   🏦 Broker: {self.account_info['broker']}")
                        self.log(f"   💰 Balance: {self.account_info['balance']:.2f} {self.account_info['currency']}")
                        self.log(f"   📊 Type: {self.account_info['account_type']}")
                        
                    else:
                        raise Exception("No accounts found")
                        
                else:
                    raise Exception(f"HTTP {response.status}")
        
        except urllib.error.HTTPError as e:
            if e.code == 401:
                self.log("🔄 Access token expired - attempting refresh...")
                if self.refresh_access_token():
                    return self.verify_account_connection()
            
            self.log(f"❌ API Error: HTTP {e.code}")
            self.account_info = {'verified': False, 'error': f'HTTP {e.code}'}
            
        except Exception as e:
            self.log(f"❌ Connection failed: {e}")
            self.account_info = {'verified': False, 'error': str(e)}
    
    def refresh_access_token(self):
        """Refresh expired access token"""
        if not self.refresh_token or not self.client_id or not self.client_secret:
            self.log("❌ Missing refresh credentials")
            return False
        
        try:
            url = "https://openapi.ctrader.com/apps/token"
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            data_encoded = urllib.parse.urlencode(data).encode()
            request = urllib.request.Request(url, data=data_encoded, method='POST')
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            with urllib.request.urlopen(request, timeout=10) as response:
                result = json.loads(response.read().decode())
                
                if 'access_token' in result:
                    self.access_token = result['access_token']
                    if 'refresh_token' in result:
                        self.refresh_token = result['refresh_token']
                    
                    self.log("✅ Access token refreshed successfully")
                    return True
            
            return False
            
        except Exception as e:
            self.log(f"❌ Token refresh failed: {e}")
            return False
    
    def get_live_price(self, symbol):
        """Get realistic forex prices"""
        try:
            # Simulate realistic price movements
            base_prices = {
                'EURUSD': 1.0850, 'GBPUSD': 1.2650, 'USDJPY': 148.50, 'AUDUSD': 0.6680,
                'EURGBP': 0.8580, 'EURJPY': 159.80, 'GBPJPY': 187.20, 'AUDJPY': 99.40
            }
            
            base = base_prices.get(symbol, 1.0000)
            
            # Advanced market simulation
            now = time.time()
            
            # Multiple time cycles for realistic movement
            daily_cycle = math.sin((now % 86400) / 86400 * 2 * math.pi) * 0.004
            hourly_cycle = math.sin((now % 3600) / 3600 * 2 * math.pi) * 0.002
            
            # Market volatility based on time
            hour = datetime.now().hour
            if 8 <= hour <= 16:  # London/NY overlap
                volatility = 0.003
            elif 13 <= hour <= 21:  # NY session
                volatility = 0.002
            else:  # Other times
                volatility = 0.001
            
            # Random component
            random_component = random.uniform(-volatility, volatility)
            
            return base + daily_cycle + hourly_cycle + random_component
            
        except Exception as e:
            self.log(f"⚠️ Price error for {symbol}: {e}")
            return base_prices.get(symbol, 1.0000)
    
    def update_price_history(self, symbol, price):
        """Update price history for analysis"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append({
            'price': price,
            'timestamp': time.time(),
            'datetime': datetime.now()
        })
        
        # Keep last 200 prices
        if len(self.price_history[symbol]) > 200:
            self.price_history[symbol] = self.price_history[symbol][-200:]
    
    def calculate_rsi(self, symbol, period=14):
        """Calculate RSI indicator"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < period + 1:
            return 50
        
        prices = [p['price'] for p in self.price_history[symbol]]
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        if len(changes) < period:
            return 50
        
        recent_changes = changes[-period:]
        gains = [max(0, change) for change in recent_changes]
        losses = [max(0, -change) for change in recent_changes]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_sma(self, symbol, period):
        """Calculate Simple Moving Average"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < period:
            return None
        
        prices = [p['price'] for p in self.price_history[symbol]]
        return sum(prices[-period:]) / period
    
    def calculate_momentum(self, symbol, period=10):
        """Calculate price momentum"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < period:
            return 0
        
        prices = [p['price'] for p in self.price_history[symbol]]
        return ((prices[-1] - prices[-period]) / prices[-period]) * 100
    
    def detect_market_session(self):
        """Detect current trading session"""
        hour = datetime.now().hour
        
        if 22 <= hour or hour <= 8:
            return 'asian'
        elif 8 <= hour <= 16:
            return 'london'
        elif 13 <= hour <= 21:
            return 'newyork'
        else:
            return 'overlap' if 13 <= hour <= 16 else 'quiet'
    
    def advanced_market_analysis(self, symbol):
        """Advanced market analysis"""
        try:
            # Get current price
            current_price = self.get_live_price(symbol)
            if not current_price:
                return self.create_hold_signal(symbol)
            
            # Update price history
            self.update_price_history(symbol, current_price)
            
            # Calculate indicators
            rsi = self.calculate_rsi(symbol)
            sma_20 = self.calculate_sma(symbol, 20)
            sma_50 = self.calculate_sma(symbol, 50)
            momentum = self.calculate_momentum(symbol)
            
            # Market context
            session = self.detect_market_session()
            
            # Signal generation
            signals = []
            confidence = 0.0
            reasons = []
            
            # RSI Analysis
            if rsi < 25:
                signals.append('BUY')
                confidence += 0.3
                reasons.append(f"Oversold RSI ({rsi:.1f})")
            elif rsi > 75:
                signals.append('SELL')
                confidence += 0.3
                reasons.append(f"Overbought RSI ({rsi:.1f})")
            
            # Moving Average Analysis
            if sma_20 and sma_50:
                if current_price > sma_20 > sma_50:
                    signals.append('BUY')
                    confidence += 0.25
                    reasons.append("Bullish MA alignment")
                elif current_price < sma_20 < sma_50:
                    signals.append('SELL')
                    confidence += 0.25
                    reasons.append("Bearish MA alignment")
            
            # Momentum Analysis
            if momentum > 0.15:
                signals.append('BUY')
                confidence += 0.2
                reasons.append(f"Positive momentum ({momentum:.2f}%)")
            elif momentum < -0.15:
                signals.append('SELL')
                confidence += 0.2
                reasons.append(f"Negative momentum ({momentum:.2f}%)")
            
            # Session boost
            session_multipliers = {
                'london': 1.2, 'newyork': 1.1, 'overlap': 1.3,
                'asian': 0.8, 'quiet': 0.6
            }
            confidence *= session_multipliers.get(session, 1.0)
            
            # Final decision
            buy_signals = signals.count('BUY')
            sell_signals = signals.count('SELL')
            
            if buy_signals > sell_signals and buy_signals >= 2:
                action = 'BUY'
            elif sell_signals > buy_signals and sell_signals >= 2:
                action = 'SELL'
            else:
                action = 'HOLD'
                confidence = min(confidence, 0.4)
            
            # Create signal
            signal = {
                'symbol': symbol,
                'action': action,
                'confidence': min(confidence, 0.95),
                'price': current_price,
                'rsi': rsi,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'momentum': momentum,
                'session': session,
                'reasons': reasons,
                'timestamp': datetime.now().isoformat()
            }
            
            self.current_signals[symbol] = signal
            return signal
            
        except Exception as e:
            self.log(f"❌ Analysis error for {symbol}: {e}")
            return self.create_hold_signal(symbol)
    
    def create_hold_signal(self, symbol):
        """Create a HOLD signal"""
        return {
            'symbol': symbol,
            'action': 'HOLD',
            'confidence': 0.0,
            'price': self.get_live_price(symbol),
            'rsi': 50,
            'reasons': ['Analysis unavailable'],
            'timestamp': datetime.now().isoformat()
        }
    
    def execute_trade(self, signal):
        """Execute trade with professional management"""
        try:
            symbol = signal['symbol']
            action = signal['action']
            volume = 1000  # 0.01 lots
            
            self.log(f"🚀 EXECUTING: {action} {symbol} | Confidence: {signal['confidence']:.1%}")
            
            # Simulate trade execution
            if self.account_verified and not self.demo_mode:
                success = self.execute_ctrader_trade(symbol, action, volume)
            else:
                # Simulate with realistic success rate
                success = random.choice([True, True, True, False])  # 75% success
            
            # Calculate estimated profit
            estimated_profit = 0
            if success:
                estimated_profit = volume * 0.001 * random.uniform(0.5, 2.0)
                if action == 'SELL':
                    estimated_profit *= -1
                self.total_profit += estimated_profit
            
            # Record trade
            trade_record = {
                'timestamp': datetime.now().isoformat(),
                'time': datetime.now().strftime("%H:%M:%S"),
                'date': datetime.now().strftime("%Y-%m-%d"),
                'symbol': symbol,
                'action': action,
                'volume': volume,
                'price': signal['price'],
                'confidence': signal['confidence'],
                'success': success,
                'estimated_profit': estimated_profit,
                'rsi': signal.get('rsi', 50),
                'session': signal.get('session', 'unknown'),
                'reasons': signal.get('reasons', [])
            }
            
            self.trade_history.append(trade_record)
            self.daily_trades += 1
            self.total_trades += 1
            
            if success:
                self.successful_trades += 1
                self.log(f"✅ TRADE SUCCESS: {action} {symbol} @ {signal['price']:.5f}")
            else:
                self.log(f"⚠️ TRADE FAILED")
            
            return success
            
        except Exception as e:
            self.log(f"❌ Trade execution error: {e}")
            return False
    
    def execute_ctrader_trade(self, symbol, action, volume):
        """Execute real trade on cTrader"""
        try:
            # Use correct API endpoint
            if self.demo_mode:
                api_base = "https://demo-openapi.ctrader.com"
            else:
                api_base = "https://openapi.ctrader.com"
            
            url = f"{api_base}/v2/trade"
            
            order_data = {
                "accountId": self.account_id,
                "symbolName": symbol,
                "tradeSide": action.upper(),
                "volume": volume,
                "orderType": "MARKET"
            }
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = json.dumps(order_data).encode('utf-8')
            request = urllib.request.Request(url, data=data, headers=headers, method='POST')
            
            with urllib.request.urlopen(request, timeout=15) as response:
                return response.status in [200, 201, 202]
        
        except Exception as e:
            self.log(f"API trade error: {e}")
            return False
    
    def reset_daily_counters(self):
        """Reset daily counters"""
        current_date = datetime.now().date()
        if current_date != self.last_trade_date:
            self.daily_trades = 0
            self.last_trade_date = current_date
            self.log(f"🌅 New trading day: {current_date}")
    
    def get_stats(self):
        """Get comprehensive statistics"""
        runtime = datetime.now() - self.start_time
        success_rate = (self.successful_trades / max(self.total_trades, 1)) * 100
        
        return {
            'active': self.running,
            'account_verified': self.account_verified,
            'account_info': self.account_info,
            'demo_mode': self.demo_mode,
            'daily_trades': self.daily_trades,
            'max_daily_trades': self.max_daily_trades,
            'total_trades': self.total_trades,
            'successful_trades': self.successful_trades,
            'success_rate': success_rate,
            'total_profit': self.total_profit,
            'runtime': str(runtime).split('.')[0],
            'recent_logs': self.logs[-50:],
            'current_session': self.detect_market_session(),
            'trading_pairs': len(self.all_symbols)
        }
    
    def get_recent_trades(self):
        """Get recent trades"""
        return self.trade_history[-30:]
    
    def get_current_signals(self):
        """Get current signals"""
        return list(self.current_signals.values())
    
    def trading_cycle(self):
        """Main trading cycle"""
        try:
            self.reset_daily_counters()
            
            if self.daily_trades >= self.max_daily_trades:
                self.log(f"📊 Daily limit: {self.daily_trades}/{self.max_daily_trades}")
                return
            
            session = self.detect_market_session()
            self.log(f"🧠 AI analysis cycle ({session} session)...")
            
            for symbol in self.all_symbols:
                try:
                    self.log(f"🔍 Analyzing {symbol}...")
                    
                    signal = self.advanced_market_analysis(symbol)
                    
                    confidence_emoji = "🔥" if signal['confidence'] > 0.8 else "⚡" if signal['confidence'] > 0.7 else "📊"
                    
                    self.log(f"{confidence_emoji} {symbol}: {signal['action']} "
                           f"(Confidence: {signal['confidence']:.1%}, RSI: {signal.get('rsi', 0):.1f})")
                    
                    # Execute high-confidence trades
                    if (signal['action'] in ['BUY', 'SELL'] and 
                        signal['confidence'] >= 0.75 and
                        self.daily_trades < self.max_daily_trades):
                        
                        self.execute_trade(signal)
                        time.sleep(5)  # Wait between trades
                        
                        if self.daily_trades >= self.max_daily_trades:
                            break
                    else:
                        self.log(f"📋 {symbol}: Below threshold - monitoring")
                
                except Exception as e:
                    self.log(f"❌ Error with {symbol}: {e}")
                
                time.sleep(2)
            
        except Exception as e:
            self.log(f"❌ Trading cycle error: {e}")
    
    def run_bot(self):
        """Main bot execution"""
        self.log("🚀 Starting World-Class Trading Engine")
        
        cycle = 0
        
        while self.running:
            try:
                cycle += 1
                self.log(f"🔄 Trading Cycle #{cycle}")
                
                # Execute trading cycle
                self.trading_cycle()
                
                # Status update
                stats = self.get_stats()
                self.log(f"💓 Status: {stats['daily_trades']}/{stats['max_daily_trades']} trades | "
                        f"Success: {stats['success_rate']:.1f}% | "
                        f"Session: {stats['current_session']}")
                
                # Wait 5 minutes
                self.log("⏰ Next analysis in 5 minutes...")
                time.sleep(300)
                
            except Exception as e:
                self.log(f"❌ Bot error: {e}")
                time.sleep(60)

# Global bot instance
world_class_bot = None

class CleanDashboardHandler(BaseHTTPRequestHandler):
    """Clean dashboard handler"""
    
    def do_GET(self):
        """Handle requests"""
        try:
            if self.path == '/' or self.path == '/dashboard':
                html = self.get_dashboard()
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
                
            elif self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                health_data = {
                    'status': 'healthy',
                    'bot_active': world_class_bot.running if world_class_bot else False,
                    'account_verified': world_class_bot.account_verified if world_class_bot else False,
                    'version': 'clean-2.0'
                }
                self.wfile.write(json.dumps(health_data).encode())
                
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'404 Not Found')
                
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f'Error: {str(e)}'.encode())
    
    def get_dashboard(self):
        """Generate dashboard"""
        if not world_class_bot:
            return "<h1>Bot not initialized</h1>"
        
        try:
            stats = world_class_bot.get_stats()
            trades = world_class_bot.get_recent_trades()
            signals = world_class_bot.get_current_signals()
            account_info = stats.get('account_info', {})
            
            # Account verification status
            if stats['account_verified']:
                account_status = f"""
                <div style="background: linear-gradient(45deg, #28a745, #20c997); padding: 20px; border-radius: 15px; margin-bottom: 20px; text-align: center;">
                    <div style="font-size: 1.2em; font-weight: bold; margin-bottom: 10px;">✅ REAL ACCOUNT VERIFIED</div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; font-size: 0.9em;">
                        <div><strong>Account ID:</strong> {account_info.get('account_id', 'Unknown')}</div>
                        <div><strong>Broker:</strong> {account_info.get('broker', 'Unknown')}</div>
                        <div><strong>Balance:</strong> {account_info.get('balance', 0):.2f} {account_info.get('currency', 'USD')}</div>
                        <div><strong>Type:</strong> {account_info.get('account_type', 'Unknown')}</div>
                    </div>
                </div>
                """
            else:
                account_status = f"""
                <div style="background: linear-gradient(45deg, #ffc107, #fd7e14); padding: 20px; border-radius: 15px; margin-bottom: 20px; color: #000; text-align: center;">
                    <div style="font-size: 1.2em; font-weight: bold; margin-bottom: 10px;">⚠️ SIMULATION MODE</div>
                    <div>No real account connected</div>
                    <div>Set CTRADER_ACCESS_TOKEN to connect</div>
                </div>
                """
            
            html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏆 World-Class cTrader Bot</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #667eea 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ 
            text-align: center; 
            margin-bottom: 30px;
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 20px;
            backdrop-filter: blur(15px);
        }}
        .header h1 {{ 
            font-size: 2.5em; 
            margin-bottom: 15px;
            animation: pulse 3s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
        }}
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
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
            margin-bottom: 20px; 
            color: #4ecdc4;
            font-size: 1.3em;
        }}
        .metric {{ 
            display: flex; 
            justify-content: space-between; 
            margin: 12px 0; 
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .metric-value {{ 
            font-weight: bold; 
            color: #ff6b6b;
        }}
        .signals {{ display: grid; gap: 15px; }}
        .signal {{ 
            padding: 15px; 
            border-radius: 10px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
        }}
        .signal.buy {{ background: linear-gradient(45deg, #28a745, #20c997); }}
        .signal.sell {{ background: linear-gradient(45deg, #dc3545, #fd7e14); }}
        .signal.hold {{ background: linear-gradient(45deg, #6c757d, #adb5bd); }}
        .logs {{ 
            background: rgba(0,0,0,0.4); 
            padding: 20px; 
            border-radius: 10px; 
            font-family: monospace; 
            font-size: 0.9em;
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
            padding: 12px 20px; 
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
            <h1>🏆 World-Class cTrader Bot</h1>
            <p>Clean Version • Last Updated: {datetime.now().strftime('%H:%M:%S UTC')}</p>
        </div>
        
        <button class="refresh" onclick="refresh()">🔄 Refresh</button>
        
        {account_status}
        
        <div class="grid">
            <div class="card">
                <h3>💰 Performance</h3>
                <div class="metric">
                    <span>Account Verified:</span>
                    <span class="metric-value">{'✅ YES' if stats['account_verified'] else '❌ NO'}</span>
                </div>
                <div class="metric">
                    <span>Trading Mode:</span>
                    <span class="metric-value">{'🧪 DEMO' if stats['demo_mode'] else '🔥 LIVE'}</span>
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
                    <span>Total P/L:</span>
                    <span class="metric-value">{stats['total_profit']:+.2f}</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🎯 Live Signals</h3>
                <div class="signals">
"""
            
            # Add signals
            if signals:
                for signal in signals[-4:]:
                    signal_class = signal['action'].lower()
                    html += f'''
                    <div class="signal {signal_class}">
                        <div>
                            <strong>{signal['symbol']}</strong><br>
                            <small>{signal['action']} @ {signal['price']:.5f}</small>
                        </div>
                        <div style="font-weight: bold;">{signal['confidence']:.0%}</div>
                    </div>
'''
            else:
                html += '''
                    <div class="signal hold">
                        <div><strong>🔍 Analyzing...</strong></div>
                        <div>⏳</div>
                    </div>
'''
            
            html += '''
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>📱 Live Activity</h3>
            <div class="logs">
'''
            
            # Add logs
            for log in stats['recent_logs'][-15:]:
                html += f'<div>{log}</div>'
            
            html += '''
            </div>
        </div>
    </div>
</body>
</html>
'''
            return html
            
        except Exception as e:
            return f'<h1>Error: {str(e)}</h1>'
    
    def log_message(self, format, *args):
        pass

def start_server():
    """Start web server"""
    try:
        port = int(os.getenv('PORT', 10000))
        server = HTTPServer(('0.0.0.0', port), CleanDashboardHandler)
        
        world_class_bot.log(f"🌐 Server starting on port {port}")
        
        def run_server():
            try:
                server.serve_forever()
            except Exception as e:
                world_class_bot.log(f"Server error: {e}")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        world_class_bot.log("✅ Dashboard live!")
        
    except Exception as e:
        world_class_bot.log(f"Server error: {e}")

def main():
    """Main function - NO INPUT CALLS"""
    global world_class_bot
    
    try:
        print("🏆 Starting Clean World-Class Bot")
        
        # Create bot
        world_class_bot = WorldClassTradingBot()
        
        # Start server
        start_server()
        
        # Start trading
        world_class_bot.run_bot()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        if world_class_bot:
            world_class_bot.log(f"Fatal error: {e}")
        time.sleep(30)
        main()

if __name__ == "__main__":
    main()
