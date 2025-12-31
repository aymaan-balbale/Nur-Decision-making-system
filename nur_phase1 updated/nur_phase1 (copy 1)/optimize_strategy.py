#!/usr/bin/env python3
"""
Optimize strategy parameters based on backtest results.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.strategy import TradingStrategy
from backtest.engine_fixed import FixedBacktestEngine

def optimize_parameters():
    """Test different parameter configurations"""
    print("🔧 Optimizing Strategy Parameters")
    print("=" * 60)
    
    # Test different configurations
    configs = [
        {
            'name': 'Default',
            'risk_reward_ratio': 1.5,
            'position_size': 0.01,
            'max_trades_per_day': 5,
        },
        {
            'name': 'Aggressive RR',
            'risk_reward_ratio': 2.0,
            'position_size': 0.01,
            'max_trades_per_day': 5,
        },
        {
            'name': 'Conservative RR',
            'risk_reward_ratio': 1.2,
            'position_size': 0.01,
            'max_trades_per_day': 3,
        },
        {
            'name': 'Larger Position',
            'risk_reward_ratio': 1.5,
            'position_size': 0.02,
            'max_trades_per_day': 4,
        },
        {
            'name': 'Scalping',
            'risk_reward_ratio': 1.0,
            'position_size': 0.01,
            'max_trades_per_day': 10,
        },
    ]
    
    results = []
    
    for config in configs:
        print(f"\n🧪 Testing: {config['name']}")
        print("-" * 40)
        
        # Create engine with config
        engine_config = {
            'initial_balance': 10000.0,
            'risk_per_trade': 1.0,
            'risk_reward_ratio': config['risk_reward_ratio'],
            'position_size': config['position_size'],
            'max_trades_per_day': config['max_trades_per_day'],
            'max_daily_loss': -200.0,
            'commission_per_lot': 3.5,
            'spread': 0.20,
        }
        
        engine = FixedBacktestEngine(engine_config)
        
        # Load data
        data_path = "data/historical_xauusd_m1.csv"
        if not engine.load_data(data_path):
            continue
        
        # Run quick backtest
        engine.run(start_idx=200, end_idx=5200)  # 5000 candles
        
        # Get stats
        stats = engine.tracker.get_statistics()
        
        # Calculate metrics
        net_profit = engine.balance - 10000.0
        return_pct = ((engine.balance / 10000.0) - 1) * 100
        
        results.append({
            'name': config['name'],
            'trades': stats['total_trades'],
            'win_rate': stats['win_rate'],
            'profit_factor': stats['profit_factor'],
            'expectancy': stats['expectancy'],
            'net_profit': net_profit,
            'return_pct': return_pct,
            'avg_win': stats['avg_win'],
            'avg_loss': stats['avg_loss'],
        })
        
        print(f"   Trades: {stats['total_trades']}, Win Rate: {stats['win_rate']}%")
        print(f"   Net Profit: ${net_profit:.2f}, Return: {return_pct:.2f}%")
    
    # Print comparison
    print("\n" + "="*60)
    print("📊 OPTIMIZATION RESULTS COMPARISON")
    print("="*60)
    
    print("\n{:15} {:8} {:8} {:8} {:8} {:12} {:8}".format(
        "Config", "Trades", "Win%", "PF", "Exp$", "Net Profit", "Return%"
    ))
    print("-" * 70)
    
    for r in results:
        print("{:15} {:8} {:8.1f} {:8.2f} {:8.2f} {:12.2f} {:8.2f}".format(
            r['name'],
            r['trades'],
            r['win_rate'],
            r['profit_factor'],
            r['expectancy'],
            r['net_profit'],
            r['return_pct']
        ))
    
    # Find best configuration
    best_by_profit = max(results, key=lambda x: x['net_profit'])
    best_by_winrate = max(results, key=lambda x: x['win_rate'])
    best_by_pf = max(results, key=lambda x: x['profit_factor'])
    
    print("\n🏆 Best Performers:")
    print(f"   By Net Profit: {best_by_profit['name']} (${best_by_profit['net_profit']:.2f})")
    print(f"   By Win Rate: {best_by_winrate['name']} ({best_by_winrate['win_rate']:.1f}%)")
    print(f"   By Profit Factor: {best_by_pf['name']} ({best_by_pf['profit_factor']:.2f})")
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    # Analyze average win/loss ratio
    avg_win_loss_ratio = sum(r['avg_win'] / abs(r['avg_loss']) for r in results if r['avg_loss'] != 0) / len(results)
    print(f"   1. Average win/loss ratio: {avg_win_loss_ratio:.2f}")
    
    # Check if we need to adjust risk/reward
    if best_by_profit['profit_factor'] < 1.5:
        print("   2. Consider increasing risk/reward ratio to 2.0+")
    else:
        print("   2. Current risk/reward ratio seems optimal")
    
    # Check win rate
    if best_by_winrate['win_rate'] < 40:
        print("   3. Win rate is low - consider adding filters to entries")
    else:
        print("   3. Win rate is acceptable given profit factor > 1.2")
    
    return results

if __name__ == "__main__":
    optimize_parameters()
