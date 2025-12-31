#!/usr/bin/env python3
"""
Verify the synthetic data matches MT5 format and structure.
"""

import pandas as pd
import os

def verify_mt5_format():
    """Verify the CSV is in correct MT5 format"""
    
    filepath = "data/historical_xauusd_m1.csv"
    
    if not os.path.exists(filepath):
        print("❌ File not found:", filepath)
        return
    
    # Read the file to check format
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    print("📄 File Structure Verification")
    print("=" * 50)
    print(f"File: {filepath}")
    print(f"Size: {os.path.getsize(filepath) / 1024:.1f} KB")
    print(f"Lines: {len(lines)}")
    
    # Show first 3 lines
    print("\nFirst 3 lines of file:")
    for i in range(min(3, len(lines))):
        print(f"  {i+1}: {lines[i].strip()}")
    
    # Try to load with pandas
    try:
        df = pd.read_csv(filepath, delimiter=';', skiprows=1,
                        names=['timestamp', 'open', 'high', 'low', 'close', 
                               'tick_vol', 'real_vol', 'spread'])
        
        print("\n✅ Successfully parsed as MT5 format")
        print(f"   Candles: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        
        # Check data ranges
        print("\n📊 Data Ranges:")
        print(f"   Timestamp range: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
        print(f"   Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
        print(f"   Average spread: {df['spread'].mean():.1f}")
        
        # Check for any issues
        print("\n🔍 Data Quality Check:")
        
        # Check for NaN values
        nan_count = df.isna().sum().sum()
        if nan_count == 0:
            print("   ✅ No NaN values found")
        else:
            print(f"   ⚠️  Found {nan_count} NaN values")
        
        # Check for zero or negative prices
        invalid_prices = df[(df['open'] <= 0) | (df['high'] <= 0) | 
                           (df['low'] <= 0) | (df['close'] <= 0)]
        if len(invalid_prices) == 0:
            print("   ✅ All prices are positive")
        else:
            print(f"   ⚠️  Found {len(invalid_prices)} invalid prices")
        
        # Check chronological order
        timestamps = pd.to_datetime(df['timestamp'].str.strip('"'), format='%Y.%m.%d %H:%M')
        is_sorted = all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))
        if is_sorted:
            print("   ✅ Timestamps are in chronological order")
        else:
            print("   ⚠️  Timestamps are not sorted")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to parse file: {e}")
        return False

if __name__ == "__main__":
    verify_mt5_format()
