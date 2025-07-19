#!/usr/bin/env python3

import json
import time
import os
import urllib.request
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Simple global variables
logs = []
status = "Starting..."
connection_info = {}

def add_log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    logs.append(log_entry)
    print(log_entry)
    if len(logs) > 30:
        logs[:] = logs[-30:]

def test_ctrader():
    global status, connection_info
    
    add_log("Testing cTrader connection...")
    
    # Get token from environment
    token = os.getenv('CTRADER_ACCESS_TOKEN', '').strip()
    account = os.getenv('CTRADER_ACCOUNT_ID', '').strip()
    
    add_log(f"Token: {'Found' if token else 'Missing'} ({len(token)} chars)")
    add_log(f"Account: {account if account else 'Missing'}")
    
    if not token:
        status = "No Token"
        add_log("Cannot test - no access token")
        return
    
    # Test endpoints
    endpoints = [
        "https://openapi.ctrader.com/v1/accounts",
        "https://demo-openapi.ctrader.com/v1/accounts",
        "https://openapi.ctrader.com/accounts", 
        "https://demo-openapi.ctrader.com/accounts"
    ]
    
    for url in endpoints:
        try:
            add_log(f"Testing: {url}")
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }
            
            request = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    
                    if isinstance(data, list) and len(data) > 0:
                        account_data = data[0]
                        
                        status = "Connected"
                        connection_info = {
                            'account_id': account_data.get('accountId', 'Unknown'),
                            'balance': account_data.get('balance', 0),
                            'currency': account_data.get('currency', 'USD'),
                            'broker': account_data.get('brokerName', 'Unknown'),
                            'url': url
                        }
                        
                        add_log("SUCCESS!")
                        add_log(f"Account: {connection_info['account_id']}")
                        add_log(f"Balance: {connection_info['balance']} {connection_info['currency']}")
                        add_log(f"Broker: {connection_info['broker']}")
                        
                        return
                    else:
                        add_log("No accounts found")
                else:
                    add_log(f"HTTP {response.status}")
        
        except urllib.error.HTTPError as e:
            add_log(f"HTTP Error {e.code}")
        except Exception as e:
            add_log(f"Error: {e}")
    
    status = "Failed"
    add_log("All endpoints failed")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            html = self.get_page()
        elif self.path == '/test':
            test_ctrader()
            html = '<h1>Test Started</h1><a href="/">Back</a>'
        else:
            html = '<h1>cTrader Test</h1><a href="/">Home</a>'
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def get_page(self):
        # Status color
        if status == "Connected":
            color = "#28a745"
        elif status == "Failed":
            color = "#dc3545"
        else:
            color = "#ffc107"
        
        # Connection details
        details = ""
        if connection_info:
            details = f"""
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 20px 0;">
                <h3>Connection Details:</h3>
                <p>Account: {connection_info.get('account_id', 'Unknown')}</p>
                <p>Balance: {connection_info.get('balance', 0)} {connection_info.get('currency', 'USD')}</p>
                <p>Broker: {connection_info.get('broker', 'Unknown')}</p>
                <p>URL: {connection_info.get('url', 'Unknown')}</p>
            </div>
            """
        
        # Logs
        log_html = ""
        for log in logs:
            if "SUCCESS" in log:
                log_color = "#28a745"
            elif "Error" in log or "Failed" in log:
                log_color = "#dc3545"
            else:
                log_color = "#ffffff"
            
            log_html += f'<div style="color: {log_color}; font-family: monospace; margin: 2px 0;">{log}</div>'
        
        html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>cTrader Test</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            margin: 0;
            padding: 20px;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{
            text-align: center;
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }}
        .status {{
            background: {color};
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 30px;
        }}
        .logs {{
            background: rgba(0,0,0,0.5);
            padding: 20px;
            border-radius: 10px;
            max-height: 300px;
            overflow-y: auto;
        }}
        .btn {{
            background: #007bff;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            cursor: pointer;
            margin: 10px;
            font-size: 1.1em;
        }}
    </style>
    <script>
        setTimeout(() => location.reload(), 30000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>cTrader Connection Test</h1>
            <p>Simple cTrader API Testing</p>
            <p>Last check: {datetime.now().strftime('%H:%M:%S UTC')}</p>
        </div>
        
        <div class="status">Status: {status}</div>
        
        {details}
        
        <div style="text-align: center;">
            <button class="btn" onclick="location.href='/test'">Run Test</button>
            <button class="btn" onclick="location.reload()">Refresh</button>
        </div>
        
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin-top: 30px;">
            <h3>Logs:</h3>
            <div class="logs">
                {log_html}
            </div>
        </div>
    </div>
</body>
</html>
        '''
        
        return html
    
    def log_message(self, format, *args):
        pass

def main():
    add_log("Starting simple cTrader test...")
    
    # Start server
    port = int(os.getenv('PORT', 10000))
    
    add_log(f"Starting server on port {port}")
    
    server = HTTPServer(('0.0.0.0', port), Handler)
    
    add_log("Server started")
    
    # Test connection once
    test_ctrader()
    
    # Run server
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        add_log("Stopped")

if __name__ == "__main__":
    main()
