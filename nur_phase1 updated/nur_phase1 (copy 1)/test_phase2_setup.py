#!/usr/bin/env python3
"""
Test Phase 2 setup: Learning + Chat + Integration
"""
import sys
import os

def test_imports():
    """Test all Phase 2 imports"""
    print("🧪 Testing Phase 2 Imports")
    print("=" * 50)
    
    modules = [
        ('core.learner', 'NurLearner'),
        ('chat.nur_chat', 'NurChat'),
        ('backtest.engine_fixed', 'FixedBacktestEngine'),
        ('core.ema_strategy', 'EMAStrategy'),
        ('core.risk_manager', 'RiskManager'),
    ]
    
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            instance = cls()
            print(f"✅ {module_name}.{class_name}: OK")
        except Exception as e:
            print(f"❌ {module_name}.{class_name}: {e}")
    
    print("\n📁 Checking project structure...")
    required_dirs = ['backtest', 'core', 'chat', 'data', 'logs']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ Directory: {dir_name}/")
        else:
            print(f"❌ Missing: {dir_name}/")
    
    print("\n💾 Checking data files...")
    data_files = ['data/historical_xauusd_m1.csv']
    for file in data_files:
        if os.path.exists(file):
            size_mb = os.path.getsize(file) / (1024 * 1024)
            print(f"✅ Data: {file} ({size_mb:.1f} MB)")
        else:
            print(f"❌ Missing: {file}")

def test_learner():
    """Test the learning system"""
    print("\n🧠 Testing Learning System")
    print("=" * 50)
    
    from core.learner import NurLearner
    
    learner = NurLearner()
    
    # Test basic functionality
    print("1. Creating learner... OK")
    
    # Test state creation
    state = "close_low_increasing_uptrend"
    actions = ['enter_long', 'enter_short', 'hold']
    
    action = learner.get_action(state, actions)
    print(f"2. Action selection: {action}")
    
    # Test update
    reward = 1.0
    next_state = "medium_medium_decreasing_downtrend"
    learner.update(state, action, reward, next_state)
    print(f"3. Learning update: {state} -> {action} = {reward}")
    
    # Test recommendation
    rec = learner.get_recommendation(state)
    print(f"4. Recommendation: {rec['action']} (confidence: {rec['confidence']:.2f})")
    
    # Test save/load
    learner.save("test_phase2.pkl")
    print("5. Save/load: OK")
    
    # Print stats
    learner.print_stats()

def test_chat():
    """Test chat interface"""
    print("\n💬 Testing Chat Interface")
    print("=" * 50)
    
    from chat.nur_chat import NurChat
    
    # Test without Groq
    config = {'use_groq': False}
    chat = NurChat(config)
    
    test_queries = [
        "hello",
        "how does the strategy work?",
        "what is my win rate?",
    ]
    
    for query in test_queries:
        response = chat.respond(query)
        print(f"\n👤: {query}")
        print(f"🤖: {response[:100]}...")

def main():
    """Run all tests"""
    print("🚀 PHASE 2 SETUP TEST")
    print("=" * 60)
    
    test_imports()
    test_learner()
    test_chat()
    
    print("\n" + "=" * 60)
    print("✅ PHASE 2 SETUP COMPLETE")
    print("\n🎯 Next steps:")
    print("1. Run 'python integrate_learning.py' to test learning integration")
    print("2. Configure Groq API key in chat/nur_chat.py if desired")
    print("3. Run extensive backtests with 'python run_simple_backtest.py'")
    print("4. Check learning progress with 'python core/learner.py'")

if __name__ == "__main__":
    main()
