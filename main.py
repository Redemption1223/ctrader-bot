#!/usr/bin/env python3

import json
import time
import os
import urllib.request
from datetime import datetime
from wsgiref.simple_server import make_server, WSGIServer
from socketserver import ThreadingMixIn

# Global state
logs = []
connection_status = "Testing..."
connection_data = {}

def add_log(message):
    """Add log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    logs.append(log_entry)
    print(log_entry)
    
    # Keep last 30 logs
    if len(logs) > 30:
        logs[:] = logs[-30:]

def test_ctrader_api():
    """Test cTrader API connection"""
    global connection_status, connection_data
    
    add_log("🔌 Testing cTrader API connection...")
    
    # Get credentials from Railway environment
    access_token = os.getenv('CTRADER_ACCESS_TOKEN', '').strip()
    account_id = os.getenv('CTRADER_ACCOUNT_ID', '').strip()
    client_id = os.getenv('CTRADER_CLIENT_ID', '').strip()
    
    add_log(f"🔑 Access Token: {'✅ Found' if access_token else '❌ Missing'} ({len(access_token)} chars)")
    add_log(f"🔑 Account ID: {account_id if account_id else '❌ Missing'}")
    add_log(f"🔑 Client ID: {'✅ Found' if client_id else '❌ Missing'} ({len(client_id)} chars)")
    
    if not access_token:
        connection_status = "❌ NO ACCESS TOKEN"
        add_log("❌ Cannot test - no access token found")
        return False
    
    # Test cTrader API endpoints
    test_endpoints = [
        ("https://openapi.ctrader.com/v1/accounts", "Live v1"),
        ("https://demo-openapi.ctrader.com/v1/accounts", "Demo v1"),
        ("https://openapi.ctrader.com/accounts", "Live"),
        ("https://demo-openapi.ctrader.com/accounts", "Demo"),
        ("https://openapi.ctrader.com/v2/accounts", "Live v2"),
        ("https://demo-openapi.ctrader.com/v2/accounts", "Demo v2")
    ]
    
    for url, name in test_endpoints:
        try:
            add_log(f"🧪 Testing {name}: {url}")
            
            # Create request with proper headers
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'User-Agent': 'cTrader-Bot/1.0'
            }
            
            request = urllib.request.Request(url, headers=headers)
            
            # Make API call
            with urllib.request.urlopen(request, timeout=15) as response:
                status_code = response.status
                response_text = response.read().decode('utf-8')
                
                add_log(f"   📊 HTTP {status_code} - Response: {len(response_text)} chars")
                
                if status_code == 200:
                    try:
                        data = json.loads(response_text)
                        add_log(f"   ✅ Valid JSON response received")
                        
                        # Check for account data
                        accounts = []
                        if isinstance(data, list):
                            accounts = data
                        elif isinstance(data, dict) and 'accounts' in data:
                            accounts = data['accounts']
                        elif isinstance(data, dict):
                            accounts = [data]
                        
                        if accounts and len(accounts) > 0:
                            account = accounts[0]
                            
                            connection_status = f"✅ CONNECTED - {name}"
                            connection_data = {
                                'success': True,
                                'endpoint': url,
                                'method': name,
                                'account_id': account.get('accountId', account.get('id', 'Unknown')),
                                'balance': float(account.get('balance', 0)),
                                'currency': account.get('currency', 'USD'),
                                'broker': account.get('brokerName', account.get('broker', 'Unknown')),
                                'account_type': account.get('accountType', 'Unknown'),
                                'raw_response': json.dumps(data, indent=2)[:500]
                            }
                            
                            add_log(f"🎉 SUCCESS! cTrader API connection established!")
                            add_log(f"   🏦 Broker: {connection_data['broker']}")
                            add_log(f"   📋 Account: {connection_data['account_id']}")
                            add_log(f"   💰 Balance: {connection_data['balance']:.2f} {connection_data['currency']}")
                            add_log(f"   📊 Type: {connection_data['account_type']}")
                            add_log(f"   🔗 Endpoint: {url}")
                            
                            return True
                        else:
                            add_log(f"   ⚠️ No account data in response")
                    
                    except json.JSONDecodeError as e:
                        add_log(f"   ❌ JSON decode error: {e}")
                        add_log(f"   📄 Raw response: {response_text[:200]}...")
                else:
                    add_log(f"   ❌ HTTP {status_code} response")
        
        except urllib.error.HTTPError as e:
            add_log(f"   ❌ HTTP Error {e.code}: {e.reason}")
            if e.code == 401:
                add_log(f"   🔐 Unauthorized - token may be invalid or expired")
            elif e.code == 403:
                add_log(f"   🚫 Forbidden - access denied")
            elif e.code == 404:
                add_log(f"   🔍 Not Found - endpoint doesn't exist")
        
        except urllib.error.URLError as e:
            add_log(f"   ❌ URL Error: {e.reason}")
        
        except Exception as e:
            add_log(f"   ❌ Unexpected error: {e}")
    
    # If we get here, all endpoints failed
    connection_status = "❌ ALL ENDPOINTS FAILED"
    add_log("💥 All cTrader API endpoints failed")
    return False

def generate_html_page():
    """Generate HTML dashboard"""
    
    # Determine status color
    if "✅ CONNECTED" in connection_status:
        status_color = "#28a745"
        status_emoji = "✅"
    elif "Testing" in connection_status:
        status_color = "#ffc107"
        status_emoji = "🧪"
    else:
        status_color = "#dc3545"
        status_emoji = "❌"
    
    # Connection details section
    connection_html = ""
    if connection_data and connection_data.get('success'):
        connection_html = f"""
        <div style="background: linear-gradient(45deg, #28a745, #20c997); padding: 20px; border-radius: 15px; margin: 20px 0; color: white;">
            <h2>🎉 cTrader Connection Successful!</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
                <div><strong>Broker:</strong> {connection_data['broker']}</div>
                <div><strong>Account ID:</strong> {connection_data['account_id']}</div>
                <div><strong>Balance:</strong> {connection_data['balance']:.2f} {connection_data['currency']}</div>
                <div><strong>Type:</strong> {connection_data['account_type']}</div>
                <div><strong>Method:</strong> {connection_data['method']}</div>
            </div>
            <details style="margin-top: 15px;">
                <summary style="cursor: pointer; font-weight: bold;">Show Technical Details</summary>
                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px; margin-top: 10px;">
                    <p><strong>Endpoint:</strong> {connection_data['endpoint']}</p>
                    <p><strong>Response Preview:</strong></p>
                    <pre style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px; overflow-x: auto; font-size: 0.8em;">{connection_data.get('raw_response', 'No response data')}</pre>
                </div>
            </details>
        </div>
        """
    
    # Generate logs HTML
    logs_html = ""
    for log in logs[-25:]:  # Show last 25 logs
        log_color = "#ffffff"
        if "🎉" in log or "SUCCESS" in log or "✅" in log:
            log_color = "#28a745"
        elif "❌" in log or "Error" in log or "Failed" in log:
            log_color = "#dc3545"
        elif "🧪" in log or "Testing" in log:
            log_color = "#17a2b8"
        elif "⚠️" in log:
            log_color = "#ffc107"
        
        logs_html += f'<div style="color: {log_color}; font-family: Consolas, monospace; margin: 3px 0; font-size: 0.9em; line-height: 1.4;">{log}</div>'
    
    # Main HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔌 cTrader API Connection Test</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{ 
            text-align: center; 
            background: rgba(255,255,255,0.1); 
            padding: 30px; 
            border-radius: 20px; 
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .header h1 {{ 
            font-size: 2.5em; 
            margin-bottom: 15px;
            background: linear-gradient(45deg, #ffd700, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .status-card {{ 
            background: {status_color}; 
            padding: 25px; 
            border-radius: 15px; 
            text-align: center; 
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }}
        .status-title {{ 
            font-size: 1.8em; 
            font-weight: bold; 
            margin-bottom: 10px;
        }}
        .card {{ 
            background: rgba(255,255,255,0.1); 
            padding: 25px; 
            border-radius: 15px; 
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .card h3 {{ 
            color: #ffd700; 
            margin-bottom: 20px; 
            font-size: 1.4em;
        }}
        .logs {{ 
            background: rgba(0,0,0,0.6); 
            padding: 20px; 
            border-radius: 10px; 
            max-height: 400px; 
            overflow-y: auto;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .btn {{ 
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4); 
            color: white; 
            border: none; 
            padding: 15px 30px; 
            border-radius: 25px; 
            cursor: pointer; 
            font-size: 1.1em; 
            font-weight: bold;
            margin: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .btn:hover {{ 
            transform: translateY(-2px); 
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }}
        .credential-status {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .credential-item {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }}
        details {{ margin: 15px 0; }}
        summary {{ cursor: pointer; font-weight: bold; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px; }}
        pre {{ background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px; overflow-x: auto; font-size: 0.8em; }}
    </style>
    <script>
        // Auto-refresh every 60 seconds
        setTimeout(() => location.reload(), 60000);
        
        function refresh() {{ location.reload(); }}
        function runTest() {{ 
            fetch('/test').then(() => {{ 
                setTimeout(() => location.reload(), 2000); 
            }});
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔌 cTrader API Test</h1>
            <p>Railway Deployment • cTrader Connection Testing</p>
            <p style="opacity: 0.8;">Last Updated: {datetime.now().strftime('%H:%M:%S UTC')}</p>
        </div>
        
        <div class="status-card">
            <div class="status-title">{status_emoji} {connection_status}</div>
            <div style="font-size: 1.1em; margin-top: 10px;">
                {'Connection established successfully!' if connection_data.get('success') else 'Testing cTrader API endpoints...'}
            </div>
        </div>
        
        {connection_html}
        
        <div style="text-align: center; margin: 30px 0;">
            <button class="btn" onclick="runTest()">🧪 Run New Test</button>
            <button class="btn" onclick="refresh()">🔄 Refresh Page</button>
        </div>
        
        <div class="card">
            <h3>🔑 Credential Status</h3>
            <div class="credential-status">
                <div class="credential-item">
                    <strong>Access Token</strong><br>
                    {'✅ Found (' + str(len(os.getenv('CTRADER_ACCESS_TOKEN', ''))) + ' chars)' if os.getenv('CTRADER_ACCESS_TOKEN') else '❌ Missing'}
                </div>
                <div class="credential-item">
                    <strong>Account ID</strong><br>
                    {os.getenv('CTRADER_ACCOUNT_ID', '❌ Missing')}
                </div>
                <div class="credential-item">
                    <strong>Client ID</strong><br>
                    {'✅ Found (' + str(len(os.getenv('CTRADER_CLIENT_ID', ''))) + ' chars)' if os.getenv('CTRADER_CLIENT_ID') else '❌ Missing'}
                </div>
                <div class="credential-item">
                    <strong>Client Secret</strong><br>
                    {'✅ Found (' + str(len(os.getenv('CTRADER_CLIENT_SECRET', ''))) + ' chars)' if os.getenv('CTRADER_CLIENT_SECRET') else '❌ Missing'}
                </div>
                <div class="credential-item">
                    <strong>Refresh Token</strong><br>
                    {'✅ Found (' + str(len(os.getenv('CTRADER_REFRESH_TOKEN', ''))) + ' chars)' if os.getenv('CTRADER_REFRESH_TOKEN') else '❌ Missing'}
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>📱 Test Logs</h3>
            <div class="logs">
                {logs_html if logs_html else '<div style="text-align: center; opacity: 0.7;">No logs yet - click "Run New Test" to start</div>'}
            </div>
        </div>
    </div>
</body>
</html>
    """
    
    return html

def wsgi_app(environ, start_response):
    """WSGI application for Railway"""
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    
    if method == 'GET':
        if path == '/':
            # Main dashboard
            response_body = generate_html_page()
            status = '200 OK'
            headers = [('Content-Type', 'text/html; charset=utf-8')]
        
        elif path == '/test':
            # Run API test
            add_log("🔄 Manual test triggered from web interface")
            test_ctrader_api()
            response_body = '<h1>Test Started</h1><p><a href="/">Back to Dashboard</a></p><script>setTimeout(() => window.location.href="/", 2000);</script>'
            status = '200 OK'
            headers = [('Content-Type', 'text/html; charset=utf-8')]
        
        elif path == '/health':
            # Health check for Railway
            response_body = json.dumps({
                'status': 'healthy',
                'service': 'ctrader-api-test',
                'timestamp': datetime.now().isoformat(),
                'connection_status': connection_status,
                'credentials_loaded': bool(os.getenv('CTRADER_ACCESS_TOKEN'))
            })
            status = '200 OK'
            headers = [('Content-Type', 'application/json')]
        
        else:
            # 404 for other paths
            response_body = '<h1>404 Not Found</h1><p><a href="/">Go to Dashboard</a></p>'
            status = '404 Not Found'
            headers = [('Content-Type', 'text/html')]
    
    else:
        # Method not allowed
        response_body = '<h1>405 Method Not Allowed</h1>'
        status = '405 Method Not Allowed'
        headers = [('Content-Type', 'text/html')]
    
    # Send response
    start_response(status, headers)
    return [response_body.encode('utf-8')]

# This is what Railway will look for
app = wsgi_app

class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    """Threading WSGI server for better performance"""
    pass

if __name__ == "__main__":
    # Initialize
    add_log("🚀 Starting cTrader API Test Service on Railway")
    add_log("🔌 Railway environment detected")
    
    # Test connection on startup
    test_ctrader_api()
    
    # Start server
    port = int(os.getenv('PORT', 8000))
    add_log(f"🌐 Starting WSGI server on port {port}")
    
    try:
        # Create WSGI server
        httpd = make_server('0.0.0.0', port, app, server_class=ThreadingWSGIServer)
        add_log(f"✅ Server running at http://0.0.0.0:{port}")
        add_log("🔗 Railway will provide the public URL")
        
        # Run server
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        add_log("🛑 Server stopped by user")
    except Exception as e:
        add_log(f"❌ Server error: {e}")
