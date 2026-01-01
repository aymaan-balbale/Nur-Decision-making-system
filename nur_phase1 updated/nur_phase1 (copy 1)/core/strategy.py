#!/usr/bin/env python3
"""
Nur Trading Strategy - 200 EMA Crossover with Candle-Close Logic

Implements the exact 200 EMA crossover strategy:
- BUY when candle closes above EMA200 AND previous candle closed below
- SELL when candle closes below EMA200 AND previous candle closed above
- Uses wait_for_close=True (no repainting)
"""

from typing import Optional, Dict, Any


class TradingStrategy:
    """
    Implements the exact 200 EMA crossover strategy.
    
    Entry Conditions:
    - BUY: Candle closes above EMA200 AND previous candle was below/touching EMA
    - SELL: Candle closes below EMA200 AND previous candle was above/touching EMA
    
    No mid-candle trading. No repainting.
    """
    
    @staticmethod
    def check_buy_signal(
        current_candle: Optional[Dict[str, Any]], 
        previous_candle: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Check if BUY signal is triggered.
        
        Args:
            current_candle: dict with 'close', 'ema_200'
            previous_candle: dict with 'close', 'ema_200'
            
        Returns:
            bool: True if buy signal, False otherwise
        """
        if current_candle is None or previous_candle is None:
            return False
        
        # Check if we have EMA data
        if current_candle.get('ema_200') is None or previous_candle.get('ema_200') is None:
            return False
        
        current_close: float = current_candle['close']
        current_ema: float = current_candle['ema_200']
        prev_close: float = previous_candle['close']
        prev_ema: float = previous_candle['ema_200']
        
        # Check if current candle closes above EMA
        closes_above: bool = current_close > current_ema
        
        # Check if previous candle was below or touching EMA
        # "Touching" means within 0.5 pips (0.05 for XAUUSD)
        touching_threshold: float = 0.05
        prev_below_or_touching: bool = prev_close <= (prev_ema + touching_threshold)
        
        # Both conditions must be true
        buy_signal: bool = closes_above and prev_below_or_touching
        
        if buy_signal:
            print(f"📈 BUY Signal: {current_close:.2f} > {current_ema:.2f} "
                  f"(prev: {prev_close:.2f} <= {prev_ema:.2f})")
        
        return buy_signal
    
    @staticmethod
    def check_sell_signal(
        current_candle: Optional[Dict[str, Any]], 
        previous_candle: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Check if SELL signal is triggered.
        
        Args:
            current_candle: dict with 'close', 'ema_200'
            previous_candle: dict with 'close', 'ema_200'
            
        Returns:
            bool: True if sell signal, False otherwise
        """
        if current_candle is None or previous_candle is None:
            return False
        
        # Check if we have EMA data
        if current_candle.get('ema_200') is None or previous_candle.get('ema_200') is None:
            return False
        
        current_close: float = current_candle['close']
        current_ema: float = current_candle['ema_200']
        prev_close: float = previous_candle['close']
        prev_ema: float = previous_candle['ema_200']
        
        # Check if current candle closes below EMA
        closes_below: bool = current_close < current_ema
        
        # Check if previous candle was above or touching EMA
        touching_threshold: float = 0.05
        prev_above_or_touching: bool = prev_close >= (prev_ema - touching_threshold)
        
        # Both conditions must be true
        sell_signal: bool = closes_below and prev_above_or_touching
        
        if sell_signal:
            print(f"📉 SELL Signal: {current_close:.2f} < {current_ema:.2f} "
                  f"(prev: {prev_close:.2f} >= {prev_ema:.2f})")
        
        return sell_signal
    
    @staticmethod
    def get_signal(
        current_candle: Optional[Dict[str, Any]], 
        previous_candle: Optional[Dict[str, Any]]
    ) -> str:
        """
        Get trading signal (BUY, SELL, or HOLD).
        
        Args:
            current_candle: Current candle data
            previous_candle: Previous candle data
        
        Returns:
            str: 'BUY', 'SELL', or 'HOLD'
        """
        if TradingStrategy.check_buy_signal(current_candle, previous_candle):
            return 'BUY'
        elif TradingStrategy.check_sell_signal(current_candle, previous_candle):
            return 'SELL'
        else:
            return 'HOLD'


# Test the strategy
def test_strategy() -> None:
    """Test the strategy logic with sample data"""
    print("🧪 Testing Strategy Logic")
    print("=" * 50)
    
    # Test Case 1: Buy Signal
    print("\nTest 1 - Buy Signal:")
    current = {'close': 2050.0, 'ema_200': 2049.5}
    previous = {'close': 2049.0, 'ema_200': 2049.8}
    signal = TradingStrategy.get_signal(current, previous)
    print(f"Signal: {signal}")
    
    # Test Case 2: Sell Signal
    print("\nTest 2 - Sell Signal:")
    current = {'close': 2049.0, 'ema_200': 2049.5}
    previous = {'close': 2050.0, 'ema_200': 2049.8}
    signal = TradingStrategy.get_signal(current, previous)
    print(f"Signal: {signal}")
    
    # Test Case 3: No Signal (already above)
    print("\nTest 3 - No Signal (already above EMA):")
    current = {'close': 2050.5, 'ema_200': 2049.5}
    previous = {'close': 2050.2, 'ema_200': 2049.8}
    signal = TradingStrategy.get_signal(current, previous)
    print(f"Signal: {signal}")
    
    # Test Case 4: Touching condition
    print("\nTest 4 - Buy with touching:")
    current = {'close': 2049.55, 'ema_200': 2049.5}
    previous = {'close': 2049.55, 'ema_200': 2049.5}  # Exactly on EMA
    signal = TradingStrategy.get_signal(current, previous)
    print(f"Signal: {signal}")

if __name__ == "__main__":
    test_strategy()
