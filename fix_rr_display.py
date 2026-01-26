#!/usr/bin/env python3
"""
Fix Risk/Reward display issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Check where RR is calculated in backtest engine
print("Checking RR calculation in backtest engine...")

with open("backtest/engine_fixed.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "Risk/Reward" in line:
        print(f"Line {i+1}: {line.strip()}")
        # Show context
        for j in range(max(0, i-2), min(len(lines), i+3)):
            print(f"  {j+1}: {lines[j].rstrip()}")

# The issue is in _enter_trade method - RR is calculated but not stored
print("\nThe issue is that RR is calculated but not used consistently.")
print("Let's create a proper fix...")
