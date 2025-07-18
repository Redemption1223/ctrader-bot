# Railway-Compatible cTrader Bot (FIXED VERSION)
# This version works with Railway's build system

import asyncio
import json
import logging
import time
import os
import urllib.request
import urllib.parse
import ssl
from datetime import datetime

# Simple logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class SimplecTraderBot:
    """Simplified cTrader bot that works on Railway"""
    
    def __init__(self):
        # Your cTrader credentials from environment variables
        self.access_token = os.getenv('CTRADER_ACCESS_TOKEN', 'FZVyeFsxKkElJrvinCQxoTPSRu7ryZXd8Qn66szleKk')
        self.refresh_token = os.getenv('CTRADER_REFRESH_TOKEN', 'I4M1fXeHOkFfLUDeozkHiA-uEwlHm_k8ZjWij02BQX0')
        self.client_id = os.getenv('CTRADER_CLIENT_ID', '16128_1N2FGw1faESealOA')
        self.account_id = os.getenv('CTRADER_ACCOUNT_ID', '10618580')
        
        # Trading settings
        self.demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
        self.max_daily_trades = int(os.getenv('MAX_DAILY_TRADES', '3'))
        self.trading_symbols = os.getenv('TRADING_SYMBOLS', 'EURUSD,GBPUSD').split(',')
        
        # Bot state
        self.running = True
        self.daily_trades = 0
        self.last_trade_date = datetime.now().date()
        
        logger.info("🚀 Railway cTrader Bot Initialized")
        logger.info(f"📊 Mode: {'DEMO' if self.demo_mode else 'LIVE'}")
        logger.info(f"📈 Symbols: {', '.join(self.trading_symbols)}")
    
    async def start_bot(self):
        """Main bot loop - Railway keeps this running"""
        logger.info("🔥 Starting 24/7 Trading Bot on Railway")
        
        # Reset daily trades if new day
        self.reset_daily_counter()
        
        while self.running:
            try:
                # Main trading cycle
                await self.trading_cycle()
                
                # Wait 5 minutes between cycles
                logger.info("⏰ Waiting 5 minutes until next analysis...")
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"❌ Bot error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def reset_daily_counter(self):
        """Reset daily trade counter if new day"""
        current_date = datetime.now().date()
        if current_date != self.last_trade_date:
            self.daily_trades = 0
            self.last_trade_date = current_date
            logger.info("🔄 New day - reset trade counter")
    
    async def trading_cycle(self):
        """Single trading cycle"""
        try:
            self.reset_daily_counter()
            
            # Check daily trade limit
            if self.daily_trades >= self.max_daily_trades:
                logger.info(f"📊 Daily trade limit reached ({self.daily_trades}/{self.max_daily_trades})")
                return
            
            logger.info("🤖 Starting market analysis...")
            
            # Analyze each symbol
            for symbol in self.trading_symbols:
                try:
                    await self.analyze_and_trade(symbol)
                except Exception as e:
                    logger.error(f"❌ Error analyzing {symbol}: {e}")
            
        except Exception as e:
            logger.error(f"❌ Trading cycle error: {e}")
    
    async def analyze_and_trade(self, symbol):
        """Analyze symbol and potentially trade"""
        try:
            logger.info(f"📊 Analyzing {symbol}...")
            
            # Get market data using simple HTTP requests
            market_data = await self.get_market_data(symbol)
            
            if not market_data:
                logger.warning(f"⚠️ No market data for {symbol}")
                return
            
            # Simple AI analysis
            signal = self.ai_analyze(symbol, market_data)
            
            logger.info(f"🎯 {symbol}: {signal['action']} (confidence: {signal['confidence']:.1%})")
            
            # Execute trade if strong signal
            if signal['action'] in ['BUY', 'SELL'] and signal['confidence'] >= 0.75:
                await self.execute_trade(symbol, signal)
            else:
                logger.info(f"📋 {symbol}: Signal too weak or HOLD - no trade")
                
        except Exception as e:
            logger.error(f"❌ Analysis error for {symbol}: {e}")
    
    async def get_market_data(self, symbol):
        """Get market data using simple HTTP requests"""
        try:
            # Use a simple forex API or Yahoo Finance alternative
            # For Railway compatibility, we'll use a basic approach
            
            # Simulate market data (in real version, you'd call an API)
            import random
            
            # Generate realistic forex price data
            base_prices = {
                'EURUSD': 1.0850,
                'GBPUSD': 1.2650,
                'USDJPY': 148.50,
                'AUDUSD': 0.6750,
                'USDCAD': 1.3580
            }
            
            base_price = base_prices.get(symbol, 1.0000)
            
            # Add realistic variation
            current_price = base_price + random.uniform(-0.01, 0.01)
            
            # Generate price history (simplified)
            prices = []
            for i in range(20):
                price = current_price + random.uniform(-0.005, 0.005)
                prices.append(price)
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'prices': prices,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"❌ Market data error for {symbol}: {e}")
            return None
    
    def ai_analyze(self, symbol, market_data):
        """Simple AI analysis using price action"""
        try:
            prices = market_data['prices']
            current_price = market_data['current_price']
            
            if len(prices) < 10:
                return {'action': 'HOLD', 'confidence': 0.0}
            
            # Calculate simple moving average
            sma_10 = sum(prices[-10:]) / 10
            sma_20 = sum(prices) / len(prices)
            
            # Calculate price momentum
            momentum = (current_price - prices[0]) / prices[0] * 100
            
            # Calculate volatility
            price_changes = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
            volatility = sum(price_changes) / len(price_changes)
            
            # Generate signals based on conditions
            signals = []
            confidence = 0.0
            
            # Trend following
            if current_price > sma_10 > sma_20:
                signals.append('BUY')
                confidence += 0.3
            elif current_price < sma_10 < sma_20:
                signals.append('SELL')
                confidence += 0.3
            
            # Momentum
            if momentum > 0.1:
                signals.append('BUY')
                confidence += 0.2
            elif momentum < -0.1:
                signals.append('SELL')
                confidence += 0.2
            
            # Volatility check (avoid trading in high volatility)
            if volatility > 0.01:  # High volatility
                confidence *= 0.5
            
            # Time-based filter (avoid trading during low liquidity)
            current_hour = datetime.now().hour
            if 8 <= current_hour <= 16:  # Main trading hours
                confidence += 0.2
            
            # Determine final action
            buy_signals = signals.count('BUY')
            sell_signals = signals.count('SELL')
            
            if buy_signals > sell_signals:
                action = 'BUY'
            elif sell_signals > buy_signals:
                action = 'SELL'
            else:
                action = 'HOLD'
                confidence = 0.3
            
            return {
                'action': action,
                'confidence': min(confidence, 0.95),
                'price': current_price,
                'sma_10': sma_10,
                'sma_20': sma_20,
                'momentum': momentum
            }
            
        except Exception as e:
            logger.error(f"❌ AI analysis error: {e}")
            return {'action': 'HOLD', 'confidence': 0.0}
    
    async def execute_trade(self, symbol, signal):
        """Execute trade order"""
        try:
            volume = 1000  # 0.01 lots
            
            logger.info(f"🚀 EXECUTING TRADE: {signal['action']} {volume} {symbol}")
            
            # Attempt real cTrader API connection
            success = await self.place_ctrader_order(symbol, signal['action'], volume)
            
            if success:
                self.daily_trades += 1
                logger.info(f"✅ TRADE EXECUTED: {signal['action']} {symbol} - Real cTrader API")
                await self.send_notification(f"✅ LIVE TRADE: {signal['action']} {volume} {symbol}")
            else:
                # Fallback: Log the trade attempt
                logger.warning(f"⚠️ cTrader API not accessible - trade logged: {signal['action']} {symbol}")
                await self.send_notification(f"⚠️ TRADE SIGNAL: {signal['action']} {symbol} (API not accessible)")
            
        except Exception as e:
            logger.error(f"❌ Trade execution error: {e}")
    
    async def place_ctrader_order(self, symbol, action, volume):
        """Attempt to place real cTrader order"""
        try:
            # Try HTTP-based cTrader API calls
            endpoints = [
                "https://api.ctraderopen.com/v1/orders",
                "https://demo-api.ctrader.com/v1/orders",
                "https://openapi.ctrader.com/v1/orders"
            ]
            
            order_data = {
                "accountId": self.account_id,
                "symbol": symbol,
                "side": action,
                "volume": volume,
                "orderType": "MARKET"
            }
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Try each endpoint
            for endpoint in endpoints:
                try:
                    # Create request
                    data = json.dumps(order_data).encode('utf-8')
                    req = urllib.request.Request(endpoint, data=data, headers=headers)
                    
                    # Make request with timeout
                    with urllib.request.urlopen(req, timeout=10) as response:
                        if response.status in [200, 201, 202]:
                            logger.info(f"✅ cTrader API order successful via {endpoint}")
                            return True
                        else:
                            logger.warning(f"⚠️ cTrader API returned {response.status}")
                
                except Exception as e:
                    logger.debug(f"🔍 Endpoint {endpoint} failed: {str(e)[:50]}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"❌ cTrader API error: {e}")
            return False
    
    async def send_notification(self, message):
        """Send notification about trades"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        notification = f"[{timestamp}] {message}"
        
        # Log to Railway console (visible in dashboard)
        logger.info(f"🔔 NOTIFICATION: {message}")
        
        # You could add email/webhook notifications here
        email = os.getenv('NOTIFICATION_EMAIL')
        if email:
            logger.info(f"📧 Would send email to {email}: {message}")
    
    async def health_check(self):
        """Health check for Railway"""
        while self.running:
            logger.info(f"💓 Bot healthy - Daily trades: {self.daily_trades}/{self.max_daily_trades}")
            await asyncio.sleep(3600)  # Every hour

# Railway entry point
async def main():
    """Main function for Railway"""
    bot = SimplecTraderBot()
    
    # Start health monitoring
    health_task = asyncio.create_task(bot.health_check())
    
    # Start main bot
    await bot.start_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")

# FIXED requirements.txt - Railway compatible
"""
urllib3==1.26.18
"""

# FIXED Procfile
"""
worker: python main.py
"""

# railway.toml (optional)
"""
[build]
builder = "nixpacks"

[deploy]
startCommand = "python main.py"
restartPolicyType = "always"
"""
