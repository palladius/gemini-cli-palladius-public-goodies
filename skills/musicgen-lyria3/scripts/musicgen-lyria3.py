#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-genai",
# ]
# ///

'''
Lyria 3 Music Generation Script
-------------------------------
This script generates 30-second music clips using Google's Lyria 3 model.

Usage:
    uv run musicgen-lyria3.py --prompt "A fast-paced EDM track with heavy bass"

Requirements:
    - uv (recommended) or google-genai package
    - GOOGLE_API_KEY environment variable (if not using ADC)
'''

import argparse
from google import genai
from google.genai import types

def main():
    parser = argparse.ArgumentParser(
        description="Generate 30-second Lyria 3 music clips using Google GenAI.",
        epilog="Example usage: ./musicgen-lyria3.py --prompt \"A fast-paced EDM track with heavy bass\""
    )
    parser.add_argument(
        "-p", "--prompt", 
        type=str, 
        default="Create a 30-second cheerful acoustic folk song with guitar and harmonica.", 
        help="The text prompt describing the music you want the AI to generate."
    )
    args = parser.parse_args()

    client = genai.Client()

    print(f"Generating music for prompt: '{args.prompt}'...")
    try:
        response = client.models.generate_content(
            model="lyria-3-clip-preview",
            contents=args.prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO", "TEXT"],
            ),
        )

        # Parse the response
        found_audio = False
        for part in response.parts:
            if part.text is not None:
                print(f"Model response: {part.text}")
            elif part.inline_data is not None:
                with open("clip.mp3", "wb") as f:
                    f.write(part.inline_data.data)
                print("✅ Audio saved to clip.mp3")
                found_audio = True
        
        if not found_audio:
            print("❌ No audio was generated in the response.")

    except Exception as e:
        print(f"❌ Error generating music: {str(e)}")

if __name__ == "__main__":
    main()
