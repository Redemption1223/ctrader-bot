#!/usr/bin/env python3
"""
SUPER AGGRESSIVE DEBUG CTRADER BOT
Maximum debugging and credential testing
"""

import json
import time
import os
import urllib.request
import urllib.parse
import random
import math
import threading
import base64
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

print("🔥 SUPER AGGRESSIVE DEBUG CTRADER BOT")
print("=" * 60)

class SuperDebugBot:
    """Super aggressive debugging bot to force connection"""
    
    def __init__(self):
        self.logs = []
        self.log("🔥 STARTING SUPER AGGRESSIVE DEBUG MODE")
        
        # SUPER AGGRESSIVE CREDENTIAL HUNTING
        self.access_token = self.super_hunt_credential('CTRADER_ACCESS_TOKEN')
        self.refresh_token = self.super_hunt_credential('CTRADER_REFRESH_TOKEN')
        self.client_id = self.super_hunt_credential('CTRADER_CLIENT_ID')
        self.client_secret = self.super_hunt_credential('CTRADER_CLIENT_SECRET')
        self.account_id = self.super_hunt_credential('CTRADER_ACCOUNT_ID')
        
        # Bot state
        self.running = True
        self.account_verified = False
        self.account_info = {}
        self.current_balance = 0.0
        self.daily_trades = 0
        self.total_trades = 0
        self.successful_trades = 0
        self.total_profit = 0.0
        self.trade_history = []
        self.current_signals = {}
        self.start_time = datetime.now()
        
        # Show what we found
        self.log("🔍 CREDENTIAL HUNT RESULTS:")
        self.log(f"   Access Token: {'✅' if self.access_token else '❌'} ({len(self.access_token or '')} chars)")
        self.log(f"   Refresh Token: {'✅' if self.refresh_token else '❌'} ({len(self.refresh_token or '')} chars)")
        self.log(f"   Client ID: {'✅' if self.client_id else '❌'} ({len(self.client_id or '')} chars)")
        self.log(f"   Client Secret: {'✅' if self.client_secret else '❌'} ({len(self.client_secret or '')} chars)")
        self.log(f"   Account ID: {'✅' if self.account_id else '❌'} ({self.account_id or 'None'})")
        
        if self.access_token:
            self.log(f"   Token Preview: {self.access_token[:15]}...{self.access_token[-10:]}")
        
        # Super aggressive testing
        self.super_test_everything()
    
    def log(self, message):
        """Enhanced logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        
        if len(self.logs) > 200:
            self.logs = self.logs[-200:]
        
        print(log_entry)
    
    def super_hunt_credential(self, key):
        """Super aggressive credential hunting"""
        self.log(f"🔍 HUNTING FOR: {key}")
        
        # Method 1: Standard os.getenv
        value = os.getenv(key)
        if value and value.strip():
            self.log(f"   ✅ Found via os.getenv: {len(value.strip())} chars")
            return value.strip()
        
        # Method 2: os.environ direct
        value = os.environ.get(key)
        if value and value.strip():
            self.log(f"   ✅ Found via os.environ: {len(value.strip())} chars")
            return value.strip()
        
        # Method 3: Case insensitive search
        for env_key, env_value in os.environ.items():
            if env_key.upper() == key.upper() and env_value.strip():
                self.log(f"   ✅ Found via case match ({env_key}): {len(env_value.strip())} chars")
                return env_value.strip()
        
        # Method 4: Partial match search
        for env_key, env_value in os.environ.items():
            if key.lower() in env_key.lower() and env_value.strip():
                self.log(f"   🔍 Partial match found ({env_key}): {len(env_value.strip())} chars")
        
        # Method 5: Show all environment variables that might be related
        ctrader_vars = {k: v for k, v in os.environ.items() if 'ctrader' in k.lower() or 'trader' in k.lower()}
        if ctrader_vars:
            self.log(f"   🔍 Found cTrader-related vars: {list(ctrader_vars.keys())}")
        
        self.log(f"   ❌ Could not find {key}")
        return None
    
    def super_test_everything(self):
        """Test EVERYTHING possible"""
        self.log("🧪 SUPER TESTING ALL POSSIBILITIES...")
        
        if not self.access_token:
            self.log("❌ No access token - cannot test APIs")
            self.account_info = {'error': 'No access token found', 'verified': False}
            return
        
        # Test multiple endpoints and methods
        test_configs = [
            ('https://openapi.ctrader.com', 'LIVE', '/v2/accounts'),
            ('https://demo-openapi.ctrader.com', 'DEMO', '/v2/accounts'),
            ('https://openapi.ctrader.com', 'LIVE', '/v1/accounts'),
            ('https://demo-openapi.ctrader.com', 'DEMO', '/v1/accounts'),
        ]
        
        for base_url, mode, endpoint in test_configs:
            self.log(f"🧪 Testing {mode} - {base_url}{endpoint}")
            result = self.test_api_endpoint(base_url, endpoint, mode)
            
            if result.get('success'):
                self.log(f"🎉 SUCCESS with {mode} endpoint!")
                self.account_info = result
                self.account_verified = True
                self.current_balance = result.get('balance', 0)
                return
            else:
                self.log(f"❌ Failed {mode}: {result.get('error', 'Unknown error')}")
        
        # If all failed, try token refresh
        if self.refresh_token:
            self.log("🔄 ALL ENDPOINTS FAILED - TRYING TOKEN REFRESH...")
            if self.super_refresh_token():
                self.log("✅ Token refreshed - retrying...")
                return self.super_test_everything()
        
        self.log("💥 ALL TESTS FAILED!")
        self.account_info = {'error': 'All endpoints and refresh failed', 'verified': False}
    
    def test_api_endpoint(self, base_url, endpoint, mode):
        """Test a specific API endpoint"""
        try:
            url = f"{base_url}{endpoint}"
            self.log(f"📡 Making request to: {url}")
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'User-Agent': 'SuperDebugBot/1.0'
            }
            
            # Log request details (be careful with sensitive data)
            self.log(f"🔑 Using token: {self.access_token[:10]}...{self.access_token[-5:]}")
            self.log(f"📋 Headers: {json.dumps({k: v for k, v in headers.items() if k != 'Authorization'})}")
            
            request = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(request, timeout=30) as response:
                status = response.status
                response_text = response.read().decode()
                
                self.log(f"📊 Response Status: {status}")
                self.log(f"📦 Response Length: {len(response_text)} chars")
                
                if status == 200:
                    try:
                        data = json.loads(response_text)
                        self.log(f"✅ Valid JSON response received")
                        
                        if isinstance(data, list) and len(data) > 0:
                            account = data[0]
                            result = {
                                'success': True,
                                'account_id': account.get('accountId', 'Unknown'),
                                'account_type': account.get('accountType', 'Unknown'),
                                'broker': account.get('brokerName', 'Unknown'),
                                'balance': float(account.get('balance', 0)),
                                'equity': float(account.get('equity', 0)),
                                'currency': account.get('currency', 'USD'),
                                'server': account.get('server', 'Unknown'),
                                'mode': mode,
                                'endpoint': base_url,
                                'verified': True,
                                'raw_response': json.dumps(data, indent=2)[:500]  # First 500 chars
                            }
                            
                            self.log(f"🎯 Account found: {result['account_id']}")
                            self.log(f"🏦 Broker: {result['broker']}")
                            self.log(f"💰 Balance: {result['balance']:.2f} {result['currency']}")
                            
                            return result
                        else:
                            return {'success': False, 'error': 'No accounts in response'}
                    
                    except json.JSONDecodeError as e:
                        self.log(f"❌ JSON decode error: {e}")
                        self.log(f"📄 Raw response: {response_text[:200]}...")
                        return {'success': False, 'error': f'JSON decode error: {e}'}
                else:
                    self.log(f"❌ HTTP {status} response")
                    self.log(f"📄 Response body: {response_text[:200]}...")
                    return {'success': False, 'error': f'HTTP {status}'}
        
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if hasattr(e, 'read') else 'No body'
            self.log(f"❌ HTTP Error {e.code}: {e.reason}")
            self.log(f"📄 Error body: {error_body[:200]}...")
            
            if e.code == 401:
                return {'success': False, 'error': f'Unauthorized (401) - Token may be invalid or expired'}
            elif e.code == 403:
                return {'success': False, 'error': f'Forbidden (403) - Access denied'}
            elif e.code == 404:
                return {'success': False, 'error': f'Not Found (404) - Endpoint may not exist'}
            else:
                return {'success': False, 'error': f'HTTP {e.code}: {e.reason}'}
        
        except urllib.error.URLError as e:
            self.log(f"❌ URL Error: {e.reason}")
            return {'success': False, 'error': f'URL Error: {e.reason}'}
        
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}")
            return {'success': False, 'error': f'Unexpected error: {e}'}
    
    def super_refresh_token(self):
        """Super aggressive token refresh"""
        if not all([self.refresh_token, self.client_id, self.client_secret]):
            self.log("❌ Missing refresh credentials")
            return False
        
        try:
            self.log("🔄 ATTEMPTING SUPER TOKEN REFRESH...")
            
            url = "https://openapi.ctrader.com/apps/token"
            
            # Try multiple refresh methods
            methods = [
                self.refresh_method_1,
                self.refresh_method_2,
                self.refresh_method_3
            ]
            
            for i, method in enumerate(methods, 1):
                self.log(f"🔄 Trying refresh method #{i}")
                result = method(url)
                if result:
                    return True
            
            return False
            
        except Exception as e:
            self.log(f"❌ Super refresh failed: {e}")
            return False
    
    def refresh_method_1(self, url):
        """Standard refresh method"""
        try:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            data_encoded = urllib.parse.urlencode(data).encode()
            request = urllib.request.Request(url, data=data_encoded, method='POST')
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            with urllib.request.urlopen(request, timeout=20) as response:
                result = json.loads(response.read().decode())
                
                if 'access_token' in result:
                    old_token = self.access_token[:10] + "..." if self.access_token else "None"
                    self.access_token = result['access_token']
                    
                    if 'refresh_token' in result:
                        self.refresh_token = result['refresh_token']
                    
                    self.log(f"✅ Method 1 success - new token: {self.access_token[:10]}...")
                    return True
            
            return False
            
        except Exception as e:
            self.log(f"❌ Method 1 failed: {e}")
            return False
    
    def refresh_method_2(self, url):
        """Basic auth refresh method"""
        try:
            # Try with basic auth
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
            
            data_encoded = urllib.parse.urlencode(data).encode()
            request = urllib.request.Request(url, data=data_encoded, method='POST')
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            request.add_header('Authorization', f'Basic {auth_b64}')
            
            with urllib.request.urlopen(request, timeout=20) as response:
                result = json.loads(response.read().decode())
                
                if 'access_token' in result:
                    self.access_token = result['access_token']
                    if 'refresh_token' in result:
                        self.refresh_token = result['refresh_token']
                    
                    self.log(f"✅ Method 2 success with basic auth")
                    return True
            
            return False
            
        except Exception as e:
            self.log(f"❌ Method 2 failed: {e}")
            return False
    
    def refresh_method_3(self, url):
        """JSON refresh method"""
        try:
            # Try with JSON body
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            data_json = json.dumps(data).encode()
            request = urllib.request.Request(url, data=data_json, method='POST')
            request.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(request, timeout=20) as response:
                result = json.loads(response.read().decode())
                
                if 'access_token' in result:
                    self.access_token = result['access_token']
                    if 'refresh_token' in result:
                        self.refresh_token = result['refresh_token']
                    
                    self.log(f"✅ Method 3 success with JSON")
                    return True
            
            return False
            
        except Exception as e:
            self.log(f"❌ Method 3 failed: {e}")
            return False
    
    def get_stats(self):
        """Get bot statistics"""
        runtime = datetime.now() - self.start_time
        success_rate = (self.successful_trades / max(self.total_trades, 1)) * 100
        
        return {
            'active': self.running,
            'account_verified': self.account_verified,
            'account_info': self.account_info,
            'live_mode': True,
            'daily_trades': self.daily_trades,
            'total_trades': self.total_trades,
            'successful_trades': self.successful_trades,
            'success_rate': success_rate,
            'current_balance': self.current_balance,
            'total_profit': self.total_profit,
            'runtime': str(runtime).split('.')[0],
            'recent_logs': self.logs[-100:],
            'debug_mode': True
        }
    
    def run_bot(self):
        """Main bot execution - Debug mode"""
        self.log("🔥 SUPER DEBUG BOT RUNNING")
        self.log("📊 Check logs for detailed connection information")
        
        cycle = 0
        
        while self.running:
            try:
                cycle += 1
                self.log(f"🔄 Debug Cycle #{cycle}")
                
                # Re-test connection every 10 cycles
                if cycle % 10 == 0:
                    self.log("🔄 Re-testing connection...")
                    self.super_test_everything()
                
                # Status
                stats = self.get_stats()
                self.log(f"💓 Status: Verified: {'✅' if stats['account_verified'] else '❌'} | "
                        f"Balance: {stats['current_balance']:.2f}")
                
                # Show environment debug info every 5 cycles
                if cycle % 5 == 0:
                    self.show_environment_debug()
                
                time.sleep(60)  # 1 minute cycles
                
            except Exception as e:
                self.log(f"❌ Debug cycle error: {e}")
                time.sleep(30)
    
    def show_environment_debug(self):
        """Show detailed environment debugging"""
        self.log("🔍 ENVIRONMENT DEBUG:")
        
        # Show all environment variables
        all_env = dict(os.environ)
        self.log(f"   Total env vars: {len(all_env)}")
        
        # Show cTrader related vars
        ctrader_vars = {k: f"{v[:10]}...{v[-5:]}" if len(v) > 20 else v 
                       for k, v in all_env.items() 
                       if any(term in k.lower() for term in ['ctrader', 'trader', 'token', 'client', 'account'])}
        
        if ctrader_vars:
            self.log(f"   cTrader-related vars found: {len(ctrader_vars)}")
            for key, value in ctrader_vars.items():
                self.log(f"     {key}: {value}")
        else:
            self.log("   No cTrader-related vars found")
        
        # Show render-specific vars
        render_vars = {k: v for k, v in all_env.items() if k.startswith('RENDER_')}
        if render_vars:
            self.log(f"   Render vars: {list(render_vars.keys())}")

# Global bot instance
debug_bot = None

class DebugDashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/' or self.path == '/dashboard':
                html = self.get_debug_dashboard()
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            elif self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                health_data = {
                    'status': 'debug_mode',
                    'bot_active': debug_bot.running if debug_bot else False,
                    'account_verified': debug_bot.account_verified if debug_bot else False,
                    'version': 'debug-1.0'
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
    
    def get_debug_dashboard(self):
        if not debug_bot:
            return "<h1>Debug Bot not initialized</h1>"
        
        try:
            stats = debug_bot.get_stats()
            account_info = stats.get('account_info', {})
            
            # Account status with detailed debugging
            if stats['account_verified']:
                account_status = f"""
                <div style="background: linear-gradient(45deg, #28a745, #20c997); padding: 25px; border-radius: 15px; margin-bottom: 20px; text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; margin-bottom: 15px;">✅ CONNECTION SUCCESSFUL!</div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; font-size: 0.9em;">
                        <div><strong>Account:</strong> {account_info.get('account_id', 'Unknown')}</div>
                        <div><strong>Broker:</strong> {account_info.get('broker', 'Unknown')}</div>
                        <div><strong>Balance:</strong> {account_info.get('balance', 0):.2f} {account_info.get('currency', 'USD')}</div>
                        <div><strong>Mode:</strong> {account_info.get('mode', 'Unknown')}</div>
                        <div><strong>Endpoint:</strong> {account_info.get('endpoint', 'Unknown')}</div>
                        <div><strong>Type:</strong> {account_info.get('account_type', 'Unknown')}</div>
                    </div>
                </div>
                """
            else:
                error_msg = account_info.get('error', 'Unknown error')
                account_status = f"""
                <div style="background: linear-gradient(45deg, #dc3545, #6f42c1); padding: 25px; border-radius: 15px; margin-bottom: 20px; text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; margin-bottom: 15px;">❌ CONNECTION FAILED</div>
                    <div style="margin-bottom: 10px;">Account verification failed</div>
                    <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 10px; margin: 10px 0;">
                        <strong>Error Details:</strong><br>
                        {error_msg}
                    </div>
                    <div style="font-size: 0.9em;">Check the detailed logs below for more information</div>
                </div>
                """
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🔥 Super Debug cTrader Bot</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #00ff00;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ 
            text-align: center; 
            margin-bottom: 30px;
            background: rgba(0,255,0,0.1);
            padding: 30px;
            border-radius: 20px;
            border: 2px solid #00ff00;
        }}
        .header h1 {{ 
            font-size: 3em; 
            color: #00ff00;
            text-shadow: 0 0 20px #00ff00;
            animation: glow 2s ease-in-out infinite alternate;
        }}
        @keyframes glow {{
            from {{ text-shadow: 0 0 20px #00ff00, 0 0 30px #00ff00; }}
            to {{ text-shadow: 0 0 30px #00ff00, 0 0 40px #00ff00, 0 0 50px #00ff00; }}
        }}
        .card {{ 
            background: rgba(0,0,0,0.7); 
            padding: 25px; 
            border-radius: 15px;
            border: 1px solid #00ff00;
            margin-bottom: 20px;
        }}
        .card h3 {{ color: #00ff00; font-size: 1.3em; margin-bottom: 20px; }}
        .logs {{ 
            background: rgba(0,0,0,0.9); 
            padding: 20px; 
            border-radius: 10px; 
            font-family: 'Courier New', monospace; 
            font-size: 0.85em;
            max-height: 600px;
            overflow-y: auto;
            border: 1px solid #00ff00;
            color: #00ff00;
        }}
        .refresh {{ 
            position: fixed; 
            top: 20px; 
            right: 20px; 
            background: #00ff00; 
            color: black; 
            border: none; 
            padding: 15px 25px; 
            border-radius: 25px; 
            cursor: pointer; 
            font-weight: bold;
            font-size: 1.1em;
        }}
        .metric {{ 
            display: flex; 
            justify-content: space-between; 
            margin: 15px 0; 
            padding: 10px 0;
            border-bottom: 1px solid rgba(0,255,0,0.3);
        }}
        .metric-value {{ font-weight: bold; color: #00ff00; }}
        .credential-info {{
            background: rgba(0,0,0,0.5);
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            border: 1px solid #ffff00;
        }}
    </style>
    <script>
        setTimeout(() => location.reload(), 45000);
        function refresh() {{ location.reload(); }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 SUPER DEBUG MODE</h1>
            <p>MAXIMUM DEBUGGING • CREDENTIAL TESTING • CONNECTION ANALYSIS</p>
            <p>Last Updated: {datetime.now().strftime('%H:%M:%S UTC')}</p>
        </div>
        
        <button class="refresh" onclick="refresh()">🔄 Refresh</button>
        
        {account_status}
        
        <div class="card">
            <h3>🔍 Credential Status</h3>
            <div class="credential-info">
                <div><strong>Access Token:</strong> {'✅ FOUND' if debug_bot.access_token else '❌ MISSING'} ({len(debug_bot.access_token or '')} chars)</div>
                <div><strong>Refresh Token:</strong> {'✅ FOUND' if debug_bot.refresh_token else '❌ MISSING'} ({len(debug_bot.refresh_token or '')} chars)</div>
                <div><strong>Client ID:</strong> {'✅ FOUND' if debug_bot.client_id else '❌ MISSING'} ({len(debug_bot.client_id or '')} chars)</div>
                <div><strong>Client Secret:</strong> {'✅ FOUND' if debug_bot.client_secret else '❌ MISSING'} ({len(debug_bot.client_secret or '')} chars)</div>
                <div><strong>Account ID:</strong> {'✅ FOUND' if debug_bot.account_id else '❌ MISSING'} ({debug_bot.account_id or 'None'})</div>
            </div>
        </div>
        
        <div class="card">
            <h3>📊 Debug Status</h3>
            <div class="metric">
                <span>Account Verified:</span>
                <span class="metric-value" style="color: {'#00ff00' if stats['account_verified'] else '#ff0000'};">{'✅ YES' if stats['account_verified'] else '❌ NO'}</span>
            </div>
            <div class="metric">
                <span>Debug Mode:</span>
                <span class="metric-value">🔥 ACTIVE</span>
            </div>
            <div class="metric">
                <span>Runtime:</span>
                <span class="metric-value">{stats['runtime']}</span>
            </div>
        </div>
        
        <div class="card">
            <h3>📱 Detailed Debug Logs</h3>
            <div class="logs">
"""
            
            # Add logs with color coding
            for log in stats['recent_logs'][-50:]:
                log_color = '#00ff00'  # Default green
                if '❌' in log or 'ERROR' in log or 'FAILED' in log:
                    log_color = '#ff0000'  # Red for errors
                elif '✅' in log or 'SUCCESS' in log:
                    log_color = '#00ff00'  # Green for success
                elif '🔍' in log or 'TESTING' in log:
                    log_color = '#ffff00'  # Yellow for testing
                elif '🔄' in log:
                    log_color = '#00ffff'  # Cyan for refresh
                
                html += f'<div style="color: {log_color}; margin: 3px 0;">{log}</div>'
            
            html += '''
            </div>
        </div>
    </div>
</body>
</html>
'''
            return html
            
        except Exception as e:
            return f'<h1>Debug Dashboard Error: {str(e)}</h1>'
    
    def log_message(self, format, *args):
        pass

def start_debug_server():
    try:
        port = int(os.getenv('PORT', 10000))
        server = HTTPServer(('0.0.0.0', port), DebugDashboardHandler)
        
        debug_bot.log(f"🌐 Debug server starting on port {port}")
        
        def run_server():
            try:
                server.serve_forever()
            except Exception as e:
                debug_bot.log(f"Server error: {e}")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        debug_bot.log("✅ Debug dashboard active!")
        
    except Exception as e:
        debug_bot.log(f"Server error: {e}")

def main():
    global debug_bot
    
    try:
        print("🔥 STARTING SUPER AGGRESSIVE DEBUG BOT")
        print("🔍 This will show EXACTLY what's wrong with the connection")
        
        # Create debug bot
        debug_bot = SuperDebugBot()
        
        # Start debug server
        start_debug_server()
        
        # Start debug bot
        debug_bot.run_bot()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        if debug_bot:
            debug_bot.log(f"Fatal error: {e}")
        time.sleep(30)
        main()

if __name__ == "__main__":
    main()
