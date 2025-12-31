#!/usr/bin/env python3
"""
Risk Management for Nur - Stop Loss and Take Profit calculations.
"""

class RiskManager:
    """
    Manages risk for trades.
    
    Stop Loss (SL):
    - BUY: Previous candle low
    - SELL: Previous candle high
    
    Take Profit (TP):
    - At least at previous swing high/low (M1)
    - Later can be extended with RR or ATR
    """
    
    @staticmethod
    def calculate_stop_loss(signal, entry_price, previous_candle, atr=None):
        """
        Calculate stop loss based on previous candle.
        
        Args:
            signal: 'BUY' or 'SELL'
            entry_price: float, entry price
            previous_candle: dict with 'low', 'high'
            atr: optional ATR value for dynamic SL
            
        Returns:
            float: stop loss price
        """
        if previous_candle is None:
            return None
        
        if signal == 'BUY':
            # BUY SL = Previous candle low
            sl = previous_candle['low']
            
            # Optional: Add buffer (e.g., 0.5 pips below)
            buffer = 0.05  # 0.5 pips for XAUUSD
            sl = sl - buffer
            
            # Ensure SL is reasonable (not too far)
            max_sl_distance = entry_price * 0.01  # Max 1% risk
            if entry_price - sl > max_sl_distance:
                sl = entry_price - max_sl_distance
            
            return sl
            
        elif signal == 'SELL':
            # SELL SL = Previous candle high
            sl = previous_candle['high']
            
            # Optional: Add buffer
            buffer = 0.05
            sl = sl + buffer
            
            # Ensure SL is reasonable
            max_sl_distance = entry_price * 0.01
            if sl - entry_price > max_sl_distance:
                sl = entry_price + max_sl_distance
            
            return sl
        
        return None
    
    @staticmethod
    def calculate_take_profit(signal, entry_price, stop_loss, risk_reward=1.5, 
                              previous_swing=None, atr=None):
        """
        Calculate take profit.
        
        Priority:
        1. Use previous swing if provided AND better than minimum RR
        2. Use risk-reward ratio if swing not available or not good enough
        
        Args:
            signal: 'BUY' or 'SELL'
            entry_price: float
            stop_loss: float
            risk_reward: float, default 1.5
            previous_swing: dict with 'high' (for BUY) or 'low' (for SELL)
            atr: optional ATR value for dynamic TP
            
        Returns:
            float: take profit price
        """
        if stop_loss is None:
            return None
        
        # Calculate risk (distance to SL)
        if signal == 'BUY':
            risk = entry_price - stop_loss
            # Minimum TP based on risk-reward
            min_tp = entry_price + (risk * risk_reward)
            
            # Check if previous swing high is better than minimum TP
            if previous_swing and 'high' in previous_swing:
                swing_tp = previous_swing['high']
                if swing_tp > min_tp:
                    return swing_tp
            
            return min_tp
            
        elif signal == 'SELL':
            risk = stop_loss - entry_price
            # Minimum TP based on risk-reward
            min_tp = entry_price - (risk * risk_reward)
            
            # Check if previous swing low is better than minimum TP
            if previous_swing and 'low' in previous_swing:
                swing_tp = previous_swing['low']
                if swing_tp < min_tp:
                    return swing_tp
            
            return min_tp
        
        return None
    
    @staticmethod
    def calculate_position_size(account_balance, risk_percentage, entry_price, stop_loss):
        """
        Calculate position size based on risk.
        
        Args:
            account_balance: float, account balance
            risk_percentage: float, percentage to risk (e.g., 1.0 for 1%)
            entry_price: float
            stop_loss: float
            
        Returns:
            float: position size in lots (standard lot = 100,000 units)
        """
        # Calculate risk amount
        risk_amount = account_balance * (risk_percentage / 100.0)
        
        # Calculate price risk per unit
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk <= 0:
            return 0.01  # Default minimum lot size
        
        # For XAUUSD, 1 pip = $0.10 per 0.01 lot (micro)
        # We need to convert price risk to pips
        # XAUUSD pip value = 0.01 for 0.01 lot
        
        # Simplified calculation: risk amount / price risk
        # This gives us the lot size that would lose risk_amount if SL hits
        position_size = risk_amount / (price_risk * 100)  # Simplified
        
        # Apply limits
        min_lot = 0.01  # Minimum micro lot
        max_lot = 1.0   # Maximum standard lot
        
        position_size = max(min_lot, min(position_size, max_lot))
        
        # Round to nearest 0.01
        position_size = round(position_size, 2)
        
        return position_size


# Test the risk manager
def test_risk_manager():
    """Test risk management calculations"""
    print("🧪 Testing Risk Manager")
    print("=" * 50)
    
    rm = RiskManager()
    
    # Test SL calculation
    print("\n1. Stop Loss Calculation:")
    prev_candle = {'low': 2048.5, 'high': 2051.5}
    
    sl_buy = rm.calculate_stop_loss('BUY', 2050.0, prev_candle)
    sl_sell = rm.calculate_stop_loss('SELL', 2050.0, prev_candle)
    
    print(f"BUY SL for entry 2050.0: {sl_buy:.2f}")
    print(f"SELL SL for entry 2050.0: {sl_sell:.2f}")
    
    # Test TP calculation
    print("\n2. Take Profit Calculation:")
    
    tp_buy_min = rm.calculate_take_profit('BUY', 2050.0, sl_buy, risk_reward=1.5)
    tp_sell_min = rm.calculate_take_profit('SELL', 2050.0, sl_sell, risk_reward=1.5)
    
    print(f"BUY TP (RR 1.5): {tp_buy_min:.2f}")
    print(f"SELL TP (RR 1.5): {tp_sell_min:.2f}")
    
    # Test TP with previous swing
    print("\n3. TP with Previous Swing:")
    swing_high = {'high': 2060.0}
    swing_low = {'low': 2040.0}
    
    tp_buy_swing = rm.calculate_take_profit('BUY', 2050.0, sl_buy, 
                                            risk_reward=1.5, previous_swing=swing_high)
    tp_sell_swing = rm.calculate_take_profit('SELL', 2050.0, sl_sell, 
                                             risk_reward=1.5, previous_swing=swing_low)
    
    print(f"BUY TP with swing high 2060.0: {tp_buy_swing:.2f}")
    print(f"SELL TP with swing low 2040.0: {tp_sell_swing:.2f}")
    
    # Test position size
    print("\n4. Position Size Calculation:")
    account = 10000.0  # $10,000 account
    risk_pct = 1.0     # Risk 1% per trade
    
    size_buy = rm.calculate_position_size(account, risk_pct, 2050.0, sl_buy)
    size_sell = rm.calculate_position_size(account, risk_pct, 2050.0, sl_sell)
    
    print(f"BUY position size for 1% risk on $10k: {size_buy:.2f} lots")
    print(f"SELL position size for 1% risk on $10k: {size_sell:.2f} lots")

if __name__ == "__main__":
    test_risk_manager()
