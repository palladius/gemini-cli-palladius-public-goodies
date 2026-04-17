---
name: google-stt
description: Transcribe audio files using Google Gemini 1.5 Flash model. Supports batch transcription of multiple audio files.
compatibility: Gemini CLI
metadata:
  version: 0.1.0
---

# Google STT

## Overview

This skill provides the capability to transcribe audio files into text using Google's Gemini 1.5 Flash model. It is designed for quick and efficient transcription of voice notes, recordings, or any supported audio content.

## Workflow

1. Provide one or more paths to audio files (e.g., MP3, WAV).
2. The skill uses the `transcribe.py` script to upload the audio to Gemini and generate a transcription.
3. The transcription is printed to the console.

## Requirements

- A Gemini API key must be configured in `~/.openclaw/settings.json` under `apiKeys.google.gemini`.
- The `google-generativeai` Python library must be installed.
