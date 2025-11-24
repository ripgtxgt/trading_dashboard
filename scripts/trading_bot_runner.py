#!/usr/bin/env python3
"""
Trading Bot Runner - Continuous execution with real KuCoin API data
Integrates live strategy engine with database synchronization
"""

import os
import sys
import time
import signal
import asyncio
from datetime import datetime

# Import trading modules
from kucoin_trader import KuCoinTrader
from live_strategy_engine_rolling import LiveStrategyEngine
from db_integration import DatabaseIntegration
from live_trading_config import KUCOIN_CONFIG, TRADING_CONFIG, SAFETY_CONFIG

# Global flag for graceful shutdown
running = True
engine = None

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    global running, engine
    print("[Trading Bot Runner] Received shutdown signal, stopping...")
    running = False
    if engine:
        engine.emergency_stop = True

def main():
    """Main runner function"""
    global running, engine
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("10U Rolling Strategy Trading Bot - Starting")
    print("=" * 60)
    print(f"Start time: {datetime.now()}")
    print("=" * 60)
    
    # Check KuCoin API configuration
    if not KUCOIN_CONFIG.get('api_key'):
        print("[ERROR] KuCoin API key not configured")
        print("Please edit scripts/live_trading_config.py and set your API credentials")
        return 1
    
    # Check if sandbox mode
    if KUCOIN_CONFIG.get('sandbox', False):
        print("[WARNING] Running in SANDBOX mode")
        print("To use real trading, set 'sandbox': False in live_trading_config.py")
    else:
        print("[INFO] Running in LIVE TRADING mode")
        print("[WARNING] Real money will be used!")
    
    # Initialize database integration
    try:
        db = DatabaseIntegration(enable_websocket=True)
        print("[Trading Bot] Database integration initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")
        print("[WARNING] Continuing without database sync...")
        db = None
    
    # Initialize KuCoin trader
    try:
        trader = KuCoinTrader(config=KUCOIN_CONFIG)
        print("[Trading Bot] KuCoin trader initialized")
        
        # Get initial balance
        balance = trader.get_balance()
        if balance:
            print(f"[Trading Bot] Account balance: {balance} USDT")
        else:
            print("[ERROR] Failed to get account balance")
            return 1
            
    except Exception as e:
        print(f"[ERROR] Failed to initialize trader: {e}")
        return 1
    
    # Initialize strategy engine
    try:
        initial_capital = TRADING_CONFIG.get('initial_capital', 10)
        engine = LiveStrategyEngine(trader=trader, initial_capital=initial_capital)
        print(f"[Trading Bot] Strategy engine initialized with {initial_capital} USDT")
        print(f"[Trading Bot] Current stage: {engine.rolling_manager.get_current_stage(engine.capital).name}")
    except Exception as e:
        print(f"[ERROR] Failed to initialize strategy engine: {e}")
        return 1
    
    # Update bot status in database
    if db:
        try:
            db.update_bot_status(
                status='running',
                balance=engine.capital,
                profit_rate=0.0,
                stage=engine.rolling_manager.get_current_stage(engine.capital).name,
                symbol=engine.symbol
            )
        except Exception as e:
            print(f"[WARNING] Failed to update bot status: {e}")
    
    # Main trading loop
    print("=" * 60)
    print("[Trading Bot] Starting main trading loop...")
    print("Bot is now running. Press Ctrl+C to stop.")
    print("=" * 60)
    
    cycle_count = 0
    
    while running:
        try:
            cycle_count += 1
            print(f"\n[Cycle {cycle_count}] {datetime.now()}")
            
            # Run one trading cycle
            result = engine.run_cycle()
            
            if result:
                print(f"[Cycle {cycle_count}] Status: {result.get('status')}")
                print(f"  Capital: {result.get('capital', 0):.2f} USDT")
                print(f"  Stage: {result.get('stage', 'Unknown')}")
                
                if result.get('has_position'):
                    print(f"  Position: {result.get('position_side', 'N/A')}")
                    print(f"  Unrealized PnL: {result.get('unrealized_pnl', 0):.2f} USDT")
                else:
                    print(f"  Position: None")
                
                # Update database
                if db:
                    try:
                        # Update bot status
                        db.update_bot_status(
                            status='running',
                            balance=result.get('capital', 0),
                            profit_rate=((result.get('capital', 0) - initial_capital) / initial_capital * 100),
                            stage=result.get('stage', 'Unknown'),
                            symbol=engine.symbol
                        )
                        
                        # Update position if exists
                        if result.get('has_position'):
                            position = engine.rolling_manager.position
                            if position:
                                db.update_position(
                                    symbol=engine.symbol,
                                    direction=position.side,
                                    entry_price=position.entry_price,
                                    quantity=position.size,
                                    current_price=result.get('current_price', 0)
                                )
                        else:
                            # Clear position
                            db.update_position(
                                symbol=engine.symbol,
                                direction=None,
                                entry_price=0,
                                quantity=0,
                                current_price=0
                            )
                    except Exception as e:
                        print(f"[WARNING] Failed to update database: {e}")
            
            # Wait for next cycle (check_interval seconds)
            wait_time = engine.check_interval
            print(f"[Cycle {cycle_count}] Waiting {wait_time} seconds until next cycle...")
            
            # Sleep in small increments to allow graceful shutdown
            for _ in range(wait_time):
                if not running:
                    break
                time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n[Trading Bot] Keyboard interrupt received")
            break
        except Exception as e:
            print(f"[ERROR] Error in trading cycle: {e}")
            import traceback
            traceback.print_exc()
            print("[Trading Bot] Waiting 60 seconds before retry...")
            time.sleep(60)
    
    # Cleanup and shutdown
    print("\n" + "=" * 60)
    print("[Trading Bot] Shutting down...")
    print("=" * 60)
    
    try:
        # Get final status
        status = engine.get_status()
        print(f"Final capital: {status.get('capital', 0):.2f} USDT")
        print(f"Total trades: {status.get('total_trades', 0)}")
        
        if status.get('total_trades', 0) > 0:
            print(f"Win rate: {status.get('win_rate', 0):.1f}%")
        
        # Close any open position
        if status.get('has_position'):
            print("[Trading Bot] Closing open position...")
            engine.close_position(reason="Bot shutdown")
        
        # Update database
        if db:
            try:
                db.update_bot_status(
                    status='stopped',
                    balance=status.get('capital', 0),
                    profit_rate=((status.get('capital', 0) - initial_capital) / initial_capital * 100),
                    stage=status.get('stage', 'Unknown'),
                    symbol=engine.symbol
                )
            except Exception as e:
                print(f"[WARNING] Failed to update final status: {e}")
        
        # Close database connection
        if db:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] Error during cleanup: {e}")
    
    print("[Trading Bot] Stopped")
    return 0

if __name__ == "__main__":
    sys.exit(main())
