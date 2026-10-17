#!/usr/bin/env python3
"""
Demo script showing how OpenBB, OpenTerminal, and NautilusTrader concepts can be integrated.

This script:
1. Uses yfinance (as a stand-in for OpenBB data access) to fetch AAPL historical data.
2. Saves the data to CSV (could be fed into OpenTerminal's SQLite or used by NautilusTrader).
3. Shows a simple moving average crossover strategy logic (as would be used in NautilusTrader).
4. Outputs signals that could be visualized in OpenTerminal's chart or portfolio widgets.
"""

import yfinance as yf
import pandas as pd

def fetch_data(symbol="AAPL", start="2024-01-01", end="2024-01-31"):
    """Fetch historical price data using yfinance."""
    print(f"Fetching {symbol} data from {start} to {end}...")
    data = yf.download(symbol, start=start, end=end)
    if data.empty:
        raise ValueError("No data returned")
    return data

def generate_signals(data, fast=5, slow=20):
    """Generate simple MA crossover signals."""
    data = data.copy()
    data['fast_ma'] = data['Close'].rolling(window=fast).mean()
    data['slow_ma'] = data['Close'].rolling(window=slow).mean()
    data['signal'] = 0
    data.loc[data['fast_ma'] > data['slow_ma'], 'signal'] = 1   # Long
    data.loc[data['fast_ma'] < data['slow_ma'], 'signal'] = -1  # Short
    data['positions'] = data['signal'].diff()
    return data

def main():
    # 1. Data fetch (simulating OpenBB provider)
    df = fetch_data()
    print("\nFirst 5 rows of data:")
    print(df.head())

    # 2. Save data (could be imported by OpenTerminal or NautilusTrader)
    csv_path = "aapl_historical.csv"
    df.to_csv(csv_path)
    print(f"\nData saved to {csv_path}")

    # 3. Strategy simulation (NautilusTrader-like logic)
    df_with_signals = generate_signals(df)
    print("\nData with signals (last 5 rows):")
    print(df_with_signals[['Close', 'fast_ma', 'slow_ma', 'signal', 'positions']].tail())

    # 4. Extract trades
    trades = df_with_signals[df_with_signals['positions'] != 0]
    print(f"\nNumber of trade signals generated: {len(trades)}")
    if not trades.empty:
        print("Trade signals:")
        print(trades[['Close', 'signal', 'positions']])

    # 5. Show how this could integrate:
    print("\n=== Integration Concepts ===")
    print("1. OpenTerminal: Could read this CSV/SQLite to display chart with MA overlays.")
    print("2. OpenBB: Replace yfinance calls with obb.equity.price.historical(...) for multiple providers.")
    print("3. NautilusTrader: The generate_signals logic would live in a Strategy class,")
    print("   executed via BacktestEngine/LiveNode with proper risk/execution models.")
    print("\nAll three can run on the same machine, sharing data via files/database.")

if __name__ == "__main__":
    main()