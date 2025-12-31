#!/usr/bin/env python3
"""
Integrate learning system into backtest engine.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtest.engine_fixed import FixedBacktestEngine
from core.learner import NurLearner
from chat.nur_chat import NurChat

class LearningBacktestEngine(FixedBacktestEngine):
    """Backtest engine with integrated learning"""
    
    def __init__(self, config=None):
        super().__init__(config)
        
        # Initialize learner
        self.learner = NurLearner()
        
        # Track states for learning
        self.current_state = None
        self.previous_state = None
        self.current_action = None
        
        # Learning statistics
        self.learning_stats = {
            'learner_decisions': 0,
            'learner_profitable': 0,
            'learner_loss': 0,
            'total_reward': 0,
        }
    
    def _enter_trade(self, signal, current_candle, previous_candle):
        """Enter a new trade with learning influence"""
        # Get market state for learning
        self.current_state = self.learner.get_state(self.market, current_candle['timestamp'])
        
        # Available actions based on signal
        if signal == 'BUY':
            available_actions = ['enter_long', 'hold']
        else:  # SELL
            available_actions = ['enter_short', 'hold']
        
        # Get learner recommendation
        trade_context = {'signal_type': signal}
        learner_action = self.learner.get_action(
            self.current_state, 
            available_actions, 
            trade_context
        )
        
        # Record action for learning
        self.current_action = learner_action
        
        # Apply learner decision
        if learner_action == 'hold':
            print(f"🧠 Learner decided to HOLD (state: {self.current_state})")
            return  # Don't enter trade
        
        # Proceed with trade entry
        super()._enter_trade(signal, current_candle, previous_candle)
        
        self.learning_stats['learner_decisions'] += 1
    
    def _close_trade(self, exit_price, exit_reason, exit_time):
        """Close trade and update learning"""
        if not self.open_trade:
            return
        
        # Calculate reward based on trade outcome
        reward = self._calculate_reward(exit_reason)
        
        # Get next state (state after trade closes)
        next_state = self.learner.get_state(self.market, exit_time)
        
        # Update learner
        self.learner.update(
            state=self.current_state,
            action=self.current_action,
            reward=reward,
            next_state=next_state,
            is_terminal=True  # Trade closed is terminal state
        )
        
        # Update statistics
        self.learning_stats['total_reward'] += reward
        if reward > 0:
            self.learning_stats['learner_profitable'] += 1
        elif reward < 0:
            self.learning_stats['learner_loss'] += 1
        
        # Call parent to close trade
        super()._close_trade(exit_price, exit_reason, exit_time)
        
        # Reset learning tracking
        self.current_state = None
        self.current_action = None
    
    def _calculate_reward(self, exit_reason):
        """Calculate reward based on trade outcome"""
        if 'TP hit' in exit_reason:
            return 1.0  # Good outcome
        elif 'SL hit' in exit_reason:
            return -1.0  # Bad outcome
        elif 'Early:' in exit_reason:
            # Early exit - small penalty if it was a loss
            if self.open_trade:
                # Check if early exit saved us from bigger loss
                entry = self.open_trade['entry_price']
                current = self.open_trade.get('current_price', entry)
                
                if self.open_trade['direction'] == 'BUY':
                    pnl_pct = (current - entry) / entry * 100
                else:
                    pnl_pct = (entry - current) / entry * 100
                
                if pnl_pct < 0:
                    return -0.2  # Small penalty for early exit loss
                else:
                    return 0.5   # Reward for taking profit early
        return 0.0  # Neutral outcome
    
    def print_results(self):
        """Print results including learning statistics"""
        super().print_results()
        
        print("\n" + "="*60)
        print("🧠 LEARNING INTEGRATION RESULTS")
        print("="*60)
        
        print(f"\n📊 Learning Statistics:")
        print(f"   Learner Decisions: {self.learning_stats['learner_decisions']}")
        print(f"   Profitable Decisions: {self.learning_stats['learner_profitable']}")
        print(f"   Loss Decisions: {self.learning_stats['learner_loss']}")
        print(f"   Total Reward: {self.learning_stats['total_reward']:.2f}")
        
        if self.learning_stats['learner_decisions'] > 0:
            success_rate = (self.learning_stats['learner_profitable'] / 
                          self.learning_stats['learner_decisions']) * 100
            print(f"   Success Rate: {success_rate:.1f}%")
        
        # Print learner stats
        self.learner.print_stats()
        
        # Save learning state
        self.learner.save("learning_integration.pkl")
        
        print("\n💡 Learning integrated successfully!")


def test_learning_integration():
    """Test the integrated learning system"""
    print("🧪 Testing Learning Integration")
    print("=" * 60)
    
    # Create engine with learning
    engine = LearningBacktestEngine()
    
    # Load data
    data_path = "data/historical_xauusd_m1.csv"
    if not engine.load_data(data_path):
        return
    
    # Run backtest with learning
    print("\n🚀 Running backtest with learning...")
    engine.run(start_idx=200, end_idx=2000)  # 1800 candles for quick test
    
    # Print results
    engine.print_results()
    
    # Test chat interface
    print("\n" + "="*60)
    print("💬 TESTING CHAT INTERFACE")
    print("="*60)
    
    chat_config = {
        'use_groq': False,  # Test with rule-based
    }
    
    chat = NurChat(chat_config)
    
    # Test some queries
    test_queries = [
        "how does the learning system work?",
        "what's my trading performance?",
        "explain the EMA strategy",
    ]
    
    for query in test_queries:
        print(f"\n👤 Query: {query}")
        response = chat.respond(query)
        print(f"🤖 Response: {response[:150]}...")
    
    print("\n✅ Learning integration test complete!")
    
    return engine

if __name__ == "__main__":
    test_learning_integration()
