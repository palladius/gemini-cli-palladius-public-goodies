#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai",
#     "rich",
# ]
# ///

"""
Nano Banana Sample 🍌

This script generates an image using Gemini's image generation models (Imagen).
It leverages the new google-genai SDK, PEP 723 for dependencies via uv,
and rich for a colorful, emoji-filled CLI experience! 🎨✨
"""

import argparse
import json
import os
import sys

from google import genai
from google.genai import errors
from rich.console import Console
from rich.panel import Panel

# ============================================================================
# Constants
# ============================================================================
IMAGES_GEMINI_MODEL = "imagen-4.0-generate-001"
DEFAULT_OUTPUT_IMAGE = "output.jpg"
DEFAULT_ASPECT_RATIO = "1:1"


console = Console()

def generate_image(
    prompt: str,
    output_image: str = DEFAULT_OUTPUT_IMAGE,
    api_key: str | None = None,
    model: str = IMAGES_GEMINI_MODEL,
    number_of_images: int = 1,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    input_image: str | None = None,
    json_output: bool = False,
) -> None:
    """
    Generates an image using the google-genai SDK.

    Args:
        prompt: The text prompt describing the image.
        output_image: The path to save the generated image.
        api_key: Your Gemini API Key.
        model: The model version to use for generation.
        number_of_images: How many images to generate.
        aspect_ratio: The aspect ratio of the output image.
        input_image: Optional reference image path.
        json_output: If True, output results as clean JSON for parsing.
    """
    resolved_api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not resolved_api_key:
        error_msg = "GEMINI_API_KEY environment variable is not set and --api-key was not provided."
        if json_output:
            print(json.dumps({"error": error_msg}))
        else:
            console.print(f"[bold red]❌ Error:[/bold red] {error_msg}")
        sys.exit(1)

    try:
        client = genai.Client(api_key=resolved_api_key)
        
        if not json_output:
            console.print(f"[bold cyan]🚀 Generating image with model '{model}'...[/bold cyan]")
            console.print(Panel(prompt, title="[yellow]Prompt[/yellow]", border_style="green"))
        
        config = dict(
            number_of_images=number_of_images,
            output_mime_type="image/jpeg",
            aspect_ratio=aspect_ratio
        )
        
        if input_image and not json_output:
            console.print(f"[bold yellow]⚠️ Warning:[/bold yellow] --input-image provided ({input_image}). Reference images may require specific configurations depending on the API version.")
            
        result = client.models.generate_images(
            model=model,
            prompt=prompt,
            config=config
        )
        
        saved_files = []
        for i, generated_image in enumerate(result.generated_images):
            output_file = output_image
            if number_of_images > 1:
                base, ext = os.path.splitext(output_file)
                output_file = f"{base}_{i}{ext}"
                
            with open(output_file, 'wb') as f:
                f.write(generated_image.image.image_bytes)
            
            saved_files.append(output_file)
            
            if not json_output:
                console.print(f"[bold green]✅ Success![/bold green] Image saved to [bold blue]{output_file}[/bold blue] 🖼️")
        
        if json_output:
            print(json.dumps({
                "status": "success",
                "model": model,
                "prompt": prompt,
                "images": saved_files
            }))
            
    except errors.APIError as e:
        error_msg = f"API Error: {e}"
        if json_output:
            print(json.dumps({"error": error_msg}))
        else:
            console.print(f"[bold red]❌ {error_msg}[/bold red]")
        sys.exit(1)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        if json_output:
            print(json.dumps({"error": error_msg}))
        else:
            console.print(f"[bold red]❌ {error_msg}[/bold red]")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="🍌 Generate an image using Gemini Nano Banana (Imagen 3/4).")
    parser.add_argument("--prompt", required=True, help="The prompt for image generation.")
    parser.add_argument("--input-image", help="Optional input image path.")
    parser.add_argument("--output-image", default=DEFAULT_OUTPUT_IMAGE, help=f"The output image file path (default: {DEFAULT_OUTPUT_IMAGE}).")
    parser.add_argument("--api-key", help="Gemini API Key (default: uses GEMINI_API_KEY env var).")
    parser.add_argument("--model", default=IMAGES_GEMINI_MODEL, help=f"Model name (default: {IMAGES_GEMINI_MODEL}).")
    parser.add_argument("--number-of-images", dest="number_of_images", type=int, default=1, help="Number of images to generate (default: 1).")
    parser.add_argument("--aspect-ratio", dest="aspect_ratio", default=DEFAULT_ASPECT_RATIO, help=f"Aspect ratio (default: {DEFAULT_ASPECT_RATIO}).")
    parser.add_argument("--json", action="store_true", help="Output the results in JSON format.")
    
    args = parser.parse_args()

    generate_image(
        prompt=args.prompt,
        output_image=args.output_image,
        api_key=args.api_key,
        model=args.model,
        number_of_images=args.number_of_images,
        aspect_ratio=args.aspect_ratio,
        input_image=args.input_image,
        json_output=args.json,
    )

if __name__ == "__main__":
    main()
