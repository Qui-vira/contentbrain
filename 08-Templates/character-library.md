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
African man, sharp features, short cropped hair, light goatee, bold square black-frame glasses with blue-light lenses, confident commanding expression, Web3 creator aesthetic
```

**Reference images** (32 photos, all angles):

| Category | Files | Use For |
|----------|-------|---------|
| Extreme close-up | `img_4647.jpg`, `img_4648.jpg`, `img_4652.jpg` | Hook shots, dramatic reveals |
| Close-up | `img_4649.jpg`, `img_4650.jpg`, `img_4651.jpg` | Authority, talking head, CTA |
| Medium close-up | `img_4653.jpg`, `img_4654.jpg` | Narration, body shots |
| Medium shot | `img_4655.jpg`, `img_4671.jpg` | Standard talking head, teaching |
| Low angle (power) | `img_4656.jpg`, `img_4657.jpg`, `img_4663.jpg`, `img_4664.jpg`, `img_4665.jpg`, `img_4666.jpg`, `img_4667.jpg` | Authority, flex, bold claims |
| Full body wide | `img_4675.jpg`, `img_4676.jpg`, `img_4677.jpg` | Establishing, wide power |
| Profile (left) | `img_4673.jpg`, `img_4679.jpg` | Cinematic transitions |
| Profile (right) | `img_4678.jpg` | Cinematic, opposite direction |
| Three-quarter | `img_4670.jpg`, `img_4672.jpg` | Editorial, casual |
| Over-the-shoulder | `img_4668.jpg` | Trading desk, screen scenes |
| POV first-person | `img_4669.jpg` | Chart analysis, demo energy |
| Arms crossed | `img_4674.jpg` | Authority, thumbnails |
| Back of head | `img_4680.jpg` | Mystery reveal, rear shot |
| Mirror/creative | `img_4660.jpg`, `img_4662.jpg` | Creative angles |

All files at: `08-Media/characters/`

**Primary model (use for ALL character shots):**
- Model: Nano Banana Pro Edit
- Model ID: `fal-ai/nano-banana-pro/edit`
- Input: image_urls=[character reference URL, scene reference URLs] + scene prompt from prompt-library.md blocks
- IMPORTANT: `fal-ai/nano-banana-pro` (without /edit) is text-only and CANNOT accept reference images. Always use the /edit variant for character shots.
- Why: Same tool used for backgrounds. Prompt library has all building blocks. No need for extra models.

**Fallback only (if Nano Banana Edit fails at face consistency):**
- Model: IP-Adapter Face ID
- Model ID: `fal-ai/ip-adapter-face-id`
- Input: `face_image_url` → primary face reference above

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

## VISUAL HOOK SCENE TYPES

When generating first-frame scroll-stoppers featuring a character, use these pose + action combinations. Pair with Visual Hook Techniques from prompt-library.md.

| Scene Type | Character Action | Best Camera Angle | Best Lighting |
|-----------|-----------------|-------------------|---------------|
| Chart reaction | Looking at screen, intense focus, slight lean forward | Close-up or medium close-up | Screen glow only or neon crypto |
| Authority reveal | Arms crossed or one hand on chin, direct gaze at camera | Low angle (power) | Red accent (Quivira brand) |
| Teaching moment | Hand gesturing toward whiteboard or screen annotation | Medium shot or three-quarter | Clean studio or dramatic side light |
| Trade entry | Hands on keyboard, mid-action, decisive posture | POV first-person or over-the-shoulder | Screen glow + practical lights |
| Alpha drop | Leaning back in chair, confident smirk, one hand up | Medium wide | Dark-to-spotlight reveal |
| Pattern interrupt | Unexpected pose or location, breaking the expected frame | Dutch angle (tension) | Split light or silhouette |

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
1b. Upload the selected reference image(s) to fal.ai storage:
    ```python
    import fal_client
    ref_url = fal_client.upload_file("08-Media/characters/[filename]")
    ```
    Use the returned URL in all subsequent fal.ai API calls for this character.
    fal.ai requires publicly accessible HTTP URLs — local file paths will NOT work.
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
