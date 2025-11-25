#!/usr/bin/env python3
"""
Insert test data into trading database for Dashboard testing
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(__file__), 'trading_data.db')

def insert_test_data():
    """Insert sample data for testing Dashboard"""
    print(f"Inserting test data into: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now()
    
    try:
        # Insert bot state
        print("Inserting bot state...")
        cursor.execute('''
            INSERT INTO bot_state (
                timestamp, status, current_balance, initial_balance, 
                total_profit, profit_rate, current_stage, today_trades, 
                total_trades, win_rate, risk_level, market_volatility, 
                suggested_position
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            now.isoformat(),
            'running',
            11.41,
            10.0,
            1.41,
            14.1,
            'stage1',
            2,
            5,
            60.0,
            'low',
            0.15,
            100
        ))
        
        # Insert current position
        print("Inserting current position...")
        cursor.execute('''
            INSERT INTO positions (
                timestamp, symbol, side, size, entry_price, 
                current_price, unrealized_pnl, leverage, margin, 
                liquidation_price
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            now.isoformat(),
            'XBTUSDTM',
            'long',
            0.001,
            95000.0,
            96000.0,
            1.0,
            10,
            9.5,
            85500.0
        ))
        
        # Insert sample trades
        print("Inserting sample trades...")
        trades = [
            (now - timedelta(hours=5), 'XBTUSDTM', 'long', 0.001, 94000.0, 95000.0, 1.0, 1.06, 'closed', 'ma_cross', 'stage1', 'MA5 crossed above MA20'),
            (now - timedelta(hours=10), 'XBTUSDTM', 'long', 0.001, 93000.0, 93500.0, 0.5, 0.54, 'closed', 'ma_cross', 'stage1', 'Take profit'),
            (now - timedelta(hours=15), 'XBTUSDTM', 'long', 0.001, 92000.0, 91500.0, -0.5, -0.54, 'closed', 'ma_cross', 'stage1', 'Stop loss'),
            (now - timedelta(hours=20), 'XBTUSDTM', 'long', 0.001, 91000.0, 92000.0, 1.0, 1.10, 'closed', 'ma_cross', 'stage1', 'Take profit'),
            (now - timedelta(hours=25), 'XBTUSDTM', 'long', 0.001, 90000.0, 90500.0, 0.5, 0.56, 'closed', 'ma_cross', 'stage1', 'Take profit'),
        ]
        
        for trade in trades:
            cursor.execute('''
                INSERT INTO trades (
                    timestamp, symbol, side, size, entry_price, 
                    exit_price, pnl, pnl_rate, status, signal_type, 
                    stage, reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (trade[0].isoformat(), *trade[1:]))
        
        # Insert balance snapshots (last 24 hours)
        print("Inserting balance snapshots...")
        balance = 10.0
        for i in range(24):
            timestamp = now - timedelta(hours=23-i)
            balance += random.uniform(-0.1, 0.2)
            cursor.execute('''
                INSERT INTO balance_snapshots (
                    timestamp, balance, equity, unrealized_pnl, 
                    margin_used, available_balance
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                timestamp.isoformat(),
                balance,
                balance + random.uniform(-0.5, 0.5),
                random.uniform(-0.3, 0.3),
                random.uniform(0, 5),
                balance - random.uniform(0, 5)
            ))
        
        # Insert sample klines (last 100 hours)
        print("Inserting klines...")
        base_price = 90000.0
        for i in range(100):
            timestamp = now - timedelta(hours=99-i)
            open_price = base_price + random.uniform(-500, 500)
            close_price = open_price + random.uniform(-300, 300)
            high_price = max(open_price, close_price) + random.uniform(0, 200)
            low_price = min(open_price, close_price) - random.uniform(0, 200)
            
            cursor.execute('''
                INSERT INTO klines (
                    timestamp, symbol, interval, open, high, low, 
                    close, volume, ma5, ma20
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp.isoformat(),
                'XBTUSDTM',
                '1h',
                open_price,
                high_price,
                low_price,
                close_price,
                random.uniform(1000, 5000),
                close_price + random.uniform(-100, 100),
                close_price + random.uniform(-200, 200)
            ))
            base_price = close_price
        
        # Insert sample signals
        print("Inserting signals...")
        signals = [
            (now - timedelta(hours=5), 'XBTUSDTM', 'long', 94000.0, 93800.0, 93500.0, 'MA5 crossed above MA20', 1),
            (now - timedelta(hours=10), 'XBTUSDTM', 'long', 93000.0, 92800.0, 92500.0, 'MA5 crossed above MA20', 1),
            (now - timedelta(hours=15), 'XBTUSDTM', 'long', 92000.0, 91800.0, 91500.0, 'MA5 crossed above MA20', 1),
        ]
        
        for signal in signals:
            cursor.execute('''
                INSERT INTO signals (
                    timestamp, symbol, signal_type, price, ma5, 
                    ma20, reason, executed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (signal[0].isoformat(), *signal[1:]))
        
        conn.commit()
        print("Test data inserted successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM bot_state")
        bot_state_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM positions")
        positions_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM trades")
        trades_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM balance_snapshots")
        snapshots_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM klines")
        klines_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM signals")
        signals_count = cursor.fetchone()[0]
        
        print(f"\nData summary:")
        print(f"  - bot_state: {bot_state_count} records")
        print(f"  - positions: {positions_count} records")
        print(f"  - trades: {trades_count} records")
        print(f"  - balance_snapshots: {snapshots_count} records")
        print(f"  - klines: {klines_count} records")
        print(f"  - signals: {signals_count} records")
        
    except Exception as e:
        print(f"Error inserting test data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    insert_test_data()
