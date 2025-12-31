#!/usr/bin/env python3
"""
Analyze performance and suggest improvements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.market import MT5MarketData
from core.strategy import TradingStrategy
from core.risk_manager import RiskManager
import pandas as pd
import numpy as np

def analyze_and_improve():
    """Analyze strategy performance and suggest improvements"""
    
    print("🔍 ANALYZING STRATEGY PERFORMANCE")
    print("=" * 60)
    
    # Load data
    data_path = "data/historical_xauusd_m1.csv"
    market = MT5MarketData(data_path)
    market.load_data()
    market.calculate_ema_mt5()
    df = market.get_dataframe()
    
    # Get signals
    strategy = TradingStrategy()
    signals = []
    
    for i in range(200, min(10000, len(df))):
        current = market.get_candle(i)
        previous = market.get_candle(i-1)
        
        signal = strategy.get_signal(current, previous)
        if signal != 'HOLD':
            signals.append({
                'index': i,
                'signal': signal,
                'price': current['close'],
                'ema': current['ema_200'],
                'timestamp': current['timestamp']
            })
    
    print(f"\n📊 Signal Analysis ({len(signals)} signals):")
    
    # Analyze signal quality
    buy_signals = [s for s in signals if s['signal'] == 'BUY']
    sell_signals = [s for s in signals if s['signal'] == 'SELL']
    
    print(f"   BUY signals: {len(buy_signals)}")
    print(f"   SELL signals: {len(sell_signals)}")
    
    # Analyze what happens after signals
    print("\n📈 Signal Outcome Analysis:")
    
    outcomes = []
    rm = RiskManager()
    
    for sig in signals[:100]:  # Analyze first 100 signals
        entry_idx = sig['index']
        entry_price = sig['price']
        previous = market.get_candle(entry_idx-1)
        
        # Calculate SL/TP
        sl = rm.calculate_stop_loss(sig['signal'], entry_price, previous)
        tp = rm.calculate_take_profit(sig['signal'], entry_price, sl, risk_reward=1.5)
        
        # Look ahead 50 candles for outcome
        outcome = "NO_EXIT"
        exit_price = entry_price
        candles_to_exit = 0
        
        for lookahead in range(1, 51):
            if entry_idx + lookahead >= len(df):
                break
                
            future_price = market.get_candle(entry_idx + lookahead)['close']
            
            if sig['signal'] == 'BUY':
                if future_price <= sl:
                    outcome = "SL"
                    exit_price = sl
                    candles_to_exit = lookahead
                    break
                elif future_price >= tp:
                    outcome = "TP"
                    exit_price = tp
                    candles_to_exit = lookahead
                    break
            else:  # SELL
                if future_price >= sl:
                    outcome = "SL"
                    exit_price = sl
                    candles_to_exit = lookahead
                    break
                elif future_price <= tp:
                    outcome = "TP"
                    exit_price = tp
                    candles_to_exit = lookahead
                    break
        
        outcomes.append({
            'signal': sig['signal'],
            'outcome': outcome,
            'candles_to_exit': candles_to_exit,
            'risk': abs(entry_price - sl),
            'potential_reward': abs(tp - entry_price)
        })
    
    # Calculate statistics
    total_outcomes = len(outcomes)
    tp_outcomes = [o for o in outcomes if o['outcome'] == 'TP']
    sl_outcomes = [o for o in outcomes if o['outcome'] == 'SL']
    no_exit = [o for o in outcomes if o['outcome'] == 'NO_EXIT']
    
    win_rate = len(tp_outcomes) / total_outcomes * 100 if total_outcomes > 0 else 0
    loss_rate = len(sl_outcomes) / total_outcomes * 100 if total_outcomes > 0 else 0
    
    print(f"   TP outcomes: {len(tp_outcomes)} ({win_rate:.1f}%)")
    print(f"   SL outcomes: {len(sl_outcomes)} ({loss_rate:.1f}%)")
    print(f"   No exit in 50 candles: {len(no_exit)}")
    
    if tp_outcomes:
        avg_candles_to_tp = sum(o['candles_to_exit'] for o in tp_outcomes) / len(tp_outcomes)
        print(f"   Avg candles to TP: {avg_candles_to_tp:.1f}")
    
    if sl_outcomes:
        avg_candles_to_sl = sum(o['candles_to_exit'] for o in sl_outcomes) / len(sl_outcomes)
        print(f"   Avg candles to SL: {avg_candles_to_sl:.1f}")
    
    # Calculate expected value
    if tp_outcomes and sl_outcomes:
        avg_win = sum(o['potential_reward'] for o in tp_outcomes) / len(tp_outcomes)
        avg_loss = sum(o['risk'] for o in sl_outcomes) / len(sl_outcomes)
        
        expected_value = (win_rate/100 * avg_win) - (loss_rate/100 * avg_loss)
        
        print(f"\n💰 Expected Value Analysis:")
        print(f"   Average win: {avg_win:.2f}")
        print(f"   Average loss: {avg_loss:.2f}")
        print(f"   Win/Loss ratio: {avg_win/avg_loss:.2f}")
        print(f"   Expected value per trade: {expected_value:.2f}")
        
        if expected_value > 0:
            print("   ✅ Strategy has positive expectancy")
        else:
            print("   ❌ Strategy has negative expectancy")
    
    # Suggest improvements
    print("\n💡 SUGGESTED IMPROVEMENTS:")
    
    if win_rate < 40:
        print("1. Win rate is low - consider adding filters:")
        print("   • Only trade during high volume hours")
        print("   • Add momentum confirmation (RSI, MACD)")
        print("   • Wait for pullback after signal")
    
    if tp_outcomes and sl_outcomes:
        risk_reward_ratio = sum(o['potential_reward'] for o in outcomes) / sum(o['risk'] for o in outcomes) if sum(o['risk'] for o in outcomes) > 0 else 0
        
        if risk_reward_ratio < 1.5:
            print(f"2. Risk/Reward ratio is {risk_reward_ratio:.2f} - aim for 1.5+")
            print("   • Increase TP distance")
            print("   • Use tighter SL with ATR")
    
    # Check for over-trading
    signals_per_day = len(signals) / (len(df) / 1440)
    if signals_per_day > 10:
        print(f"3. Over-trading detected: {signals_per_day:.1f} signals per day")
        print("   • Add minimum distance between trades")
        print("   • Reduce sensitivity (increase touching threshold)")
    
    # Final recommendation
    print("\n🎯 RECOMMENDATION:")
    
    if win_rate > 40 and expected_value > 0:
        print("   Strategy shows promise. Proceed to Phase 2 with current logic.")
    elif win_rate > 35 and expected_value > 0:
        print("   Strategy has potential but needs refinement. Consider improvements above.")
    else:
        print("   Strategy needs significant improvement before Phase 2.")
    
    return win_rate, expected_value if 'expected_value' in locals() else 0

if __name__ == "__main__":
    win_rate, expected_value = analyze_and_improve()
    
    print("\n" + "="*60)
    if win_rate > 35 and expected_value > 0:
        print("✅ PHASE 1 READY - Proceed with improvements in Phase 2")
    else:
        print("⚠️  PHASE 1 NEEDS WORK - Fix strategy before Phase 2")
    print("="*60)
