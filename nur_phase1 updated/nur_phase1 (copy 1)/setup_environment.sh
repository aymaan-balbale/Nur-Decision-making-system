#!/bin/bash
# Setup script for Nur Phase 1

echo "🚀 Setting up Nur Phase 1 Development Environment"
echo "=" * 60

# Check Python version
echo "Checking Python version..."
python3 --version

# Create data directory if not exists
mkdir -p data

# Generate synthetic data if not exists
if [ ! -f "data/historical_xauusd_m1.csv" ]; then
    echo "Generating synthetic XAUUSD data..."
    python3 data/generate_mt5_data.py
    mv historical_xauusd_m1.csv data/
else
    echo "✅ Data file already exists"
fi

# Run verification
echo "Verifying data format..."
python3 verify_data.py

# Test the market data loader
echo "Testing MT5 data loader..."
python3 test_data.py

echo ""
echo "✅ Setup complete!"
echo "Next steps:"
echo "1. Review the visualization: python data/view_data.py"
echo "2. Start implementing strategy.py"
echo "3. Run initial backtest when ready"
