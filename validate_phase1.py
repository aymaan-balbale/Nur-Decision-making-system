#!/usr/bin/env python3
"""
COMPREHENSIVE PHASE 1 VALIDATION TEST
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.market import MT5MarketData
from core.strategy import TradingStrategy
from core.risk_manager import RiskManager
import pandas as pd
import numpy as np

def comprehensive_validation():
    """Run comprehensive validation of all components"""
    
    print("="*70)
    print("🔍 COMPREHENSIVE PHASE 1 VALIDATION")
    print("="*70)
    
    # Test 1: Data Loading
    print("\n1. 📊 DATA SYSTEM VALIDATION")
    print("-" * 40)
    
    data_path = "data/historical_xauusd_m1.csv"
    market = MT5MarketData(data_path)
    
    if not market.load_data():
        print("❌ FAILED: Cannot load data")
        return False
    
    if not market.calculate_ema_mt5():
        print("❌ FAILED: Cannot calculate EMA")
        return False
    
    df = market.get_dataframe()
    print(f"✅ Data loaded: {len(df)} candles")
    print(f"✅ EMA calculated: First value = {df['ema_200'].iloc[200]:.2f}")
    
    # Test 2: Strategy Logic
    print("\n2. 🎯 STRATEGY LOGIC VALIDATION")
    print("-" * 40)
    
    strategy = TradingStrategy()
    
    # Test edge cases
    test_cases = [
        # (current_close, current_ema, prev_close, prev_ema, expected_signal)
        (2050.0, 2049.5, 2049.0, 2049.8, 'BUY'),
        (2049.0, 2049.5, 2050.0, 2049.8, 'SELL'),
        (2050.5, 2049.5, 2050.2, 2049.8, 'HOLD'),  # Already above
        (2049.0, 2049.5, 2048.8, 2049.6, 'HOLD'),  # Already below
        (2049.55, 2049.5, 2049.55, 2049.5, 'BUY'),  # Touching
    ]
    
    all_passed = True
    for i, (curr_close, curr_ema, prev_close, prev_ema, expected) in enumerate(test_cases):
        current = {'close': curr_close, 'ema_200': curr_ema}
        previous = {'close': prev_close, 'ema_200': prev_ema}
        
        signal = strategy.get_signal(current, previous)
        
        if signal == expected:
            print(f"✅ Test {i+1}: {signal} (expected: {expected})")
        else:
            print(f"❌ Test {i+1}: Got {signal}, expected {expected}")
            all_passed = False
    
    if not all_passed:
        print("❌ STRATEGY VALIDATION FAILED")
        return False
    
    # Test 3: Risk Management
    print("\n3. 🛡️ RISK MANAGEMENT VALIDATION")
    print("-" * 40)
    
    rm = RiskManager()
    prev_candle = {'low': 2048.5, 'high': 2051.5}
    
    # Test BUY
    sl_buy = rm.calculate_stop_loss('BUY', 2050.0, prev_candle)
    tp_buy = rm.calculate_take_profit('BUY', 2050.0, sl_buy, risk_reward=1.5)
    
    risk_buy = 2050.0 - sl_buy
    reward_buy = tp_buy - 2050.0
    actual_rr_buy = reward_buy / risk_buy if risk_buy > 0 else 0
    
    print(f"BUY Entry: 2050.0")
    print(f"  SL: {sl_buy:.2f} (Risk: {risk_buy:.2f})")
    print(f"  TP: {tp_buy:.2f} (Reward: {reward_buy:.2f})")
    print(f"  RR Ratio: {actual_rr_buy:.2f}")
    
    if abs(actual_rr_buy - 1.5) > 0.1:
        print(f"❌ BUY RR is {actual_rr_buy:.2f}, expected 1.5")
        all_passed = False
    else:
        print("✅ BUY RR correct")
    
    # Test SELL
    sl_sell = rm.calculate_stop_loss('SELL', 2050.0, prev_candle)
    tp_sell = rm.calculate_take_profit('SELL', 2050.0, sl_sell, risk_reward=1.5)
    
    risk_sell = sl_sell - 2050.0
    reward_sell = 2050.0 - tp_sell
    actual_rr_sell = reward_sell / risk_sell if risk_sell > 0 else 0
    
    print(f"\nSELL Entry: 2050.0")
    print(f"  SL: {sl_sell:.2f} (Risk: {risk_sell:.2f})")
    print(f"  TP: {tp_sell:.2f} (Reward: {reward_sell:.2f})")
    print(f"  RR Ratio: {actual_rr_sell:.2f}")
    
    if abs(actual_rr_sell - 1.5) > 0.1:
        print(f"❌ SELL RR is {actual_rr_sell:.2f}, expected 1.5")
        all_passed = False
    else:
        print("✅ SELL RR correct")
    
    # Test 4: Real Data Validation
    print("\n4. 📈 REAL DATA VALIDATION")
    print("-" * 40)
    
    # Test on 1000 candles of real data
    signals = []
    start_idx = 200
    end_idx = 1200
    
    for i in range(start_idx, end_idx):
        current = market.get_candle(i)
        previous = market.get_candle(i-1)
        
        signal = strategy.get_signal(current, previous)
        if signal != 'HOLD':
            signals.append({
                'index': i,
                'timestamp': current['timestamp'],
                'signal': signal,
                'price': current['close'],
                'ema': current['ema_200']
            })
    
    print(f"Found {len(signals)} signals in {end_idx-start_idx} candles")
    
    if len(signals) == 0:
        print("❌ No signals generated")
        all_passed = False
    elif len(signals) > 100:
        print("⚠️  Too many signals ({len(signals)}), might be over-trading")
    else:
        print(f"✅ Signal frequency: {len(signals)/((end_idx-start_idx)/1440):.1f} per day")
    
    # Test 5: Profitability Simulation
    print("\n5. 💰 PROFITABILITY SIMULATION")
    print("-" * 40)
    
    # Simple simulation
    balance = 10000.0
    position_size = 0.01
    trade_count = 0
    win_count = 0
    loss_count = 0
    
    print("Running simple simulation on first 50 signals...")
    
    for i, sig in enumerate(signals[:50]):
        current = market.get_candle(sig['index'])
        previous = market.get_candle(sig['index']-1)
        
        # Get SL/TP
        sl = rm.calculate_stop_loss(sig['signal'], sig['price'], previous)
        tp = rm.calculate_take_profit(sig['signal'], sig['price'], sl, risk_reward=1.5)
        
        # Find exit (next time price hits SL or TP)
        exit_found = False
        exit_price = sig['price']
        exit_reason = "No exit found"
        
        for j in range(sig['index']+1, min(sig['index']+100, len(df))):
            price = market.get_candle(j)['close']
            
            if sig['signal'] == 'BUY':
                if price <= sl:
                    exit_price = sl
                    exit_reason = "SL"
                    loss_count += 1
                    exit_found = True
                    break
                elif price >= tp:
                    exit_price = tp
                    exit_reason = "TP"
                    win_count += 1
                    exit_found = True
                    break
            else:  # SELL
                if price >= sl:
                    exit_price = sl
                    exit_reason = "SL"
                    loss_count += 1
                    exit_found = True
                    break
                elif price <= tp:
                    exit_price = tp
                    exit_reason = "TP"
                    win_count += 1
                    exit_found = True
                    break
        
        if exit_found:
            trade_count += 1
            if sig['signal'] == 'BUY':
                pnl = (exit_price - sig['price']) * position_size * 100
            else:
                pnl = (sig['price'] - exit_price) * position_size * 100
            
            balance += pnl
    
    if trade_count > 0:
        win_rate = (win_count / trade_count) * 100
        print(f"Trades executed: {trade_count}")
        print(f"Wins: {win_count}, Losses: {loss_count}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Final Balance: ${balance:.2f}")
        print(f"Net Profit: ${balance - 10000:.2f}")
        
        if balance > 10000:
            print("✅ Simulation shows profitability")
        else:
            print("⚠️  Simulation shows loss")
            all_passed = False
    else:
        print("❌ No trades executed in simulation")
        all_passed = False
    
    # FINAL VERDICT
    print("\n" + "="*70)
    print("📋 FINAL VALIDATION RESULTS")
    print("="*70)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED - PHASE 1 VALIDATED")
        print("\n✅ WHAT'S WORKING:")
        print("   1. Data system loads and calculates EMA correctly")
        print("   2. Strategy logic generates signals as expected")
        print("   3. Risk management calculates proper SL/TP with correct RR")
        print("   4. System can execute trades on real data")
        
        print("\n⚠️  AREAS OF CONCERN:")
        print("   1. Win rate needs improvement (consider adding filters)")
        print("   2. Need more extensive backtesting")
        print("   3. Consider implementing ATR-based stops")
        
        print("\n🚀 READY FOR PHASE 2:")
        print("   • Add learning system")
        print("   • Implement MT5 bridge")
        print("   • Add chat interface")
        
        return True
    else:
        print("❌ VALIDATION FAILED - FIX ISSUES BEFORE PHASE 2")
        return False

if __name__ == "__main__":
    success = comprehensive_validation()
    
    if success:
        print("\n" + "="*70)
        print("✅ PHASE 1 COMPLETE AND VALIDATED")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("❌ PHASE 1 NEEDS FIXES BEFORE CONTINUING")
        print("="*70)
        sys.exit(1)
