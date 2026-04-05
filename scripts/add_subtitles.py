"""
Auto-generate and burn subtitles into a video using Whisper + FFmpeg.
Usage: python scripts/add_subtitles.py <input_video> <output_video>
"""

import sys
import subprocess
import whisper
from pathlib import Path


def transcribe_to_srt(video_path: str, srt_path: str):
    """Transcribe video audio to SRT subtitle file using Whisper."""
    print("[1/3] Transcribing audio with Whisper...")
    model = whisper.load_model("base")
    result = model.transcribe(video_path, word_timestamps=True)

    segments = []
    # Build word-level subtitle segments (3-5 words per line for TikTok style)
    words = []
    for segment in result["segments"]:
        if "words" in segment:
            words.extend(segment["words"])

    if not words:
        # Fallback to segment-level if no word timestamps
        for i, seg in enumerate(result["segments"], 1):
            segments.append({
                "index": i,
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
            })
    else:
        # Group words into chunks of 4-5 for punchy subtitle style
        chunk_size = 4
        idx = 1
        for i in range(0, len(words), chunk_size):
            chunk = words[i : i + chunk_size]
            segments.append({
                "index": idx,
                "start": chunk[0]["start"],
                "end": chunk[-1]["end"],
                "text": " ".join(w["word"].strip() for w in chunk),
            })
            idx += 1

    # Write SRT
    with open(srt_path, "w", encoding="utf-8") as f:
        for seg in segments:
            start = format_ts(seg["start"])
            end = format_ts(seg["end"])
            f.write(f"{seg['index']}\n{start} --> {end}\n{seg['text']}\n\n")

    print(f"  Generated {len(segments)} subtitle segments -> {srt_path}")
    return srt_path


def format_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def burn_subtitles(input_video: str, srt_path: str, output_video: str):
    """Burn SRT subtitles into video using FFmpeg."""
    print("[2/3] Burning subtitles into video...")

    # Convert backslashes for FFmpeg subtitle filter on Windows
    srt_clean = srt_path.replace("\\", "/").replace(":", "\\\\:")

    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-vf", (
            f"subtitles='{srt_clean}'"
            ":force_style='FontName=Arial Black,"
            "FontSize=18,"
            "PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,"
            "Outline=2,"
            "Shadow=1,"
            "Alignment=2,"
            "MarginV=40'"
        ),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_video,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr[-500:]}")
        raise RuntimeError("FFmpeg subtitle burn failed")

    print(f"[3/3] Done! -> {output_video}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/add_subtitles.py <input_video> <output_video>")
        sys.exit(1)

    input_vid = sys.argv[1]
    output_vid = sys.argv[2]
    srt_file = str(Path(input_vid).with_suffix(".srt"))

    transcribe_to_srt(input_vid, srt_file)
    burn_subtitles(input_vid, srt_file, output_vid)
    print(f"\nSubtitled video: {output_vid}")
