---
name: voice-message
description: Formats the transcript of a voice message with a standardized, fixed-width layout. Use this skill whenever a voice message is received to present the transcript clearly before taking action.
compatibility: Gemini CLI
metadata:
  version: 0.1
---
# Voice Message Formatter

This skill standardizes the presentation of voice message transcripts. It wraps the transcript in a fixed-width markdown block, includes the appropriate language flag, and separates it with horizontal lines.

This ensures that transcripts are clearly distinguished from regular conversation and easy to read.

## Usage

When a voice message is received and transcribed, use the `format_transcript.sh` script to format the output.

### Command

```bash
{baseDir}/scripts/format_transcript.sh --lang [it|en] --transcript "The transcribed text goes here."
```

### Parameters

- `--lang`: The two-letter language code of the transcript (`it` for Italian, `en` for English).
- `--transcript`: The full text of the voice message transcript.

### Example

```bash
# For an Italian voice message
{baseDir}/scripts/format_transcript.sh --lang "it" --transcript "Ciao Lobby, come stai?"

# For an English voice message
{baseDir}/scripts/format_transcript.sh --lang "en" --transcript "Hey Lobby, how are you?"
```

## Internal Protocol

Moving forward, this skill should be the default way to handle incoming voice messages. The workflow is:
1. Receive voice message.
2. Transcribe it.
3. Use this skill's script to format the transcript.
4. Present the formatted transcript to the user.
5. Proceed with the user's request.
