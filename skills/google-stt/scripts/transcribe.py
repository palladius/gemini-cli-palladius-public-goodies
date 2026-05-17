import google.generativeai as genai
import sys
import os
import json

def get_gemini_api_key():
    """Reads the Gemini API key from the settings.json file."""
    settings_path = os.path.expanduser("~/.openclaw/settings.json")
    if not os.path.exists(settings_path):
        print(f"Error: settings file not found at {settings_path}", file=sys.stderr)
        sys.exit(1)
    with open(settings_path, 'r') as f:
        settings = json.load(f)
    api_key = settings.get("apiKeys", {}).get("google", {}).get("gemini")
    if not api_key:
        print("Error: Gemini API key not found in settings.json", file=sys.stderr)
        print("Please add it to apiKeys.google.gemini", file=sys.stderr)
        sys.exit(1)
    return api_key

def transcribe_audio(file_path):
    """Transcribes a single audio file using the Gemini API."""
    try:
        audio_file = genai.upload_file(path=file_path)
        model = genai.GenerativeModel(model_name="models/gemini-3.1-flash-lite")
        response = model.generate_content(["Please transcribe this audio file.", audio_file])
        # It seems that the response.text is empty, and the transcription is in the candidates
        if response.candidates:
            # The transcription is in the first candidate's content parts
            if response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text.strip()
        return "Transcription not available."

    except Exception as e:
        return f"Error during transcription: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_file_1> [<audio_file_2> ...]", file=sys.stderr)
        sys.exit(1)

    api_key = get_gemini_api_key()
    genai.configure(api_key=api_key)

    for file_path in sys.argv[1:]:
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}", file=sys.stderr)
            continue
        transcription = transcribe_audio(file_path)
        print(transcription)
