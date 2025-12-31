#!/usr/bin/env python3
"""
Backtesting Engine - The core of Phase 1.
Replays historical data candle-by-candle, simulating real trading.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.market import MT5MarketData
from core.strategy import TradingStrategy
from core.risk_manager import RiskManager
from core.observer import TradeObserver
from core.tracker import TradeTracker
import pandas as pd
from datetime import datetime

class BacktestEngine:
    """
    Main backtesting engine that simulates live trading on historical data.
    """
    
    def __init__(self, config=None):
        self.config = config or {
            'initial_balance': 10000.0,
            'risk_per_trade': 1.0,  # 1% risk per trade
            'risk_reward_ratio': 1.5,
            'position_size': 0.01,  # Default micro lot
            'max_trades_per_day': 5,
            'max_daily_loss': -200.0,  # $200 max daily loss
            'commission_per_lot': 3.5,  # $3.5 per lot commission
            'spread': 0.20,  # 20 pips average spread
        }
        
        # Initialize components
        self.market = None
        self.strategy = TradingStrategy()
        self.risk_manager = RiskManager()
        self.observer = TradeObserver()
        self.tracker = TradeTracker()
        
        # Trading state
        self.current_balance = self.config['initial_balance']
        self.equity_curve = []
        self.open_trade = None
        self.trade_counter = 0
        self.daily_trades = 0
        self.daily_pnl = 0
        
        # Statistics
        self.signals_generated = 0
        self.trades_executed = 0
        
    def load_data(self, data_path):
        """Load market data for backtesting"""
        print(f"📂 Loading data from: {data_path}")
        self.market = MT5MarketData(data_path)
        if not self.market.load_data():
            return False
        if not self.market.calculate_ema_mt5():
            return False
        
        print(f"✅ Loaded {self.market.get_candle_count()} candles")
        return True
    
    def run(self, start_idx=200, end_idx=None, show_progress=True):
        """
        Run the backtest.
        
        Args:
            start_idx: Start index (after enough data for EMA)
            end_idx: End index (None for all data)
            show_progress: Show progress bar/updates
        """
        if self.market is None:
            print("❌ No data loaded. Call load_data() first.")
            return
        
        total_candles = self.market.get_candle_count()
        if end_idx is None:
            end_idx = total_candles
        
        print(f"\n🚀 Starting Backtest")
        print(f"   Candles: {start_idx} to {end_idx} ({end_idx - start_idx} total)")
        print(f"   Date range: {self.market.get_candle(start_idx)['timestamp']} "
              f"to {self.market.get_candle(end_idx-1)['timestamp']}")
        print(f"   Initial balance: ${self.config['initial_balance']:.2f}")
        print("-" * 60)
        
        # Reset state
        self.equity_curve = [self.current_balance]
        self.open_trade = None
        self.trade_counter = 0
        self.daily_trades = 0
        self.daily_pnl = 0
        
        # Main backtesting loop
        for i in range(start_idx, end_idx):
            current_candle = self.market.get_candle(i)
            previous_candle = self.market.get_candle(i-1)
            
            # Check for new day (reset daily counters)
            if i > start_idx:
                prev_candle = self.market.get_candle(i-1)
                if current_candle['timestamp'].date() != prev_candle['timestamp'].date():
                    self.daily_trades = 0
                    self.daily_pnl = 0
            
            # Show progress
            if show_progress and i % 1000 == 0:
                progress = (i - start_idx) / (end_idx - start_idx) * 100
                print(f"   Progress: {progress:.1f}% (Candle {i}/{end_idx})")
            
            # 1. If we have an open trade, manage it
            if self.open_trade:
                self._manage_open_trade(i, current_candle)
            
            # 2. Check for new entry signal (if no open trade and within limits)
            if not self.open_trade and self.daily_trades < self.config['max_trades_per_day']:
                self._check_entry_signal(i, current_candle, previous_candle)
            
            # 3. Update equity curve (every 10 candles for performance)
            if i % 10 == 0:
                self.equity_curve.append(self.current_balance)
        
        # Close any remaining open trade
        if self.open_trade:
            print("⚠️  Force closing open trade at end of backtest")
            self._close_trade(
                exit_price=current_candle['close'],
                exit_reason="End of backtest",
                candle_idx=i
            )
        
        # Print final results
        self._print_final_results()
        
    def _check_entry_signal(self, candle_idx, current_candle, previous_candle):
        """Check for new entry signal"""
        signal = self.strategy.get_signal(current_candle, previous_candle)
        
        if signal != 'HOLD':
            self.signals_generated += 1
            
            # Check risk limits
            if self.daily_pnl <= self.config['max_daily_loss']:
                print(f"⚠️  Skipping signal - daily loss limit reached")
                return
            
            # Calculate position size based on risk
            position_size = self.risk_manager.calculate_position_size(
                self.current_balance,
                self.config['risk_per_trade'],
                current_candle['close'],
                self._calculate_potential_sl(signal, current_candle, previous_candle)
            )
            
            # Ensure minimum position size
            position_size = max(0.01, position_size)
            
            # Calculate commission
            commission = (position_size / 0.01) * (self.config['commission_per_lot'] / 100)
            
            # Execute trade
            self._execute_trade(
                signal=signal,
                entry_price=current_candle['close'] + (self.config['spread']/100 if signal == 'BUY' else -self.config['spread']/100),
                candle_idx=candle_idx,
                current_candle=current_candle,
                previous_candle=previous_candle,
                position_size=position_size,
                commission=commission
            )
    
    def _calculate_potential_sl(self, signal, current_candle, previous_candle):
        """Calculate potential stop loss for position sizing"""
        return self.risk_manager.calculate_stop_loss(
            signal,
            current_candle['close'],
            previous_candle
        )
    
    def _execute_trade(self, signal, entry_price, candle_idx, current_candle, 
                      previous_candle, position_size, commission):
        """Execute a new trade"""
        self.trade_counter += 1
        trade_id = f"TRADE_{self.trade_counter:04d}"
        
        # Calculate SL and TP
        sl = self.risk_manager.calculate_stop_loss(
            signal,
            entry_price,
            previous_candle
        )
        
        tp = self.risk_manager.calculate_take_profit(
            signal,
            entry_price,
            sl,
            risk_reward=self.config['risk_reward_ratio']
        )
        
        # Deduct commission from balance
        self.current_balance -= commission
        
        # Create open trade record
        self.open_trade = {
            'trade_id': trade_id,
            'signal': signal,
            'entry_price': entry_price,
            'entry_candle_idx': candle_idx,
            'entry_time': current_candle['timestamp'],
            'stop_loss': sl,
            'take_profit': tp,
            'position_size': position_size,
            'commission': commission,
            'current_price': entry_price,
            'highest_price': entry_price,
            'lowest_price': entry_price,
            'candles_in_trade': 0
        }
        
        # Start observer tracking
        self.observer.start_trade(
            signal,
            entry_price,
            current_candle['timestamp']
        )
        
        # Start tracker
        self.tracker.start_trade(
            trade_id=trade_id,
            direction=signal,
            entry_price=entry_price,
            stop_loss=sl,
            take_profit=tp,
            position_size=position_size,
            entry_time=current_candle['timestamp']
        )
        
        self.daily_trades += 1
        self.trades_executed += 1
        
        print(f"\n🎯 {signal} Trade Executed #{trade_id}")
        print(f"   Entry: {entry_price:.2f} | SL: {sl:.2f} | TP: {tp:.2f}")
        print(f"   Position: {position_size:.2f} lots | Commission: ${commission:.2f}")
        print(f"   Balance: ${self.current_balance:.2f}")
    
    def _manage_open_trade(self, candle_idx, current_candle):
        """Manage an open trade"""
        if not self.open_trade:
            return
        
        self.open_trade['candles_in_trade'] += 1
        current_price = current_candle['close']
        self.open_trade['current_price'] = current_price
        
        # Update price extremes
        self.open_trade['highest_price'] = max(
            self.open_trade['highest_price'],
            current_candle['high']
        )
        self.open_trade['lowest_price'] = min(
            self.open_trade['lowest_price'],
            current_candle['low']
        )
        
        # Update tracker
        pnl, pnl_pct = self.tracker.update_trade(
            current_price,
            current_candle['timestamp']
        )
        
        # Check for SL/TP hit
        exit_reason = None
        exit_price = None
        
        if self.open_trade['signal'] == 'BUY':
            if current_price <= self.open_trade['stop_loss']:
                exit_reason = "SL hit"
                exit_price = self.open_trade['stop_loss']
            elif current_price >= self.open_trade['take_profit']:
                exit_reason = "TP hit"
                exit_price = self.open_trade['take_profit']
        else:  # SELL
            if current_price >= self.open_trade['stop_loss']:
                exit_reason = "SL hit"
                exit_price = self.open_trade['stop_loss']
            elif current_price <= self.open_trade['take_profit']:
                exit_reason = "TP hit"
                exit_price = self.open_trade['take_profit']
        
        # Check observer for early exit
        if not exit_reason:
            ema_value = current_candle.get('ema_200')
            observer_exit = self.observer.update(current_candle, ema_value)
            
            if observer_exit:
                exit_reason = f"Early: {observer_exit['exit_reason']}"
                exit_price = observer_exit['exit_price']
        
        # Close trade if exit condition met
        if exit_reason:
            self._close_trade(exit_price, exit_reason, candle_idx)
    
    def _close_trade(self, exit_price, exit_reason, candle_idx):
        """Close the current open trade"""
        if not self.open_trade:
            return
        
        # Update daily PnL before closing
        if self.open_trade['signal'] == 'BUY':
            trade_pnl = (exit_price - self.open_trade['entry_price']) * self.open_trade['position_size'] * 100
        else:  # SELL
            trade_pnl = (self.open_trade['entry_price'] - exit_price) * self.open_trade['position_size'] * 100
        
        # Subtract commission (already deducted)
        trade_pnl -= self.open_trade['commission']
        
        # Update balance
        self.current_balance += trade_pnl
        self.daily_pnl += trade_pnl
        
        # Close in tracker
        trade_record = self.tracker.close_trade(
            exit_price=exit_price,
            exit_reason=exit_reason,
            exit_time=self.market.get_candle(candle_idx)['timestamp']
        )
        
        # Reset open trade
        self.open_trade = None
        self.observer = TradeObserver()  # Reset observer
    
    def _print_final_results(self):
        """Print final backtest results"""
        print("\n" + "="*60)
        print("📊 BACKTEST COMPLETE")
        print("="*60)
        
        # Get tracker statistics
        stats = self.tracker.get_statistics()
        
        print(f"\n📈 Performance Summary:")
        print(f"   Initial Balance: ${self.config['initial_balance']:.2f}")
        print(f"   Final Balance: ${self.current_balance:.2f}")
        print(f"   Net Profit: ${self.current_balance - self.config['initial_balance']:.2f}")
        print(f"   Return: {((self.current_balance / self.config['initial_balance']) - 1) * 100:.2f}%")
        
        print(f"\n📊 Trade Statistics:")
        print(f"   Signals Generated: {self.signals_generated}")
        print(f"   Trades Executed: {self.trades_executed}")
        print(f"   Win Rate: {stats['win_rate']}%")
        print(f"   Profit Factor: {stats['profit_factor']:.2f}")
        print(f"   Expectancy: ${stats['expectancy']:.2f}")
        
        print(f"\n💰 PnL Analysis:")
        print(f"   Total PnL: ${stats['total_pnl']:.2f}")
        print(f"   Average PnL: ${stats['avg_pnl']:.2f}")
        print(f"   Largest Win: ${stats['largest_win']:.2f}")
        print(f"   Largest Loss: ${stats['largest_loss']:.2f}")
        
        # Calculate Sharpe ratio (simplified)
        if len(self.equity_curve) > 1:
            returns = pd.Series(self.equity_curve).pct_change().dropna()
            if len(returns) > 0 and returns.std() > 0:
                sharpe = (returns.mean() / returns.std()) * (252 ** 0.5)  # Annualized
                print(f"   Sharpe Ratio: {sharpe:.2f}")
        
        print(f"\n⚠️  Risk Metrics:")
        print(f"   Max Daily Trades: {self.config['max_trades_per_day']}")
        print(f"   Max Daily Loss: ${self.config['max_daily_loss']:.0f}")
        print(f"   Risk per Trade: {self.config['risk_per_trade']}%")
        
        print("\n" + "="*60)
        
        # Print detailed tracker report
        self.tracker.print_summary_report()
    
    def save_results(self, output_dir="backtest_results"):
        """Save backtest results to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save equity curve
        equity_df = pd.DataFrame({
            'balance': self.equity_curve,
            'candle_index': range(0, len(self.equity_curve) * 10, 10)
        })
        equity_df.to_csv(f"{output_dir}/equity_curve.csv", index=False)
        
        # Save trade log (already saved by tracker)
        
        # Save configuration
        config_df = pd.DataFrame([self.config])
        config_df.to_csv(f"{output_dir}/backtest_config.csv", index=False)
        
        # Save summary
        stats = self.tracker.get_statistics()
        summary = {
            'initial_balance': self.config['initial_balance'],
            'final_balance': self.current_balance,
            'net_profit': self.current_balance - self.config['initial_balance'],
            'return_pct': ((self.current_balance / self.config['initial_balance']) - 1) * 100,
            **stats
        }
        
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv(f"{output_dir}/summary.csv", index=False)
        
        print(f"\n💾 Results saved to: {output_dir}/")
        print(f"   - equity_curve.csv")
        print(f"   - summary.csv")
        print(f"   - backtest_config.csv")
        print(f"   - See logs/ for detailed trade records")


# Run a backtest
def run_backtest():
    """Run a sample backtest"""
    print("🧪 Running Sample Backtest")
    print("=" * 60)
    
    # Configuration
    config = {
        'initial_balance': 10000.0,
        'risk_per_trade': 1.0,
        'risk_reward_ratio': 1.5,
        'max_trades_per_day': 3,
        'max_daily_loss': -100.0,
        'commission_per_lot': 3.5,
        'spread': 20.0,  # 20 pips
    }
    
    # Create and run engine
    engine = BacktestEngine(config)
    
    # Load data
    data_path = "data/historical_xauusd_m1.csv"
    if not engine.load_data(data_path):
        print("❌ Failed to load data")
        return
    
    # Run backtest on first 5000 candles (about 3.5 days)
    engine.run(
        start_idx=200,  # Start after EMA calculation
        end_idx=5200,   # About 5000 candles
        show_progress=True
    )
    
    # Save results
    engine.save_results("backtest_results/sample_test")
    
    return engine

if __name__ == "__main__":
    run_backtest()
