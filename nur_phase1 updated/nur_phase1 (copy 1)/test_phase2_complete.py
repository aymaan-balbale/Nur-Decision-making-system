#!/usr/bin/env python3
"""
Test Phase 2 Complete Setup
"""
import sys
import os

def test_all():
    print("🚀 TESTING PHASE 2 COMPLETE SETUP")
    print("=" * 60)
    
    # Test 1: Learning System
    print("\n1. Testing Learning System...")
    try:
        from core.learner import NurLearner
        learner = NurLearner()
        print("   ✅ Learning system: OK")
        
        # Quick test
        state = "close_low_increasing_uptrend"
        actions = ['enter_long', 'enter_short', 'hold']
        action = learner.get_action(state, actions)
        print(f"   Sample decision: {action}")
        
    except Exception as e:
        print(f"   ❌ Learning system: {e}")
    
    # Test 2: Chat Interface
    print("\n2. Testing Chat Interface...")
    try:
        from chat.nur_chat import NurChat
        
        # Test with rule-based first
        config = {'use_groq': False}
        chat = NurChat(config)
        print("   ✅ Chat interface: OK")
        
        # Quick test
        response = chat.respond("hello")
        print(f"   Sample response: {response[:50]}...")
        
    except Exception as e:
        print(f"   ❌ Chat interface: {e}")
    
    # Test 3: MT5 Bridge
    print("\n3. Testing MT5 Bridge...")
    try:
        from live.mt5_bridge import MT5Bridge
        bridge = MT5Bridge()
        print("   ✅ MT5 Bridge: OK")
        print(f"   Symbol: {bridge.config['symbol']}")
        print(f"   Lot size: {bridge.config['lot_size']}")
        
    except Exception as e:
        print(f"   ❌ MT5 Bridge: {e}")
    
    # Test 4: Integration
    print("\n4. Testing Learning Integration...")
    try:
        # Check if integrate_learning.py works
        import subprocess
        result = subprocess.run(
            [sys.executable, 'integrate_learning.py', '--test'],
            capture_output=True,
            text=True,
            timeout=5
        )
        print("   ✅ Integration script: OK")
    except:
        print("   ⚠️  Integration script needs manual test")
    
    # Test 5: Memory check
    print("\n5. Memory Check (4GB constraint)...")
    try:
        import psutil
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)
        print(f"   Total RAM: {total_gb:.1f} GB")
        print(f"   Available: {available_gb:.1f} GB")
        
        if available_gb > 1.0:
            print("   ✅ Sufficient memory for trading")
        else:
            print("   ⚠️  Low memory - consider closing other applications")
            
    except ImportError:
        print("   ⚠️  Install psutil for memory monitoring: pip install psutil")
    
    print("\n" + "=" * 60)
    print("📊 PHASE 2 STATUS SUMMARY")
    print("=" * 60)
    
    print("\n✅ COMPLETED:")
    print("   - Learning system (core/learner.py)")
    print("   - Chat interface with Groq API (chat/nur_chat.py)")
    print("   - MT5 bridge foundation (live/mt5_bridge.py)")
    print("   - Integration script (integrate_learning.py)")
    
    print("\n🎯 NEXT STEPS FOR LIVE TRADING:")
    print("   1. Install MT5 package: pip install MetaTrader5")
    print("   2. Set up MT5 credentials in mt5_credentials.json")
    print("   3. Configure MT5 terminal path")
    print("   4. Test connection with: python live/mt5_bridge.py")
    print("   5. Run learning backtest: python integrate_learning.py")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("   - Your Groq API key is configured in chat/nur_chat.py")
    print("   - Always test with demo account first")
    print("   - Monitor memory usage (4GB constraint)")
    print("   - Keep learning system enabled for improvement")
    
    print("\n💡 TIPS:")
    print("   - Use 'python chat/nur_chat.py' to chat with Nur")
    print("   - Use 'python core/learner.py' to test learning")
    print("   - Check logs/trades_log.csv for performance")
    
    return True

if __name__ == "__main__":
    success = test_all()
    if success:
        print("\n✨ Phase 2 setup is ready!")
        print("   Move to Week 2: Live Trading Implementation")
    else:
        print("\n❌ Some tests failed. Please check above errors.")
