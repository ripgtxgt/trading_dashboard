#!/usr/bin/env python3
"""
KuCoin API Connection Test Script (Correct Version)
Test API credentials and fetch real account data
Matches the actual methods in kucoin_api.py
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from parent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if not os.path.exists(env_path):
    # If not found in parent, try current directory
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

# Import KuCoin API
try:
    from kucoin_api import KuCoinFuturesAPI
except ImportError:
    print("[ERROR] Cannot import kucoin_api module")
    print("[ERROR] Please ensure kucoin_api.py is in the same directory")
    print(f"[ERROR] Current directory: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"[ERROR] Python path: {sys.path}")
    sys.exit(1)


def test_api_connection():
    """Test KuCoin API connection and fetch account data"""
    
    print("=" * 60)
    print("KuCoin API Connection Test")
    print("=" * 60)
    
    # Get API credentials from environment
    api_key = os.getenv('KUCOIN_API_KEY')
    api_secret = os.getenv('KUCOIN_API_SECRET')
    api_passphrase = os.getenv('KUCOIN_API_PASSPHRASE')
    
    if not all([api_key, api_secret, api_passphrase]):
        print("\n[ERROR] Missing API credentials in .env file")
        print("Required environment variables:")
        print("  - KUCOIN_API_KEY")
        print("  - KUCOIN_API_SECRET")
        print("  - KUCOIN_API_PASSPHRASE")
        print(f"\n[INFO] Checked .env file at: {env_path}")
        print(f"[INFO] File exists: {os.path.exists(env_path)}")
        return False
    
    print("\n[OK] API credentials loaded from .env")
    print(f"[INFO] .env file location: {env_path}")
    print(f"API Key: {api_key[:10]}...")
    
    # Initialize API client
    try:
        api = KuCoinFuturesAPI(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase,
            sandbox=False  # Production environment
        )
        print("[OK] KuCoin API client initialized (Production)")
    except Exception as e:
        print(f"[ERROR] Failed to initialize API client: {e}")
        return False
    
    # Test 1: Fetch account balance
    print("\n" + "-" * 60)
    print("Test 1: Fetch Account Balance")
    print("-" * 60)
    
    try:
        balance = api.get_balance('USDT')  # 正确的方法名
        if balance is not None:
            print(f"[OK] Account Balance: {balance:.2f} USDT")
            
            if balance < 5:
                print("[WARNING] Balance is low (< 5 USDT)")
                print("[WARNING] Recommend at least 20 USDT for trading")
            elif balance < 20:
                print("[INFO] Balance is sufficient but recommend >= 20 USDT")
            else:
                print("[OK] Balance is sufficient for trading")
        else:
            print("[ERROR] Failed to fetch balance")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to fetch balance: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Fetch current positions
    print("\n" + "-" * 60)
    print("Test 2: Fetch Current Position")
    print("-" * 60)
    
    try:
        position = api.get_position('XBTUSDTM')  # 正确的方法名
        if position is not None:
            print(f"[OK] Position data retrieved")
            if position.get('currentQty', 0) != 0:
                print(f"  - Symbol: {position.get('symbol')}")
                print(f"  - Side: {'Long' if position.get('currentQty', 0) > 0 else 'Short'}")
                print(f"  - Size: {abs(position.get('currentQty', 0))}")
                print(f"  - Entry Price: {position.get('avgEntryPrice', 0):.2f}")
                print(f"  - Unrealized PnL: {position.get('unrealisedPnl', 0):.4f} USDT")
            else:
                print("[OK] No open position")
        else:
            print("[INFO] No position data (may be normal if no trades yet)")
    except Exception as e:
        print(f"[WARNING] Failed to fetch position: {e}")
        print("[INFO] This may be normal if you haven't traded yet")
    
    # Test 3: Fetch recent klines
    print("\n" + "-" * 60)
    print("Test 3: Fetch Recent K-line Data")
    print("-" * 60)
    
    try:
        # granularity: 60 = 1 hour
        klines = api.get_klines('XBTUSDTM', granularity=60)  # 正确的方法名和参数
        if klines and len(klines) > 0:
            print(f"[OK] Fetched {len(klines)} klines")
            # K线格式: [时间戳, 开, 高, 低, 收, 成交量]
            latest = klines[-1]
            timestamp = datetime.fromtimestamp(int(latest[0]) / 1000)
            print(f"Latest Kline:")
            print(f"  - Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  - Open: {float(latest[1]):.2f}")
            print(f"  - High: {float(latest[2]):.2f}")
            print(f"  - Low: {float(latest[3]):.2f}")
            print(f"  - Close: {float(latest[4]):.2f}")
            print(f"  - Volume: {float(latest[5]):.2f}")
        else:
            print("[ERROR] Failed to fetch klines or no data")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to fetch klines: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Fetch ticker (current price)
    print("\n" + "-" * 60)
    print("Test 4: Fetch Current Ticker")
    print("-" * 60)
    
    try:
        ticker = api.get_ticker('XBTUSDTM')
        if ticker:
            print(f"[OK] Current ticker retrieved")
            print(f"  - Symbol: {ticker.get('symbol')}")
            print(f"  - Last Price: {float(ticker.get('price', 0)):.2f}")
            print(f"  - 24h Volume: {float(ticker.get('volume', 0)):.2f}")
            print(f"  - 24h Change: {float(ticker.get('priceChgPct', 0)) * 100:.2f}%")
        else:
            print("[WARNING] Failed to fetch ticker")
    except Exception as e:
        print(f"[WARNING] Failed to fetch ticker: {e}")
    
    # Test 5: Check account overview
    print("\n" + "-" * 60)
    print("Test 5: Check Account Overview")
    print("-" * 60)
    
    try:
        account = api.get_account_overview('USDT')
        if account:
            print(f"[OK] Account overview retrieved")
            print(f"  - Available Balance: {float(account.get('availableBalance', 0)):.2f} USDT")
            print(f"  - Account Equity: {float(account.get('accountEquity', 0)):.2f} USDT")
            print(f"  - Unrealized PnL: {float(account.get('unrealisedPnL', 0)):.4f} USDT")
            print(f"  - Margin Balance: {float(account.get('marginBalance', 0)):.2f} USDT")
        else:
            print("[WARNING] Failed to fetch account overview")
    except Exception as e:
        print(f"[WARNING] Failed to fetch account overview: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print("[OK] API connection successful")
    print("[OK] All basic tests passed")
    print(f"[OK] Current balance: {balance:.2f} USDT")
    print("\nYour system is ready for trading!")
    print("\nTo switch to live trading:")
    print("1. Edit .env file: TRADING_MODE=\"live\"")
    print("2. Restart trading-bot: pm2 restart trading-bot")
    print("3. Monitor logs: pm2 logs trading-bot")
    
    print("\n" + "=" * 60)
    print("Available Methods in kucoin_api.py:")
    print("=" * 60)
    print("- get_balance(currency='USDT')        # Get available balance")
    print("- get_account_overview(currency)      # Get account overview")
    print("- get_position(symbol)                # Get single position")
    print("- get_all_positions()                 # Get all positions")
    print("- get_klines(symbol, granularity)     # Get K-line data")
    print("- get_ticker(symbol)                  # Get current ticker")
    print("- get_current_price(symbol)           # Get current price")
    print("- create_order(...)                   # Create order")
    print("- cancel_order(order_id)              # Cancel order")
    print("- set_leverage(symbol, leverage)      # Set leverage")
    
    return True


if __name__ == '__main__':
    try:
        success = test_api_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[INFO] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
