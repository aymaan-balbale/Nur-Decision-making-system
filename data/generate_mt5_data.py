#!/usr/bin/env python3
"""
Generate synthetic XAUUSD M1 data in MT5 CSV format.
This creates realistic price movements for development and testing.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_xauusd_data(days=30, start_price=2030.0):
    """
    Generate synthetic XAUUSD M1 data.
    
    Args:
        days: Number of trading days to generate
        start_price: Starting price for XAUUSD
    
    Returns:
        DataFrame with MT5-format data
    """
    
    # XAUUSD trades 24/5 (Monday 00:00 to Friday 23:59)
    minutes_per_day = 24 * 60
    total_minutes = days * minutes_per_day
    
    # Generate timestamps
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    timestamps = [start_date + timedelta(minutes=i) for i in range(total_minutes)]
    
    # Remove weekends (keep only Monday-Friday)
    # In reality, XAUUSD trades Friday 23:59 to Sunday 23:59 is closed, but we'll simplify
    timestamps = [ts for ts in timestamps if ts.weekday() < 5]
    
    # Generate price movements
    prices = []
    current_price = start_price
    
    for i in range(len(timestamps)):
        # Time-based volatility (higher during London/NY overlap)
        hour = timestamps[i].hour
        if 13 <= hour <= 17:  # London/NY overlap
            volatility = 0.0015  # 0.15%
        elif 8 <= hour <= 12:  # London session
            volatility = 0.0010  # 0.10%
        elif 18 <= hour <= 22:  # NY session
            volatility = 0.0012  # 0.12%
        else:  # Asian session
            volatility = 0.0005  # 0.05%
        
        # Random walk with drift
        change = np.random.normal(0.00001, volatility)  # Slight upward drift
        current_price = current_price * (1 + change)
        
        # Add some spikes (news events)
        if random.random() < 0.001:  # 0.1% chance of news spike
            spike = np.random.choice([-1, 1]) * volatility * 5
            current_price = current_price * (1 + spike)
        
        # Ensure price stays in reasonable range
        current_price = max(1950.0, min(2100.0, current_price))
        
        prices.append(current_price)
    
    # Create OHLC data from prices
    data = []
    
    for i in range(len(timestamps)):
        base_price = prices[i]
        
        # Create realistic candle ranges
        if random.random() < 0.7:  # 70% normal candles
            candle_range = base_price * 0.0003  # 0.03% range
        else:  # 30% wider candles
            candle_range = base_price * 0.0008  # 0.08% range
        
        # Generate OHLC
        open_price = base_price
        high_price = open_price + abs(np.random.normal(0, candle_range/2))
        low_price = open_price - abs(np.random.normal(0, candle_range/2))
        close_price = low_price + abs(high_price - low_price) * random.random()
        
        # Ensure proper ordering
        prices_sorted = sorted([open_price, high_price, low_price, close_price])
        low_price = prices_sorted[0]
        high_price = prices_sorted[3]
        
        # Adjust open/close to be within range
        open_price = np.random.uniform(low_price + (high_price - low_price) * 0.3, 
                                       low_price + (high_price - low_price) * 0.7)
        close_price = np.random.uniform(low_price + (high_price - low_price) * 0.3, 
                                        low_price + (high_price - low_price) * 0.7)
        
        # Volume (tick volume)
        if 13 <= hour <= 17:  # High volume during overlap
            tick_vol = random.randint(100, 300)
        else:
            tick_vol = random.randint(20, 150)
        
        # Spread (typical XAUUSD spread)
        spread = random.choice([10, 15, 20, 25, 30])
        
        data.append({
            'timestamp': timestamps[i],
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'tick_vol': tick_vol,
            'real_vol': 0,  # MT5 often has 0 for real volume in forex
            'spread': spread
        })
    
    return pd.DataFrame(data)

def save_mt5_format(df, filename):
    """
    Save DataFrame in exact MT5 CSV format.
    
    MT5 format:
    "<DATE> <TIME>";<OPEN>;<HIGH>;<LOW>;<CLOSE>;<TICK VOL>;<VOL>;<SPREAD>
    "2024.01.01 00:00";2030.50;2030.80;2029.90;2030.20;150;0;15
    """
    
    # Format timestamp as MT5 expects
    df['timestamp_str'] = df['timestamp'].dt.strftime('"%Y.%m.%d %H:%M"')
    
    # Create the CSV content
    mt5_lines = []
    
    # Header
    mt5_lines.append('<TICKER>;<PER>;<DATE>;<TIME>;<OPEN>;<HIGH>;<LOW>;<CLOSE>;<VOL>')
    
    # Data rows
    for _, row in df.iterrows():
        line = f'{row["timestamp_str"]};{row["open"]};{row["high"]};{row["low"]};{row["close"]};{row["tick_vol"]};{row["real_vol"]};{row["spread"]}'
        mt5_lines.append(line)
    
    # Write to file
    with open(filename, 'w') as f:
        f.write('\n'.join(mt5_lines))
    
    print(f"✅ Generated {len(df)} candles")
    print(f"📁 Saved to: {filename}")
    print(f"📅 Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"💰 Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")

def main():
    """Main function to generate and save data"""
    
    print("🎲 Generating Synthetic XAUUSD M1 Data")
    print("=" * 50)
    
    # Generate 60 days of data (about 2 months)
    print("Generating 60 days of XAUUSD M1 data...")
    df = generate_xauusd_data(days=60, start_price=2030.0)
    
    # Save in MT5 format
    output_file = "historical_xauusd_m1.csv"
    save_mt5_format(df, output_file)
    
    # Show sample
    print("\n📊 Sample data (first 5 rows):")
    print(df[['timestamp', 'open', 'high', 'low', 'close']].head())
    
    # Create a simple plot of closing prices
    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(12, 6))
        plt.plot(df['timestamp'], df['close'], linewidth=0.5, alpha=0.7)
        plt.title('Synthetic XAUUSD M1 Data')
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('data/xauusd_sample_plot.png', dpi=100)
        print("📈 Chart saved: data/xauusd_sample_plot.png")
    except:
        print("⚠️  matplotlib not installed, skipping chart generation")
        print("   Install with: pip install matplotlib")

if __name__ == "__main__":
    main()
