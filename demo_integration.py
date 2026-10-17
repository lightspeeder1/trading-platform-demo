#!/usr/bin/env python3
"""
Demo script showing how OpenBB, OpenTerminal, and NautilusTrader concepts can be integrated.

This script:
1. Uses yfinance (as a stand-in for OpenBB data access) to fetch AAPL historical data.
2. Saves the data to CSV (could be fed into OpenTerminal's SQLite or used by NautilusTrader).
3. Generates moving average crossover signals and equity curve.
4. Outputs signals that could be visualized in OpenTerminal's chart or portfolio widgets.
5. Shows how Nautilus Trader could be used for backtesting (see backtest.py).

Run this script to see the data pipeline in action.
"""
import yfinance as yf
import pandas as pd
from pathlib import Path
from signals import generate_signals

def fetch_data(symbol="AAPL", start="2022-01-01", end="2024-12-31"):
    """Fetch historical price data using yfinance."""
    print(f"Fetching {symbol} data from {start} to {end}...")
    data = yf.download(symbol, start=start, end=end, progress=False)
    if data.empty:
        raise ValueError("No data returned")
    
    # yfinance returns MultiIndex columns for single ticker: (Price, Ticker)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]  # Flatten to just price type
    
    # Reset index to have Date as column
    data = data.reset_index()
    
    # Rename columns to lowercase and remove spaces
    data.rename(columns={
        'Date': 'timestamp',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    }, inplace=True)
    
    # Ensure timestamp is in ISO format with timezone (UTC)
    data['timestamp'] = pd.to_datetime(data['timestamp']).dt.tz_localize('UTC')
    
    # Select and order columns
    data = data[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    
    # Save to CSV
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    csv_path = data_dir / f"{symbol}_daily_bar.csv"
    data.to_csv(csv_path, index=False)
    print(f"Data saved to {csv_path}")
    return csv_path

def main():
    print("=" * 60)
    print("OpenTerminal + OpenBB + NautilusTrader Integration Demo")
    print("=" * 60)
    
    # 1. Data fetch (simulating OpenBB provider)
    csv_path = fetch_data()
    
    # 2. Show first 5 rows of data
    df = pd.read_csv(csv_path)
    print("\nFirst 5 rows of data:")
    print(df.head())
    
    # 3. Generate signals and equity curve (strategy logic)
    print("\nGenerating trading signals...")
    df_with_signals, trades = generate_signals(str(csv_path))
    
    # 4. Show signals summary
    print(f"\nNumber of trade signals generated: {len(trades)}")
    if not trades.empty:
        print("Recent trade signals:")
        print(trades.tail()[['timestamp', 'close', 'signal', 'shares']])
    
    # 5. Show how this could integrate:
    print("\n" + "=" * 60)
    print("INTEGRATION POINTS")
    print("=" * 60)
    print("1. OpenTerminal: Could read data/aapl_daily_bar.csv and signals/aapl_ma_signals.csv")
    print("   to display price chart with buy/sell markers and equity curve.")
    print("2. OpenBB: Replace yfinance calls with obb.equity.price.historical(...) for")
    print("   multiple data providers (yahoo, fmp, polygon, etc.)")
    print("3. NautilusTrader: The MA strategy logic lives in strategy/ma_strategy.py")
    print("   and can be executed via BacktestEngine/LiveNode with proper risk/execution")
    print("   models. See backtest.py for a basic backtest framework.")
    print("\nAll three can run on the same machine, sharing data via files/database.")
    print("\nNext steps:")
    print("- Start OpenTerminal backend: cd OpenTerminal/server && npm run dev")
    print("- Connect OpenTerminal to data source (CSV/SQLite or OpenBB API)")
    print("- Deploy Nautilus Trader strategies for live trading")
    print("- Feed strategy performance back to OpenTerminal for visualization")

if __name__ == "__main__":
    main()