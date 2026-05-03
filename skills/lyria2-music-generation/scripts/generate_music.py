#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
#     "google-auth",
# ]
# ///
"""
Generate music using Google's Lyria model via Vertex AI REST API.
Adapted from user-provided Colab snippet.

Usage:
    uv run generate_music.py --prompt "a funky bassline" --filename "output.wav" --project-id "my-project" --location "us-central1"
"""

import argparse
import base64
import json
import os
import sys
import subprocess
from pathlib import Path
import requests
import google.auth
from google.auth.transport.requests import Request

def get_access_token():
    """Get the access token using google-auth or gcloud as fallback."""
    try:
        credentials, project = google.auth.default()
        credentials.refresh(Request())
        return credentials.token, project
    except Exception as e:
        print(f"Warning: google-auth failed ({e}), trying gcloud...", file=sys.stderr)
        try:
            token = subprocess.check_output(
                ["gcloud", "auth", "print-access-token"], text=True
            ).strip()
            project = subprocess.check_output(
                ["gcloud", "config", "get-value", "project"], text=True
            ).strip()
            return token, project
        except subprocess.CalledProcessError as e:
            print(f"Error getting access token: {e}", file=sys.stderr)
            sys.exit(1)

def generate_music(prompt, output_file, project_id, location, negative_prompt=None, sample_count=1):
    token, default_project = get_access_token()
    
    if not project_id:
        project_id = default_project

    model_name = os.environ.get("LYRIA_MODEL", "lyria-002")
    print(f"🎵 Project: {project_id} | Location: {location} | Model: {model_name}")
    print(f"📝 Prompt: {prompt}")

    # Vertex AI Endpoint for Lyria
    endpoint = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_name}:predict"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Construct payload based on Colab snippet structure
    instance_data = {"prompt": prompt}
    if negative_prompt:
        instance_data["negative_prompt"] = negative_prompt

    payload = {
        "instances": [instance_data],
        "parameters": {
             "sample_count": sample_count
        }
    }

    print(f"🚀 Sending request to {endpoint}...")
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        predictions = result.get("predictions", [])
        
        if not predictions:
            print("❌ No predictions found.")
            print(json.dumps(result, indent=2))
            return

        for i, prediction in enumerate(predictions):
            # The Colab snippet reveals the key is 'bytesBase64Encoded', not 'audioContent'
            audio_b64 = prediction.get("bytesBase64Encoded") or prediction.get("audioContent")
            
            if not audio_b64:
                # Fallback: check if it's a dict wrapper
                if isinstance(prediction, dict):
                     audio_b64 = prediction.get("bytesBase64Encoded")

            if not audio_b64:
                print(f"❌ Prediction {i} content missing 'bytesBase64Encoded'.")
                print(f"Debug prediction keys: {prediction.keys() if isinstance(prediction, dict) else prediction}")
                continue

            audio_data = base64.b64decode(audio_b64)
            
            final_path = Path(output_file)
            final_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(final_path, "wb") as f:
                f.write(audio_data)
            
            print(f"💾 Saved audio to {final_path} ({len(audio_data)} bytes)")
            print(f"MEDIA: {final_path.resolve()}")

    except Exception as e:
        print(f"💥 Error: {e}")
        if 'response' in locals():
             print(f"Response text: {response.text}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", "-p", required=True)
    parser.add_argument("--filename", "-f", default="output.wav")
    parser.add_argument("--project-id", help="GCP Project ID")
    parser.add_argument("--location", default="us-central1", help="Vertex AI Location")
    # Compat args
    parser.add_argument("--model", "-m", help="Ignored")
    parser.add_argument("--duration", "-d", help="Ignored")
    parser.add_argument("--api-key", "-k", help="Ignored")
    parser.add_argument("--negative-prompt", "-n", help="Negative prompt")
    parser.add_argument("--sample-count", type=int, default=1, help="Number of samples")

    args = parser.parse_args()

    generate_music(
        prompt=args.prompt, 
        output_file=args.filename, 
        project_id=args.project_id, 
        location=args.location,
        negative_prompt=args.negative_prompt,
        sample_count=args.sample_count
    )

if __name__ == "__main__":
    main()
