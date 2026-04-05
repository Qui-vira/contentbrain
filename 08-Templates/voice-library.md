# Voice Library

## How to Add a Voice
1. Go to platform.minimax.io or fal.ai voice cloning
2. Upload a sample audio clip of the voice (10-30 seconds of clear speech)
3. Copy the returned voice_id
4. Add it to this file

## Available Voices

### Quivira (Primary)
- voice_id (MiniMax direct): moss_audio_71d1c282-1ec9-11f1-8030-1609d96f7258
- voice_id (fal.ai clone): Voice15d6039b1774374566
- Provider: MiniMax via fal.ai (`fal-ai/minimax/voice-clone`)
- Source audio: `C:\Users\Bigquiv\Downloads\Alimosho 29.m4a`
- Description: My voice. Bold, calm, authoritative, Nigerian accent.
- Use for: All personal brand content, tutorials, commentary
- Note: fal.ai clone voice_id expires after 7 days without use. Re-clone from source audio if needed.

### Narrator (Secondary)
- voice_id: [TO BE ADDED]
- Description: Clean, neutral, professional narrator voice.
- Use for: Explainer videos, educational content

### Character (Optional)
- voice_id: [TO BE ADDED]
- Description: [To be defined]
- Use for: Storytelling, skits, dramatic content

## How It Works in the Pipeline
Before generating any video with voiceover, Claude Code must:
1. Read this file
2. Show me the available voices
3. Ask: "Which voice do you want for this video?"
4. Use the selected voice_id in the fal.ai/Kling API call or MiniMax T2A call
