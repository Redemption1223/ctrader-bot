#!/usr/bin/env python3
"""
QUICK CTRADER SETUP SCRIPT
Helps you get API credentials in 5 minutes
"""

import webbrowser
import urllib.parse
import json
import urllib.request

def quick_setup():
    print("🚀 Quick cTrader Account Connection Setup")
    print("=" * 50)
    
    print("\n📋 STEP 1: Create cTrader App")
    print("-" * 30)
    print("1. Opening cTrader Apps website...")
    
    # Open cTrader apps page
    webbrowser.open("https://ctrader.com/apps/")
    
    print("2. Click 'Create App' button")
    print("3. Fill in these details:")
    print("   App Name: My Trading Bot")
    print("   Description: Personal trading automation")
    print("   Redirect URI: https://your-app-name.onrender.com/callback")
    print("   Scopes: ✅ Trading ✅ Accounts ✅ Read")
    
    input("\nPress Enter when you've created the app...")
    
    print("\n🔑 STEP 2: Get Your Credentials")
    print("-" * 30)
    client_id = input("Enter your Client ID: ").strip()
    client_secret = input("Enter your Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Both Client ID and Secret are required!")
        return
    
    print("\n🔐 STEP 3: Get Access Token")
    print("-" * 30)
    
    # Build OAuth URL
    redirect_uri = "https://your-app-name.onrender.com/callback"
    scope = "trading accounts"
    
    auth_url = (
        f"https://openapi.ctrader.com/apps/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        f"scope={urllib.parse.quote(scope)}&"
        f"response_type=code"
    )
    
    print("Opening authorization page...")
    webbrowser.open(auth_url)
    
    print("\nFollow these steps:")
    print("1. Login to your cTrader account")
    print("2. Authorize the application")
    print("3. Copy the 'code' from the redirect URL")
    print("   (Look for: ?code=XXXXX in the address bar)")
    
    auth_code = input("\nEnter the authorization code: ").strip()
    
    if not auth_code:
        print("❌ Authorization code is required!")
        return
    
    print("\n🔄 STEP 4: Exchange for Tokens")
    print("-" * 30)
    
    try:
        # Exchange code for tokens
        token_data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri
        }
        
        data = urllib.parse.urlencode(token_data).encode()
        request = urllib.request.Request(
            'https://openapi.ctrader.com/apps/token', 
            data=data, 
            method='POST'
        )
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.loads(response.read().decode())
            
            if 'access_token' in result:
                access_token = result['access_token']
                refresh_token = result.get('refresh_token', '')
                
                print("✅ Tokens received successfully!")
                
                # Get account info
                print("\n📊 STEP 5: Get Account Information")
                print("-" * 30)
                
                try:
                    account_request = urllib.request.Request(
                        'https://openapi.ctrader.com/v2/accounts'
                    )
                    account_request.add_header('Authorization', f'Bearer {access_token}')
                    account_request.add_header('Accept', 'application/json')
                    
                    with urllib.request.urlopen(account_request, timeout=10) as acc_response:
                        accounts = json.loads(acc_response.read().decode())
                        
                        if accounts and len(accounts) > 0:
                            account = accounts[0]
                            account_id = str(account.get('accountId', ''))
                            broker = account.get('brokerName', 'Unknown')
                            balance = account.get('balance', 0)
                            currency = account.get('currency', 'USD')
                            acc_type = account.get('accountType', 'Unknown')
                            
                            print(f"✅ Account found!")
                            print(f"   Account ID: {account_id}")
                            print(f"   Broker: {broker}")
                            print(f"   Balance: {balance} {currency}")
                            print(f"   Type: {acc_type}")
                        else:
                            account_id = input("No accounts found. Enter your Account ID manually: ").strip()
                
                except Exception as e:
                    print(f"⚠️ Couldn't fetch account info: {e}")
                    account_id = input("Enter your Account ID manually: ").strip()
                
                # Display final credentials
                print("\n🎉 SUCCESS! Your cTrader Credentials:")
                print("=" * 60)
                print("Copy these to your Render environment variables:")
                print()
                print(f"CTRADER_CLIENT_ID={client_id}")
                print(f"CTRADER_CLIENT_SECRET={client_secret}")
                print(f"CTRADER_ACCESS_TOKEN={access_token}")
                print(f"CTRADER_REFRESH_TOKEN={refresh_token}")
                print(f"CTRADER_ACCOUNT_ID={account_id}")
                print("DEMO_MODE=false")
                print("MAX_DAILY_TRADES=20")
                print("RISK_PERCENTAGE=0.02")
                print("=" * 60)
                
                print("\n📋 NEXT STEPS:")
                print("1. Go to your Render dashboard")
                print("2. Click on your service → Environment tab")
                print("3. Add each variable above")
                print("4. Click 'Save Changes'")
                print("5. Wait 2-3 minutes for redeploy")
                print("6. Refresh your dashboard")
                print("7. See 'REAL ACCOUNT VERIFIED' instead of 'SIMULATION MODE'!")
                
                # Save to file
                try:
                    with open('ctrader_credentials.txt', 'w') as f:
                        f.write("# cTrader Bot Credentials\n")
                        f.write("# Copy these to Render environment variables\n\n")
                        f.write(f"CTRADER_CLIENT_ID={client_id}\n")
                        f.write(f"CTRADER_CLIENT_SECRET={client_secret}\n")
                        f.write(f"CTRADER_ACCESS_TOKEN={access_token}\n")
                        f.write(f"CTRADER_REFRESH_TOKEN={refresh_token}\n")
                        f.write(f"CTRADER_ACCOUNT_ID={account_id}\n")
                        f.write("DEMO_MODE=false\n")
                        f.write("MAX_DAILY_TRADES=20\n")
                        f.write("RISK_PERCENTAGE=0.02\n")
                    
                    print(f"\n💾 Credentials saved to: ctrader_credentials.txt")
                    
                except Exception as e:
                    print(f"⚠️ Couldn't save file: {e}")
                
            else:
                print(f"❌ Token exchange failed: {result}")
                
    except Exception as e:
        print(f"❌ Error getting tokens: {e}")
        print("\nTry the manual setup instead:")
        print("1. Go to https://ctrader.com/apps/")
        print("2. Create your app")
        print("3. Use OAuth playground for tokens")

def quick_test():
    """Test existing credentials"""
    print("🧪 Quick Test Existing Credentials")
    print("=" * 40)
    
    access_token = input("Enter your access token to test: ").strip()
    
    if not access_token:
        print("❌ Access token required for testing")
        return
    
    try:
        request = urllib.request.Request('https://openapi.ctrader.com/v2/accounts')
        request.add_header('Authorization', f'Bearer {access_token}')
        request.add_header('Accept', 'application/json')
        
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status == 200:
                accounts = json.loads(response.read().decode())
                
                print("✅ API connection successful!")
                print(f"📊 Found {len(accounts)} account(s)")
                
                for i, account in enumerate(accounts):
                    print(f"\nAccount {i+1}:")
                    print(f"  ID: {account.get('accountId', 'Unknown')}")
                    print(f"  Broker: {account.get('brokerName', 'Unknown')}")
                    print(f"  Balance: {account.get('balance', 0)} {account.get('currency', 'USD')}")
                    print(f"  Type: {account.get('accountType', 'Unknown')}")
                
                print("\n🎯 Your credentials are working!")
                print("Set them in Render to connect your bot.")
                
            else:
                print(f"❌ API test failed: HTTP {response.status}")
                
    except Exception as e:
        print(f"❌ Connection test failed: {e}")

def main():
    print("🔗 cTrader Account Connection Helper")
    print("=" * 40)
    print("1. Get new credentials (full setup)")
    print("2. Test existing credentials")
    print("3. Exit")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == '1':
        quick_setup()
    elif choice == '2':
        quick_test()
    elif choice == '3':
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice")
        main()

if __name__ == "__main__":
    main()
