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
- `dark moody background, red accent lighting, cinematic color grading`
- `professional Web3 aesthetic, futuristic minimal, blockchain visual language`
- `high contrast, deep blacks, selective red highlights`
- `clean typography overlay space, room for text`

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
