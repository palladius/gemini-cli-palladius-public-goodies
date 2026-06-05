#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-cloud-api-keys",
# ]
# ///
import sys
from google.cloud import api_keys_v2

def list_keys(project_id, search_uid=None):
    client = api_keys_v2.ApiKeysClient()
    parent = f"projects/{project_id}/locations/global"
    print(f"Searching keys for {project_id}...")
    try:
        response = client.list_keys(parent=parent)
        for key in response:
            if search_uid and key.uid != search_uid:
                continue
            print(f"Name: {key.display_name}")
            print(f"  UID: {key.uid}")
            print(f"  Key String (truncated): {key.key_string[:14]}...")
            print("-" * 20)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    project = sys.argv[1] if len(sys.argv) > 1 else "palladius-genai"
    uid = sys.argv[2] if len(sys.argv) > 2 else None
    list_keys(project, uid)
