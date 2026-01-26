#!/usr/bin/env python3
"""
Test script to verify MT5 data loading and EMA calculation.
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.market import test_mt5_data

if __name__ == "__main__":
    print("🧪 Testing MT5 Data Loader")
    print("=" * 50)
    
    market = test_mt5_data()
    
    if market:
        # Verify we have enough data for backtesting
        candle_count = market.get_candle_count()
        print(f"\n📈 Total candles loaded: {candle_count}")
        print(f"📅 Days of data: {candle_count / (24 * 60):.1f} days")
        
        if candle_count < 10000:
            print("⚠️  Warning: Less than 10,000 candles (about 7 days)")
            print("   Consider exporting more data for meaningful backtesting")
        else:
            print("✅ Sufficient data for backtesting")
    else:
        print("\n❌ Failed to load data. Please check the file path and format.")
