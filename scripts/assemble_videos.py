"""
Assemble all 4 videos:
1. Copy assets to content-studio/public/
2. Create shot manifest JSONs (no SFX — voiceover + visuals only)
"""
import os, shutil, json

BRAIN = os.path.join(os.path.dirname(__file__), "..")
STUDIO = "C:/Users/Bigquiv/onedrive/desktop/content-studio"
PUBLIC = os.path.join(STUDIO, "public")
FPS = 30


def setup_project(name, source_dir):
    """Copy keyframes + voiceover to content-studio/public/{name}/"""
    dest = os.path.join(PUBLIC, name)
    os.makedirs(dest, exist_ok=True)

    copied = 0
    for f in os.listdir(source_dir):
        if f.endswith(('.png', '.mp3', '.mp4', '.wav')):
            src = os.path.join(source_dir, f)
            dst = os.path.join(dest, f)
            if not os.path.exists(dst) or os.path.getsize(src) != os.path.getsize(dst):
                shutil.copy2(src, dst)
                copied += 1
    print(f"  Copied {copied} files to public/{name}/")
    return dest


# ============================================================
# VIDEO 1: 20M Bitcoin TikTok — 49.4s voiceover, 10 shots
# ============================================================
print("1. 20M Bitcoin TikTok")
src1 = os.path.join(BRAIN, "06-Drafts", "visuals", "20m-bitcoin-tiktok")
setup_project("20m-bitcoin-tiktok", src1)

v1_manifest = {
    "fps": 30,
    "durationInFrames": int(50 * FPS),
    "projectDir": "20m-bitcoin-tiktok",
    "shots": [
        {"id": 1, "src": "shot-01.mp4", "type": "video", "startFrame": 0, "durationFrames": int(3.8*FPS),
         "effect": "SlamIn", "flash": True, "trackDir": "left", "textOverlay": "ONLY 1 MILLION LEFT"},
        {"id": 2, "src": "shot-02.mp4", "type": "video", "startFrame": int(3.8*FPS), "durationFrames": int(3.9*FPS),
         "effect": "KenBurns", "kenDirection": "in", "flash": True, "trackDir": "right"},
        {"id": 3, "src": "shot-03.mp4", "type": "video", "startFrame": int(7.7*FPS), "durationFrames": int(6.7*FPS),
         "effect": "KenBurns", "kenDirection": "out", "trackDir": "left"},
        {"id": 4, "src": "shot-04.mp4", "type": "video", "startFrame": int(14.4*FPS), "durationFrames": int(6.0*FPS),
         "effect": "KenBurns", "kenDirection": "in", "trackDir": "right", "textOverlay": "114 YEARS TO MINE"},
        {"id": 5, "src": "shot-05.mp4", "type": "video", "startFrame": int(20.4*FPS), "durationFrames": int(4.1*FPS),
         "effect": "PunchZoom", "flash": True, "trackDir": "left", "textOverlay": "THE HALVING"},
        {"id": 6, "src": "shot-06.mp4", "type": "video", "startFrame": int(24.5*FPS), "durationFrames": int(2.6*FPS),
         "effect": "KenBurns", "kenDirection": "in", "flash": True, "trackDir": "right"},
        {"id": 7, "src": "shot-07.mp4", "type": "video", "startFrame": int(27.1*FPS), "durationFrames": int(5.5*FPS),
         "effect": "PunchZoom", "trackDir": "left", "textOverlay": "SUPPLY vs DEMAND"},
        {"id": 8, "src": "shot-08.mp4", "type": "video", "startFrame": int(32.6*FPS), "durationFrames": int(5.9*FPS),
         "effect": "CameraShake", "flash": True, "trackDir": "right", "textOverlay": "$100K"},
        {"id": 9, "src": "shot-09.mp4", "type": "video", "startFrame": int(38.5*FPS), "durationFrames": int(6.6*FPS),
         "effect": "KenBurns", "kenDirection": "in", "trackDir": "left"},
        {"id": 10, "src": "shot-10.mp4", "type": "video", "startFrame": int(45.1*FPS), "durationFrames": int(4.9*FPS),
         "effect": "PunchZoom", "flash": True, "trackDir": "right", "textOverlay": "FOLLOW @BIG_QUIV"},
    ],
    "voiceover": "voiceover.mp3",
    "musicVolume": 0.15,
}

# ============================================================
# VIDEO 2: 3 Cleared Tokens Reel — 59.8s voiceover, 12 shots
# ============================================================
print("2. 3 Cleared Tokens Reel")
src2 = os.path.join(BRAIN, "06-Drafts", "visuals", "3-cleared-tokens-reel")
setup_project("3-cleared-tokens-reel", src2)

v2_manifest = {
    "fps": 30,
    "durationInFrames": int(60 * FPS),
    "projectDir": "3-cleared-tokens-reel",
    "shots": [
        {"id": 1, "src": "shot-01.mp4", "type": "video", "startFrame": 0, "durationFrames": int(3.2*FPS),
         "effect": "SlamIn", "flash": True, "trackDir": "left", "textOverlay": "3 TOKENS NOBODY'S WATCHING"},
        {"id": 2, "src": "shot-02.mp4", "type": "video", "startFrame": int(3.2*FPS), "durationFrames": int(4.4*FPS),
         "effect": "KenBurns", "kenDirection": "in", "flash": True, "trackDir": "right"},
        {"id": 3, "src": "shot-03.mp4", "type": "video", "startFrame": int(7.6*FPS), "durationFrames": int(3.0*FPS),
         "effect": "PunchZoom", "trackDir": "left"},
        {"id": 4, "src": "shot-04.mp4", "type": "video", "startFrame": int(10.6*FPS), "durationFrames": int(9.7*FPS),
         "effect": "SlamIn", "flash": True, "trackDir": "right", "textOverlay": "#1 AVAX"},
        {"id": 5, "src": "shot-05.mp4", "type": "video", "startFrame": int(20.3*FPS), "durationFrames": int(5.0*FPS),
         "effect": "KenBurns", "kenDirection": "out", "trackDir": "left"},
        {"id": 6, "src": "shot-06.mp4", "type": "video", "startFrame": int(25.3*FPS), "durationFrames": int(3.1*FPS),
         "effect": "SlamIn", "flash": True, "trackDir": "right", "textOverlay": "#2 LINK"},
        {"id": 7, "src": "shot-07.mp4", "type": "video", "startFrame": int(28.4*FPS), "durationFrames": int(12.1*FPS),
         "effect": "KenBurns", "kenDirection": "in", "trackDir": "left"},
        {"id": 8, "src": "shot-08.mp4", "type": "video", "startFrame": int(40.5*FPS), "durationFrames": int(2.7*FPS),
         "effect": "SlamIn", "flash": True, "trackDir": "right", "textOverlay": "#3 DOT"},
        {"id": 9, "src": "shot-09.mp4", "type": "video", "startFrame": int(43.2*FPS), "durationFrames": int(8.9*FPS),
         "effect": "KenBurns", "kenDirection": "in", "trackDir": "left"},
        {"id": 10, "src": "shot-10.mp4", "type": "video", "startFrame": int(52.1*FPS), "durationFrames": int(2.7*FPS),
         "effect": "PunchZoom", "flash": True, "trackDir": "right"},
        {"id": 11, "src": "shot-11.mp4", "type": "video", "startFrame": int(54.8*FPS), "durationFrames": int(1.2*FPS),
         "effect": "SlamIn", "flash": True, "trackDir": "left", "textOverlay": "COMMENT ALPHA"},
        {"id": 12, "src": "shot-12.mp4", "type": "video", "startFrame": int(56.0*FPS), "durationFrames": int(4.0*FPS),
         "effect": "KenBurns", "kenDirection": "in", "trackDir": "right"},
    ],
    "voiceover": "voiceover.mp3",
    "musicVolume": 0.15,
}

# ============================================================
# VIDEO 3: Day In Life KOL Reel — 44.5s voiceover (full), 10 shots
# ============================================================
print("3. Day In Life KOL Reel")
src3 = os.path.join(BRAIN, "06-Drafts", "visuals", "day-in-life-kol-reel")
setup_project("day-in-life-kol-reel", src3)

# Load word-level captions from Whisper transcription
v3_captions_path = os.path.join(PUBLIC, "day-in-life-kol-reel", "captions.json")
v3_words = []
if os.path.exists(v3_captions_path):
    with open(v3_captions_path) as f:
        v3_words = json.load(f)
    print(f"  Loaded {len(v3_words)} caption words")

v3_manifest = {
    "fps": 30,
    "durationInFrames": int(45 * FPS),
    "projectDir": "day-in-life-kol-reel",
    "shots": [
        {"id": 1, "src": "shot-01.mp4", "type": "video", "startFrame": 0, "durationFrames": int(6.0*FPS),
         "effect": "SlamIn", "flash": True, "trackDir": "left", "textOverlay": "MY MORNING AS A TRADER"},
        {"id": 2, "src": "shot-02.mp4", "type": "video", "startFrame": int(6.0*FPS), "durationFrames": int(3.2*FPS),
         "effect": "PunchZoom", "flash": True, "trackDir": "right", "textOverlay": "3 SIGNALS APPROVED"},
        {"id": 3, "src": "shot-03.mp4", "type": "video", "startFrame": int(9.2*FPS), "durationFrames": int(2.8*FPS),
         "effect": "KenBurns", "kenDirection": "in", "trackDir": "left"},
        {"id": 4, "src": "shot-04.mp4", "type": "video", "startFrame": int(12.0*FPS), "durationFrames": int(3.1*FPS),
         "effect": "KenBurns", "kenDirection": "out", "flash": True, "trackDir": "right"},
        {"id": 5, "src": "shot-05.mp4", "type": "video", "startFrame": int(15.1*FPS), "durationFrames": int(4.3*FPS),
         "effect": "PunchZoom", "trackDir": "left", "textOverlay": "SCANS EVERY 4 HOURS"},
        {"id": 6, "src": "shot-06.mp4", "type": "video", "startFrame": int(19.4*FPS), "durationFrames": int(7.5*FPS),
         "effect": "KenBurns", "kenDirection": "in", "flash": True, "trackDir": "right"},
        {"id": 7, "src": "shot-07.mp4", "type": "video", "startFrame": int(26.9*FPS), "durationFrames": int(1.6*FPS),
         "effect": "KenBurns", "kenDirection": "out", "trackDir": "left"},
        {"id": 8, "src": "shot-08.mp4", "type": "video", "startFrame": int(28.5*FPS), "durationFrames": int(9.5*FPS),
         "effect": "KenBurns", "kenDirection": "in", "flash": True, "trackDir": "right", "textOverlay": "I BUILT THE MACHINE"},
        {"id": 9, "src": "shot-09.mp4", "type": "video", "startFrame": int(38.0*FPS), "durationFrames": int(3.0*FPS),
         "effect": "PunchZoom", "flash": True, "trackDir": "left"},
        {"id": 10, "src": "shot-10.mp4", "type": "video", "startFrame": int(41.0*FPS), "durationFrames": int(4.5*FPS),
         "effect": "KenBurns", "kenDirection": "in", "trackDir": "right", "textOverlay": "COMMENT OS"},
    ],
    "voiceover": "voiceover_full.mp3",
    "musicVolume": 0.15,
    "words": v3_words,
}

# ============================================================
# VIDEO 4: Claude Code Portfolio Reel — 44.2s voiceover, 8 shots
# ============================================================
print("4. Claude Code Portfolio Reel")
src4 = os.path.join(BRAIN, "06-Drafts", "visuals", "claude-code-portfolio-reel")
setup_project("claude-code-portfolio-reel", src4)

v4_manifest = {
    "fps": 30,
    "durationInFrames": int(45 * FPS),
    "projectDir": "claude-code-portfolio-reel",
    "shots": [
        {"id": 1, "src": "shot-01.mp4", "type": "video", "startFrame": 0, "durationFrames": int(5.5*FPS),
         "effect": "SlamIn", "flash": True, "trackDir": "left", "textOverlay": "AI FOUND 3 THINGS I MISSED"},
        {"id": 2, "src": "shot-02.mp4", "type": "video", "startFrame": int(5.5*FPS), "durationFrames": int(6.9*FPS),
         "effect": "KenBurns", "kenDirection": "in", "flash": True, "trackDir": "right"},
        {"id": 3, "src": "shot-03.mp4", "type": "video", "startFrame": int(12.4*FPS), "durationFrames": int(3.2*FPS),
         "effect": "PunchZoom", "flash": True, "trackDir": "left", "textOverlay": "40% CORRELATED"},
        {"id": 4, "src": "shot-04.mp4", "type": "video", "startFrame": int(15.6*FPS), "durationFrames": int(7.2*FPS),
         "effect": "KenBurns", "kenDirection": "out", "trackDir": "right"},
        {"id": 5, "src": "shot-05.mp4", "type": "video", "startFrame": int(22.8*FPS), "durationFrames": int(7.3*FPS),
         "effect": "PunchZoom", "flash": True, "trackDir": "left", "textOverlay": "FREE YIELD"},
        {"id": 6, "src": "shot-06.mp4", "type": "video", "startFrame": int(30.1*FPS), "durationFrames": int(3.6*FPS),
         "effect": "KenBurns", "kenDirection": "in", "trackDir": "right"},
        {"id": 7, "src": "shot-07.mp4", "type": "video", "startFrame": int(33.7*FPS), "durationFrames": int(6.6*FPS),
         "effect": "SlamIn", "flash": True, "trackDir": "left", "textOverlay": "2 MIN vs 1 HOUR"},
        {"id": 8, "src": "shot-08.mp4", "type": "video", "startFrame": int(40.3*FPS), "durationFrames": int(4.7*FPS),
         "effect": "KenBurns", "kenDirection": "in", "trackDir": "right", "textOverlay": "COMMENT PORTFOLIO"},
    ],
    "voiceover": "voiceover.mp3",
    "musicVolume": 0.15,
}

# ─── Save all manifests ───
manifests = [
    ("20m-bitcoin-tiktok", v1_manifest),
    ("3-cleared-tokens-reel", v2_manifest),
    ("day-in-life-kol-reel", v3_manifest),
    ("claude-code-portfolio-reel", v4_manifest),
]

print("\nSaving manifests...")
for name, m in manifests:
    path = os.path.join(PUBLIC, name, "manifest.json")
    with open(path, "w") as f:
        json.dump({"manifest": m}, f, indent=2)
    print(f"  {name}/manifest.json ({len(m['shots'])} shots, {m['durationInFrames']/m['fps']:.0f}s)")

# ─── Verify all assets exist ───
print("\nVerifying assets...")
missing = []
for name, m in manifests:
    proj_dir = os.path.join(PUBLIC, name)
    for shot in m["shots"]:
        fp = os.path.join(proj_dir, shot["src"])
        if not os.path.exists(fp):
            missing.append(f"{name}/{shot['src']}")
    if m.get("voiceover"):
        vp = os.path.join(proj_dir, m["voiceover"])
        if not os.path.exists(vp):
            missing.append(f"{name}/{m['voiceover']}")

if missing:
    print(f"  WARNING: {len(missing)} missing assets:")
    for m in missing:
        print(f"    - {m}")
else:
    print("  All assets present!")

print(f"\n{'='*50}")
print("ASSEMBLY COMPLETE — NO SFX")
print(f"{'='*50}")
print(f"Manifests saved to content-studio/public/*/manifest.json")
print(f"\nTo render all 4 (1080p):")
for name, m in manifests:
    print(f'  npx remotion render ManifestVideo --props=public/{name}/manifest.json --output=out/{name}.mp4')
