import sys
import csv
import argparse
from collections import defaultdict

def draw_ascii_bar(value, max_value, width=40):
    if max_value == 0:
        return "░" * width
    bar_length = int((value / max_value) * width)
    return "█" * bar_length + "░" * (width - bar_length)

def print_graph(csv_path):
    data = []
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['usage_count'] = float(row['usage_count'])
                data.append(row)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    if not data:
        print("No data to graph.")
        return

    # Aggregate by date
    daily_usage = defaultdict(float)
    for row in data:
        daily_usage[row['date']] += row['usage_count']
    
    sorted_dates = sorted(daily_usage.keys())
    max_usage = max(daily_usage.values()) if daily_usage else 0

    print("\nDaily Total Usage Graph")
    print("=" * 70)
    for date in sorted_dates:
        val = daily_usage[date]
        bar = draw_ascii_bar(val, max_usage)
        print(f"{date} | {bar} | {val:10.0f}")
    print("=" * 70)

    # Aggregate by key
    key_usage = defaultdict(float)
    for row in data:
        key_usage[row['key_name']] += row['usage_count']
    
    sorted_keys = sorted(key_usage.keys(), key=lambda x: key_usage[x], reverse=True)
    max_key_usage = max(key_usage.values()) if key_usage else 0

    print("\nUsage per API Key")
    print("=" * 70)
    for key in sorted_keys:
        val = key_usage[key]
        bar = draw_ascii_bar(val, max_key_usage)
        print(f"{key:<20} | {bar} | {val:10.0f}")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    args = parser.parse_args()
    print_graph(args.csv_file)

if __name__ == "__main__":
    main()
