#!/usr/bin/env python3
"""
Quick view of data - light on memory.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.market import MT5MarketData
import matplotlib.pyplot as plt

def quick_view():
    """Quick visualization of first 1000 candles"""
    
    data_path = "data/historical_xauusd_m1.csv"
    market = MT5MarketData(data_path)
    market.load_data()
    market.calculate_ema_mt5()
    df = market.get_dataframe()
    
    # Take first 1000 candles for quick view
    df_sample = df.iloc[200:1200]  # Skip first 200 for EMA
    
    plt.figure(figsize=(12, 6))
    plt.plot(df_sample.index, df_sample['close'], label='Close', linewidth=0.8, alpha=0.7)
    plt.plot(df_sample.index, df_sample['ema_200'], label='EMA 200', linewidth=1.5, color='red')
    
    # Mark crossings
    above = df_sample['close'] > df_sample['ema_200']
    crossings = (above != above.shift(1))
    buy_points = df_sample[crossings & above]
    sell_points = df_sample[crossings & ~above]
    
    plt.scatter(buy_points.index, buy_points['close'], color='green', 
                s=40, marker='^', label='Buy Signal', zorder=5)
    plt.scatter(sell_points.index, sell_points['close'], color='red', 
                s=40, marker='v', label='Sell Signal', zorder=5)
    
    plt.title('XAUUSD M1 - First 1000 Candles with EMA 200')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('data/quick_view.png', dpi=100)
    print("📈 Quick view saved: data/quick_view.png")
    
    # Statistics
    total_crossings = len(buy_points) + len(sell_points)
    print(f"\n📊 Quick Statistics (first 1000 candles):")
    print(f"Buy signals: {len(buy_points)}")
    print(f"Sell signals: {len(sell_points)}")
    print(f"Total crossings: {total_crossings}")
    print(f"Avg candles between signals: {1000/total_crossings:.1f}")

if __name__ == "__main__":
    quick_view()
