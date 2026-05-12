#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-cloud-monitoring",
# ]
# ///
import sys
import datetime
from google.cloud import monitoring_v3

def debug_labels(project_id, service_filter):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"
    now = datetime.datetime.now(datetime.timezone.utc)
    start_time = now - datetime.timedelta(hours=12)
    interval = monitoring_v3.TimeInterval({"end_time": now, "start_time": start_time})

    filter_str = f'metric.type = "serviceruntime.googleapis.com/api/request_count" AND resource.labels.service = "{service_filter}"'
    
    print(f"Querying labels for {service_filter} in {project_id}...")
    results = client.list_time_series(request={
        "name": project_name,
        "filter": filter_str,
        "interval": interval,
        "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.HEADERS, # Just headers to see labels
    })

    found = False
    for series in results:
        found = True
        print("\n--- Series Found ---")
        print("Metric Labels:")
        for k, v in series.metric.labels.items():
            print(f"  {k}: {v}")
        print("Resource Labels:")
        for k, v in series.resource.labels.items():
            print(f"  {k}: {v}")
    
    if not found:
        print("No series found for this filter.")

if __name__ == "__main__":
    project = sys.argv[1] if len(sys.argv) > 1 else "palladius-genai"
    service = sys.argv[2] if len(sys.argv) > 2 else "generativelanguage.googleapis.com"
    debug_labels(project, service)
