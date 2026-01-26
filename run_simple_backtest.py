#!/usr/bin/env python3
"""
Simple backtest for quick validation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.market import MT5MarketData
from core.strategy import TradingStrategy
from core.risk_manager import RiskManager
from core.observer import TradeObserver
from core.tracker import TradeTracker

def simple_backtest():
    """Simple backtest on 1000 candles"""
    print("🧪 Simple Backtest (1000 candles)")
    print("=" * 60)
    
    # Load data
    data_path = "data/historical_xauusd_m1.csv"
    market = MT5MarketData(data_path)
    market.load_data()
    market.calculate_ema_mt5()
    
    # Initialize components
    strategy = TradingStrategy()
    risk_manager = RiskManager()
    tracker = TradeTracker("logs/simple_backtest.csv")
    
    # Configuration
    initial_balance = 10000.0
    balance = initial_balance
    position_size = 0.01  # Micro lot
    spread = 0.20  # 20 pips
    
    # State
    open_trade = None
    observer = None
    trade_counter = 0
    
    # Run on first 1000 candles after EMA
    start_idx = 200
    end_idx = 1200
    
    print(f"Running on candles {start_idx} to {end_idx}")
    
    for i in range(start_idx, end_idx):
        current = market.get_candle(i)
        previous = market.get_candle(i-1)
        
        # Manage open trade
        if open_trade:
            # Update observer
            exit_recommendation = observer.update(current, current.get('ema_200'))
            
            # Check SL/TP
            current_price = current['close']
            exit_reason = None
            exit_price = None
            
            if open_trade['direction'] == 'BUY':
                if current_price <= open_trade['sl']:
                    exit_reason = "SL hit"
                    exit_price = open_trade['sl']
                elif current_price >= open_trade['tp']:
                    exit_reason = "TP hit"
                    exit_price = open_trade['tp']
            else:  # SELL
                if current_price >= open_trade['sl']:
                    exit_reason = "SL hit"
                    exit_price = open_trade['sl']
                elif current_price <= open_trade['tp']:
                    exit_reason = "TP hit"
                    exit_price = open_trade['tp']
            
            # Check observer recommendation
            if not exit_reason and exit_recommendation:
                exit_reason = f"Early: {exit_recommendation['exit_reason']}"
                exit_price = exit_recommendation['exit_price']
            
            # Close trade if needed
            if exit_reason:
                # Calculate PnL
                if open_trade['direction'] == 'BUY':
                    pnl = (exit_price - open_trade['entry_price']) * position_size * 100
                else:
                    pnl = (open_trade['entry_price'] - exit_price) * position_size * 100
                
                balance += pnl
                
                # Close in tracker
                tracker.close_trade(
                    exit_price=exit_price,
                    exit_reason=exit_reason,
                    exit_time=current['timestamp']
                )
                
                print(f"  Closed {open_trade['direction']}: PnL ${pnl:.2f}, Balance: ${balance:.2f}")
                open_trade = None
                observer = None
        
        # Check for new signal (if no open trade)
        if not open_trade:
            signal = strategy.get_signal(current, previous)
            
            if signal != 'HOLD':
                trade_counter += 1
                
                # Calculate entry with spread
                entry_price = current['close']
                if signal == 'BUY':
                    entry_price += spread / 100
                else:
                    entry_price -= spread / 100
                
                # Calculate SL/TP
                sl = risk_manager.calculate_stop_loss(signal, entry_price, previous)
                tp = risk_manager.calculate_take_profit(signal, entry_price, sl, risk_reward=1.5)
                
                # Start trade
                open_trade = {
                    'id': f"T{trade_counter:03d}",
                    'direction': signal,
                    'entry_price': entry_price,
                    'entry_time': current['timestamp'],
                    'sl': sl,
                    'tp': tp,
                }
                
                # Start observer
                observer = TradeObserver()
                observer.start_trade(signal, entry_price, current['timestamp'])
                
                # Start tracker
                tracker.start_trade(
                    trade_id=open_trade['id'],
                    direction=signal,
                    entry_price=entry_price,
                    stop_loss=sl,
                    take_profit=tp,
                    position_size=position_size,
                    entry_time=current['timestamp']
                )
                
                print(f"\n📈 {signal} #{open_trade['id']} at {entry_price:.2f}")
                print(f"   SL: {sl:.2f}, TP: {tp:.2f}")
    
    # Close any remaining trade
    if open_trade:
        last_candle = market.get_candle(end_idx-1)
        tracker.close_trade(
            exit_price=last_candle['close'],
            exit_reason="End of backtest",
            exit_time=last_candle['timestamp']
        )
        print(f"\n⚠️  Closed open trade at end of backtest")
    
    # Print results
    print("\n" + "="*60)
    print("📊 SIMPLE BACKTEST RESULTS")
    print("="*60)
    
    stats = tracker.get_statistics()
    
    print(f"\n💰 Balance: ${balance:.2f}")
    print(f"   Initial: ${initial_balance:.2f}")
    print(f"   Net Profit: ${balance - initial_balance:.2f}")
    print(f"   Return: {((balance / initial_balance) - 1) * 100:.2f}%")
    
    print(f"\n📊 Trades: {stats['total_trades']}")
    print(f"   Win Rate: {stats['win_rate']}%")
    print(f"   Profit Factor: {stats['profit_factor']:.2f}")
    print(f"   Expectancy: ${stats['expectancy']:.2f}")
    
    # Print exit reasons
    print(f"\n🔍 Exit Reasons:")
    # We'd need to parse the log file for this
    
    print("\n✅ Backtest complete!")

if __name__ == "__main__":
    simple_backtest()
