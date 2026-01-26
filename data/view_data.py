#!/usr/bin/env python3
"""
Visualize the generated data and EMA.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.market import MT5MarketData
import matplotlib.pyplot as plt

def visualize_data():
    """Load and visualize the synthetic data"""
    
    data_path = "data/historical_xauusd_m1.csv"
    
    if not os.path.exists(data_path):
        print("❌ Data file not found")
        return
    
    # Load data
    market = MT5MarketData(data_path)
    if not market.load_data():
        return
    
    market.calculate_ema_mt5()
    df = market.get_dataframe()
    
    # Filter to remove NaN values for EMA
    df_valid = df[df['ema_200'].notna()]
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), height_ratios=[3, 1])
    
    # Plot 1: Price and EMA
    ax1.plot(df_valid.index, df_valid['close'], label='Close Price', 
             linewidth=0.5, alpha=0.7, color='blue')
    ax1.plot(df_valid.index, df_valid['ema_200'], label='EMA 200', 
             linewidth=1.5, alpha=0.9, color='red')
    ax1.set_title('XAUUSD M1 - Price with 200 EMA (Synthetic Data)')
    ax1.set_ylabel('Price (USD)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add buy/sell signals example
    # Find where price crosses EMA
    df_valid['above_ema'] = df_valid['close'] > df_valid['ema_200']
    df_valid['cross_above'] = (df_valid['above_ema'] == True) & (df_valid['above_ema'].shift(1) == False)
    df_valid['cross_below'] = (df_valid['above_ema'] == False) & (df_valid['above_ema'].shift(1) == True)
    
    buy_signals = df_valid[df_valid['cross_above']]
    sell_signals = df_valid[df_valid['cross_below']]
    
    ax1.scatter(buy_signals.index, buy_signals['close'], 
                color='green', s=30, marker='^', label='Potential Buy', zorder=5)
    ax1.scatter(sell_signals.index, sell_signals['close'], 
                color='red', s=30, marker='v', label='Potential Sell', zorder=5)
    
    # Plot 2: Volume
    ax2.bar(df_valid.index, df_valid['tick_vol'], alpha=0.5, color='gray')
    ax2.set_title('Tick Volume')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Volume')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save and show
    output_path = "data/data_visualization.png"
    plt.savefig(output_path, dpi=120)
    print(f"📈 Visualization saved to: {output_path}")
    
    # Show some statistics
    print("\n📊 Data Statistics:")
    print(f"Total candles: {len(df)}")
    print(f"Candles with EMA: {len(df_valid)}")
    print(f"Buy signals (cross above EMA): {len(buy_signals)}")
    print(f"Sell signals (cross below EMA): {len(sell_signals)}")
    print(f"Average daily candles: {len(df_valid) / 60:.1f}")
    
    plt.show()

if __name__ == "__main__":
    visualize_data()
