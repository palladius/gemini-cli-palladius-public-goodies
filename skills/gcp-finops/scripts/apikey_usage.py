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
WHITE = "\033[0m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def generate_sparkline(vals, num_bins=12):
    if not vals:
        return " " * num_bins
    if len(vals) < num_bins:
        vals = [0] * (num_bins - len(vals)) + list(vals)
    splits = np.array_split(vals, num_bins)
    binned = np.array([np.sum(s) if len(s) > 0 else 0 for s in splits])
    vmin, vmax = np.min(binned), np.max(binned)
    if vmin == vmax:
        return "▄" * num_bins
    normalized = np.round((binned - vmin) / (vmax - vmin) * 7).astype(int)
    chars = [' ', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    shape_str = "".join([chars[i] for i in normalized])
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
            key_info[key.uid] = disp_name
    except Exception:
        pass
    return key_info

def fetch_and_display(project_id, breakdown_by_product=False, allowed_types=None, filter_id=None):
    if allowed_types is None:
        allowed_types = ["apikey"]
    
    # If filtering for a specific ID, we want to see everything about it
    if filter_id:
        allowed_types = ["all"]
        breakdown_by_product = True

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

    ranges = {
        "24h": {"days": 1, "alignment": 3600, "bins": 8},
        "30d": {"days": 30, "alignment": 86400, "bins": 10}
    }

    usage_data = defaultdict(lambda: {"24h": [], "30d": []})
    group_by = ["metric.labels.credential_id", "resource.labels.credential_id"]
    if breakdown_by_product:
        group_by.append("resource.labels.service")
        if filter_id:
            group_by.append("resource.labels.method")

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

            if filter_id and filter_id not in raw_cred:
                continue
            if not filter_id and cred_type not in allowed_types and "all" not in allowed_types:
                continue

            if breakdown_by_product:
                service = series.resource.labels.get("service", "unknown")
                if filter_id:
                    method = series.resource.labels.get("method", "unknown").split(".")[-1]
                    unique_id = f"{cred_type}:{cred_id}|{service}|{method}"
                else:
                    unique_id = f"{cred_type}:{cred_id}|{service}"
            else:
                unique_id = f"{cred_type}:{cred_id}"

            points = sorted(series.points, key=lambda p: p.interval.start_time)
            usage_data[unique_id][r_name] = [p.value.int64_value for p in points]

    key_info = get_api_key_info(project_id)
    
    # Group by type for display
    grouped_rows = defaultdict(list)
    for unique_id, ranges_data in usage_data.items():
        total_24h = sum(ranges_data["24h"])
        total_30d = sum(ranges_data["30d"])
        if total_24h == 0 and total_30d == 0:
            continue
        
        full_cred = unique_id.split("|")[0]
        cred_type = full_cred.split(":")[0]
        grouped_rows[cred_type].append({
            "unique_id": unique_id,
            "total_24h": total_24h,
            "total_30d": total_30d,
            "ranges_data": ranges_data
        })

    print(f"\nGenAI usage for Project: {project_id} (Filter: {filter_id or ', '.join(allowed_types)})")
    print("=" * 180)

    for c_type in sorted(grouped_rows.keys()):
        type_label = c_type.upper()
        if c_type == "apikey": type_emoji = "🔑"
        elif c_type == "serviceaccount": type_emoji = "👤"
        elif c_type == "oauth2": type_emoji = "🆔"
        else: type_emoji = "❓"
        
        print(f"\n{BOLD}{type_emoji} {type_label}{RESET}")
        print("-" * 180)
        print(f"{'Cost (24h)':>10} | {'Cost (30d)':>10} | {'24h':<8} | {'30d':<10} | {'Identifier (ID)':<40} | {'Identity':<30}" + (" | Service -> Method" if filter_id else " | Service"))
        print("-" * 180)

        rows = sorted(grouped_rows[c_type], key=lambda x: x["total_30d"], reverse=True)
        for row in rows:
            unique_id, total_24h, total_30d, ranges_data = row["unique_id"], row["total_24h"], row["total_30d"], row["ranges_data"]
            
            service_display = ""
            if breakdown_by_product:
                parts = unique_id.split("|")
                full_cred = parts[0]
                raw_service = parts[1]
                method_suffix = f" -> {parts[2]}" if len(parts) > 2 else ""
                
                cred_type, cred_id = full_cred.split(":", 1)
                clean_service = raw_service.split(".")[0] if "." in raw_service else raw_service
                
                service_emoji = ""
                if clean_service in ["generativelanguage", "aiplatform", "cloudaicompanion"]: service_emoji = " ♊"
                elif clean_service in ["logging", "monitoring", "telemetry", "cloudtrace", "errorreporting"]: service_emoji = " 👀"
                elif clean_service == "compute": service_emoji = " 💻"
                elif clean_service == "storage": service_emoji = " 🪣"
                elif clean_service in ["firestore", "sqladmin", "spanner", "bigtable"]: service_emoji = " 🛢️"
                elif clean_service == "run": service_emoji = " 🏃"
                elif clean_service.startswith("container"): service_emoji = " 🚢"
                
                display_service = f"{clean_service}{service_emoji}{method_suffix}"
                service_display = f" | {display_service}"
            else:
                cred_type, cred_id = unique_id.split(":", 1)

            raw_spark_24h = generate_sparkline(ranges_data["24h"], num_bins=8)
            raw_spark_30d = generate_sparkline(ranges_data["30d"], num_bins=10)
            colored_spark_24h = f"{GRAY}{raw_spark_24h[:split_idx_24h]}{WHITE}{raw_spark_24h[split_idx_24h:]}"
            colored_spark_30d = f"{GRAY}{raw_spark_30d[:split_idx_30d]}{WHITE}{raw_spark_30d[split_idx_30d:]}"

            identity = "Unknown"
            id_color = RESET
            if cred_type == "apikey":
                name = key_info.get(cred_id)
                if name:
                    identity = name
                    id_color = YELLOW if "mini" in name.lower() or "lobby" in name.lower() else CYAN
            elif cred_type == "serviceaccount": identity = "Service Account"
            elif cred_type == "oauth2": identity = "OAuth2 Client"

            c24_str, c30_str = f"${total_24h*0.002:,.2f}", f"${total_30d*0.002:,.2f}"
            print(f"{c24_str:>10} | {c30_str:>10} | {colored_spark_24h} | {colored_spark_30d} | {cred_id:<40} | {id_color}{identity:<30}{RESET}{service_display}")

    print("\n" + "=" * 180)
    print(f"Note: Cost is estimated at $0.002 per request. Generated at {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project")
    parser.add_argument("--breakdown-by-product", action="store_true", help="Add service-level breakdown")
    parser.add_argument("--credential-types", default="apikey", help="Comma-separated types: apikey,serviceaccount,oauth2,unknown,all")
    parser.add_argument("--for-id", help="Filter for a specific credential ID (UUID, email, etc.)")
    args = parser.parse_args()
    fetch_and_display(args.project, args.breakdown_by_product, args.credential_types.split(","), args.for_id)

if __name__ == "__main__":
    main()
