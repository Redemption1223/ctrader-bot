#!/usr/bin/env python3
"""
ENHANCED WORLD-CLASS CTRADER BOT
Advanced algorithms, risk management, and live trading
⚠️ WARNING: Trading involves substantial risk of loss
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
import hashlib
import hmac

print("🚀 Starting Enhanced World-Class cTrader Bot")
print("⚠️ WARNING: Trading involves substantial risk of loss")
print("=" * 60)

class EnhancedTradingBot:
    """Enhanced world-class cTrader trading bot with advanced algorithms"""
    
    def __init__(self):
        # Real cTrader API credentials from environment
        self.access_token = os.getenv('CTRADER_ACCESS_TOKEN', '')
        self.refresh_token = os.getenv('CTRADER_REFRESH_TOKEN', '')
        self.client_id = os.getenv('CTRADER_CLIENT_ID', '')
        self.client_secret = os.getenv('CTRADER_CLIENT_SECRET', '')
        self.account_id = os.getenv('CTRADER_ACCOUNT_ID', '')
        
        # Enhanced trading configuration
        self.demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
        self.max_daily_trades = int(os.getenv('MAX_DAILY_TRADES', '50'))
        self.base_risk_percentage = float(os.getenv('RISK_PERCENTAGE', '0.01'))  # 1% base risk
        self.max_risk_per_trade = float(os.getenv('MAX_RISK_PER_TRADE', '0.02'))  # 2% max risk
        self.max_portfolio_risk = float(os.getenv('MAX_PORTFOLIO_RISK', '0.10'))  # 10% max portfolio risk
        
        # Professional trading pairs with volatility ratings
        self.currency_pairs = {
            # Major pairs (lower risk, higher liquidity)
            'EURUSD': {'volatility': 'low', 'spread': 0.8, 'base_volume': 10000},
            'GBPUSD': {'volatility': 'medium', 'spread': 1.2, 'base_volume': 10000},
            'USDJPY': {'volatility': 'low', 'spread': 0.9, 'base_volume': 10000},
            'AUDUSD': {'volatility': 'medium', 'spread': 1.5, 'base_volume': 8000},
            
            # Minor pairs (medium risk)
            'EURGBP': {'volatility': 'low', 'spread': 1.8, 'base_volume': 8000},
            'EURJPY': {'volatility': 'medium', 'spread': 1.6, 'base_volume': 8000},
            'GBPJPY': {'volatility': 'high', 'spread': 2.5, 'base_volume': 6000},
            'AUDJPY': {'volatility': 'medium', 'spread': 2.0, 'base_volume': 6000},
            
            # Cross pairs (higher risk, but more opportunities)
            'EURCHF': {'volatility': 'low', 'spread': 2.2, 'base_volume': 6000},
            'GBPCHF': {'volatility': 'medium', 'spread': 3.0, 'base_volume': 5000},
            'AUDCAD': {'volatility': 'medium', 'spread': 2.8, 'base_volume': 5000},
            'NZDUSD': {'volatility': 'high', 'spread': 2.5, 'base_volume': 5000}
        }
        
        # Enhanced bot state
        self.running = True
        self.daily_trades = 0
        self.total_trades = 0
        self.successful_trades = 0
        self.total_profit = 0.0
        self.daily_profit = 0.0
        self.max_drawdown = 0.0
        self.peak_balance = 0.0
        self.start_time = datetime.now()
        self.last_trade_date = datetime.now().date()
        
        # Advanced data storage
        self.trade_history = []
        self.price_history = {}
        self.current_signals = {}
        self.market_sentiment = {}
        self.correlation_matrix = {}
        self.volatility_tracker = {}
        self.news_sentiment = {}
        self.logs = []
        
        # Risk management
        self.open_positions = {}
        self.daily_loss_limit = 0.05  # 5% daily loss limit
        self.consecutive_losses = 0
        self.max_consecutive_losses = 5
        
        # Account verification
        self.account_verified = False
        self.account_info = {}
        self.current_balance = 0.0
        
        # Advanced indicators storage
        self.indicators = {}
        
        self.log("🚀 Enhanced World-Class cTrader Bot Initialized")
        self.log(f"💰 Mode: {'DEMO' if self.demo_mode else 'LIVE TRADING'}")
        self.log(f"📊 Trading {len(self.currency_pairs)} currency pairs")
        self.log(f"⚠️ Daily loss limit: {self.daily_loss_limit:.1%}")
        
        # Initialize components
        self.initialize_indicators()
        self.verify_account_connection()
    
    def log(self, message):
        """Enhanced professional logging with categories"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        
        # Keep last 200 logs
        if len(self.logs) > 200:
            self.logs = self.logs[-200:]
        
        print(log_entry)
    
    def initialize_indicators(self):
        """Initialize advanced technical indicators"""
        for symbol in self.currency_pairs:
            self.indicators[symbol] = {
                'rsi': [],
                'macd': {'line': [], 'signal': [], 'histogram': []},
                'bollinger': {'upper': [], 'middle': [], 'lower': []},
                'stochastic': {'k': [], 'd': []},
                'ema_fast': [],
                'ema_slow': [],
                'atr': [],
                'adx': [],
                'cci': [],
                'williams_r': []
            }
    
    def verify_account_connection(self):
        """Enhanced account verification with detailed info"""
        self.log("🔍 Verifying cTrader account connection...")
        
        if not self.access_token:
            self.log("⚠️ No access token - running in simulation mode")
            self.account_info = {
                'account_id': 'SIMULATION',
                'account_type': 'DEMO',
                'broker': 'Simulation Mode',
                'balance': 50000.0,  # Increased simulation balance
                'currency': 'USD',
                'verified': False
            }
            self.current_balance = 50000.0
            self.peak_balance = 50000.0
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
                'User-Agent': 'EnhancedBot/3.0'
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
                            'equity': float(account.get('equity', 0)),
                            'currency': account.get('currency', 'USD'),
                            'server': account.get('server', 'Unknown'),
                            'verified': True,
                            'last_update': datetime.now().isoformat()
                        }
                        
                        self.current_balance = self.account_info['balance']
                        self.peak_balance = self.current_balance
                        self.account_verified = True
                        
                        self.log("✅ REAL ACCOUNT VERIFIED!")
                        self.log(f"   📋 Account: {self.account_info['account_id']}")
                        self.log(f"   🏦 Broker: {self.account_info['broker']}")
                        self.log(f"   💰 Balance: {self.account_info['balance']:.2f} {self.account_info['currency']}")
                        self.log(f"   📊 Equity: {self.account_info.get('equity', 0):.2f} {self.account_info['currency']}")
                        self.log(f"   🎯 Type: {self.account_info['account_type']}")
                        
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
    
    def get_enhanced_price_data(self, symbol):
        """Get enhanced price data with OHLC simulation"""
        try:
            # Base prices with more realistic spreads
            base_prices = {
                'EURUSD': 1.0850, 'GBPUSD': 1.2650, 'USDJPY': 148.50, 'AUDUSD': 0.6680,
                'EURGBP': 0.8580, 'EURJPY': 159.80, 'GBPJPY': 187.20, 'AUDJPY': 99.40,
                'EURCHF': 0.9720, 'GBPCHF': 1.1580, 'AUDCAD': 0.9120, 'NZDUSD': 0.6150
            }
            
            base = base_prices.get(symbol, 1.0000)
            pair_info = self.currency_pairs.get(symbol, {})
            
            # Enhanced market simulation with multiple cycles
            now = time.time()
            
            # Daily cycle (major trend)
            daily_cycle = math.sin((now % 86400) / 86400 * 2 * math.pi) * 0.003
            
            # Hourly cycle (medium-term moves)
            hourly_cycle = math.sin((now % 3600) / 3600 * 2 * math.pi) * 0.002
            
            # 15-minute cycle (short-term fluctuations)
            minute_cycle = math.sin((now % 900) / 900 * 2 * math.pi) * 0.001
            
            # Enhanced volatility based on time and pair characteristics
            hour = datetime.now().hour
            
            # London/NY overlap (highest volatility)
            if 13 <= hour <= 16:
                volatility_multiplier = 1.5
            # London session
            elif 8 <= hour <= 16:
                volatility_multiplier = 1.2
            # NY session
            elif 13 <= hour <= 21:
                volatility_multiplier = 1.1
            # Asian session
            elif 22 <= hour or hour <= 8:
                volatility_multiplier = 0.8
            else:
                volatility_multiplier = 0.6
            
            # Pair-specific volatility
            volatility_map = {'low': 0.0015, 'medium': 0.0025, 'high': 0.0035}
            base_volatility = volatility_map.get(pair_info.get('volatility', 'medium'), 0.0025)
            
            # News impact simulation (random spikes)
            news_impact = 0
            if random.random() < 0.02:  # 2% chance of news event
                news_impact = random.uniform(-0.005, 0.005)
                if abs(news_impact) > 0.003:
                    self.log(f"📈 Simulated news impact on {symbol}: {news_impact:+.4f}")
            
            # Final price calculation
            volatility = base_volatility * volatility_multiplier
            random_component = random.uniform(-volatility, volatility)
            
            bid_price = base + daily_cycle + hourly_cycle + minute_cycle + random_component + news_impact
            
            # Calculate ask price with spread
            spread_pips = pair_info.get('spread', 1.5)
            if symbol.endswith('JPY'):
                spread = spread_pips * 0.01
            else:
                spread = spread_pips * 0.0001
            
            ask_price = bid_price + spread
            
            # Generate OHLC data for last period
            ohlc = {
                'open': bid_price + random.uniform(-volatility*0.5, volatility*0.5),
                'high': bid_price + random.uniform(0, volatility*2),
                'low': bid_price - random.uniform(0, volatility*2),
                'close': bid_price,
                'bid': bid_price,
                'ask': ask_price,
                'spread': spread,
                'timestamp': time.time(),
                'datetime': datetime.now()
            }
            
            # Ensure high >= close >= low and high >= open >= low
            ohlc['high'] = max(ohlc['high'], ohlc['open'], ohlc['close'])
            ohlc['low'] = min(ohlc['low'], ohlc['open'], ohlc['close'])
            
            return ohlc
            
        except Exception as e:
            self.log(f"⚠️ Price error for {symbol}: {e}")
            return {
                'open': base_prices.get(symbol, 1.0), 'high': base_prices.get(symbol, 1.0),
                'low': base_prices.get(symbol, 1.0), 'close': base_prices.get(symbol, 1.0),
                'bid': base_prices.get(symbol, 1.0), 'ask': base_prices.get(symbol, 1.0),
                'spread': 0.0002, 'timestamp': time.time(), 'datetime': datetime.now()
            }
    
    def update_price_history(self, symbol, price_data):
        """Update price history with OHLC data"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(price_data)
        
        # Keep last 500 bars for advanced analysis
        if len(self.price_history[symbol]) > 500:
            self.price_history[symbol] = self.price_history[symbol][-500:]
    
    def calculate_advanced_rsi(self, symbol, period=14):
        """Calculate RSI with smoothing"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < period + 1:
            return 50
        
        prices = [p['close'] for p in self.price_history[symbol]]
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        if len(changes) < period:
            return 50
        
        # Use Wilder's smoothing method
        gains = [max(0, change) for change in changes[-period:]]
        losses = [max(0, -change) for change in changes[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Store in indicators
        if symbol in self.indicators:
            self.indicators[symbol]['rsi'].append(rsi)
            if len(self.indicators[symbol]['rsi']) > 100:
                self.indicators[symbol]['rsi'] = self.indicators[symbol]['rsi'][-100:]
        
        return rsi
    
    def calculate_macd(self, symbol, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < slow:
            return {'line': 0, 'signal': 0, 'histogram': 0}
        
        prices = [p['close'] for p in self.price_history[symbol]]
        
        # Calculate EMAs
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line (EMA of MACD)
        macd_values = self.indicators[symbol]['macd']['line'] + [macd_line]
        signal_line = self.calculate_ema(macd_values, signal) if len(macd_values) >= signal else macd_line
        
        histogram = macd_line - signal_line
        
        # Store values
        if symbol in self.indicators:
            self.indicators[symbol]['macd']['line'].append(macd_line)
            self.indicators[symbol]['macd']['signal'].append(signal_line)
            self.indicators[symbol]['macd']['histogram'].append(histogram)
            
            # Keep last 100 values
            for key in ['line', 'signal', 'histogram']:
                if len(self.indicators[symbol]['macd'][key]) > 100:
                    self.indicators[symbol]['macd'][key] = self.indicators[symbol]['macd'][key][-100:]
        
        return {'line': macd_line, 'signal': signal_line, 'histogram': histogram}
    
    def calculate_ema(self, prices, period):
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return sum(prices) / len(prices)
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def calculate_bollinger_bands(self, symbol, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < period:
            current_price = self.price_history[symbol][-1]['close'] if self.price_history[symbol] else 1.0
            return {'upper': current_price, 'middle': current_price, 'lower': current_price}
        
        prices = [p['close'] for p in self.price_history[symbol][-period:]]
        
        middle = sum(prices) / period
        variance = sum((p - middle) ** 2 for p in prices) / period
        std = math.sqrt(variance)
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {'upper': upper, 'middle': middle, 'lower': lower}
    
    def calculate_stochastic(self, symbol, k_period=14, d_period=3):
        """Calculate Stochastic Oscillator"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < k_period:
            return {'k': 50, 'd': 50}
        
        recent_data = self.price_history[symbol][-k_period:]
        
        current_close = recent_data[-1]['close']
        lowest_low = min(p['low'] for p in recent_data)
        highest_high = max(p['high'] for p in recent_data)
        
        if highest_high == lowest_low:
            k_percent = 50
        else:
            k_percent = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
        
        # Store K values and calculate D (moving average of K)
        if symbol in self.indicators:
            self.indicators[symbol]['stochastic']['k'].append(k_percent)
            if len(self.indicators[symbol]['stochastic']['k']) > 50:
                self.indicators[symbol]['stochastic']['k'] = self.indicators[symbol]['stochastic']['k'][-50:]
            
            # Calculate D
            k_values = self.indicators[symbol]['stochastic']['k']
            if len(k_values) >= d_period:
                d_percent = sum(k_values[-d_period:]) / d_period
            else:
                d_percent = sum(k_values) / len(k_values)
            
            self.indicators[symbol]['stochastic']['d'].append(d_percent)
            if len(self.indicators[symbol]['stochastic']['d']) > 50:
                self.indicators[symbol]['stochastic']['d'] = self.indicators[symbol]['stochastic']['d'][-50:]
        else:
            d_percent = k_percent
        
        return {'k': k_percent, 'd': d_percent}
    
    def calculate_atr(self, symbol, period=14):
        """Calculate Average True Range for volatility"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < period + 1:
            return 0.001
        
        data = self.price_history[symbol][-period-1:]
        true_ranges = []
        
        for i in range(1, len(data)):
            high_low = data[i]['high'] - data[i]['low']
            high_close_prev = abs(data[i]['high'] - data[i-1]['close'])
            low_close_prev = abs(data[i]['low'] - data[i-1]['close'])
            
            true_range = max(high_low, high_close_prev, low_close_prev)
            true_ranges.append(true_range)
        
        atr = sum(true_ranges) / len(true_ranges)
        
        # Store ATR
        if symbol in self.indicators:
            self.indicators[symbol]['atr'].append(atr)
            if len(self.indicators[symbol]['atr']) > 50:
                self.indicators[symbol]['atr'] = self.indicators[symbol]['atr'][-50:]
        
        return atr
    
    def detect_market_session_enhanced(self):
        """Enhanced market session detection with overlap periods"""
        hour = datetime.now().hour
        minute = datetime.now().minute
        
        # More precise session timing
        if 22 <= hour or hour < 8:
            if hour == 22 or (hour == 7 and minute >= 30):
                return 'asian_opening'
            return 'asian'
        elif 8 <= hour < 13:
            if hour == 8:
                return 'london_opening'
            return 'london'
        elif 13 <= hour < 17:
            if hour == 13:
                return 'overlap_opening'
            return 'london_ny_overlap'  # Highest volatility
        elif 17 <= hour < 22:
            return 'ny_closing'
        else:
            return 'quiet'
    
    def advanced_sentiment_analysis(self, symbol):
        """Advanced market sentiment analysis"""
        try:
            if symbol not in self.price_history or len(self.price_history[symbol]) < 50:
                return {'sentiment': 'neutral', 'strength': 0.5}
            
            recent_data = self.price_history[symbol][-50:]
            prices = [p['close'] for p in recent_data]
            
            # Price momentum
            short_ma = sum(prices[-10:]) / 10
            long_ma = sum(prices[-30:]) / 30
            momentum = (short_ma - long_ma) / long_ma
            
            # Volume analysis (simulated based on volatility)
            volumes = []
            for data in recent_data:
                vol_range = data['high'] - data['low']
                simulated_volume = vol_range * 1000000  # Simulate volume
                volumes.append(simulated_volume)
            
            avg_volume = sum(volumes) / len(volumes)
            recent_volume = sum(volumes[-5:]) / 5
            volume_trend = (recent_volume - avg_volume) / avg_volume
            
            # Combine signals
            sentiment_score = (momentum * 0.6) + (volume_trend * 0.4)
            
            if sentiment_score > 0.02:
                sentiment = 'bullish'
                strength = min(abs(sentiment_score) * 10, 1.0)
            elif sentiment_score < -0.02:
                sentiment = 'bearish'
                strength = min(abs(sentiment_score) * 10, 1.0)
            else:
                sentiment = 'neutral'
                strength = 0.5
            
            self.market_sentiment[symbol] = {
                'sentiment': sentiment,
                'strength': strength,
                'momentum': momentum,
                'volume_trend': volume_trend,
                'timestamp': datetime.now()
            }
            
            return self.market_sentiment[symbol]
            
        except Exception as e:
            self.log(f"❌ Sentiment analysis error for {symbol}: {e}")
            return {'sentiment': 'neutral', 'strength': 0.5}
    
    def calculate_position_size(self, symbol, signal_strength, atr):
        """Advanced position sizing with risk management"""
        try:
            # Base position size on account balance and risk percentage
            account_balance = self.current_balance
            
            # Adjust risk based on signal strength and market conditions
            base_risk = self.base_risk_percentage
            risk_multiplier = signal_strength  # Higher confidence = larger position
            
            # Reduce risk during high volatility
            if atr > 0.002:  # High volatility threshold
                risk_multiplier *= 0.7
            
            # Reduce risk after consecutive losses
            if self.consecutive_losses > 2:
                risk_multiplier *= (0.8 ** (self.consecutive_losses - 2))
            
            # Calculate position size
            risk_amount = account_balance * base_risk * risk_multiplier
            
            # Use ATR for stop loss calculation
            stop_loss_pips = atr * 2  # 2x ATR stop loss
            
            if symbol.endswith('JPY'):
                pip_value = 1000 / stop_loss_pips  # Approximate for JPY pairs
            else:
                pip_value = 10000 / stop_loss_pips  # Approximate for major pairs
            
            position_size = int((risk_amount / stop_loss_pips) * pip_value)
            
            # Minimum and maximum position sizes
            pair_info = self.currency_pairs.get(symbol, {})
            base_volume = pair_info.get('base_volume', 10000)
            
            position_size = max(1000, min(position_size, base_volume * 3))
            
            # Additional safety checks
            max_position = account_balance * self.max_risk_per_trade * 10000
            position_size = min(position_size, int(max_position))
            
            return position_size
            
        except Exception as e:
            self.log(f"❌ Position sizing error: {e}")
            return 1000  # Safe default
    
    def advanced_market_analysis(self, symbol):
        """Ultra-advanced market analysis with multiple strategies"""
        try:
            # Get enhanced price data
            price_data = self.get_enhanced_price_data(symbol)
            if not price_data:
                return self.create_hold_signal(symbol)
            
            # Update price history
            self.update_price_history(symbol, price_data)
            
            current_price = price_data['close']
            
            # Calculate all indicators
            rsi = self.calculate_advanced_rsi(symbol)
            macd = self.calculate_macd(symbol)
            bollinger = self.calculate_bollinger_bands(symbol)
            stochastic = self.calculate_stochastic(symbol)
            atr = self.calculate_atr(symbol)
            
            # Enhanced moving averages
            if len(self.price_history[symbol]) >= 50:
                prices = [p['close'] for p in self.price_history[symbol]]
                ema_12 = self.calculate_ema(prices, 12)
                ema_26 = self.calculate_ema(prices, 26)
                sma_50 = sum(prices[-50:]) / 50
                sma_200 = sum(prices[-200:]) / 200 if len(prices) >= 200 else sma_50
            else:
                ema_12 = ema_26 = sma_50 = sma_200 = current_price
            
            # Market context
            session = self.detect_market_session_enhanced()
            sentiment = self.advanced_sentiment_analysis(symbol)
            
            # Advanced signal generation
            signals = []
            confidence = 0.0
            reasons = []
            
            # === MULTI-STRATEGY ANALYSIS ===
            
            # 1. RSI Strategy (Mean Reversion)
            if rsi < 20:
                signals.append('BUY')
                confidence += 0.4
                reasons.append(f"Extremely oversold RSI ({rsi:.1f})")
            elif rsi < 30:
                signals.append('BUY')
                confidence += 0.2
                reasons.append(f"Oversold RSI ({rsi:.1f})")
            elif rsi > 80:
                signals.append('SELL')
                confidence += 0.4
                reasons.append(f"Extremely overbought RSI ({rsi:.1f})")
            elif rsi > 70:
                signals.append('SELL')
                confidence += 0.2
                reasons.append(f"Overbought RSI ({rsi:.1f})")
            
            # 2. MACD Strategy (Trend Following)
            if macd['line'] > macd['signal'] and macd['histogram'] > 0:
                signals.append('BUY')
                confidence += 0.25
                reasons.append("MACD bullish crossover")
            elif macd['line'] < macd['signal'] and macd['histogram'] < 0:
                signals.append('SELL')
                confidence += 0.25
                reasons.append("MACD bearish crossover")
            
            # 3. Bollinger Bands Strategy
            bb_position = (current_price - bollinger['lower']) / (bollinger['upper'] - bollinger['lower'])
            if bb_position < 0.1:
                signals.append('BUY')
                confidence += 0.2
                reasons.append("Price near lower Bollinger Band")
            elif bb_position > 0.9:
                signals.append('SELL')
                confidence += 0.2
                reasons.append("Price near upper Bollinger Band")
            
            # 4. Moving Average Strategy
            if current_price > ema_12 > ema_26 > sma_50:
                signals.append('BUY')
                confidence += 0.3
                reasons.append("Strong bullish MA alignment")
            elif current_price < ema_12 < ema_26 < sma_50:
                signals.append('SELL')
                confidence += 0.3
                reasons.append("Strong bearish MA alignment")
            elif current_price > ema_12 > ema_26:
                signals.append('BUY')
                confidence += 0.15
                reasons.append("Bullish short-term MA")
            elif current_price < ema_12 < ema_26:
                signals.append('SELL')
                confidence += 0.15
                reasons.append("Bearish short-term MA")
            
            # 5. Stochastic Strategy
            if stochastic['k'] < 20 and stochastic['d'] < 20:
                signals.append('BUY')
                confidence += 0.15
                reasons.append(f"Stochastic oversold ({stochastic['k']:.1f})")
            elif stochastic['k'] > 80 and stochastic['d'] > 80:
                signals.append('SELL')
                confidence += 0.15
                reasons.append(f"Stochastic overbought ({stochastic['k']:.1f})")
            
            # 6. Market Sentiment Integration
            if sentiment['sentiment'] == 'bullish' and sentiment['strength'] > 0.7:
                signals.append('BUY')
                confidence += 0.2
                reasons.append("Strong bullish market sentiment")
            elif sentiment['sentiment'] == 'bearish' and sentiment['strength'] > 0.7:
                signals.append('SELL')
                confidence += 0.2
                reasons.append("Strong bearish market sentiment")
            
            # 7. Session-based adjustments
            session_multipliers = {
                'london_ny_overlap': 1.4,  # Highest confidence during overlap
                'london_opening': 1.2,
                'overlap_opening': 1.3,
                'london': 1.1,
                'ny_closing': 1.0,
                'asian_opening': 0.9,
                'asian': 0.7,
                'quiet': 0.5
            }
            confidence *= session_multipliers.get(session, 1.0)
            
            # 8. Volatility adjustment
            if atr > 0.003:  # Very high volatility
                confidence *= 0.8
                reasons.append("High volatility adjustment")
            elif atr < 0.001:  # Low volatility
                confidence *= 0.9
                reasons.append("Low volatility adjustment")
            
            # === FINAL DECISION LOGIC ===
            buy_signals = signals.count('BUY')
            sell_signals = signals.count('SELL')
            total_signals = len(signals)
            
            # Require minimum confluence
            min_signals = 3
            
            if buy_signals >= min_signals and buy_signals > sell_signals:
                action = 'BUY'
                confluence = buy_signals / total_signals if total_signals > 0 else 0
                confidence *= confluence
            elif sell_signals >= min_signals and sell_signals > buy_signals:
                action = 'SELL'
                confluence = sell_signals / total_signals if total_signals > 0 else 0
                confidence *= confluence
            else:
                action = 'HOLD'
                confidence = min(confidence, 0.5)
                reasons.append("Insufficient signal confluence")
            
            # Risk management override
            if self.consecutive_losses >= self.max_consecutive_losses:
                action = 'HOLD'
                confidence = 0
                reasons = [f"Risk management: {self.consecutive_losses} consecutive losses"]
            
            # Daily loss limit check
            if self.daily_profit < -self.current_balance * self.daily_loss_limit:
                action = 'HOLD'
                confidence = 0
                reasons = ["Daily loss limit reached"]
            
            # Position size calculation
            position_size = self.calculate_position_size(symbol, confidence, atr)
            
            # Create enhanced signal
            signal = {
                'symbol': symbol,
                'action': action,
                'confidence': min(confidence, 0.98),  # Cap at 98%
                'position_size': position_size,
                'price': current_price,
                'bid': price_data['bid'],
                'ask': price_data['ask'],
                'spread': price_data['spread'],
                
                # Technical indicators
                'rsi': rsi,
                'macd': macd,
                'bollinger': bollinger,
                'stochastic': stochastic,
                'atr': atr,
                'ema_12': ema_12,
                'ema_26': ema_26,
                'sma_50': sma_50,
                
                # Market context
                'session': session,
                'sentiment': sentiment,
                'volatility': 'high' if atr > 0.002 else 'medium' if atr > 0.001 else 'low',
                
                # Signal details
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'total_signals': total_signals,
                'reasons': reasons,
                'confluence': confluence if action != 'HOLD' else 0,
                
                # Risk management
                'stop_loss': atr * 2,
                'take_profit': atr * 3,
                
                'timestamp': datetime.now().isoformat()
            }
            
            self.current_signals[symbol] = signal
            return signal
            
        except Exception as e:
            self.log(f"❌ Advanced analysis error for {symbol}: {e}")
            return self.create_hold_signal(symbol)
    
    def create_hold_signal(self, symbol):
        """Create a HOLD signal with current market data"""
        try:
            price_data = self.get_enhanced_price_data(symbol)
            return {
                'symbol': symbol,
                'action': 'HOLD',
                'confidence': 0.0,
                'position_size': 1000,
                'price': price_data['close'],
                'bid': price_data['bid'],
                'ask': price_data['ask'],
                'spread': price_data['spread'],
                'rsi': 50,
                'session': self.detect_market_session_enhanced(),
                'reasons': ['Analysis unavailable or insufficient signals'],
                'timestamp': datetime.now().isoformat()
            }
        except:
            return {
                'symbol': symbol, 'action': 'HOLD', 'confidence': 0.0,
                'price': 1.0, 'reasons': ['Error in analysis'], 'timestamp': datetime.now().isoformat()
            }
    
    def execute_enhanced_trade(self, signal):
        """Execute trade with advanced order management"""
        try:
            symbol = signal['symbol']
            action = signal['action']
            volume = signal.get('position_size', 1000)
            price = signal['price']
            
            self.log(f"🚀 EXECUTING: {action} {symbol} | Size: {volume} | Confidence: {signal['confidence']:.1%}")
            self.log(f"   💡 Confluence: {signal.get('buy_signals', 0)} BUY, {signal.get('sell_signals', 0)} SELL")
            self.log(f"   📊 RSI: {signal['rsi']:.1f} | ATR: {signal.get('atr', 0):.5f}")
            
            # Enhanced trade execution
            if self.account_verified and not self.demo_mode:
                success = self.execute_ctrader_order(symbol, action, volume, signal)
            else:
                # Enhanced simulation with more realistic outcomes
                confidence = signal['confidence']
                session = signal.get('session', 'unknown')
                
                # Session-based success rates
                session_success_rates = {
                    'london_ny_overlap': 0.85,
                    'london_opening': 0.80,
                    'london': 0.75,
                    'ny_closing': 0.70,
                    'asian': 0.60,
                    'quiet': 0.50
                }
                
                base_success_rate = session_success_rates.get(session, 0.70)
                confidence_bonus = confidence * 0.2
                final_success_rate = min(base_success_rate + confidence_bonus, 0.95)
                
                success = random.random() < final_success_rate
            
            # Enhanced profit calculation
            estimated_profit = 0
            if success:
                # More sophisticated P&L calculation
                atr = signal.get('atr', 0.001)
                volatility = signal.get('volatility', 'medium')
                
                # Profit range based on volatility and market conditions
                if volatility == 'high':
                    profit_range = (-atr * 1.5, atr * 4)
                elif volatility == 'low':
                    profit_range = (-atr * 0.5, atr * 2)
                else:
                    profit_range = (-atr * 1, atr * 3)
                
                # Random profit within realistic range
                profit_multiplier = random.uniform(*profit_range)
                estimated_profit = (volume / 10000) * profit_multiplier * 100000
                
                if action == 'SELL':
                    estimated_profit *= -1
                
                # Apply slippage and spread costs
                spread_cost = signal.get('spread', 0.0002) * (volume / 10000) * 100000
                estimated_profit -= spread_cost
                
                self.total_profit += estimated_profit
                self.daily_profit += estimated_profit
                self.current_balance += estimated_profit
                
                # Update peak balance and drawdown
                if self.current_balance > self.peak_balance:
                    self.peak_balance = self.current_balance
                
                drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
                self.max_drawdown = max(self.max_drawdown, drawdown)
            
            # Record enhanced trade
            trade_record = {
                'timestamp': datetime.now().isoformat(),
                'time': datetime.now().strftime("%H:%M:%S"),
                'date': datetime.now().strftime("%Y-%m-%d"),
                'symbol': symbol,
                'action': action,
                'volume': volume,
                'price': price,
                'bid': signal.get('bid', price),
                'ask': signal.get('ask', price),
                'spread': signal.get('spread', 0),
                'confidence': signal['confidence'],
                'success': success,
                'estimated_profit': estimated_profit,
                'running_balance': self.current_balance,
                
                # Technical data
                'rsi': signal.get('rsi', 50),
                'atr': signal.get('atr', 0),
                'session': signal.get('session', 'unknown'),
                'volatility': signal.get('volatility', 'unknown'),
                'sentiment': signal.get('sentiment', {}),
                
                # Signal analysis
                'buy_signals': signal.get('buy_signals', 0),
                'sell_signals': signal.get('sell_signals', 0),
                'confluence': signal.get('confluence', 0),
                'reasons': signal.get('reasons', []),
                
                # Risk management
                'stop_loss': signal.get('stop_loss', 0),
                'take_profit': signal.get('take_profit', 0)
            }
            
            self.trade_history.append(trade_record)
            
            # Update counters
            self.daily_trades += 1
            self.total_trades += 1
            
            if success:
                self.successful_trades += 1
                self.consecutive_losses = 0
                profit_emoji = "💚" if estimated_profit > 0 else "💛"
                self.log(f"✅ TRADE SUCCESS: {action} {symbol} @ {price:.5f} | "
                        f"{profit_emoji} P&L: {estimated_profit:+.2f}")
            else:
                self.consecutive_losses += 1
                self.log(f"⚠️ TRADE FAILED: {action} {symbol}")
                self.log(f"   📊 Consecutive losses: {self.consecutive_losses}")
            
            return success
            
        except Exception as e:
            self.log(f"❌ Enhanced trade execution error: {e}")
            return False
    
    def execute_ctrader_order(self, symbol, action, volume, signal):
        """Execute real order on cTrader with advanced features"""
        try:
            # Use correct API endpoint
            if self.demo_mode:
                api_base = "https://demo-openapi.ctrader.com"
            else:
                api_base = "https://openapi.ctrader.com"
            
            url = f"{api_base}/v2/trade"
            
            # Calculate stop loss and take profit
            atr = signal.get('atr', 0.001)
            current_price = signal['price']
            
            if action == 'BUY':
                stop_loss = current_price - (atr * 2)
                take_profit = current_price + (atr * 3)
            else:
                stop_loss = current_price + (atr * 2)
                take_profit = current_price - (atr * 3)
            
            order_data = {
                "accountId": self.account_id,
                "symbolName": symbol,
                "tradeSide": action.upper(),
                "volume": volume,
                "orderType": "MARKET",
                "stopLossInPips": abs(current_price - stop_loss) * 10000,
                "takeProfitInPips": abs(take_profit - current_price) * 10000,
                "comment": f"EnhancedBot-{signal['confidence']:.0%}"
            }
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'User-Agent': 'EnhancedBot/3.0'
            }
            
            data = json.dumps(order_data).encode('utf-8')
            request = urllib.request.Request(url, data=data, headers=headers, method='POST')
            
            with urllib.request.urlopen(request, timeout=15) as response:
                if response.status in [200, 201, 202]:
                    response_data = json.loads(response.read().decode())
                    order_id = response_data.get('orderId', 'Unknown')
                    self.log(f"📝 Order executed - ID: {order_id}")
                    return True
                else:
                    self.log(f"❌ Order failed - HTTP {response.status}")
                    return False
        
        except Exception as e:
            self.log(f"❌ API order error: {e}")
            return False
    
    def reset_daily_counters(self):
        """Reset daily counters and apply daily risk management"""
        current_date = datetime.now().date()
        if current_date != self.last_trade_date:
            # Log daily performance
            if self.last_trade_date:
                self.log(f"📈 Daily Summary ({self.last_trade_date}):")
                self.log(f"   🔢 Trades: {self.daily_trades}")
                self.log(f"   💰 Daily P&L: {self.daily_profit:+.2f}")
                self.log(f"   💼 Balance: {self.current_balance:.2f}")
                self.log(f"   📉 Max Drawdown: {self.max_drawdown:.1%}")
            
            # Reset daily counters
            self.daily_trades = 0
            self.daily_profit = 0.0
            self.last_trade_date = current_date
            
            # Reset consecutive losses if it's a new day
            if self.consecutive_losses > 0:
                self.log(f"🌅 New day - resetting consecutive losses ({self.consecutive_losses})")
                self.consecutive_losses = 0
            
            self.log(f"🌅 New trading day: {current_date}")
    
    def get_enhanced_stats(self):
        """Get comprehensive enhanced statistics"""
        runtime = datetime.now() - self.start_time
        success_rate = (self.successful_trades / max(self.total_trades, 1)) * 100
        
        # Calculate additional metrics
        profit_factor = 0
        if self.total_trades > 0:
            winning_trades = [t for t in self.trade_history if t['success'] and t.get('estimated_profit', 0) > 0]
            losing_trades = [t for t in self.trade_history if t['success'] and t.get('estimated_profit', 0) <= 0]
            
            total_wins = sum(t.get('estimated_profit', 0) for t in winning_trades)
            total_losses = abs(sum(t.get('estimated_profit', 0) for t in losing_trades))
            
            profit_factor = total_wins / max(total_losses, 1)
        
        # Calculate Sharpe ratio (simplified)
        if len(self.trade_history) > 10:
            profits = [t.get('estimated_profit', 0) for t in self.trade_history if t['success']]
            if profits:
                avg_profit = statistics.mean(profits)
                std_profit = statistics.stdev(profits) if len(profits) > 1 else 1
                sharpe_ratio = avg_profit / max(std_profit, 0.01)
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0
        
        return {
            'active': self.running,
            'account_verified': self.account_verified,
            'account_info': self.account_info,
            'demo_mode': self.demo_mode,
            
            # Trading metrics
            'daily_trades': self.daily_trades,
            'max_daily_trades': self.max_daily_trades,
            'total_trades': self.total_trades,
            'successful_trades': self.successful_trades,
            'success_rate': success_rate,
            'consecutive_losses': self.consecutive_losses,
            
            # Financial metrics
            'current_balance': self.current_balance,
            'total_profit': self.total_profit,
            'daily_profit': self.daily_profit,
            'max_drawdown': self.max_drawdown,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            
            # Market data
            'runtime': str(runtime).split('.')[0],
            'current_session': self.detect_market_session_enhanced(),
            'trading_pairs': len(self.currency_pairs),
            'active_signals': len([s for s in self.current_signals.values() if s['action'] != 'HOLD']),
            
            # Risk management
            'daily_loss_limit': self.daily_loss_limit,
            'max_risk_per_trade': self.max_risk_per_trade,
            'base_risk_percentage': self.base_risk_percentage,
            
            # Logs
            'recent_logs': self.logs[-100:]
        }
    
    def get_recent_trades(self):
        """Get recent trades with enhanced data"""
        return self.trade_history[-50:]
    
    def get_current_signals(self):
        """Get current signals sorted by confidence"""
        signals = list(self.current_signals.values())
        return sorted(signals, key=lambda x: x['confidence'], reverse=True)
    
    def trading_cycle_enhanced(self):
        """Enhanced main trading cycle with advanced logic"""
        try:
            self.reset_daily_counters()
            
            # Check daily limits
            if self.daily_trades >= self.max_daily_trades:
                self.log(f"📊 Daily trade limit reached: {self.daily_trades}/{self.max_daily_trades}")
                return
            
            # Check daily loss limit
            if self.daily_profit < -self.current_balance * self.daily_loss_limit:
                self.log(f"🛑 Daily loss limit hit: {self.daily_profit:.2f} ({self.daily_loss_limit:.1%})")
                return
            
            # Check consecutive losses
            if self.consecutive_losses >= self.max_consecutive_losses:
                self.log(f"⏸️ Max consecutive losses reached: {self.consecutive_losses}")
                return
            
            session = self.detect_market_session_enhanced()
            self.log(f"🧠 Enhanced AI analysis cycle ({session} session)...")
            
            # Analyze all pairs
            analyzed_signals = []
            
            for symbol in self.currency_pairs:
                try:
                    self.log(f"🔍 Deep analysis: {symbol}...")
                    
                    signal = self.advanced_market_analysis(symbol)
                    analyzed_signals.append(signal)
                    
                    # Enhanced logging
                    confidence_emoji = "🔥" if signal['confidence'] > 0.85 else "⚡" if signal['confidence'] > 0.75 else "📊"
                    action_emoji = "🟢" if signal['action'] == 'BUY' else "🔴" if signal['action'] == 'SELL' else "⚪"
                    
                    self.log(f"{confidence_emoji} {action_emoji} {symbol}: {signal['action']} "
                           f"(Conf: {signal['confidence']:.1%}, RSI: {signal.get('rsi', 0):.1f}, "
                           f"Signals: {signal.get('buy_signals', 0)}B/{signal.get('sell_signals', 0)}S)")
                    
                    # Show top reasons
                    if signal.get('reasons'):
                        top_reasons = signal['reasons'][:2]
                        self.log(f"   💡 {' | '.join(top_reasons)}")
                
                except Exception as e:
                    self.log(f"❌ Error analyzing {symbol}: {e}")
                
                time.sleep(1)  # Small delay between analyses
            
            # Sort signals by confidence and execute best ones
            tradeable_signals = [s for s in analyzed_signals if s['action'] in ['BUY', 'SELL'] and s['confidence'] >= 0.80]
            tradeable_signals.sort(key=lambda x: x['confidence'], reverse=True)
            
            if tradeable_signals:
                self.log(f"🎯 Found {len(tradeable_signals)} high-confidence signals")
                
                # Execute top signals (up to 3 per cycle)
                executed = 0
                max_executions = min(3, self.max_daily_trades - self.daily_trades)
                
                for signal in tradeable_signals[:max_executions]:
                    if self.daily_trades >= self.max_daily_trades:
                        break
                    
                    self.log(f"🚀 Executing #{executed + 1}: {signal['symbol']} {signal['action']}")
                    
                    if self.execute_enhanced_trade(signal):
                        executed += 1
                        time.sleep(10)  # Wait between executions
                    
                    if self.consecutive_losses >= self.max_consecutive_losses:
                        self.log("⏸️ Stopping due to consecutive losses")
                        break
                
                self.log(f"✅ Executed {executed} trades this cycle")
            else:
                self.log("📋 No high-confidence signals found")
            
        except Exception as e:
            self.log(f"❌ Enhanced trading cycle error: {e}")
    
    def run_enhanced_bot(self):
        """Main enhanced bot execution with advanced monitoring"""
        self.log("🚀 Starting Enhanced World-Class Trading Engine")
        self.log("⚠️ Remember: Past performance does not guarantee future results")
        
        cycle = 0
        last_balance_log = time.time()
        
        while self.running:
            try:
                cycle += 1
                cycle_start = time.time()
                
                self.log(f"🔄 Enhanced Trading Cycle #{cycle}")
                
                # Execute enhanced trading cycle
                self.trading_cycle_enhanced()
                
                # Detailed status update
                stats = self.get_enhanced_stats()
                
                # Balance update every 10 minutes
                if time.time() - last_balance_log > 600:
                    self.log(f"💼 Balance Update: {stats['current_balance']:.2f} "
                           f"(P&L: {stats['total_profit']:+.2f}, Daily: {stats['daily_profit']:+.2f})")
                    last_balance_log = time.time()
                
                # Cycle summary
                self.log(f"💓 Status: {stats['daily_trades']}/{stats['max_daily_trades']} trades | "
                        f"Success: {stats['success_rate']:.1f}% | "
                        f"Session: {stats['current_session']} | "
                        f"Active signals: {stats['active_signals']}")
                
                if stats['consecutive_losses'] > 0:
                    self.log(f"⚠️ Consecutive losses: {stats['consecutive_losses']}")
                
                # Performance metrics
                if cycle % 5 == 0:  # Every 5 cycles
                    self.log(f"📊 Performance: PF: {stats['profit_factor']:.2f} | "
                           f"Drawdown: {stats['max_drawdown']:.1%} | "
                           f"Sharpe: {stats['sharpe_ratio']:.2f}")
                
                # Calculate next cycle time (adaptive)
                cycle_time = time.time() - cycle_start
                
                # Adaptive wait time based on session
                session = stats['current_session']
                if session in ['london_ny_overlap', 'london_opening']:
                    wait_time = 180  # 3 minutes during high activity
                elif session in ['london', 'ny_closing']:
                    wait_time = 300  # 5 minutes during medium activity
                else:
                    wait_time = 600  # 10 minutes during low activity
                
                self.log(f"⏰ Next enhanced analysis in {wait_time//60} minutes...")
                time.sleep(wait_time)
                
            except Exception as e:
                self.log(f"❌ Enhanced bot error: {e}")
                time.sleep(120)  # Wait 2 minutes on error

# Global bot instance
enhanced_bot = None

class EnhancedDashboardHandler(BaseHTTPRequestHandler):
    """Enhanced dashboard handler with advanced metrics"""
    
    def do_GET(self):
        """Handle HTTP requests"""
        try:
            if self.path == '/' or self.path == '/dashboard':
                html = self.get_enhanced_dashboard()
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
                
            elif self.path == '/api/stats':
                stats = enhanced_bot.get_enhanced_stats() if enhanced_bot else {}
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(stats).encode())
                
            elif self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                health_data = {
                    'status': 'healthy',
                    'bot_active': enhanced_bot.running if enhanced_bot else False,
                    'account_verified': enhanced_bot.account_verified if enhanced_bot else False,
                    'version': 'enhanced-3.0',
                    'features': ['advanced_analysis', 'risk_management', 'multi_strategy']
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
    
    def get_enhanced_dashboard(self):
        """Generate enhanced dashboard with advanced metrics"""
        if not enhanced_bot:
            return "<h1>Enhanced Bot not initialized</h1>"
        
        try:
            stats = enhanced_bot.get_enhanced_stats()
            trades = enhanced_bot.get_recent_trades()
            signals = enhanced_bot.get_current_signals()
            account_info = stats.get('account_info', {})
            
            # Account status
            if stats['account_verified']:
                account_status = f"""
                <div style="background: linear-gradient(45deg, #28a745, #20c997); padding: 20px; border-radius: 15px; margin-bottom: 20px; text-align: center;">
                    <div style="font-size: 1.3em; font-weight: bold; margin-bottom: 15px;">✅ LIVE ACCOUNT CONNECTED</div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; font-size: 0.95em;">
                        <div><strong>Account:</strong> {account_info.get('account_id', 'Unknown')}</div>
                        <div><strong>Broker:</strong> {account_info.get('broker', 'Unknown')}</div>
                        <div><strong>Balance:</strong> {stats['current_balance']:.2f} {account_info.get('currency', 'USD')}</div>
                        <div><strong>Equity:</strong> {account_info.get('equity', stats['current_balance']):.2f} {account_info.get('currency', 'USD')}</div>
                        <div><strong>Type:</strong> {account_info.get('account_type', 'Unknown')}</div>
                        <div><strong>P&L:</strong> <span style="color: {'#00ff00' if stats['total_profit'] >= 0 else '#ff4444'};">{stats['total_profit']:+.2f}</span></div>
                    </div>
                </div>
                """
            else:
                account_status = f"""
                <div style="background: linear-gradient(45deg, #ffc107, #fd7e14); padding: 20px; border-radius: 15px; margin-bottom: 20px; color: #000; text-align: center;">
                    <div style="font-size: 1.3em; font-weight: bold; margin-bottom: 15px;">⚠️ SIMULATION MODE</div>
                    <div style="margin-bottom: 10px;">Enhanced simulation with realistic market conditions</div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; font-size: 0.9em;">
                        <div><strong>Balance:</strong> {stats['current_balance']:.2f} USD</div>
                        <div><strong>P&L:</strong> <span style="color: {'green' if stats['total_profit'] >= 0 else 'red'};">{stats['total_profit']:+.2f}</span></div>
                        <div><strong>Drawdown:</strong> {stats['max_drawdown']:.1%}</div>
                    </div>
                    <div style="margin-top: 10px; font-size: 0.85em;">Set CTRADER_ACCESS_TOKEN for live trading</div>
                </div>
                """
            
            # Performance color coding
            success_color = '#28a745' if stats['success_rate'] > 60 else '#ffc107' if stats['success_rate'] > 45 else '#dc3545'
            profit_color = '#28a745' if stats['total_profit'] > 0 else '#dc3545'
            
            html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏆 Enhanced World-Class cTrader Bot</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #334155 50%, #475569 75%, #64748b 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
            animation: backgroundShift 60s ease-in-out infinite;
        }}
        
        @keyframes backgroundShift {{
            0%, 100% {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #334155 50%, #475569 75%, #64748b 100%); }}
            50% {{ background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 25%, #4338ca 50%, #5b21b6 75%, #7c3aed 100%); }}
        }}
        
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ 
            text-align: center; 
            margin-bottom: 30px;
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 20px;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .header h1 {{ 
            font-size: 2.8em; 
            margin-bottom: 15px;
            background: linear-gradient(45deg, #ffd700, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: pulse 3s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
        }}
        .version {{ 
            background: rgba(255,255,255,0.2); 
            padding: 8px 15px; 
            border-radius: 20px; 
            display: inline-block; 
            font-size: 0.9em;
            margin-top: 10px;
        }}
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); 
            gap: 25px; 
            margin-bottom: 30px; 
        }}
        .card {{ 
            background: rgba(255,255,255,0.1); 
            padding: 25px; 
            border-radius: 20px; 
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }}
        .card:hover {{ transform: translateY(-5px); }}
        .card h3 {{ 
            margin-bottom: 20px; 
            color: #4ecdc4;
            font-size: 1.4em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .metric {{ 
            display: flex; 
            justify-content: space-between; 
            margin: 15px 0; 
            padding: 12px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .metric-value {{ 
            font-weight: bold; 
            font-size: 1.1em;
        }}
        .signals {{ display: grid; gap: 15px; }}
        .signal {{ 
            padding: 18px; 
            border-radius: 12px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            transition: all 0.3s ease;
        }}
        .signal:hover {{ transform: scale(1.02); }}
        .signal.buy {{ background: linear-gradient(45deg, #28a745, #20c997); }}
        .signal.sell {{ background: linear-gradient(45deg, #dc3545, #fd7e14); }}
        .signal.hold {{ background: linear-gradient(45deg, #6c757d, #adb5bd); }}
        .signal-info {{ flex: 1; }}
        .signal-confidence {{ 
            font-size: 1.3em; 
            font-weight: bold; 
            min-width: 60px; 
            text-align: center;
        }}
        .logs {{ 
            background: rgba(0,0,0,0.5); 
            padding: 20px; 
            border-radius: 15px; 
            font-family: 'Courier New', monospace; 
            font-size: 0.9em;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .refresh {{ 
            position: fixed; 
            top: 20px; 
            right: 20px; 
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4); 
            color: white; 
            border: none; 
            padding: 15px 25px; 
            border-radius: 30px; 
            cursor: pointer; 
            font-weight: bold;
            font-size: 1em;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }}
        .refresh:hover {{ transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.4); }}
        .trades-grid {{ 
            display: grid; 
            gap: 10px; 
            max-height: 300px; 
            overflow-y: auto; 
        }}
        .trade-item {{ 
            background: rgba(255,255,255,0.05); 
            padding: 12px; 
            border-radius: 8px; 
            font-size: 0.9em;
            border-left: 4px solid;
        }}
        .trade-item.success {{ border-left-color: #28a745; }}
        .trade-item.failed {{ border-left-color: #dc3545; }}
        .performance-indicator {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }}
        .status-active {{ background-color: #28a745; }}
        .status-warning {{ background-color: #ffc107; }}
        .status-error {{ background-color: #dc3545; }}
    </style>
    <script>
        setTimeout(() => location.reload(), 45000);
        function refresh() {{ location.reload(); }}
        
        // Add some dynamic effects
        document.addEventListener('DOMContentLoaded', function() {{
            const cards = document.querySelectorAll('.card');
            cards.forEach((card, index) => {{
                card.style.animationDelay = (index * 0.1) + 's';
                card.style.animation = 'fadeInUp 0.6s ease forwards';
            }});
        }});
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏆 Enhanced World-Class cTrader Bot</h1>
            <div class="version">
                <span class="status-indicator {'status-active' if stats['active'] else 'status-error'}"></span>
                Enhanced v3.0 • Last Updated: {datetime.now().strftime('%H:%M:%S UTC')}
            </div>
            <p style="margin-top: 15px; opacity: 0.9;">Advanced AI Trading with Multi-Strategy Analysis & Risk Management</p>
        </div>
        
        <button class="refresh" onclick="refresh()">🔄 Refresh</button>
        
        {account_status}
        
        <div class="grid">
            <div class="card">
                <h3>💰 Performance Metrics</h3>
                <div class="metric">
                    <span>Account Status:</span>
                    <span class="metric-value" style="color: {'#28a745' if stats['account_verified'] else '#ffc107'};">
                        {'✅ VERIFIED' if stats['account_verified'] else '⚠️ SIMULATION'}
                    </span>
                </div>
                <div class="metric">
                    <span>Trading Mode:</span>
                    <span class="metric-value" style="color: {'#dc3545' if not stats['demo_mode'] else '#ffc107'};">
                        {'🔥 LIVE' if not stats['demo_mode'] else '🧪 DEMO'}
                    </span>
                </div>
                <div class="metric">
                    <span>Today's Trades:</span>
                    <span class="metric-value">{stats['daily_trades']}/{stats['max_daily_trades']}</span>
                </div>
                <div class="metric">
                    <span>Success Rate:</span>
                    <span class="metric-value" style="color: {success_color};">{stats['success_rate']:.1f}%</span>
                </div>
                <div class="metric">
                    <span>Total P&L:</span>
                    <span class="metric-value" style="color: {profit_color};">{stats['total_profit']:+.2f}</span>
                </div>
                <div class="metric">
                    <span>Daily P&L:</span>
                    <span class="metric-value" style="color: {'#28a745' if stats['daily_profit'] >= 0 else '#dc3545'};">{stats['daily_profit']:+.2f}</span>
                </div>
            </div>
            
            <div class="card">
                <h3>📊 Advanced Analytics</h3>
                <div class="metric">
                    <span>Max Drawdown:</span>
                    <span class="metric-value" style="color: {'#28a745' if stats['max_drawdown'] < 0.05 else '#ffc107' if stats['max_drawdown'] < 0.1 else '#dc3545'};">{stats['max_drawdown']:.1%}</span>
                </div>
                <div class="metric">
                    <span>Profit Factor:</span>
                    <span class="metric-value" style="color: {'#28a745' if stats['profit_factor'] > 1.5 else '#ffc107' if stats['profit_factor'] > 1.0 else '#dc3545'};">{stats['profit_factor']:.2f}</span>
                </div>
                <div class="metric">
                    <span>Sharpe Ratio:</span>
                    <span class="metric-value" style="color: {'#28a745' if stats['sharpe_ratio'] > 1.0 else '#ffc107' if stats['sharpe_ratio'] > 0.5 else '#dc3545'};">{stats['sharpe_ratio']:.2f}</span>
                </div>
                <div class="metric">
                    <span>Consecutive Losses:</span>
                    <span class="metric-value" style="color: {'#28a745' if stats['consecutive_losses'] == 0 else '#ffc107' if stats['consecutive_losses'] < 3 else '#dc3545'};">{stats['consecutive_losses']}</span>
                </div>
                <div class="metric">
                    <span>Current Session:</span>
                    <span class="metric-value">{stats['current_session'].replace('_', ' ').title()}</span>
                </div>
                <div class="metric">
                    <span>Active Signals:</span>
                    <span class="metric-value">{stats['active_signals']}</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🎯 Live Signals</h3>
                <div class="signals">
"""
            
            # Enhanced signals display
            if signals:
                for signal in signals[:5]:  # Top 5 signals
                    signal_class = signal['action'].lower()
                    confidence_text = f"{signal['confidence']:.0%}"
                    
                    # Additional signal info
                    rsi_status = "🔥" if signal.get('rsi', 50) > 70 else "❄️" if signal.get('rsi', 50) < 30 else "📊"
                    session_emoji = "⚡" if 'overlap' in signal.get('session', '') else "🌅" if 'opening' in signal.get('session', '') else "📈"
                    
                    html += f'''
                    <div class="signal {signal_class}">
                        <div class="signal-info">
                            <div style="font-weight: bold; font-size: 1.1em;">{signal['symbol']} {signal['action']}</div>
                            <div style="font-size: 0.9em; opacity: 0.9;">
                                @ {signal['price']:.5f} | RSI: {signal.get('rsi', 50):.1f} {rsi_status} | {session_emoji} {signal.get('session', 'unknown').replace('_', ' ').title()}
                            </div>
                            <div style="font-size: 0.8em; margin-top: 5px;">
                                Signals: {signal.get('buy_signals', 0)}B/{signal.get('sell_signals', 0)}S | Vol: {signal.get('volatility', 'medium').title()}
                            </div>
                        </div>
                        <div class="signal-confidence">{confidence_text}</div>
                    </div>
'''
            else:
                html += '''
                    <div class="signal hold">
                        <div class="signal-info">
                            <div style="font-weight: bold;">🔍 Deep Market Analysis</div>
                            <div style="font-size: 0.9em;">Advanced AI scanning {len(enhanced_bot.currency_pairs)} pairs...</div>
                        </div>
                        <div class="signal-confidence">⏳</div>
                    </div>
'''
            
            html += '''
                </div>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 30px;">
'''
            
            # Recent trades
            html += '''
            <div class="card">
                <h3>📈 Recent Trades</h3>
                <div class="trades-grid">
'''
            
            if trades:
                for trade in trades[-10:]:
                    trade_class = 'success' if trade['success'] else 'failed'
                    action_emoji = "🟢" if trade['action'] == 'BUY' else "🔴"
                    profit_text = f"{trade.get('estimated_profit', 0):+.2f}" if trade['success'] else "Failed"
                    
                    html += f'''
                    <div class="trade-item {trade_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>{action_emoji} {trade['symbol']}</strong> @ {trade['price']:.5f}
                                <div style="font-size: 0.85em; opacity: 0.8;">{trade['time']} | Vol: {trade['volume']}</div>
                            </div>
                            <div style="font-weight: bold;">
                                {profit_text}
                            </div>
                        </div>
                    </div>
'''
            else:
                html += '<div style="text-align: center; opacity: 0.7;">No trades yet</div>'
            
            html += '''
                </div>
            </div>
'''
            
            # Risk management
            html += f'''
            <div class="card">
                <h3>🛡️ Risk Management</h3>
                <div class="metric">
                    <span>Daily Risk Limit:</span>
                    <span class="metric-value">{stats['daily_loss_limit']:.1%}</span>
                </div>
                <div class="metric">
                    <span>Max Risk/Trade:</span>
                    <span class="metric-value">{stats['max_risk_per_trade']:.1%}</span>
                </div>
                <div class="metric">
                    <span>Base Risk:</span>
                    <span class="metric-value">{stats['base_risk_percentage']:.1%}</span>
                </div>
                <div class="metric">
                    <span>Daily P&L vs Limit:</span>
                    <span class="metric-value" style="color: {'#28a745' if stats['daily_profit'] > -stats['current_balance'] * stats['daily_loss_limit'] * 0.5 else '#ffc107' if stats['daily_profit'] > -stats['current_balance'] * stats['daily_loss_limit'] * 0.8 else '#dc3545'};">
                        {(stats['daily_profit'] / (stats['current_balance'] * stats['daily_loss_limit'])) * 100:.1f}%
                    </span>
                </div>
                <div class="metric">
                    <span>Risk Status:</span>
                    <span class="metric-value" style="color: {'#28a745' if stats['consecutive_losses'] < 2 else '#ffc107' if stats['consecutive_losses'] < 4 else '#dc3545'};">
                        {'✅ SAFE' if stats['consecutive_losses'] < 2 else '⚠️ CAUTION' if stats['consecutive_losses'] < 4 else '🛑 HIGH RISK'}
                    </span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>📱 Live Activity Feed</h3>
            <div class="logs">
'''
            
            # Enhanced logs
            for log in stats['recent_logs'][-20:]:
                html += f'<div style="margin: 5px 0; padding: 5px; border-left: 3px solid #4ecdc4;">{log}</div>'
            
            html += '''
            </div>
        </div>
    </div>
</body>
</html>
'''
            return html
            
        except Exception as e:
            return f'<h1>Dashboard Error: {str(e)}</h1>'
    
    def log_message(self, format, *args):
        pass

def start_enhanced_server():
    """Start enhanced web server"""
    try:
        port = int(os.getenv('PORT', 10000))
        server = HTTPServer(('0.0.0.0', port), EnhancedDashboardHandler)
        
        enhanced_bot.log(f"🌐 Enhanced server starting on port {port}")
        
        def run_server():
            try:
                server.serve_forever()
            except Exception as e:
                enhanced_bot.log(f"Server error: {e}")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        enhanced_bot.log("✅ Enhanced dashboard live with advanced metrics!")
        
    except Exception as e:
        enhanced_bot.log(f"Server error: {e}")

def main():
    """Main function - Enhanced version with no input calls"""
    global enhanced_bot
    
    try:
        print("🏆 Starting Enhanced World-Class cTrader Bot")
        print("⚠️ RISK WARNING: Trading involves substantial risk of loss")
        print("📊 Features: Advanced AI, Multi-Strategy, Risk Management")
        
        # Create enhanced bot
        enhanced_bot = EnhancedTradingBot()
        
        # Start enhanced server
        start_enhanced_server()
        
        # Start enhanced trading
        enhanced_bot.run_enhanced_bot()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        if enhanced_bot:
            enhanced_bot.log(f"Fatal error: {e}")
        time.sleep(60)
        main()

if __name__ == "__main__":
    main()
