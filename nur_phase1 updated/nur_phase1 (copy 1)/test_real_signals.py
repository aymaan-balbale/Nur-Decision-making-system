#!/usr/bin/env python3
"""
Test strategy on real synthetic data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.market import MT5MarketData
from core.strategy import TradingStrategy
from core.risk_manager import RiskManager

def test_on_real_data():
    """Test strategy on the first 500 candles of real data"""
    
    print("🧪 Testing Strategy on Real Data")
    print("=" * 60)
    
    # Load data
    data_path = "data/historical_xauusd_m1.csv"
    market = MT5MarketData(data_path)
    market.load_data()
    market.calculate_ema_mt5()
    
    # Get first 500 candles after EMA calculation
    start_idx = 200  # Start after we have EMA
    end_idx = 700    # Look at 500 candles
    
    signals = []
    
    for i in range(start_idx, end_idx):
        current = market.get_candle(i)
        previous = market.get_candle(i-1)
        
        signal = TradingStrategy.get_signal(current, previous)
        
        if signal != 'HOLD':
            signals.append({
                'index': i,
                'timestamp': current['timestamp'],
                'signal': signal,
                'price': current['close'],
                'ema': current['ema_200']
            })
    
    # Print results
    print(f"\n📊 Found {len(signals)} signals in {end_idx-start_idx} candles")
    print(f"📅 Date range: {market.get_candle(start_idx)['timestamp']} to {market.get_candle(end_idx-1)['timestamp']}")
    
    if signals:
        print("\n🔍 Signal Details:")
        for i, sig in enumerate(signals[:10]):  # Show first 10
            print(f"{i+1}. {sig['timestamp']} - {sig['signal']} at {sig['price']:.2f} "
                  f"(EMA: {sig['ema']:.2f})")
        
        if len(signals) > 10:
            print(f"... and {len(signals)-10} more signals")
        
        # Calculate signals per day
        candles_per_day = 24 * 60
        days_covered = (end_idx - start_idx) / candles_per_day
        signals_per_day = len(signals) / days_covered
        
        print(f"\n📈 Signals per day: {signals_per_day:.1f}")
        print(f"Average candles between signals: {(end_idx-start_idx)/len(signals):.0f}")
        
        # Show SL/TP for first signal
        if signals:
            first_signal = signals[0]
            prev_candle = market.get_candle(first_signal['index']-1)
            rm = RiskManager()
            
            sl = rm.calculate_stop_loss(
                first_signal['signal'], 
                first_signal['price'], 
                prev_candle
            )
            
            tp = rm.calculate_take_profit(
                first_signal['signal'], 
                first_signal['price'], 
                sl,
                risk_reward=1.5
            )
            
            print(f"\n💰 Sample Trade for first signal:")
            print(f"   Entry: {first_signal['price']:.2f}")
            print(f"   SL: {sl:.2f} ({abs(first_signal['price']-sl):.2f} risk)")
            print(f"   TP: {tp:.2f} ({abs(tp-first_signal['price']):.2f} reward)")
            print(f"   Risk/Reward: {abs(tp-first_signal['price'])/abs(first_signal['price']-sl):.1f}")
    else:
        print("❌ No signals found in this data range")

if __name__ == "__main__":
    test_on_real_data()
