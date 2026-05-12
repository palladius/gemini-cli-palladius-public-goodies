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
    
    print(f"Searching for UID {search_uid} across projects...")
    
    projects = rm_client.search_projects(query="state:ACTIVE")
    for p in projects:
        project_id = p.project_id
        # print(f"Checking {project_id}...")
        parent = f"projects/{project_id}/locations/global"
        try:
            response = ak_client.list_keys(parent=parent)
            for key in response:
                if key.uid == search_uid:
                    print(f"\nFOUND MATCH in project: {project_id}")
                    print(f"Name: {key.display_name}")
                    print(f"Key String (truncated): {key.key_string[:14]}...")
                    return
        except Exception:
            continue
    print("\nNo match found in accessible active projects.")

if __name__ == "__main__":
    uid = sys.argv[1] if len(sys.argv) > 1 else "fff1a659-9432-4366-8bcd-d98f5847bedc"
    find_key_globally(uid)
