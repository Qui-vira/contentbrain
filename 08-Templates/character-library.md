# Character Library

The video-editor skill reads this file to maintain visual consistency across all shots in a video. Each character has a description, reference image path, and assigned fal.ai model for generation.

---

## HOW CHARACTER CONSISTENCY WORKS

### The Problem
AI image generators create a different-looking person every time, even with the same prompt. To keep the same character across all shots in a video, you need reference images + the right model.

### The Solution
For each character in a video:
1. Load their reference image(s) from this file
2. Use the assigned fal.ai model (each model handles consistency differently)
3. Feed the reference image + scene prompt to the model
4. The model generates the new scene while preserving the character's identity

---

## CHARACTERS

### Quivira (Primary — @big_quiv)

**Description prompt** (use in every shot featuring this character):
```
African man, confident expression, sharp features, dark premium hoodie, commanding presence, Web3 creator aesthetic
```

**Reference images** (add your photos here):
- Primary face reference: `08-Media/characters/quivira-face-01.jpg` [TO BE ADDED]
- Full body reference: `08-Media/characters/quivira-full-01.jpg` [TO BE ADDED]
- Profile reference: `08-Media/characters/quivira-profile-01.jpg` [TO BE ADDED]

**Assigned model for face consistency:**
- Model: IP-Adapter Face ID
- Model ID: `fal-ai/ip-adapter-face-id`
- Input: `face_image_url` → primary face reference above
- Model type: `SDXL-v2-plus` (best quality)

**Alternative model (for full-body poses):**
- Model: Instant Character
- Model ID: `fal-ai/instant-character`
- Input: `image_url` → full body reference above

**For editing existing shots (keep character, change scene):**
- Model: FLUX Kontext
- Model ID: `fal-ai/flux-pro/kontext`
- Input: `image_url` → the previously generated image to edit

**For swapping face into AI-generated scene:**
- Model: Face Swap
- Model ID: `fal-ai/face-swap`
- Input: source face → primary face reference, target → AI-generated scene image

### Character Slot 2: [EMPTY]

**Name:** [TO BE ADDED]
**Description prompt:** [TO BE ADDED]
**Reference images:** [TO BE ADDED]
**Assigned model:** [TO BE ADDED]

### Character Slot 3: [EMPTY]

**Name:** [TO BE ADDED]
**Description prompt:** [TO BE ADDED]
**Reference images:** [TO BE ADDED]
**Assigned model:** [TO BE ADDED]

---

## HOW TO ADD A NEW CHARACTER

1. Save 1-3 clear reference photos to `08-Media/characters/[name]-face-01.jpg` (and full/profile if available)
2. Write a description prompt that captures their distinctive features
3. Choose the right model:
   - **Face only matters** → `fal-ai/ip-adapter-face-id`
   - **Full body + pose matters** → `fal-ai/instant-character`
   - **Editing existing images** → `fal-ai/flux-pro/kontext`
4. Fill in a character slot above

---

## MODEL SELECTION GUIDE

| Scenario | Model | Model ID | Why |
|----------|-------|----------|-----|
| Same face, completely new scene | IP-Adapter Face ID | `fal-ai/ip-adapter-face-id` | Best face preservation, any scene |
| Same character, different pose/style | Instant Character | `fal-ai/instant-character` | Full identity control, no fine-tuning |
| Edit existing image, keep character | FLUX Kontext | `fal-ai/flux-pro/kontext` | Iterative editing, $0.04/image |
| Multiple reference images for context | Nano Banana 2 Edit | `fal-ai/nano-banana-pro/edit` | Up to 14 reference images |
| Swap real face into AI scene | Face Swap | `fal-ai/face-swap` | Post-process any generated image |
| Swap real face into AI video | Face Swap Video | `half-moon-ai/ai-face-swap/faceswapvideo` | Post-process any generated video |
| Generate with character + style ref | Ideogram V3 Character | `fal-ai/ideogram/character` | Strong character + style control |
| Identity-preserving portraits | PhotoMaker | `fal-ai/photomaker` | Up to 4 ref images via ZIP |

---

## CONSISTENCY RULES

1. **Same character = same reference image** across ALL shots in a video. Never switch reference images mid-project.
2. **Same description prompt** for the character in every shot. Copy it exactly from this file.
3. **Same model** for all shots of the same character in one video. Do not mix IP-Adapter and Instant Character for the same person in the same project.
4. **Same style tags** across all shots. If shot 1 uses "cinematic, 8K, editorial," every shot uses those same tags.
5. **Same lighting setup** description across all shots unless the script specifically calls for a lighting change.
6. **Face swap as fallback**: If a generated image looks great but the face is wrong, run `fal-ai/face-swap` as a post-processing step rather than re-generating the entire image.

---

## GENERATION WORKFLOW PER CHARACTER SHOT

```
1. Read this file → get character description + reference image path
2. Read prompt-library.md → get camera angle, lighting, mood, environment blocks
3. Combine: character description + scene prompt + style modifiers
4. Select model from this file based on scenario
5. Call fal.ai:
   - IP-Adapter: face_image_url=reference, prompt=combined prompt
   - Instant Character: image_url=reference, prompt=combined prompt
   - Nano Banana Edit: image_urls=[reference, scene refs], prompt=combined prompt
   - FLUX Kontext: image_url=previous image, prompt=edit instruction
6. Review output for face/identity match
7. If face is off → post-process with fal-ai/face-swap
8. Save to project assets folder
```
