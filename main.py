import os
import json
import urllib.request
from datetime import datetime

# Global variables
test_result = "Not tested yet"
connection_info = {}

def test_connection():
    global test_result, connection_info
    
    print("Testing cTrader connection...")
    
    token = os.getenv('CTRADER_ACCESS_TOKEN', '').strip()
    if not token:
        test_result = "No access token"
        print("ERROR: No access token found")
        return
    
    print(f"Token found: {len(token)} characters")
    
    # Test the most basic endpoint
    url = "https://openapi.ctrader.com/v1/accounts"
    
    try:
        headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
        request = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                if data and len(data) > 0:
                    account = data[0]
                    test_result = "SUCCESS"
                    connection_info = {
                        'account_id': account.get('accountId', 'Unknown'),
                        'balance': account.get('balance', 0),
                        'broker': account.get('brokerName', 'Unknown')
                    }
                    print(f"SUCCESS! Account: {connection_info['account_id']}")
                    print(f"Balance: {connection_info['balance']}")
                    print(f"Broker: {connection_info['broker']}")
                else:
                    test_result = "No accounts found"
                    print("ERROR: No accounts in response")
            else:
                test_result = f"HTTP {response.status}"
                print(f"ERROR: HTTP {response.status}")
    
    except urllib.error.HTTPError as e:
        test_result = f"HTTP Error {e.code}"
        print(f"ERROR: HTTP {e.code} - {e.reason}")
    except Exception as e:
        test_result = f"Error: {str(e)}"
        print(f"ERROR: {e}")

def app(environ, start_response):
    """Simple WSGI app for Railway"""
    
    path = environ.get('PATH_INFO', '/')
    
    if path == '/test':
        test_connection()
    
    # Generate simple HTML
    html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>cTrader Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #2c3e50; color: white; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        .status {{ padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center; font-size: 1.5em; }}
        .success {{ background: #27ae60; }}
        .error {{ background: #e74c3c; }}
        .pending {{ background: #f39c12; }}
        .btn {{ background: #3498db; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 1.1em; }}
        .info {{ background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔌 cTrader Connection Test</h1>
        <p>Testing connection to cTrader API</p>
        <p>Time: {datetime.now().strftime('%H:%M:%S UTC')}</p>
        
        <div class="status {'success' if test_result == 'SUCCESS' else 'error' if 'Error' in test_result or 'HTTP' in test_result else 'pending'}">
            Status: {test_result}
        </div>
        
        {"<div class='info'><h3>Connection Details:</h3><p>Account: " + connection_info.get('account_id', 'Unknown') + "</p><p>Balance: " + str(connection_info.get('balance', 0)) + "</p><p>Broker: " + connection_info.get('broker', 'Unknown') + "</p></div>" if connection_info else ""}
        
        <div style="text-align: center;">
            <button class="btn" onclick="location.href='/test'">Run Test</button>
            <button class="btn" onclick="location.reload()">Refresh</button>
        </div>
        
        <div class="info">
            <h3>Credentials:</h3>
            <p>Access Token: {"Found (" + str(len(os.getenv('CTRADER_ACCESS_TOKEN', ''))) + " chars)" if os.getenv('CTRADER_ACCESS_TOKEN') else "Missing"}</p>
            <p>Account ID: {os.getenv('CTRADER_ACCOUNT_ID', 'Missing')}</p>
        </div>
    </div>
</body>
</html>
    '''
    
    status = '200 OK'
    headers = [('Content-Type', 'text/html')]
    start_response(status, headers)
    return [html.encode('utf-8')]

if __name__ == "__main__":
    print("Starting cTrader test...")
    test_connection()
    
    # Start server
    from wsgiref.simple_server import make_server
    port = int(os.getenv('PORT', 8000))
    httpd = make_server('0.0.0.0', port, app)
    print(f"Server running on port {port}")
    httpd.serve_forever()
