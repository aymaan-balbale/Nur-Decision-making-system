#!/usr/bin/env python3
"""
Simple Backtesting Engine - Fixed version
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after path is set
from core.market import MT5MarketData
from core.strategy import TradingStrategy
from core.risk_manager import RiskManager
from core.observer import TradeObserver
from core.tracker import TradeTracker
import pandas as pd
from datetime import datetime

class SimpleBacktestEngine:
    """Simplified backtest engine"""
    
    def __init__(self):
        self.market = None
        self.strategy = TradingStrategy()
        self.risk_manager = RiskManager()
        self.tracker = TradeTracker("logs/engine_test.csv")
        
    def run(self):
        """Run simple backtest"""
        print("🚀 Running Simple Backtest Engine")
        
        # Load data
        data_path = "data/historical_xauusd_m1.csv"
        self.market = MT5MarketData(data_path)
        self.market.load_data()
        self.market.calculate_ema_mt5()
        
        # Run on 500 candles
        start_idx = 200
        end_idx = 700
        trade_count = 0
        open_trade = None
        observer = None
        
        for i in range(start_idx, end_idx):
            current = self.market.get_candle(i)
            previous = self.market.get_candle(i-1)
            
            # Check for exit if trade is open
            if open_trade:
                # Simple exit logic
                current_price = current['close']
                should_exit = False
                exit_reason = ""
                exit_price = current_price
                
                if open_trade['direction'] == 'BUY':
                    if current_price <= open_trade['sl']:
                        should_exit = True
                        exit_reason = "SL hit"
                        exit_price = open_trade['sl']
                    elif current_price >= open_trade['tp']:
                        should_exit = True
                        exit_reason = "TP hit"
                        exit_price = open_trade['tp']
                else:  # SELL
                    if current_price >= open_trade['sl']:
                        should_exit = True
                        exit_reason = "SL hit"
                        exit_price = open_trade['sl']
                    elif current_price <= open_trade['tp']:
                        should_exit = True
                        exit_reason = "TP hit"
                        exit_price = open_trade['tp']
                
                # Check EMA crossback
                ema = current.get('ema_200')
                if ema and not should_exit:
                    if open_trade['direction'] == 'BUY' and current_price < ema:
                        should_exit = True
                        exit_reason = "EMA crossback"
                    elif open_trade['direction'] == 'SELL' and current_price > ema:
                        should_exit = True
                        exit_reason = "EMA crossback"
                
                if should_exit:
                    # Calculate PnL
                    if open_trade['direction'] == 'BUY':
                        pnl = (exit_price - open_trade['entry_price']) * 0.01 * 100
                    else:
                        pnl = (open_trade['entry_price'] - exit_price) * 0.01 * 100
                    
                    # Close in tracker
                    self.tracker.close_trade(
                        exit_price=exit_price,
                        exit_reason=exit_reason,
                        exit_time=current['timestamp']
                    )
                    
                    print(f"  Closed {open_trade['direction']}: {exit_reason}, PnL: ${pnl:.2f}")
                    open_trade = None
                    observer = None
            
            # Check for new entry
            if not open_trade:
                signal = self.strategy.get_signal(current, previous)
                
                if signal != 'HOLD':
                    trade_count += 1
                    entry_price = current['close']
                    
                    # Calculate SL/TP
                    sl = self.risk_manager.calculate_stop_loss(signal, entry_price, previous)
                    tp = self.risk_manager.calculate_take_profit(signal, entry_price, sl)
                    
                    open_trade = {
                        'id': f"T{trade_count:03d}",
                        'direction': signal,
                        'entry_price': entry_price,
                        'sl': sl,
                        'tp': tp,
                        'entry_time': current['timestamp']
                    }
                    
                    # Start observer
                    observer = TradeObserver()
                    observer.start_trade(signal, entry_price, current['timestamp'])
                    
                    # Start tracker
                    self.tracker.start_trade(
                        trade_id=open_trade['id'],
                        direction=signal,
                        entry_price=entry_price,
                        stop_loss=sl,
                        take_profit=tp,
                        position_size=0.01,
                        entry_time=current['timestamp']
                    )
                    
                    print(f"\n🎯 {signal} #{open_trade['id']} at {entry_price:.2f}")
                    print(f"   SL: {sl:.2f}, TP: {tp:.2f}")
        
        # Print results
        print("\n" + "="*60)
        print("📊 BACKTEST COMPLETE")
        print("="*60)
        
        stats = self.tracker.get_statistics()
        
        print(f"\n📊 Statistics:")
        print(f"   Total Trades: {stats['total_trades']}")
        print(f"   Win Rate: {stats['win_rate']}%")
        print(f"   Total PnL: ${stats['total_pnl']:.2f}")
        print(f"   Profit Factor: {stats['profit_factor']:.2f}")
        
        self.tracker.print_summary_report()

if __name__ == "__main__":
    engine = SimpleBacktestEngine()
    engine.run()
