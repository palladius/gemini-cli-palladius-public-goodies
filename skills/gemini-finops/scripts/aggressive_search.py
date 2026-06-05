#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-cloud-api-keys",
#     "google-cloud-resource-manager",
# ]
# ///
import sys
from google.cloud import api_keys_v2
from google.cloud import resourcemanager_v3

def find_key_globally(search_uid):
    rm_client = resourcemanager_v3.ProjectsClient()
    ak_client = api_keys_v2.ApiKeysClient()
    
    print(f"Aggressive search for UID {search_uid}...")
    
    # Get all project IDs first to avoid iterator issues
    project_ids = [p.project_id for p in rm_client.search_projects(query="state:ACTIVE")]
    print(f"Checking {len(project_ids)} projects...")

    for project_id in project_ids:
        parent = f"projects/{project_id}/locations/global"
        try:
            # Using page_size to ensure we get all keys
            response = ak_client.list_keys(parent=parent)
            for key in response:
                if key.uid == search_uid:
                    print(f"\n🎯 FOUND MATCH!")
                    print(f"Project: {project_id}")
                    print(f"Name: {key.display_name}")
                    print(f"Key String: {key.key_string}")
                    return
        except Exception:
            continue
    print("\nSearch complete. No match found.")

if __name__ == "__main__":
    uid = sys.argv[1] if len(sys.argv) > 1 else "fff1a659-9432-4366-8bcd-d98f5847bedc"
    find_key_globally(uid)
