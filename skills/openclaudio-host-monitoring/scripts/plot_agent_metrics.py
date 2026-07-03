#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "matplotlib",
#     "pandas",
# ]
# ///

import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
import argparse

def parse_time(time_str):
    if not time_str or time_str.lower() == 'now':
        return pd.Timestamp.now()
    if time_str.endswith('.ago'):
        time_str = time_str[:-4]
    try:
        # Try to parse as timedelta, e.g., '24h', '1d'
        delta = pd.to_timedelta(time_str)
        return pd.Timestamp.now() - delta
    except:
        # Try to parse as absolute datetime
        return pd.to_datetime(time_str)

def main():
    parser = argparse.ArgumentParser(description='Plot agent CPU and RAM metrics.')
    parser.add_argument('--from', dest='from_time', help='Start time (e.g., "24h.ago", "24h", "2026-07-01")')
    parser.add_argument('--to', dest='to_time', help='End time (e.g., "now", "2026-07-02")')
    args = parser.parse_args()

    log_file = os.path.expanduser('~/.hermes/logs/agent_metrics.csv')
    if not os.path.exists(log_file):
        print(f"Error: {log_file} does not exist.")
        sys.exit(1)

    try:
        df = pd.read_csv(log_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        df = df.resample('1min').mean()
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)

    if args.from_time:
        start_time = parse_time(args.from_time)
        df = df[df.index >= start_time]
    
    if args.to_time:
        end_time = parse_time(args.to_time)
        df = df[df.index <= end_time]

    if df.empty:
        print("No data available for the specified time range.")
        sys.exit(0)

    # Detect large gaps (more than 5 consecutive missing minutes)
    is_nan = df['total_cpu'].isna()
    group = (is_nan != is_nan.shift()).cumsum()
    nan_groups = df[is_nan].groupby(group)

    large_gaps = []
    for k, g in nan_groups:
        if len(g) > 5:
            large_gaps.append((g.index[0], g.index[-1]))

    # Interpolate small gaps (up to 5 minutes)
    df = df.interpolate(limit=5)

    output_file = os.path.expanduser('~/.hermes/logs/agent_metrics.png')

    plt.figure(figsize=(12, 10))

    # Normalize CPU usage by number of cores
    cpu_cols = [c for c in df.columns if 'cpu' in c]
    num_cores = os.cpu_count() or 1
    for col in cpu_cols:
        df[col] = df[col] / num_cores

    # Plot CPU
    plt.subplot(2, 1, 1)
    if 'ermete_cpu' in df.columns: plt.plot(df.index, df['ermete_cpu'], label='Ermete CPU', color='blue', alpha=0.7)
    if 'lobby_cpu' in df.columns: plt.plot(df.index, df['lobby_cpu'], label='Lobby CPU', color='orange', alpha=0.7)
    if 'tailscale_cpu' in df.columns: plt.plot(df.index, df['tailscale_cpu'], label='Tailscale CPU', color='green', alpha=0.7)
    if 'total_cpu' in df.columns: plt.plot(df.index, df['total_cpu'], label='Total CPU', color='red', linestyle='--', alpha=0.5)
    
    # Highlight large gaps
    for start, end in large_gaps:
        plt.axvspan(start, end, color='lightgray', alpha=0.3, label='Missing Data' if start == large_gaps[0][0] else "")

    plt.title('CPU Usage Over Time')
    plt.ylabel('% CPU')
    plt.legend()
    plt.grid(True)

    # Plot MEM
    plt.subplot(2, 1, 2)
    if 'ermete_mem' in df.columns: plt.plot(df.index, df['ermete_mem'], label='Ermete Mem', color='blue', alpha=0.7)
    if 'lobby_mem' in df.columns: plt.plot(df.index, df['lobby_mem'], label='Lobby Mem', color='orange', alpha=0.7)
    if 'tailscale_mem' in df.columns: plt.plot(df.index, df['tailscale_mem'], label='Tailscale Mem', color='green', alpha=0.7)
    if 'total_mem' in df.columns: plt.plot(df.index, df['total_mem'], label='Total Mem', color='red', linestyle='--', alpha=0.5)
    
    # Highlight large gaps
    for start, end in large_gaps:
        plt.axvspan(start, end, color='lightgray', alpha=0.3, label='Missing Data' if start == large_gaps[0][0] else "")

    plt.title('Memory Usage Over Time')
    plt.ylabel('% MEM')
    plt.xlabel('Time')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Successfully generated metrics graph at {output_file}")

if __name__ == '__main__':
    main()
