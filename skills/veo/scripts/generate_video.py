#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import base64
import os
import re
import sys
import time
import requests
import subprocess

# --- Inlined Dependencies from user's libraries ---

# Constants
LOCATION_ID = "us-central1"
API_ENDPOINT = "us-central1-aiplatform.googleapis.com"
VEO_MODEL_ID = "veo-3.1-fast-generate-001"
VEO_PROJECT_ID = "palladius-genai" # Assuming this is the correct project
DFLT_POLLING_INTERVAL = 10
DFLT_MAX_POLLING_ATTEMPTS = 60
DEFAULT_OUTPUT_FOLDER = "veo_videos/"

def get_access_token():
    """Fetches the GCP access token."""
    try:
        token = subprocess.check_output("gcloud auth print-access-token", shell=True, text=True).strip()
        return token
    except subprocess.CalledProcessError as e:
        print(f"Error getting gcloud access token: {e}", file=sys.stderr)
        sys.exit(1)

def async_trigger_video_generation(prompt: str, image_file: str = None) -> str:
    """Generates a video, returns an operation id."""
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    single_instance = {"prompt": prompt}
    if image_file:
        print(f"✅ Using input image: {image_file}", file=sys.stderr)
        with open(image_file, "rb") as f:
            image_data = f.read()
        encoded_image = base64.b64encode(image_data).decode("utf-8")
        single_instance["image"] = {
            "bytesBase64Encoded": encoded_image,
            "mimeType": "image/png", # Basic assumption
        }

    request_data = {
        "instances": [single_instance],
        "parameters": {
            "aspectRatio": "16:9",
            "sampleCount": 1,
            "durationSeconds": "8",
            "fps": "24",
            "generateAudio": True,
        },
    }

    url = f"https://{API_ENDPOINT}/v1/projects/{VEO_PROJECT_ID}/locations/{LOCATION_ID}/publishers/google/models/{VEO_MODEL_ID}:predictLongRunning"
    response = requests.post(url, headers=headers, json=request_data)
    response.raise_for_status()

    operation_name_match = re.search(r'"name":\s*"([^"]+)"', response.text)
    if operation_name_match:
        operation_id = operation_name_match.group(1)
        print(f"⏳ Video generation started. Operation ID: {operation_id}", file=sys.stderr)
        return operation_id
    else:
        raise ValueError(f"Could not extract operation ID. Response: {response.text}")

def retrieve_video_status(operation_id: str) -> dict:
    """Retrieves the video generation result."""
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    url = f"https://{API_ENDPOINT}/v1/projects/{VEO_PROJECT_ID}/locations/{LOCATION_ID}/publishers/google/models/{VEO_MODEL_ID}:fetchPredictOperation"
    response = requests.post(url, headers=headers, json={"operationName": operation_id})
    response.raise_for_status()
    return response.json()

def clean_prompt_for_filename(prompt: str) -> str:
    """Cleans a prompt to be used in a filename."""
    cleaned = re.sub(r"[^\w\s-]", "", prompt).strip().replace(" ", "_")
    return cleaned[:80]

def decode_and_save_video(response_json: dict, prompt: str, output_folder: str) -> str:
    """Decodes and saves the first video from the response, with error checking."""
    # Check for API errors first
    if "error" in response_json:
        error_details = response_json["error"]
        raise ValueError(f"API Error: {error_details.get('message', 'Unknown error')}")

    os.makedirs(output_folder, exist_ok=True)
    video_data = response_json.get("response", {}).get("videos", [{}])[0]
    
    if "bytesBase64Encoded" not in video_data:
        raise ValueError("Video data not found in response.")

    base64_data = video_data["bytesBase64Encoded"]
    
    filename = f"{time.strftime('%Y%m%d-%H%M%S')}-{clean_prompt_for_filename(prompt)}.mp4"
    output_path = os.path.join(output_folder, filename)
    
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(base64_data))
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Generate a video using Google's Veo model.")
    parser.add_argument("prompt", type=str, help="The text prompt for video generation.")
    parser.add_argument("-i", "--image", type=str, help="Optional path to an input image.")
    
    args = parser.parse_args()
    
    try:
        operation_id = async_trigger_video_generation(args.prompt, args.image)
        
        for i in range(DFLT_MAX_POLLING_ATTEMPTS):
            print(f"Polling attempt {i+1}/{DFLT_MAX_POLLING_ATTEMPTS}...", file=sys.stderr)
            status_response = retrieve_video_status(operation_id)
            
            if status_response.get("done"):
                print("✅ Generation complete!", file=sys.stderr)
                video_path = decode_and_save_video(status_response, args.prompt, DEFAULT_OUTPUT_FOLDER)
                print(f"Video saved to: {video_path}", file=sys.stderr)
                # Output MEDIA path for OpenClaw
                print(f"MEDIA:{video_path}")
                sys.exit(0)
            
            time.sleep(DFLT_POLLING_INTERVAL)
            
        print("❌ Polling timed out. The video is taking too long to generate.", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
