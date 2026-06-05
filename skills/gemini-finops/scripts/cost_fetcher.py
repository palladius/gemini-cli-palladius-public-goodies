#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-cloud-monitoring",
#     "google-cloud-api-keys",
#     "pandas",
# ]
# ///
import os
import sys
import argparse
import datetime
import csv
from google.cloud import monitoring_v3
from google.cloud import api_keys_v2

def get_api_key_info(project_id):
    """Maps credential_id (UID) to (Display Name, Truncated Key)."""
    client = api_keys_v2.ApiKeysClient()
    parent = f"projects/{project_id}/locations/global"
    
    key_info = {}
    try:
        response = client.list_keys(parent=parent)
        for key in response:
            # key.uid is the credential_id in monitoring
            # key.key_string is the actual AIZA... key (might be empty depending on permissions)
            disp_name = key.display_name or key.name.split('/')[-1]
            trunc_key = (key.key_string[:10] + "...") if key.key_string else "UnknownKey"
            key_info[key.uid] = (disp_name, trunc_key)
    except Exception as e:
        print(f"Warning: Could not fetch API Key info: {e}", file=sys.stderr)
    return key_info

def fetch_usage(project_id, days=2):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"

    now = datetime.datetime.now(datetime.timezone.utc)
    start_time = now - datetime.timedelta(days=days)

    interval = monitoring_v3.TimeInterval({
        "end_time": {"seconds": int(now.timestamp())},
        "start_time": {"seconds": int(start_time.timestamp())},
    })

    filter_str = 'metric.type = "serviceruntime.googleapis.com/api/request_count"'
    
    aggregation = monitoring_v3.Aggregation({
        "alignment_period": {"seconds": 3600}, # 1 hour alignment for sparklines
        "per_series_aligner": monitoring_v3.Aggregation.Aligner.ALIGN_SUM,
        "cross_series_reducer": monitoring_v3.Aggregation.Reducer.REDUCE_SUM,
        "group_by_fields": ["metric.labels.credential_id", "resource.labels.service"],
    })

    results = client.list_time_series(
        request={
            "name": project_name,
            "filter": filter_str,
            "interval": interval,
            "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            "aggregation": aggregation,
        }
    )

    data = []
    key_info_map = get_api_key_info(project_id)

    for result in results:
        cred_id = result.metric.labels.get("credential_id", "unknown")
        service = result.resource.labels.get("service", "unknown")
        disp_name, trunc_key = key_info_map.get(cred_id, (cred_id, "Unknown"))

        for point in result.points:
            timestamp = point.interval.start_time
            usage = point.value.int64_value
            data.append({
                "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "cred_id": cred_id,
                "key_name": disp_name,
                "trunc_key": trunc_key,
                "service": service,
                "usage_count": usage
            })

    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--days", type=int, default=2)
    parser.add_argument("--output", help="CSV output path")
    args = parser.parse_args()

    data = fetch_usage(args.project, args.days)
    if not data:
        print(f"No usage data found for project {args.project}.")
        return

    fieldnames = ["timestamp", "cred_id", "key_name", "trunc_key", "service", "usage_count"]
    
    if args.output:
        with open(args.output, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        print(f"Data saved to {args.output}")
    else:
        # Print a simple summary
        print(f"{'Timestamp':<20} | {'Key Name':<20} | {'Service':<30} | {'Usage':<10}")
        print("-" * 90)
        for row in data[:20]: # Limit output
            print(f"{row['timestamp']:<20} | {row['key_name']:<20} | {row['service']:<30} | {row['usage_count']:<10}")

if __name__ == "__main__":
    main()
