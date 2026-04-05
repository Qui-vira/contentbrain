# AI Video Production Reference

This file is the reference manual for AI-assisted video production. The video editor skill reads this file when creating AI-generated videos. Claude Code uses these instructions to produce detailed prompts for each AI tool in the pipeline.

---

## TOOLS AND WHAT THEY DO

### Image Generation: Nano Banana (Google)
Purpose: Generate still images for scenes, thumbnails, B-roll frames, and keyframes.
Use when: You need a specific visual that does not exist (no stock footage, no screen recording).

### Video Generation: Kling AI
Purpose: Turn images or text prompts into short video clips (5-10 seconds per clip).
Versions: Kling 1.0, 1.5, 1.6, 2.0, 2.1 (use latest available).
Use when: You need animated scenes, transitions, or visual storytelling clips.

### Voice Cloning: MiniMax
Purpose: Clone @big_quiv's voice and generate narration from text.
Use when: You need voiceover without recording. Narrate scripts, add commentary, create intros/outros.

### Video Editing/Assembly: Remotion
Purpose: Programmatically assemble video clips, images, text overlays, and audio into a final video.
Use when: Combining multiple AI-generated clips into one finished video with timing, transitions, and captions.

---

## PROMPT ENGINEERING REFERENCE

### Image Prompts (Nano Banana)

#### Structure
```
[Subject], [Action/Pose], [Environment/Setting], [Lighting], [Camera Angle], [Style], [Mood], [Details]
```

#### Emotions and Expressions
- Confident: "confident expression, direct eye contact, slight smirk, chin slightly raised"
- Serious: "serious focused expression, furrowed brows, intense gaze"
- Excited: "wide eyes, genuine smile, animated expression, leaning forward"
- Thoughtful: "contemplative expression, hand on chin, looking slightly upward"
- Mysterious: "half-shadowed face, one eye visible, enigmatic expression"
- Powerful: "commanding posture, squared shoulders, unwavering gaze"

#### Camera Angles
- Close-up: "extreme close-up, face fills frame, shallow depth of field"
- Medium shot: "waist up, subject centered, room for text overlay"
- Wide establishing: "full body, environment visible, subject small in frame"
- Low angle (power): "shot from below, subject appears dominant, sky visible"
- High angle (vulnerability): "shot from above, subject appears smaller"
- Dutch angle (tension): "tilted frame 15-30 degrees, creates unease"
- Over shoulder: "shot from behind subject looking at screen/charts/data"
- POV: "first person perspective, hands visible, looking at laptop/phone/charts"

#### Lighting Styles
- Dramatic/moody: "single key light from left, deep shadows on right, noir style"
- Neon crypto: "blue and purple neon backlighting, dark room, face lit by screen glow"
- Clean professional: "soft even lighting, white background, minimal shadows"
- Golden hour: "warm orange light from window, long shadows, cinematic"
- Screen glow: "face illuminated only by monitor light, dark room, green/blue tint"
- Red accent: "dark background, single red light source, matches Quivira brand"

#### Style Keywords for Quivira Brand
- "dark moody background, cinematic color grading"
- "red accent lighting, dark theme"
- "clean typography overlay space"
- "professional Web3 aesthetic"
- "futuristic minimal, blockchain visual language"
- "high contrast, deep blacks, selective color"

#### Example Complete Image Prompts
```
Confident African man in dark hoodie, arms crossed, looking directly at camera, dark studio background with subtle red backlight, dramatic side lighting, medium shot, cinematic style, powerful mood, 8k quality

Close-up of hands typing on laptop showing trading charts, screen glow illuminating fingers, dark room, neon blue and green reflections, shallow depth of field, moody tech aesthetic

Wide shot of modern minimal desk setup, multiple monitors showing crypto charts, dark room, purple and blue ambient lighting, establishing shot for YouTube thumbnail, clean professional style
```

---

### Video Prompts (Kling AI)

#### Structure
```
[Starting scene description], [Motion/Action], [Camera movement], [Duration guidance], [Style/mood]
```

#### Camera Movements
- Static: "locked camera, no movement, subject moves within frame"
- Slow zoom in: "gradual zoom toward subject face, 5 seconds"
- Slow zoom out: "pull back revealing environment, 5 seconds"
- Pan left/right: "smooth horizontal pan revealing scene"
- Tilt up: "camera tilts upward from desk to face, reveals subject"
- Dolly in: "camera physically moves toward subject, parallax visible"
- Orbit: "camera slowly orbits around subject, 180 degrees"
- Crane up: "camera rises from ground level to eye level"
- Handheld subtle: "slight natural movement, documentary feel"

#### Motion Control
- Slow motion: "0.5x speed, dramatic emphasis, every detail visible"
- Normal: "1x speed, natural movement, conversational"
- Time-lapse: "4x speed, showing process over time, day to night"
- Freeze frame: "subject freezes mid-action, camera continues moving"

#### Scene Transitions (for multi-clip videos)
- Cut: "hard cut, instant scene change"
- Dissolve: "soft blend between scenes, 0.5 seconds"
- Whip pan: "fast pan connecting two scenes"
- Zoom through: "zoom into detail in scene A, zoom out reveals scene B"
- Glitch: "digital glitch effect between scenes, crypto aesthetic"
- Light flash: "bright flash to white, new scene appears"

#### Example Complete Video Prompts
```
African man in dark hoodie sitting at desk with multiple monitors, slowly turns chair to face camera with confident expression, camera slowly zooms in from medium shot to close-up over 5 seconds, moody dark lighting with blue screen glow, cinematic style

Close-up of trading chart on monitor screen, green candles rapidly forming upward, camera slowly pulls back to reveal person watching with slight smile, dark room neon lighting, 5 seconds, professional trading aesthetic

Smooth orbit shot around a modern desk setup, starting from behind showing monitors, orbiting 180 degrees to reveal the person's face, dark studio with red accent lighting, 8 seconds, cinematic quality
```

---

### Voice Cloning Prompts (MiniMax)

#### Tone Control
- Authority: "Speak with confidence and authority. Measured pace. Pause after key points."
- Storytelling: "Conversational tone. Slightly lower pitch. Natural pauses. Like telling a friend."
- Hype: "Higher energy. Faster pace. Emphasis on numbers and results. Build excitement."
- Teaching: "Clear and patient. Slightly slower. Emphasize new terms. Approachable."
- Serious: "Lower register. Slower pace. Weight behind every word. No filler."

#### Pacing Control
- Fast (hype content): "130-150 words per minute"
- Normal (educational): "110-130 words per minute"
- Slow (dramatic): "90-110 words per minute"
- Mixed (storytelling): "Start slow, speed up in middle, slow for conclusion"

#### Emphasis Markers (use in script)
- [PAUSE 1s] = 1 second silence
- [PAUSE 2s] = 2 second silence
- [EMPHASIS] before a word = stress this word
- [SLOW] = slow down for this sentence
- [FAST] = speed up for this sentence
- [WHISPER] = lower volume, intimate tone
- [LOUD] = higher volume, commanding

#### Example Script with Markers
```
[SLOW] The next 100x play in DeFi [PAUSE 1s] is not a new chain.

[NORMAL] It is AI agents managing your portfolio [EMPHASIS] while you sleep.

[PAUSE 2s]

[FAST] And most people are not paying attention.

[SLOW] Here is why. [PAUSE 1s]
```

---

## PRODUCTION WORKFLOW

### Stage 1: Script (Claude Code via /video-editor skill)
Output: Full script with spoken text, visual descriptions, timing, and emphasis markers.
Saved to: 06-Drafts/[date]-video-[topic].md with production_status: script-ready

### Stage 2: Scene Planning (Claude Code)
From the script, generate:
- A scene breakdown table: scene number, duration, visual description, camera angle, motion
- Image generation prompts for each keyframe (Nano Banana)
- Video generation prompts for each scene (Kling)
- Voice script with emphasis markers for each scene (MiniMax)
Saved to: 06-Drafts/[date]-video-[topic]-production.md

### Stage 3: Asset Generation (You execute, Claude Code writes the prompts)
1. Generate keyframe images using Nano Banana Edit (`fal-ai/nano-banana-pro/edit`):
   - Include character reference image URL as `image_urls[0]` in every call
   - Include scene reference image URLs from Art Direction step as `image_urls[1+]`
   - After generating Shot 1, add Shot 1's output URL to the reference set for Shot 2
   - This ensures visual continuity across all shots
2. Generate video clips using Kling prompts (feed keyframe images as input where supported)
3. Generate voiceover using MiniMax with the marked-up script
4. Save all assets to a folder: assets/[date]-[topic]/

### Stage 4: Assembly (Remotion or manual editing)
Claude Code can generate a Remotion script that:
- Sequences video clips in order
- Overlays text captions at correct timestamps
- Syncs voiceover audio
- Adds transitions between scenes
- Exports final video in 9:16 (TikTok/Reels) or 16:9 (YouTube)

If not using Remotion, the production.md file serves as an editing guide for a human editor.

### Stage 5: Review and Post
- Review the assembled video
- Update production_status to: approved
- Post or schedule via Buffer
- Update production_status to: posted

---

## SCENE BREAKDOWN TABLE FORMAT

When Claude Code creates a production plan, it uses this format:

```
| Scene | Duration | Visual Description | Camera | Motion | Image Prompt | Video Prompt | Voice |
|-------|----------|-------------------|--------|--------|-------------|-------------|-------|
| 1     | 0-3s     | Hook visual       | Close-up| Slow zoom in | [prompt] | [prompt] | [text with markers] |
| 2     | 3-8s     | Problem setup     | Medium | Static | [prompt] | [prompt] | [text with markers] |
| 3     | 8-20s    | Solution/value    | Wide   | Pan right | [prompt] | [prompt] | [text with markers] |
| 4     | 20-25s   | CTA               | Close-up| Zoom in | [prompt] | [prompt] | [text with markers] |
```

---

## ADDITIONAL PROMPT TIPS

### Consistency Across Scenes
- Use the same subject description in every prompt (weak signal — helps but is NOT sufficient alone)
- Use the same lighting setup text: "dark background (#0A0A0F), red accent light (#E63946)"
- Use the same style tags: "cinematic, 8k, professional"
- **REQUIRED: Pass reference images for true consistency:**
  - Upload character reference from character-library.md: `ref_url = fal_client.upload_file("08-Media/characters/[file]")`
  - Pass as `image_urls[0]` in every `fal-ai/nano-banana-pro/edit` call
  - After generating Shot 1, add its output URL as `image_urls[1]` for Shot 2 (shot chaining)
  - Text repetition alone does NOT ensure visual consistency — diffusion models are stochastic

### Negative Prompts (what to avoid)
- "no blurry, no low quality, no distorted face, no extra fingers, no watermark"
- "no cartoon style, no anime, no bright cheerful colors"
- "no generic stock photo look, no corporate sterile"

### Aspect Ratios
- TikTok/Reels/Shorts: 9:16 (1080x1920)
- YouTube: 16:9 (1920x1080)
- Instagram Feed: 1:1 (1080x1080) or 4:5 (1080x1350)
- Thumbnail: 16:9 (1280x720)

### Output Quality
- Always specify: "8k quality, high detail, photorealistic" for images
- For video: "high quality, smooth motion, cinematic grade"
- For voice: "studio quality, no background noise, clear pronunciation"

### Remotion Effect Components Reference

When writing Remotion compositions, use these effect components for professional editing:

| Effect | When to Use | Visual Result |
|--------|-------------|---------------|
| PunchZoom | Dialogue cuts, emphasis moments | Quick spring zoom in (1.0 → 1.15 → 1.0) |
| SlamIn | Stat reveals, data points, bold claims | Element scales from 1.4 → 1.0 with bounce |
| CameraShake | Dramatic openings, impact moments | Random x/y offset with spring decay |
| CameraTrack | Every shot (subtle drift) | Slow directional pan for organic motion |
| KenBurns | Static images (always) | Slow zoom in or out over duration |
| FlashTransition | Scene category changes | White flash overlay at cut point |
| LoopFade | Looping video clips | Crossfade at loop boundary |

### SFX Placement Rules

- Place a bass_drop or impact SFX at every hard cut
- Place a whoosh SFX at every flash transition
- Place a rise SFX before dramatic reveals
- Place scan/glitch SFX on data/chart reveals
- Sync SFX hits to the first frame of each new shot
- Volume: impacts at 0.7-0.8, ambient SFX at 0.3-0.4

### Shot Manifest Format for Data-Driven Compositions

```json
{
  "shots": [
    {
      "start_frame": 0,
      "duration_frames": 90,
      "type": "image",
      "asset": "shot_01.png",
      "effect": "punch",
      "flash": true,
      "ken_direction": "in",
      "track_direction": "left",
      "sfx": "bass_drop",
      "sfx_volume": 0.8,
      "text_overlay": "Caption text here"
    }
  ],
  "voiceover": "voiceover.mp3",
  "music": "background_music.mp3",
  "music_volume": 0.15
}
```
