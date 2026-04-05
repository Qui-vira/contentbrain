"""Generate 7 AI backgrounds for Trading Mistakes V2 carousel via fal.ai"""
import requests, os, time, json
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '.env'))
FAL_KEY = os.getenv('FAL_KEY')
headers = {'Authorization': f'Key {FAL_KEY}', 'Content-Type': 'application/json'}
output_dir = os.path.dirname(os.path.abspath(__file__))

def gen_bg(prompt, filename):
    print(f'Generating {filename}...')
    payload = {
        'prompt': prompt,
        'negative_prompt': 'text, words, letters, numbers, watermark, logo, blurry, low quality, cartoon, anime, distorted, bright cheerful colors, flat lighting',
        'image_size': {'width': 1080, 'height': 1350},
        'num_images': 1, 'guidance_scale': 7.5, 'num_inference_steps': 30
    }
    resp = requests.post('https://queue.fal.run/fal-ai/nano-banana-pro', json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    rid = resp.json()['request_id']
    for _ in range(60):
        time.sleep(3)
        st = requests.get(f'https://queue.fal.run/fal-ai/nano-banana-pro/requests/{rid}/status', headers=headers, timeout=15).json()
        if st.get('status') == 'COMPLETED':
            break
    result = requests.get(f'https://queue.fal.run/fal-ai/nano-banana-pro/requests/{rid}', headers=headers, timeout=30).json()
    img_data = requests.get(result['images'][0]['url'], timeout=60).content
    fp = os.path.join(output_dir, filename)
    with open(fp, 'wb') as f:
        f.write(img_data)
    print(f'  Saved {filename} ({len(img_data)} bytes)')

backgrounds = [
    ("Scattered dollar bills burning and disintegrating into ash and embers, dramatic fire lighting from below, dark smoky atmosphere, cinematic, ultra detailed, 8k, no text, no words, no letters, no watermark, photorealistic", "bg1_cover.png"),
    ("Trading chart on a massive dark screen showing a sharp red candlestick crash, dramatic red backlighting, dark trading floor environment, cinematic, 8k, no text, no words, no letters, no watermark", "bg2_stoploss.png"),
    ("A single casino chip balanced on the edge of a cliff over a dark void, dramatic side lighting, danger and risk concept, cinematic, 8k, no text, no words, no letters, no watermark, photorealistic", "bg3_oversize.png"),
    ("Clenched fist slamming on a dark desk with a cracked laptop screen showing red charts, dramatic red and orange lighting, anger and frustration concept, dark moody atmosphere, cinematic, 8k, no text, no words, no letters, no watermark", "bg4_revenge.png"),
    ("Three golden compass needles all pointing in the same direction on a dark reflective surface, precision and alignment concept, dramatic golden lighting, dark background, cinematic, 8k, no text, no words, no letters, no watermark", "bg5_confluence.png"),
    ("Tangled mess of wires and cables in complete chaos on a dark surface, disorder concept, dramatic harsh lighting creating deep shadows, dark moody atmosphere, cinematic, 8k, no text, no words, no letters, no watermark", "bg6_nosystem.png"),
    ("Dramatic spotlight cone of warm golden light cutting through darkness and fog, theatrical stage lighting, dark atmospheric environment, volumetric light rays, cinematic, 8k, no text, no words, no letters, no watermark", "bg7_cta.png"),
]

for prompt, filename in backgrounds:
    gen_bg(prompt, filename)

print("\nAll 7 backgrounds generated.")
