#!/usr/bin/env python3
"""Test all imports"""

print("Testing imports...")

try:
    from core.market import MT5MarketData
    print("✅ core.market")
except ImportError as e:
    print(f"❌ core.market: {e}")

try:
    from core.strategy import TradingStrategy
    print("✅ core.strategy")
except ImportError as e:
    print(f"❌ core.strategy: {e}")

try:
    from core.risk_manager import RiskManager
    print("✅ core.risk_manager")
except ImportError as e:
    print(f"❌ core.risk_manager: {e}")

try:
    from core.observer import TradeObserver
    print("✅ core.observer")
except ImportError as e:
    print(f"❌ core.observer: {e}")

try:
    from core.tracker import TradeTracker
    print("✅ core.tracker")
except ImportError as e:
    print(f"❌ core.tracker: {e}")

print("\n✅ All imports tested")
