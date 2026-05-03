#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-cloud-aiplatform",
#     "google-auth",
# ]
# ///
import sys
import argparse
from google.cloud import aiplatform
import google.auth

def list_models(project_id, location, filters):
    try:
        credentials, default_project = google.auth.default()
    except Exception:
        credentials, default_project = None, None
        
    if not project_id:
        project_id = default_project
        
    if not project_id:
        print("❌ Error: No GCP Project ID found. Set GOOGLE_CLOUD_PROJECT or use --project.")
        sys.exit(1)

    try:
        aiplatform.init(project=project_id, location=location, credentials=credentials)
        print(f"🔍 Searching for music/audio models in '{project_id}' at '{location}'...")
        print(f"📡 Keywords: {', '.join(filters)}")
        
        models = aiplatform.Model.list()
        
        found_any = False
        for model in models:
            meta_str = f"{model.display_name} {model.resource_name}".lower()
            if any(f.lower() in meta_str for f in filters):
                print("-" * 40)
                print(f"🎵 Model Found: {model.display_name}")
                print(f"🆔 ID: {model.resource_name}")
                print(f"🏷️ Version: {model.version_id}")
                found_any = True
                
        if not found_any:
            print("🤷 No specific music/audio models found in this region.")
        else:
            print("-" * 40)
            print("✅ Search complete. Use the model ID in your generation command.")
    except Exception as e:
        print(f"💥 Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=\"List music/audio capable models on Vertex AI.\")
    parser.add_argument(\"--project\", help=\"GCP Project ID\")
    parser.add_argument(\"--location\", default=\"us-central1\", help=\"GCP Location\")
    parser.add_argument(\"--extra-filters\", nargs=\"*\", default=[], help=\"Additional keywords to search for.\")
    
    args = parser.parse_args()
    
    # Default keywords for music generation
    keywords = [\"lyria\", \"music\", \"audio\", \"sound\"] + args.extra_filters
    
    try:
        list_models(args.project, args.location, keywords)
    except Exception as e:
        print(f\"💥 Error: {e}\")
        sys.exit(1)
