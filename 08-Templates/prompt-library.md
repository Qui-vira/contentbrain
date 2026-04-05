# Prompt Library

The video-editor skill reads this file to build generation prompts per shot. Each section contains reusable prompt blocks that get combined based on the shot deck requirements.

---

## CAMERA ANGLES

Use one per shot. Copy the exact prompt text.

| Angle | Prompt Block |
|-------|-------------|
| Extreme close-up | `extreme close-up, face fills frame, eyes and expression dominant, shallow depth of field f/1.4` |
| Close-up | `close-up shot, head and shoulders, subject fills 70% of frame, shallow depth of field` |
| Medium close-up | `medium close-up, chest up, room for text overlay on sides, balanced framing` |
| Medium shot | `medium shot, waist up, subject centered, environment partially visible` |
| Medium wide | `medium wide shot, knees up, subject in context of environment, natural framing` |
| Wide / establishing | `wide establishing shot, full body visible, environment dominant, subject placed on rule of thirds` |
| Bird's eye | `bird's eye view, directly overhead, flat layout perspective, geometric composition` |
| Low angle (power) | `low angle shot from below, subject appears dominant and powerful, sky or ceiling visible behind` |
| High angle (vulnerability) | `high angle looking down on subject, appears smaller, introspective feeling` |
| Dutch angle (tension) | `Dutch angle tilted 20 degrees, creates visual tension and unease, dynamic composition` |
| Over-the-shoulder | `over-the-shoulder shot, back of head visible, subject looking at screen/object, depth layers` |
| POV first-person | `first-person POV, hands visible in frame, looking at laptop/phone/charts, immersive perspective` |
| Profile / side | `profile shot, subject facing left/right, silhouette-ready, clean background separation` |
| Three-quarter | `three-quarter angle, face turned 45 degrees from camera, dimensional and editorial` |
| Macro-to-wide reveal | `extreme macro close-up transitioning to wide shot, starts on small detail then pulls back to reveal full context, cinematic rack focus` |
| Hand-in-frame action | `first-person view with hands visible performing an action, natural movement, immersive crafting perspective` |
| Split screen comparison | `split screen side-by-side composition, left panel vs right panel, clean dividing line, before-and-after energy` |
| Green screen overlay | `creator composited over reference footage or screenshots, picture-in-picture with background content visible` |

---

## LIGHTING STYLES

Use one primary + optional accent. Copy the exact prompt text.

| Style | Prompt Block |
|-------|-------------|
| Dramatic side light | `single key light from camera left at 45 degrees, deep shadows on right side, noir-style contrast, dramatic mood` |
| Neon crypto | `neon blue and purple backlighting, dark room, face lit by soft screen glow, cyberpunk-adjacent, tech aesthetic` |
| Red accent (Quivira brand) | `dark background, single red accent light from behind, red rim light on edges, high contrast, brand signature` |
| Golden hour | `warm golden light streaming from window at low angle, long soft shadows, cinematic warmth, orange-amber tones` |
| Screen glow only | `face illuminated only by monitor light, completely dark room, green and blue screen reflections on skin, intimate tech mood` |
| Clean studio | `soft even studio lighting, white or neutral background, minimal shadows, professional headshot quality` |
| Silhouette | `strong backlight, subject in full silhouette, rim light on edges only, mysterious and powerful` |
| Split light | `light hitting exactly half the face, other half in complete shadow, Rembrandt-style, high drama` |
| Overhead / top light | `light source directly above, shadows under eyes and chin, editorial fashion style, moody` |
| Practical lights | `lit only by practical sources in scene — desk lamp, monitor, candles — naturalistic, warm, authentic` |
| Dark-to-spotlight reveal | `starts in near-total darkness, single spotlight snaps on to illuminate subject or object, dramatic contrast shift, visual hook energy` |
| Single candle glow | `one candle flame illuminating face in darkness, warm flicker on skin, everything else black, intimate and raw` |

---

## MOODS / ATMOSPHERE

Use one per shot. Sets the emotional tone.

| Mood | Prompt Block |
|------|-------------|
| Intense / powerful | `intense atmosphere, commanding presence, sharp focus, high contrast, every detail deliberate` |
| Calm / wise | `calm serene atmosphere, composed and centered, soft tones, unhurried energy, meditative quality` |
| Chaotic / urgent | `chaotic energy, multiple data streams, fast-moving particles, screen glitches, information overload aesthetic` |
| Luxurious / premium | `luxury aesthetic, rich textures, matte surfaces, gold and dark tones, aspirational quality` |
| Gritty / streetwise | `raw gritty aesthetic, urban textures, concrete and steel, imperfect surfaces, authentic not polished` |
| Clean / minimal | `ultra clean minimalist aesthetic, negative space, single focal point, modern design sensibility` |
| Mysterious | `mysterious atmosphere, fog or haze, partial visibility, questions unanswered, intrigue` |
| Futuristic | `futuristic environment, holographic elements, floating data, clean lines, advanced technology` |
| Warm / personal | `warm personal atmosphere, soft light, comfortable environment, approachable and relatable` |
| Dark / ominous | `dark ominous atmosphere, deep shadows, sense of warning, something at stake, tension` |
| Pattern interrupt | `jarring visual contrast, unexpected composition, something visually wrong that forces a second look, scroll-stopping energy` |
| Demo energy | `hands-on active demonstration in progress, tools visible, mid-action frozen moment, workshop feel` |
| Reveal moment | `split-second of discovery, curtain-pull energy, the exact moment something hidden becomes visible, dramatic unveiling` |

---

## ENVIRONMENTS / SETTINGS

Match the scene context. Combine with lighting and mood.

| Environment | Prompt Block |
|-------------|-------------|
| Trading desk | `modern trading desk with multiple monitors showing crypto charts, dark room, ambient screen glow, professional setup` |
| Studio (dark) | `dark professional studio, clean background, controlled lighting, content creator setup` |
| Studio (bright) | `bright clean studio, white walls, soft diffused light, modern minimalist` |
| Urban rooftop | `city rooftop at night, skyline in background, ambient city lights, urban atmosphere` |
| Conference stage | `professional conference stage, spotlight on speaker, dark audience in background, authority positioning` |
| Abstract void | `pure black void background, subject floating in darkness, isolated focus, cinematic` |
| Digital space | `abstract digital environment, data streams, blockchain nodes, floating code, matrix-inspired` |
| Home office | `clean home office, natural light from window, plants, personal touches, authentic workspace` |
| Luxury interior | `high-end interior, marble surfaces, dark wood, ambient lighting, premium atmosphere` |
| Street / outdoor | `urban street environment, concrete walls, natural light, candid feel, real world` |
| Whiteboard / teaching | `clean whiteboard or glass board in background, marker annotations visible, educational setup, authority positioning` |
| Multi-monitor command center | `wall of monitors showing charts, data, and dashboards, command center aesthetic, ambient multi-screen glow, high-stakes operation feel` |

---

## STYLE MODIFIERS

Add to any prompt for quality and aesthetic control.

### Quality Tags (always include at least one)
- `photograph, ultra realistic, editorial quality, 8K resolution`
- `photorealistic, high detail, professional photography, sharp focus`
- `cinematic still frame, film quality, color graded`

### Aesthetic Tags (pick what fits)
- `cinematic color grading, film grain, anamorphic` — for cinematic feel
- `clean digital, sharp, modern` — for professional/corporate
- `matte finish, desaturated, editorial` — for premium feel
- `high contrast, deep blacks, selective color` — for drama
- `35mm film, natural grain, slight vignette` — for authentic/raw

### Quivira Brand Tags (use for brand-consistent content)
- `dark background (#0A0A0F deep black), red accent lighting (#E63946), cinematic color grading, warm shadows`
- `dark navy-black environment (#0C0C1E), subtle hexagonal grid at 10% opacity, thin teal (#0EA5E9) node connections, matte finish surfaces`
- `high contrast, deep blacks (#0A0A0F), selective red highlights (#E63946), gold accent (#FFD700) at 5% usage`
- `clean negative space for typography overlay, room for text, no clutter in upper 30% of frame`
- **Brand reference image:** Always pass `08-Media/references/styles/quivira-brand-canonical.png` as `image_urls[0]` alongside these text tags when using Nano Banana Edit. Upload to fal.ai storage first.

---

## NEGATIVE PROMPTS

Standard exclusions. Always include unless the shot specifically needs what's listed.

### Default Negative (use for all photorealistic shots)
```
blurry, low quality, distorted face, extra fingers, extra limbs, watermark, text, logo, cartoon, anime, illustration, painting, 3D render, CGI look, overexposed, underexposed, cropped, out of frame, duplicate, disfigured
```

### For Brand Content (add to default)
```
bright cheerful colors, pastel, generic stock photo, corporate sterile, clip art, childish, unprofessional
```

### For Character Shots (add to default)
```
wrong ethnicity, different person, inconsistent features, morphed face, uncanny valley, plastic skin, wax figure
```

---

## PROMPT ASSEMBLY GUIDE

When building a prompt for a shot, the video-editor skill combines blocks in this order:

```
[Character description from character-library.md], [Action/Pose], [Environment block], [Lighting block], [Camera angle block], [Style modifiers], [Mood block], [Aspect ratio]
```

**CRITICAL: Reference Image Injection**
The text prompt handles scene composition. Reference images handle identity preservation and style consistency.
- Load character reference image(s) from paths in character-library.md
- Upload to fal.ai storage: `url = fal_client.upload_file("08-Media/characters/[file]")`
- Pass in `image_urls` parameter alongside the text prompt
- The text prompt alone does NOT ensure character or style consistency

### Example Assembly

Shot: "Quivira looking at charts, confident, trading desk, dramatic lighting, close-up"

Assembled prompt:
```
Confident African man in dark premium hoodie, slight smirk, looking at trading screen with focused expression, modern trading desk with multiple monitors showing crypto charts dark room ambient screen glow, single key light from camera left at 45 degrees deep shadows on right side noir-style contrast, close-up shot head and shoulders subject fills 70% of frame shallow depth of field, photograph ultra realistic editorial quality 8K resolution, cinematic color grading dark moody background red accent lighting, intense atmosphere commanding presence sharp focus, 9:16 vertical format
```

Negative prompt:
```
blurry, low quality, distorted face, extra fingers, watermark, cartoon, anime, 3D render, bright cheerful colors, generic stock photo, wrong ethnicity, different person
```

---

## VISUAL HOOK TECHNIQUES

Use these prompt blocks to generate first-frame scroll-stoppers. Each technique is designed to work as a still image that stops the scroll, then transitions into the video.

> **The 1-Second Rule:** The first frame must work as a standalone thumbnail. Design it to stop the scroll before the viewer even hears audio.

### Object Reveal Hooks

| Technique | Prompt Block |
|-----------|-------------|
| Chart close-up reveal | `extreme macro close-up of candlestick chart at key price level, single green candle in sharp focus, surrounding candles blurred, dramatic lighting, the moment before a breakout` |
| Hand-draw annotation | `hand holding marker drawing support line on physical whiteboard showing crypto chart, mid-stroke, ink visible, focused deliberate action, educational authority` |
| Price target slam | `bold red text "$100K" floating over dark background with subtle Bitcoin chart, text appears to shatter through the frame, impact energy, glass particles` |
| Portfolio reveal | `split composition: left side chaotic scattered crypto logos in disarray, right side clean organized portfolio dashboard glowing green, chaos-to-clarity transformation` |

### Dramatic Visual Hooks

| Technique | Prompt Block |
|-----------|-------------|
| Bitcoin shatter | `Bitcoin coin shattering through a laptop screen, glass shards flying toward camera, dramatic red and gold lighting, explosive energy, frozen mid-impact` |
| DeFi hologram | `DeFi dashboard transforming into a floating holographic display, blue and purple neon projections, futuristic trading interface, dark room, awe-inspiring scale` |
| Whale alert | `massive whale silhouette visible through a screen showing blockchain transactions, matrix-style data scrolling, green text on black, something big is happening` |
| Alpha countdown | `dark frame with glowing red countdown number "3" center frame, minimal, tension, the moment before a reveal, cinematic countdown aesthetic` |

### Trading-Specific Hooks

| Technique | Prompt Block |
|-----------|-------------|
| Trade replay | `screen recording aesthetic of a live trade execution, buy order flashing green, position size visible, P&L counter running, the exact moment of entry` |
| Multi-timeframe rapid | `three trading chart panels arranged horizontally (1H, 4H, Daily), all showing the same pair, key level highlighted with red line across all three, confluence moment` |
| On-chain reveal | `wallet address displayed on screen with transaction history scrolling, one massive transaction highlighted in gold, blockchain explorer aesthetic, discovery moment` |
| Candle drama | `single massive green candle rising from darkness, camera looking up at it like a skyscraper, volumetric light from above, the breakout candle that changes everything` |

---

## AI VISUAL HOOK WORKFLOW

Prompt blocks for AI-generated visual hooks using Nano Banana, Veo 3, and fal.ai. These create Hollywood-quality scroll-stoppers from static images.

### Nano Banana Prompts (via Gemini)

Feed a static frame from your video + one of these transformation prompts:

| Effect | Prompt |
|--------|--------|
| Explosive reveal | `Make this [object] explode outward toward the camera with dramatic force, glass shards and particles, cinematic slow motion` |
| Morphing transform | `Transform this [chart/dashboard] into physical gold bars and coins, magical transmutation effect, golden particles` |
| Shatter entrance | `Make this [object] shatter through the frame from behind, breaking glass effect, dramatic impact, freeze at peak moment` |
| Dissolve to reveal | `Dissolve the foreground to reveal [object] behind it, particle disintegration effect, elegant and cinematic` |
| Holographic projection | `Turn this [screen/dashboard] into a floating holographic projection, blue light, volumetric rays, futuristic` |

### AI Sound Effect Prompts (ElevenLabs)

Pair with the visual hooks above. Describe the sound you need:

| Visual Effect | Sound Prompt |
|---------------|-------------|
| Explosion / shatter | `deep bass impact followed by glass breaking and debris settling, cinematic, punchy` |
| Morphing / transform | `magical shimmer building to a satisfying crystallization sound, ethereal, premium` |
| Hologram activation | `digital power-up sound, electronic hum building to a clear tone, sci-fi, clean` |
| Text slam | `heavy bass drop with a sharp metallic impact, like a stamp hitting metal, authoritative` |
| Countdown tick | `deep resonant tick with subtle reverb, tension-building, clock-like but cinematic` |

### Composite Workflow
```
1. Export the hero frame from your video as a still image
2. Upload to Nano Banana (Gemini) with a transformation prompt above
3. Generate 3-5 variations, pick the most striking
4. Generate matching sound effect via ElevenLabs using the paired prompt
5. In CapCut: AI hook clip (2-3 sec) + whoosh transition + original video
6. Add bold text overlay on frame 1 (price target, bold claim, or question)
7. Export at 9:16 for TikTok/Reels or 16:9 for YouTube
Total production time: ~15-20 minutes per hook
```
