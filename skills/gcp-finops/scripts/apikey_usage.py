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

def fetch_and_display(project_id, breakdown_by_product=False):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"
    now = datetime.datetime.now(datetime.timezone.utc)
    
    # Calculate split indices for color
    hours_today = now.hour + now.minute / 60.0
    bins_today_24h = min(8, int(hours_today / 3.0))
    split_idx_24h = 8 - bins_today_24h

    days_this_month = now.day
    bins_this_month_30d = min(10, int(days_this_month / 3.0))
    split_idx_30d = 10 - bins_this_month_30d

    # Range definitions
    ranges = {
        "24h": {"days": 1, "alignment": 3600, "bins": 8},
        "30d": {"days": 30, "alignment": 86400, "bins": 10}
    }

    usage_data = defaultdict(lambda: {"24h": [], "30d": []})
    
    group_by = ["metric.labels.credential_id", "resource.labels.credential_id"]
    if breakdown_by_product:
        group_by.append("resource.labels.service")

    for r_name, r_config in ranges.items():
        start_time = now - datetime.timedelta(days=r_config["days"])
        interval = monitoring_v3.TimeInterval({"end_time": now, "start_time": start_time})
        
        filter_str = 'metric.type = "serviceruntime.googleapis.com/api/request_count" AND resource.type="consumed_api"'
        aggregation = monitoring_v3.Aggregation({
            "alignment_period": {"seconds": r_config["alignment"]},
            "per_series_aligner": monitoring_v3.Aggregation.Aligner.ALIGN_SUM,
            "cross_series_reducer": monitoring_v3.Aggregation.Reducer.REDUCE_SUM,
            "group_by_fields": group_by,
        })

        results = client.list_time_series(request={
            "name": project_name,
            "filter": filter_str,
            "interval": interval,
            "aggregation": aggregation,
        })

        for series in results:
            m_cred = series.metric.labels.get("credential_id")
            r_cred = series.resource.labels.get("credential_id")
            raw_cred = m_cred or r_cred or "unknown"
            
            cred_type, cred_id = "unknown", raw_cred
            if ":" in raw_cred:
                cred_type, cred_id = raw_cred.split(":", 1)

            if breakdown_by_product:
                service = series.resource.labels.get("service", "unknown")
                unique_id = f"{cred_type}:{cred_id}|{service}"
            else:
                unique_id = f"{cred_type}:{cred_id}"

            points = sorted(series.points, key=lambda p: p.interval.start_time)
            usage_data[unique_id][r_name] = [p.value.int64_value for p in points]

    key_info = get_api_key_info(project_id)
    
    # Collect and filter rows for sorting
    rows = []
    for unique_id, ranges_data in usage_data.items():
        total_24h = sum(ranges_data["24h"])
        total_30d = sum(ranges_data["30d"])
        if total_24h == 0 and total_30d == 0:
            continue
        rows.append({
            "unique_id": unique_id,
            "total_24h": total_24h,
            "total_30d": total_30d,
            "ranges_data": ranges_data
        })
    
    rows.sort(key=lambda x: x["total_30d"], reverse=True)

    print(f"\nGenAI usage for Project: {project_id}")
    print("=" * 180)
    header = f"{'Cost (24h)':>10} | {'Cost (30d)':>10} | {'24h':<8} | {'30d':<10} | {'Identifier (ID)':<40} | {'Identity':<30}"
    if breakdown_by_product:
        header += " | Service"
    print(header)
    print("-" * 180)

    for row in rows:
        unique_id = row["unique_id"]
        total_24h = row["total_24h"]
        total_30d = row["total_30d"]
        ranges_data = row["ranges_data"]

        service_display = ""
        if breakdown_by_product:
            full_cred, raw_service = unique_id.split("|")
            cred_type, cred_id = full_cred.split(":", 1)
            clean_service = raw_service.split(".")[0] if "." in raw_service else raw_service
            
            service_emoji = ""
            if clean_service in ["generativelanguage", "aiplatform", "cloudaicompanion"]:
                service_emoji = " ♊"
            elif clean_service in ["logging", "monitoring", "telemetry", "cloudtrace", "errorreporting"]:
                service_emoji = " 👀"
            elif clean_service == "compute":
                service_emoji = " 💻"
            elif clean_service == "storage":
                service_emoji = " 🪣"
            elif clean_service in ["firestore", "sqladmin", "spanner", "bigtable"]:
                service_emoji = " 🛢️"
            elif clean_service == "run":
                service_emoji = " 🏃"
            elif clean_service.startswith("container"):
                service_emoji = " 🚢"
            service_display = f" | {clean_service}{service_emoji}"
        else:
            cred_type, cred_id = unique_id.split(":", 1)

        # Calculate costs
        est_cost_24h = total_24h * 0.002 
        est_cost_30d = total_30d * 0.002
        
        raw_spark_24h = generate_sparkline(ranges_data["24h"], num_bins=ranges["24h"]["bins"])
        raw_spark_30d = generate_sparkline(ranges_data["30d"], num_bins=ranges["30d"]["bins"])
        
        # Apply Colors: Gray for past, White for current
        colored_spark_24h = f"{GRAY}{raw_spark_24h[:split_idx_24h]}{WHITE}{raw_spark_24h[split_idx_24h:]}"
        colored_spark_30d = f"{GRAY}{raw_spark_30d[:split_idx_30d]}{WHITE}{raw_spark_30d[split_idx_30d:]}"

        # New Display Logic: ID column and Identity column
        identity = "❓ Unknown"
        if cred_type == "apikey":
            disp_name, _ = key_info.get(cred_id, (None, None))
            identity = f"🔑 {disp_name}" if disp_name else "🔑 API Key"
        elif cred_type == "serviceaccount":
            identity = "👤 Service Account"
        elif cred_type == "oauth2":
            identity = "🆔 OAuth2 Client"
        elif cred_type == "unknown":
            identity = "❓ Unknown Entity"

        # Format costs
        c24_str = f"${est_cost_24h:,.2f}"
        c30_str = f"${est_cost_30d:,.2f}"
        
        # Print with IDs before Names
        print(f"{c24_str:>10} | {c30_str:>10} | {colored_spark_24h} | {colored_spark_30d} | {cred_id:<40} | {identity:<30}{service_display}")

    print("=" * 180)
    print(f"Note: Cost is estimated at $0.002 per request (Placeholder). Generated at {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project")
    parser.add_argument("--breakdown-by-product", action="store_true", help="Add service-level breakdown")
    args = parser.parse_args()
    fetch_and_display(args.project, args.breakdown_by_product)

if __name__ == "__main__":
    main()
