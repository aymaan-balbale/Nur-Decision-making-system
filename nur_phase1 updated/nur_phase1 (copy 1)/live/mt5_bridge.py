#!/usr/bin/env python3
"""
MT5 Bridge for Nur - Connects to MetaTrader 5.
This is the foundation for live trading.
"""
import time
import json
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

class MT5Bridge:
    """
    Bridge between Nur trading system and MetaTrader 5.
    
    Features:
    1. Connect to MT5 terminal
    2. Fetch real-time market data
    3. Execute trades
    4. Monitor positions
    5. Handle errors gracefully
    """
    
    def __init__(self, config=None):
        self.config = config or {
            'symbol': 'XAUUSD',
            'timeframe': 'M1',  # 1-minute timeframe
            'lot_size': 0.01,   # Minimum lot size
            'max_spread': 2.0,  # Maximum allowed spread in points
            'max_retries': 3,   # Connection retries
            'retry_delay': 5,   # Seconds between retries
            'demo_account': True,  # Use demo account
        }
        
        # MT5 connection state
        self.connected = False
        self.mt5 = None
        self.account_info = None
        
        # Trading state
        self.positions = []
        self.last_tick = None
        self.last_candle = None
        
        # Statistics
        self.stats = {
            'connection_attempts': 0,
            'trades_executed': 0,
            'errors': 0,
            'last_connection': None,
        }
        
        # Load credentials from environment or file
        self.credentials = self._load_credentials()
    
    def _load_credentials(self):
        """Load MT5 credentials"""
        # Try environment variables first
        creds = {
            'login': os.environ.get('MT5_LOGIN', ''),
            'password': os.environ.get('MT5_PASSWORD', ''),
            'server': os.environ.get('MT5_SERVER', ''),
            'path': os.environ.get('MT5_PATH', ''),
        }
        
        # Try credentials file
        creds_file = 'mt5_credentials.json'
        if os.path.exists(creds_file):
            try:
                with open(creds_file, 'r') as f:
                    file_creds = json.load(f)
                    creds.update(file_creds)
                print(f"✅ Loaded credentials from {creds_file}")
            except Exception as e:
                print(f"⚠️  Could not load credentials file: {e}")
        
        # For demo/testing
        if not all(creds.values()):
            print("⚠️  Using demo credentials - set MT5_LOGIN, MT5_PASSWORD, MT5_SERVER")
            print("   Or create mt5_credentials.json file")
            creds = {
                'login': 000000,  # Replace with your demo login
                'password': 'your_password',
                'server': 'DemoServer',
                'path': '/path/to/your/mt5/terminal',
            }
        
        return creds
    
    def connect(self):
        """
        Connect to MetaTrader 5 terminal.
        
        Returns:
            bool: True if connected successfully
        """
        print("🔌 Connecting to MetaTrader 5...")
        
        try:
            import MetaTrader5 as mt5
            
            # Initialize MT5
            if not mt5.initialize(
                path=self.credentials['path'],
                login=int(self.credentials['login']),
                password=self.credentials['password'],
                server=self.credentials['server'],
                timeout=10000  # 10 seconds
            ):
                print(f"❌ MT5 initialization failed: {mt5.last_error()}")
                return False
            
            self.mt5 = mt5
            self.connected = True
            
            # Get account info
            self.account_info = mt5.account_info()
            if self.account_info:
                print(f"✅ Connected to MT5")
                print(f"   Account: {self.account_info.login}")
                print(f"   Balance: ${self.account_info.balance:.2f}")
                print(f"   Equity: ${self.account_info.equity:.2f}")
                print(f"   Server: {self.account_info.server}")
            else:
                print("⚠️  Could not retrieve account info")
            
            self.stats['last_connection'] = datetime.now()
            self.stats['connection_attempts'] += 1
            
            # Symbol info
            symbol_info = mt5.symbol_info(self.config['symbol'])
            if symbol_info:
                print(f"✅ Symbol {self.config['symbol']}:")
                print(f"   Bid: {symbol_info.bid}")
                print(f"   Ask: {symbol_info.ask}")
                print(f"   Spread: {symbol_info.spread} points")
                print(f"   Digits: {symbol_info.digits}")
            else:
                print(f"❌ Could not get symbol info for {self.config['symbol']}")
            
            return True
            
        except ImportError:
            print("❌ MetaTrader5 package not installed.")
            print("   Install with: pip install MetaTrader5")
            return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MT5"""
        if self.mt5 and self.connected:
            self.mt5.shutdown()
            self.connected = False
            print("🔌 Disconnected from MT5")
    
    def get_market_data(self, timeframe='M1', count=100):
        """
        Get historical market data.
        
        Args:
            timeframe: 'M1', 'M5', 'M15', 'H1', etc.
            count: Number of candles to fetch
            
        Returns:
            DataFrame with OHLC data or None
        """
        if not self.connected:
            print("⚠️  Not connected to MT5")
            return None
        
        try:
            # Map timeframe string to MT5 constant
            tf_map = {
                'M1': self.mt5.TIMEFRAME_M1,
                'M5': self.mt5.TIMEFRAME_M5,
                'M15': self.mt5.TIMEFRAME_M15,
                'H1': self.mt5.TIMEFRAME_H1,
                'H4': self.mt5.TIMEFRAME_H4,
                'D1': self.mt5.TIMEFRAME_D1,
            }
            
            timeframe_val = tf_map.get(timeframe, self.mt5.TIMEFRAME_M1)
            
            # Get rates
            rates = self.mt5.copy_rates_from_pos(
                self.config['symbol'],
                timeframe_val,
                0,  # Start from current bar
                count
            )
            
            if rates is None or len(rates) == 0:
                print(f"⚠️  No data received for {self.config['symbol']}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Rename columns
            df.rename(columns={
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'tick_volume': 'tick_vol',
                'time': 'timestamp'
            }, inplace=True)
            
            # Set timestamp as index
            df.set_index('timestamp', inplace=True)
            
            print(f"📊 Fetched {len(df)} candles for {self.config['symbol']} {timeframe}")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching market data: {e}")
            return None
    
    def get_current_price(self):
        """
        Get current bid/ask price.
        
        Returns:
            tuple: (bid, ask, spread) or (None, None, None)
        """
        if not self.connected:
            return None, None, None
        
        try:
            tick = self.mt5.symbol_info_tick(self.config['symbol'])
            if tick:
                self.last_tick = tick
                return tick.bid, tick.ask, (tick.ask - tick.bid)
            return None, None, None
        except Exception as e:
            print(f"❌ Error getting current price: {e}")
            return None, None, None
    
    def check_connection(self):
        """Check if still connected to MT5"""
        if not self.connected or not self.mt5:
            return False
        
        try:
            # Try to get account info
            info = self.mt5.account_info()
            if info:
                self.account_info = info
                return True
            return False
        except:
            return False
    
    def place_order(self, order_type, volume, sl=None, tp=None, comment=""):
        """
        Place a market order.
        
        Args:
            order_type: 'buy' or 'sell'
            volume: Lot size
            sl: Stop loss price
            tp: Take profit price
            comment: Order comment
            
        Returns:
            Order result or None
        """
        if not self.connected:
            print("⚠️  Not connected to MT5")
            return None
        
        # Get current price
        bid, ask, spread = self.get_current_price()
        if bid is None or ask is None:
            print("❌ Cannot get current price")
            return None
        
        # Check spread
        if spread > self.config['max_spread'] * 0.0001:  # Convert points to price
            print(f"⚠️  Spread too high: {spread:.5f}")
            return None
        
        try:
            # Prepare order request
            symbol = self.config['symbol']
            price = ask if order_type.lower() == 'buy' else bid
            
            request = {
                "action": self.mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": self.mt5.ORDER_TYPE_BUY if order_type.lower() == 'buy' else self.mt5.ORDER_TYPE_SELL,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,  # Maximum price deviation
                "magic": 123456,  # Expert ID
                "comment": f"Nur_{comment}",
                "type_time": self.mt5.ORDER_TIME_GTC,  # Good till cancelled
                "type_filling": self.mt5.ORDER_FILLING_IOC,  # Immediate or cancel
            }
            
            # Send order
            result = self.mt5.order_send(request)
            
            if result.retcode == self.mt5.TRADE_RETCODE_DONE:
                print(f"✅ Order executed successfully")
                print(f"   Ticket: {result.order}")
                print(f"   Price: {result.price}")
                print(f"   Volume: {result.volume}")
                self.stats['trades_executed'] += 1
                return result
            else:
                print(f"❌ Order failed: {result.retcode}")
                print(f"   Error: {self.mt5.last_error()}")
                self.stats['errors'] += 1
                return None
                
        except Exception as e:
            print(f"❌ Error placing order: {e}")
            self.stats['errors'] += 1
            return None
    
    def close_position(self, ticket):
        """
        Close an open position.
        
        Args:
            ticket: Position ticket number
            
        Returns:
            Close result or None
        """
        if not self.connected:
            return None
        
        try:
            # Get position
            position = self.mt5.positions_get(ticket=ticket)
            if not position or len(position) == 0:
                print(f"❌ Position {ticket} not found")
                return None
            
            position = position[0]
            
            # Prepare close request
            symbol = position.symbol
            volume = position.volume
            order_type = position.type
            
            # Determine close price and type
            if order_type == self.mt5.ORDER_TYPE_BUY:
                close_type = self.mt5.ORDER_TYPE_SELL
                price = self.mt5.symbol_info_tick(symbol).bid
            else:  # SELL
                close_type = self.mt5.ORDER_TYPE_BUY
                price = self.mt5.symbol_info_tick(symbol).ask
            
            request = {
                "action": self.mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": close_type,
                "position": ticket,
                "price": price,
                "deviation": 20,
                "magic": 123456,
                "comment": "Nur_Close",
                "type_time": self.mt5.ORDER_TIME_GTC,
                "type_filling": self.mt5.ORDER_FILLING_IOC,
            }
            
            # Send close order
            result = self.mt5.order_send(request)
            
            if result.retcode == self.mt5.TRADE_RETCODE_DONE:
                print(f"✅ Position {ticket} closed successfully")
                return result
            else:
                print(f"❌ Failed to close position {ticket}")
                return None
                
        except Exception as e:
            print(f"❌ Error closing position: {e}")
            return None
    
    def get_open_positions(self):
        """
        Get all open positions.
        
        Returns:
            List of open positions
        """
        if not self.connected:
            return []
        
        try:
            positions = self.mt5.positions_get(symbol=self.config['symbol'])
            if positions is None:
                return []
            
            # Convert to list of dicts
            positions_list = []
            for pos in positions:
                positions_list.append({
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == 0 else 'SELL',
                    'volume': pos.volume,
                    'entry_price': pos.price_open,
                    'current_price': pos.price_current,
                    'sl': pos.sl,
                    'tp': pos.tp,
                    'profit': pos.profit,
                    'comment': pos.comment,
                    'time': pd.to_datetime(pos.time, unit='s'),
                })
            
            self.positions = positions_list
            return positions_list
            
        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return []
    
    def get_account_info(self):
        """
        Get account information.
        
        Returns:
            Dict with account info or None
        """
        if not self.connected:
            return None
        
        try:
            info = self.mt5.account_info()
            if info:
                return {
                    'login': info.login,
                    'balance': info.balance,
                    'equity': info.equity,
                    'margin': info.margin,
                    'free_margin': info.margin_free,
                    'margin_level': info.margin_level,
                    'currency': info.currency,
                    'leverage': info.leverage,
                    'name': info.name,
                    'server': info.server,
                }
            return None
        except Exception as e:
            print(f"❌ Error getting account info: {e}")
            return None
    
    def print_stats(self):
        """Print bridge statistics"""
        print("\n" + "="*60)
        print("📊 MT5 BRIDGE STATISTICS")
        print("="*60)
        
        print(f"\n🔌 Connection:")
        print(f"   Connected: {'✅' if self.connected else '❌'}")
        print(f"   Connection Attempts: {self.stats['connection_attempts']}")
        if self.stats['last_connection']:
            print(f"   Last Connection: {self.stats['last_connection']}")
        
        if self.account_info:
            print(f"\n💰 Account:")
            print(f"   Balance: ${self.account_info.balance:.2f}")
            print(f"   Equity: ${self.account_info.equity:.2f}")
            print(f"   Margin: ${self.account_info.margin:.2f}")
            print(f"   Free Margin: ${self.account_info.margin_free:.2f}")
        
        print(f"\n📈 Trading:")
        print(f"   Trades Executed: {self.stats['trades_executed']}")
        print(f"   Errors: {self.stats['errors']}")
        
        positions = self.get_open_positions()
        print(f"   Open Positions: {len(positions)}")
        
        if positions:
            print(f"\n📋 Open Positions:")
            for pos in positions:
                profit_color = '🟢' if pos['profit'] >= 0 else '🔴'
                print(f"   {profit_color} Ticket {pos['ticket']}: {pos['type']} {pos['volume']} lot")
                print(f"      Entry: {pos['entry_price']}, Current: {pos['current_price']}")
                print(f"      Profit: ${pos['profit']:.2f}")
        
        print("\n" + "="*60)

# Test the MT5 bridge
def test_mt5_bridge():
    """Test the MT5 bridge without actual connection"""
    print("🧪 Testing MT5 Bridge (Simulation Mode)")
    print("=" * 50)
    
    # Create bridge instance
    bridge = MT5Bridge()
    
    print("\n1. Testing initialization...")
    print(f"   Symbol: {bridge.config['symbol']}")
    print(f"   Timeframe: {bridge.config['timeframe']}")
    print(f"   Lot Size: {bridge.config['lot_size']}")
    
    print("\n2. Testing credential loading...")
    print(f"   Login: {bridge.credentials.get('login', 'Not set')}")
    print(f"   Server: {bridge.credentials.get('server', 'Not set')}")
    
    print("\n3. Testing connection (simulated)...")
    print("   ⚠️  This is a simulation - install MetaTrader5 package for real connection")
    print("   Run: pip install MetaTrader5")
    
    print("\n4. Testing data structures...")
    # Create simulated market data
    dates = pd.date_range('2024-01-01', periods=10, freq='1min')
    simulated_data = pd.DataFrame({
        'open': [2000.0] * 10,
        'high': [2005.0] * 10,
        'low': [1995.0] * 10,
        'close': [2002.0] * 10,
        'tick_vol': [100] * 10,
    }, index=dates)
    
    print(f"   Simulated data shape: {simulated_data.shape}")
    print(f"   Columns: {list(simulated_data.columns)}")
    
    print("\n5. Next steps for live trading:")
    print("   a) Install MetaTrader5: pip install MetaTrader5")
    print("   b) Set MT5 credentials in mt5_credentials.json:")
    print('''      {
        "login": 123456,
        "password": "your_password",
        "server": "DemoServer",
        "path": "/path/to/mt5/terminal"
      }''')
    print("   c) Test connection with: python live/mt5_bridge.py")
    
    print("\n✅ MT5 Bridge test complete (simulation mode)")
    return bridge

if __name__ == "__main__":
    test_mt5_bridge()
