#!/usr/bin/env python3
"""Cut an SFV v2 reel from shot clips, a hook line and a music bed.

Usage: python3 edit_reel.py plan.json

plan.json:
{
  "out": "reel.mp4",
  "music": "music.mp3",
  "hook": {"text": "POV: you only went out for coffee", "y": 1180, "until": 2.6},
  "font": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
  "shots": [
    {"file": "clips/c0.mp4", "in": 0,   "dur": 2.6},
    {"file": "clips/c1.mp4", "in": 0.4, "dur": 2.4}
  ]
}

"y" places the hook line in pixels from the top of the 1080x1920 frame; keep it clear of her face.
"""
import json
import subprocess
import sys

FRAME = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=24"


def main(path):
    plan = json.load(open(path))
    shots = plan["shots"]
    total = round(sum(s["dur"] for s in shots), 3)

    cmd = ["ffmpeg", "-y", "-v", "error"]
    for s in shots:
        cmd += ["-ss", str(s.get("in", 0)), "-t", str(s["dur"]), "-i", s["file"]]
    cmd += ["-i", plan["music"]]

    parts = [f"[{i}:v]{FRAME}[s{i}]" for i in range(len(shots))]
    joined = "".join(f"[s{i}]" for i in range(len(shots)))
    parts.append(f"{joined}concat=n={len(shots)}:v=1:a=0[v]")

    video = "[v]"
    hook = plan.get("hook")
    if hook:
        text = hook["text"].replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")
        parts.append(
            f"[v]drawtext=fontfile={plan['font']}:text='{text}':fontsize={hook.get('size', 56)}"
            f":fontcolor=white:shadowcolor=black@0.55:shadowx=0:shadowy=3"
            f":x=(w-text_w)/2:y={hook.get('y', 300)}"
            f":enable='between(t,0.15,{hook.get('until', 2.6)})'[vt]"
        )
        video = "[vt]"

    m = len(shots)
    parts.append(
        f"[{m}:a]atrim=0:{total},afade=t=in:d=0.15,"
        f"afade=t=out:st={max(total - 0.8, 0)}:d=0.8,volume=0.9[am]"
    )

    cmd += [
        "-filter_complex", ";".join(parts),
        "-map", video, "-map", "[am]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest",
        plan["out"],
    ]
    subprocess.run(cmd, check=True)
    print(f"{plan['out']}: {total}s, {len(shots)} shots")


if __name__ == "__main__":
    main(sys.argv[1])
