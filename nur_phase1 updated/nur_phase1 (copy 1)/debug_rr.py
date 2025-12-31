#!/usr/bin/env python3
"""
Debug Risk/Reward Calculation
"""

from core.risk_manager import RiskManager

rm = RiskManager()

# Test SL/TP calculation
print("🧪 Debugging Risk/Reward Calculation")
print("=" * 50)

# Test case
signal = 'BUY'
entry_price = 2050.0
previous_candle = {'low': 2048.5, 'high': 2051.5}

# Calculate SL
sl = rm.calculate_stop_loss(signal, entry_price, previous_candle)
print(f"Entry: {entry_price}")
print(f"SL: {sl}")
print(f"Risk: {entry_price - sl:.2f}")

# Calculate TP with different RR ratios
for rr in [1.0, 1.5, 2.0]:
    tp = rm.calculate_take_profit(signal, entry_price, sl, risk_reward=rr)
    print(f"\nRR {rr}:")
    print(f"  TP: {tp}")
    print(f"  Reward: {tp - entry_price:.2f}")
    print(f"  Actual RR: {(tp - entry_price)/(entry_price - sl):.2f}")

# Check the formula in risk_manager.py
print("\n🔍 Checking calculate_take_profit method...")
print("Current logic for BUY:")
print("  risk = entry_price - stop_loss")
print("  min_tp = entry_price + (risk * risk_reward)")
print(f"  With entry={entry_price}, sl={sl}, risk={entry_price-sl:.2f}")
print(f"  For RR=1.5: TP should be {entry_price + (entry_price-sl)*1.5:.2f}")
