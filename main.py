#!/usr/bin/env python3
"""
COMPREHENSIVE CTRADER ENDPOINT TESTER
Tests every possible cTrader API endpoint until we find the working one
"""

import json
import time
import os
import urllib.request
import urllib.parse
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

print("🔍 COMPREHENSIVE CTRADER ENDPOINT TESTER")

# Global variables
test_results = []
working_endpoint = None
test_logs = []

def log_message(msg):
    """Simple logging"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {msg}"
    test_logs.append(log_entry)
    print(log_entry)
    
    if len(test_logs) > 50:
        test_logs[:] = test_logs[-50:]

def comprehensive_endpoint_test():
    """Test EVERY possible cTrader endpoint"""
    global working_endpoint, test_results
    
    log_message("🔍 STARTING COMPREHENSIVE ENDPOINT TEST")
    
    # Get credentials from environment (we know these work)
    access_token = os.getenv('CTRADER_ACCESS_TOKEN', '').strip()
    account_id = os.getenv('CTRADER_ACCOUNT_ID', '').strip()
    client_id = os.getenv('CTRADER_CLIENT_ID', '').strip()
    
    log_message(f"🔑 Credentials loaded: Token({len(access_token)} chars), Account({account_id})")
    
    if not access_token:
        log_message("❌ No access token found")
        return
    
    # COMPREHENSIVE list of possible cTrader endpoints
    base_urls = [
        "https://openapi.ctrader.com",
        "https://demo-openapi.ctrader.com", 
        "https://api.ctrader.com",
        "https://demo-api.ctrader.com",
        "https://webapi.ctrader.com",
        "https://demo-webapi.ctrader.com",
        "https://rest.ctrader.com",
        "https://demo-rest.ctrader.com"
    ]
    
    endpoints = [
        "/v1/accounts",
        "/v2/accounts", 
        "/v3/accounts",
        "/accounts",
        "/api/v1/accounts",
        "/api/v2/accounts",
        "/api/accounts",
        "/rest/v1/accounts",
        "/rest/accounts",
        "/openapi/v1/accounts",
        "/openapi/accounts",
        f"/v1/accounts/{account_id}",
        f"/v2/accounts/{account_id}",
        f"/accounts/{account_id}",
        f"/api/v1/accounts/{account_id}",
        "/user/accounts",
        "/trader/accounts",
        "/client/accounts"
    ]
    
    # Authentication methods to try
    auth_methods = [
        lambda token: {'Authorization': f'Bearer {token}'},
        lambda token: {'Authorization': f'Token {token}'},
        lambda token: {'X-API-Key': token},
        lambda token: {'X-Auth-Token': token},
        lambda token: {'Access-Token': token},
        lambda token: {'Authorization': f'Basic {token}'},
        lambda token: {'cTrader-Token': token}
    ]
    
    test_count = 0
    
    # Test EVERY combination
    for base_url in base_urls:
        for endpoint in endpoints:
            for i, auth_method in enumerate(auth_methods):
                try:
                    test_count += 1
                    url = f"{base_url}{endpoint}"
                    
                    log_message(f"🧪 Test #{test_count}: {url} (Auth method {i+1})")
                    
                    # Create headers
                    headers = auth_method(access_token)
                    headers.update({
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'User-Agent': 'cTrader-Bot/1.0'
                    })
                    
                    # Add account ID to headers if we have it
                    if account_id:
                        headers['X-Account-Id'] = account_id
                        headers['Account-Id'] = account_id
                    
                    request = urllib.request.Request(url, headers=headers)
                    
                    with urllib.request.urlopen(request, timeout=10) as response:
                        status = response.status
                        response_text = response.read().decode()
                        
                        log_message(f"   📊 Status: {status}, Length: {len(response_text)}")
                        
                        if status == 200:
                            try:
                                data = json.loads(response_text)
                                
                                # Check if we got account data
                                accounts = []
                                if isinstance(data, list):
                                    accounts = data
                                elif isinstance(data, dict):
                                    if 'accounts' in data:
                                        accounts = data['accounts']
                                    elif 'data' in data:
                                        accounts = data['data'] if isinstance(data['data'], list) else [data['data']]
                                    elif any(key in data for key in ['accountId', 'id', 'balance']):
                                        accounts = [data]
                                
                                if accounts:
                                    account = accounts[0]
                                    
                                    working_endpoint = {
                                        'url': url,
                                        'auth_method': i + 1,
                                        'headers': dict(headers),
                                        'account_id': account.get('accountId', account.get('id', 'Unknown')),
                                        'balance': account.get('balance', account.get('accountBalance', 0)),
                                        'currency': account.get('currency', account.get('baseCurrency', 'USD')),
                                        'broker': account.get('brokerName', account.get('broker', 'Unknown')),
                                        'raw_data': data
                                    }
                                    
                                    log_message("🎉 SUCCESS! WORKING ENDPOINT FOUND!")
                                    log_message(f"   URL: {url}")
                                    log_message(f"   Auth: Method {i+1}")
                                    log_message(f"   Account: {working_endpoint['account_id']}")
                                    log_message(f"   Balance: {working_endpoint['balance']} {working_endpoint['currency']}")
                                    log_message(f"   Broker: {working_endpoint['broker']}")
                                    
                                    # Save the result
                                    test_results.append({
                                        'status': 'SUCCESS',
                                        'url': url,
                                        'auth_method': i + 1,
                                        'account_data': working_endpoint
                                    })
                                    
                                    return  # Stop testing once we find a working endpoint
                                else:
                                    log_message(f"   ⚠️ Valid response but no account data")
                                    test_results.append({
                                        'status': 'NO_ACCOUNTS',
                                        'url': url,
                                        'auth_method': i + 1,
                                        'response': response_text[:200]
                                    })
                            
                            except json.JSONDecodeError:
                                log_message(f"   ❌ Invalid JSON response")
                                test_results.append({
                                    'status': 'INVALID_JSON',
                                    'url': url,
                                    'auth_method': i + 1,
                                    'response': response_text[:200]
                                })
                        else:
                            log_message(f"   ❌ HTTP {status}")
                            test_results.append({
                                'status': f'HTTP_{status}',
                                'url': url,
                                'auth_method': i + 1
                            })
                
                except urllib.error.HTTPError as e:
                    log_message(f"   ❌ HTTP {e.code}: {e.reason}")
                    test_results.append({
                        'status': f'HTTP_ERROR_{e.code}',
                        'url': url,
                        'auth_method': i + 1,
                        'error': str(e.reason)
                    })
                
                except urllib.error.URLError as e:
                    log_message(f"   ❌ URL Error: {e.reason}")
                    test_results.append({
                        'status': 'URL_ERROR',
                        'url': url,
                        'auth_method': i + 1,
                        'error': str(e.reason)
                    })
                
                except Exception as e:
                    log_message(f"   ❌ Error: {e}")
                    test_results.append({
                        'status': 'ERROR',
                        'url': url,
                        'auth_method': i + 1,
                        'error': str(e)
                    })
                
                # Small delay between tests
                time.sleep(0.1)
    
    log_message(f"💥 COMPREHENSIVE TEST COMPLETE - {test_count} endpoints tested")
    log_message("❌ No working endpoint found")

def try_oauth_endpoints():
    """Try OAuth and token endpoints"""
    log_message("🔐 Testing OAuth endpoints...")
    
    access_token = os.getenv('CTRADER_ACCESS_TOKEN', '').strip()
    client_id = os.getenv('CTRADER_CLIENT_ID', '').strip()
    
    oauth_endpoints = [
        "https://openapi.ctrader.com/oauth/userinfo",
        "https://demo-openapi.ctrader.com/oauth/userinfo",
        "https://openapi.ctrader.com/userinfo", 
        "https://demo-openapi.ctrader.com/userinfo",
        "https://openapi.ctrader.com/oauth/me",
        "https://demo-openapi.ctrader.com/oauth/me",
        "https://openapi.ctrader.com/me",
        "https://demo-openapi.ctrader.com/me"
    ]
    
    for endpoint in oauth_endpoints:
        try:
            log_message(f"🔐 Testing OAuth: {endpoint}")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            request = urllib.request.Request(endpoint, headers=headers)
            
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    log_message(f"✅ OAuth success: {endpoint}")
                    log_message(f"   Data: {json.dumps(data, indent=2)}")
                    return True
                else:
                    log_message(f"❌ OAuth failed: HTTP {response.status}")
        
        except Exception as e:
            log_message(f"❌ OAuth error: {e}")
    
    return False

class ComprehensiveHandler(BaseHTTPRequestHandler):
    """Web handler for comprehensive testing"""
    
    def do_GET(self):
        try:
            if self.path == '/':
                html = self.get_results_page()
            elif self.path == '/test':
                # Trigger new test
                threading.Thread(target=comprehensive_endpoint_test, daemon=True).start()
                html = '<h1>Test Started</h1><p><a href="/">View Results</a></p>'
            elif self.path == '/oauth':
                # Test OAuth endpoints
                threading.Thread(target=try_oauth_endpoints, daemon=True).start()
                html = '<h1>OAuth Test Started</h1><p><a href="/">View Results</a></p>'
            elif self.path == '/health':
                html = '{"status": "testing"}'
            else:
                html = '<h1>Endpoint Tester</h1><a href="/">Results</a> | <a href="/test">New Test</a>'
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f'Error: {e}'.encode())
    
    def get_results_page(self):
        """Generate results page"""
        
        # Working endpoint info
        working_html = ""
        if working_endpoint:
            working_html = f"""
            <div style="background: #28a745; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h2>🎉 WORKING ENDPOINT FOUND!</h2>
                <p><strong>URL:</strong> {working_endpoint['url']}</p>
                <p><strong>Auth Method:</strong> {working_endpoint['auth_method']}</p>
                <p><strong>Account ID:</strong> {working_endpoint['account_id']}</p>
                <p><strong>Balance:</strong> {working_endpoint['balance']} {working_endpoint['currency']}</p>
                <p><strong>Broker:</strong> {working_endpoint['broker']}</p>
                <details>
                    <summary>Headers Used</summary>
                    <pre>{json.dumps(working_endpoint['headers'], indent=2)}</pre>
                </details>
                <details>
                    <summary>Raw Response</summary>
                    <pre>{json.dumps(working_endpoint['raw_data'], indent=2)}</pre>
                </details>
            </div>
            """
        else:
            working_html = """
            <div style="background: #dc3545; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h2>❌ NO WORKING ENDPOINT FOUND YET</h2>
                <p>Still testing or all endpoints failed</p>
            </div>
            """
        
        # Test results summary
        results_html = ""
        if test_results:
            status_counts = {}
            for result in test_results:
                status = result['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            results_html = "<h3>Test Results Summary:</h3><ul>"
            for status, count in status_counts.items():
                results_html += f"<li>{status}: {count} endpoints</li>"
            results_html += "</ul>"
        
        # Logs
        logs_html = ""
        for log in test_logs[-30:]:
            log_color = "#ffffff"
            if "🎉" in log or "SUCCESS" in log:
                log_color = "#28a745"
            elif "❌" in log or "Error" in log:
                log_color = "#dc3545"
            elif "🧪" in log:
                log_color = "#17a2b8"
            elif "🔐" in log:
                log_color = "#ffc107"
            
            logs_html += f'<div style="color: {log_color}; font-family: monospace; margin: 2px 0; font-size: 0.9em;">{log}</div>'
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🔍 cTrader Endpoint Tester</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            margin: 0;
            padding: 20px;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{
            text-align: center;
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }}
        .logs {{
            background: rgba(0,0,0,0.7);
            padding: 20px;
            border-radius: 10px;
            max-height: 400px;
            overflow-y: auto;
            font-family: monospace;
        }}
        .buttons {{
            text-align: center;
            margin: 20px 0;
        }}
        .btn {{
            background: #007bff;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            cursor: pointer;
            margin: 0 10px;
            font-size: 1.1em;
        }}
        .btn:hover {{ background: #0056b3; }}
        details {{ margin: 10px 0; }}
        summary {{ cursor: pointer; font-weight: bold; }}
        pre {{ background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px; overflow-x: auto; }}
    </style>
    <script>
        setTimeout(() => location.reload(), 60000);
        function refresh() {{ location.reload(); }}
        function startTest() {{ window.location.href = '/test'; }}
        function testOAuth() {{ window.location.href = '/oauth'; }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Comprehensive cTrader Endpoint Tester</h1>
            <p>Testing ALL possible cTrader API endpoints</p>
            <p>Last update: {datetime.now().strftime('%H:%M:%S UTC')}</p>
        </div>
        
        <div class="buttons">
            <button class="btn" onclick="startTest()">🧪 Start New Test</button>
            <button class="btn" onclick="testOAuth()">🔐 Test OAuth</button>
            <button class="btn" onclick="refresh()">🔄 Refresh</button>
        </div>
        
        {working_html}
        
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px 0;">
            {results_html}
        </div>
        
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px;">
            <h3>📱 Test Logs:</h3>
            <div class="logs">
                {logs_html}
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    def log_message(self, format, *args):
        pass

def start_server():
    """Start web server"""
    try:
        port = int(os.getenv('PORT', 10000))
        
        log_message(f"🌐 Starting comprehensive tester on port {port}")
        
        server = HTTPServer(('0.0.0.0', port), ComprehensiveHandler)
        
        def run_server():
            server.serve_forever()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        log_message("✅ Server started")
        
    except Exception as e:
        log_message(f"❌ Server error: {e}")

def main():
    """Main function"""
    
    # Start web server
    start_server()
    
    # Wait a moment
    time.sleep(2)
    
    # Start comprehensive testing
    log_message("🚀 Starting comprehensive cTrader endpoint testing...")
    comprehensive_endpoint_test()
    
    # If no working endpoint found, try OAuth
    if not working_endpoint:
        try_oauth_endpoints()
    
    # Keep running
    while True:
        try:
            time.sleep(600)  # 10 minutes
            if not working_endpoint:
                log_message("🔄 Re-running comprehensive test...")
                comprehensive_endpoint_test()
        except KeyboardInterrupt:
            log_message("🛑 Stopped")
            break
        except Exception as e:
            log_message(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
