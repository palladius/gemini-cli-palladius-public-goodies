#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-cloud-monitoring",
#     "google-cloud-api-keys",
#     "numpy",
# ]
# ///
import os
import sys
import argparse
import datetime
import numpy as np
from collections import defaultdict
from google.cloud import monitoring_v3
from google.cloud import api_keys_v2

# ANSI Colors
GRAY = "\033[90m"
WHITE = "\033[0m" # Reset to default (usually white/light)

def generate_sparkline(vals, num_bins=12):
    if not vals:
        return " " * num_bins
    
    # Ensure we have at least num_bins values by padding with zeros at the BEGINNING
    if len(vals) < num_bins:
        vals = [0] * (num_bins - len(vals)) + list(vals)
    
    # Split into EXACTLY num_bins sections
    splits = np.array_split(vals, num_bins)
    # Use 0 for empty splits (though padding above should prevent this)
    binned = np.array([np.sum(s) if len(s) > 0 else 0 for s in splits])
    
    vmin, vmax = np.min(binned), np.max(binned)
    if vmin == vmax:
        return "▄" * num_bins
    
    normalized = np.round((binned - vmin) / (vmax - vmin) * 7).astype(int)
    chars = [' ', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    shape_str = "".join([chars[i] for i in normalized])
    
    # Final safety check on length
    if len(shape_str) < num_bins:
        shape_str = shape_str.ljust(num_bins)
    return shape_str[:num_bins]

def get_api_key_info(project_id):
    client = api_keys_v2.ApiKeysClient()
    parent = f"projects/{project_id}/locations/global"
    key_info = {}
    try:
        response = client.list_keys(parent=parent)
        for key in response:
            disp_name = key.display_name or key.name.split('/')[-1]
            trunc_key = (key.key_string[:10] + "...") if key.key_string else "Unknown"
            key_info[key.uid] = (disp_name, trunc_key)
    except Exception:
        pass
    return key_info

def fetch_and_display(project_id):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"
    now = datetime.datetime.now(datetime.timezone.utc)
    
    # Calculate split indices for color
    # 24h: 8 bins (3h each). How many bins are "today" (since 00:00 UTC)?
    hours_today = now.hour + now.minute / 60.0
    bins_today_24h = min(8, int(hours_today / 3.0))
    split_idx_24h = 8 - bins_today_24h

    # 30d: 10 bins (3d each). How many bins are "this month" (since day 1)?
    days_this_month = now.day
    bins_this_month_30d = min(10, int(days_this_month / 3.0))
    split_idx_30d = 10 - bins_this_month_30d

    # Range definitions
    ranges = {
        "24h": {"days": 1, "alignment": 3600, "bins": 8},
        "30d": {"days": 30, "alignment": 86400, "bins": 10}
    }

    usage_data = defaultdict(lambda: {"24h": [], "30d": []})
    
    for r_name, r_config in ranges.items():
        start_time = now - datetime.timedelta(days=r_config["days"])
        interval = monitoring_v3.TimeInterval({"end_time": now, "start_time": start_time})
        
        filter_str = 'metric.type = "serviceruntime.googleapis.com/api/request_count" AND resource.type="consumed_api"'
        aggregation = monitoring_v3.Aggregation({
            "alignment_period": {"seconds": r_config["alignment"]},
            "per_series_aligner": monitoring_v3.Aggregation.Aligner.ALIGN_SUM,
            "cross_series_reducer": monitoring_v3.Aggregation.Reducer.REDUCE_SUM,
            "group_by_fields": ["metric.labels.credential_id", "resource.labels.service"],
        })

        results = client.list_time_series(request={
            "name": project_name,
            "filter": filter_str,
            "interval": interval,
            "aggregation": aggregation,
        })

        for series in results:
            cred_id = series.metric.labels.get("credential_id", "unknown")
            service = series.resource.labels.get("service", "unknown")
            unique_id = f"{cred_id}|{service}"
            points = sorted(series.points, key=lambda p: p.interval.start_time)
            usage_data[unique_id][r_name] = [p.value.int64_value for p in points]

    key_info = get_api_key_info(project_id)
    
    print(f"\nGenAI usage for Project: {project_id}")
    print("=" * 150)
    print(f"{'Cost (24h)':>10} | {'Cost (30d)':>10} | {'Last 24h':<8} | {'Last 30d':<10} | {'Key (Truncated)':<35} | {'Service'}")
    print("-" * 150)

    for unique_id, ranges_data in usage_data.items():
        total_24h = sum(ranges_data["24h"])
        total_30d = sum(ranges_data["30d"])
        
        if total_24h == 0 and total_30d == 0:
            continue

        cred_id, raw_service = unique_id.split("|")
        clean_service = raw_service.split(".")[0] if "." in raw_service else raw_service
        
        # Add Emojis to services (after the name)
        service_emoji = ""
        if clean_service in ["generativelanguage", "aiplatform"]:
            service_emoji = " ♊"
        elif clean_service in ["logging", "monitoring", "telemetry", "cloudtrace", "errorreporting"]:
            service_emoji = " 👀"
        elif clean_service == "compute":
            service_emoji = " 💻"
        elif clean_service == "storage":
            service_emoji = " 🪣"
        
        display_service = f"{clean_service}{service_emoji}"
        disp_name, trunc_key = key_info.get(cred_id, (cred_id, "Unknown"))
        
        # Calculate costs
        est_cost_24h = total_24h * 0.002 
        est_cost_30d = total_30d * 0.002
        
        raw_spark_24h = generate_sparkline(ranges_data["24h"], num_bins=ranges["24h"]["bins"])
        raw_spark_30d = generate_sparkline(ranges_data["30d"], num_bins=ranges["30d"]["bins"])
        
        # Apply Colors: Gray for past, White for current
        colored_spark_24h = f"{GRAY}{raw_spark_24h[:split_idx_24h]}{WHITE}{raw_spark_24h[split_idx_24h:]}"
        colored_spark_30d = f"{GRAY}{raw_spark_30d[:split_idx_30d]}{WHITE}{raw_spark_30d[split_idx_30d:]}"

        if disp_name == cred_id:
            if cred_id == "unknown":
                key_display = "🔑 ID: unknown"
            else:
                key_display = f"🔑 ID: {cred_id[:12]}..."
        else:
            key_display = f"🔑 {disp_name[:25]} ({trunc_key})"
        
        # Format costs with right-justification and commas
        c24_str = f"${est_cost_24h:,.2f}"
        c30_str = f"${est_cost_30d:,.2f}"
        
        # Print with fixed-width columns first (no quotes around sparklines)
        print(f"{c24_str:>10} | {c30_str:>10} | {colored_spark_24h} | {colored_spark_30d} | {key_display:<35} | {display_service}")

    print("=" * 150)
    print(f"Note: Cost is estimated at $0.002 per request (Placeholder). Generated at {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project")
    args = parser.parse_args()
    fetch_and_display(args.project)

if __name__ == "__main__":
    main()
