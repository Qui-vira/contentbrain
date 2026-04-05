# Reference Image Guide

The video-editor skill reads this file when a shot requires real-world reference images for scene accuracy, style matching, or compositional guidance.

---

## WHY REFERENCE IMAGES

AI image generators produce better results when given visual context. Instead of describing "a luxury trading desk setup" in words alone, feeding a real photo of one as a reference gives the AI exact visual targets for layout, color, texture, and composition.

**Use reference images when:**
- The scene requires real-world accuracy (architecture, objects, specific environments)
- You want to match a specific visual style from an existing photo
- The AI keeps getting the composition wrong from text alone
- You need consistency between shots (same environment across scenes)

**Do NOT use reference images when:**
- Simple scenes (solid backgrounds, abstract spaces)
- The prompt-library.md blocks are sufficient
- Character-only shots with no complex environment

---

## IMAGE SEARCH APIs

### Primary: Pexels API

**Endpoint:** `https://api.pexels.com/v1/search`
**Auth:** API key in header: `Authorization: [PEXELS_API_KEY from .env]`
**Rate limit:** 200 requests/hour

**Search for photos:**
```
GET https://api.pexels.com/v1/search?query={keyword}&per_page=5&orientation=portrait
```

**Search for videos:**
```
GET https://api.pexels.com/videos/search?query={keyword}&per_page=3
```

**Response fields to use:**
- `photos[].src.original` — full resolution image URL
- `photos[].src.large2x` — high quality, faster download
- `photos[].src.medium` — good for reference (smaller file)

**Best for:** Stock photos, environments, objects, mood boards, video clips

### Secondary: Unsplash API

**Endpoint:** `https://api.unsplash.com/search/photos`
**Auth:** Header: `Authorization: Client-ID [UNSPLASH_ACCESS_KEY from .env]`
**Rate limit:** 50 requests/hour (demo), 5,000/hour (production)

**Search:**
```
GET https://api.unsplash.com/search/photos?query={keyword}&per_page=5&orientation=portrait
```

**Response fields to use:**
- `results[].urls.raw` — highest quality
- `results[].urls.full` — full resolution
- `results[].urls.regular` — 1080px wide (good for reference)

**Best for:** High-quality curated photography, artistic references, premium mood boards

### Fallback: Pixabay API

**Endpoint:** `https://pixabay.com/api/`
**Auth:** Query param: `key=[PIXABAY_API_KEY from .env]`
**Rate limit:** 100 requests/minute

**Search:**
```
GET https://pixabay.com/api/?key={API_KEY}&q={keyword}&per_page=5&orientation=vertical
```

**Response fields to use:**
- `hits[].largeImageURL` — high quality
- `hits[].fullHDURL` — 1920px (requires auth)

---

## WHEN TO SEARCH (Decision Tree)

```
Shot requires specific real-world environment/object?
├── YES → Search Pexels for "[environment] [style]"
│         Download top 1-3 results to 08-Media/references/
│         Feed to nano-banana-pro/edit as reference images
└── NO → Use prompt-library.md text blocks only

Shot style needs to match a specific aesthetic?
├── YES → Search Unsplash for "[mood] [aesthetic] photography"
│         Use as style reference in prompt or nano-banana-pro/edit
└── NO → Use prompt-library.md style modifiers

AI keeps generating wrong composition?
├── YES → Search for a photo with the RIGHT composition
│         Feed to nano-banana-pro/edit or flux-kontext
└── NO → Text prompt is working fine, no reference needed
```

---

## HOW TO USE REFERENCE IMAGES WITH FAL.AI

### With Nano Banana 2 Edit (up to 14 references)
The best option when you have multiple reference images for a scene.

```
Model: fal-ai/nano-banana-pro/edit
Input:
  prompt: "[scene description combining prompt-library blocks]"
  image_urls: [
    "https://fal.ai/storage/...",   // environment reference (uploaded URL)
    "https://fal.ai/storage/...",   // lighting/mood reference (uploaded URL)
    "https://fal.ai/storage/..."    // character reference (uploaded URL)
  ]
```

### Upload Local Files to fal.ai Storage (REQUIRED)
fal.ai requires publicly accessible HTTP URLs. Local file paths will NOT work.

```python
import fal_client

# Upload each reference image to get a public URL
env_url = fal_client.upload_file("08-Media/references/environments/city_night.jpg")
char_url = fal_client.upload_file("08-Media/characters/img_4649.jpg")

# Use the returned URLs in the API call
payload = {
    "prompt": "[scene description]",
    "image_urls": [env_url, char_url],
    "image_size": {"width": 1080, "height": 1920},
}
result = fal_client.subscribe("fal-ai/nano-banana-pro/edit", arguments=payload)
```

The model understands natural language instructions about which reference to use for what. Example prompt:
```
"Create a scene like the first reference image's environment, with the lighting mood from the second reference, featuring the person from the third reference. Close-up shot, cinematic quality."
```

### With FLUX Kontext (iterative editing)
Best when you have ONE image and want to modify it.

```
Model: fal-ai/flux-pro/kontext
Input:
  image_url: "reference-or-previous-shot.jpg"
  prompt: "Change the background to a trading desk, keep the person the same"
```

### With IP-Adapter Face ID (character in new scene)
Best when you have a face reference and want a completely new scene.

```
Model: fal-ai/ip-adapter-face-id
Input:
  face_image_url: "face-reference.jpg"
  prompt: "[full scene description from prompt-library blocks]"
```

The face reference handles identity. The text prompt handles everything else.

---

## LOCAL REFERENCE CACHE

Save useful reference images for reuse across videos:

```
08-Media/references/
├── environments/          # Trading desks, offices, stages, cities
├── lighting/              # Lighting mood boards
├── compositions/          # Framing and layout references
└── styles/                # Aesthetic references (film stills, editorial shots)
```

**Naming convention:** `[category]-[description]-[source].jpg`
Example: `environments-trading-desk-neon-pexels.jpg`

**Reuse rule:** Before searching Pexels/Unsplash, check `08-Media/references/` first. If a matching reference already exists locally, use it instead of downloading a new one.

---

## API KEY SETUP

Add these to your `.env` file:

```
PEXELS_API_KEY=your_key_here
UNSPLASH_ACCESS_KEY=your_key_here
PIXABAY_API_KEY=your_key_here
```

Get free API keys:
- Pexels: https://www.pexels.com/api/
- Unsplash: https://unsplash.com/developers
- Pixabay: https://pixabay.com/api/docs/
