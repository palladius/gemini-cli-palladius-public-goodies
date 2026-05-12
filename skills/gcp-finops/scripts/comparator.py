import csv
import argparse
import sys
from collections import defaultdict

def load_data(file_path):
    data = defaultdict(float)
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row['key_name'], row['service'])
                data[key] += float(row['usage_count'])
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return data

def compare_csvs(file1, file2):
    data1 = load_data(file1)
    data2 = load_data(file2)

    all_keys = sorted(list(set(data1.keys()) | set(data2.keys())))

    print("\nCost/Usage Comparison Report")
    print("=" * 105)
    print(f"{'Key Name':<20} | {'Service':<30} | {'File 1':<10} | {'File 2':<10} | {'Diff':<10} | {'% Change':<10}")
    print("-" * 105)
    
    for key in all_keys:
        v1 = data1.get(key, 0)
        v2 = data2.get(key, 0)
        diff = v2 - v1
        pct = (diff / v1 * 100) if v1 != 0 else 0
        
        print(f"{key[0]:<20} | {key[1]:<30} | {v1:<10.0f} | {v2:<10.0f} | {diff:<10.0f} | {pct:<10.2f}%")
    print("=" * 105)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file1")
    parser.add_argument("file2")
    args = parser.parse_args()
    compare_csvs(args.file1, args.file2)

if __name__ == "__main__":
    main()
