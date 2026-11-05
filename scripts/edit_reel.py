#!/usr/bin/env python3
"""Cut an SFV reel from shot clips, a hook line and a music bed.

Usage: python3 edit_reel.py plan.json

plan.json:
{
  "out": "reel.mp4",
  "music": "music.mp3",
  "look": "good",
  "hook": {"text": "POV: you only went out for coffee", "y": 1180, "until": 2.6},
  "font": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
  "shots": [
    {"file": "clips/c0.mp4", "in": 0,   "dur": 2.6},
    {"file": "clips/c1.mp4", "in": 0.4, "dur": 2.4}
  ]
}

"look" (optional, default "good"):
  "good"   - clean and sharp, light grain, 30 fps. For garment-led posts where the fabric must read.
  "casual" - phone front-cam look: softer detail, handheld drift, auto-exposure breathing,
             luma + chroma noise, phone oversharpen, 30 fps, social-style compression.
  "raw"    - no look pass, 24 fps (the v2 default before looks existed).
The hook text is drawn after the look pass, so it stays fixed on screen like an app caption.
"y" places the hook line in pixels from the top of the 1080x1920 frame; keep it clear of her face.
"""
import json
import subprocess
import sys

FRAME = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=24"

LOOKS = {
    "raw": ("", 19),
    "good": ("noise=c0s=4:c0f=t+u,fps=30", 19),
    "casual": (",".join([
        "scale=760:-2", "scale=1134:2016:flags=bicubic",
        "crop=1080:1920:x='27+14*sin(t*1.9)+6*sin(t*5.7)':y='48+12*sin(t*1.4)+5*sin(t*4.3)'",
        "eq=eval=frame:brightness='0.025*sin(t*1.1)':contrast=1.06:saturation=1.08:gamma=1.03",
        "unsharp=5:5:0.9:5:5:0.0",
        "noise=c0s=9:c0f=t+u:c1s=4:c1f=t+u",
        "fps=30"]), 27),
}


def main(path):
    plan = json.load(open(path))
    shots = plan["shots"]
    total = round(sum(s["dur"] for s in shots), 3)
    look, crf = LOOKS[plan.get("look", "good")]

    cmd = ["ffmpeg", "-y", "-v", "error"]
    for s in shots:
        cmd += ["-ss", str(s.get("in", 0)), "-t", str(s["dur"]), "-i", s["file"]]
    cmd += ["-i", plan["music"]]

    parts = [f"[{i}:v]{FRAME}[s{i}]" for i in range(len(shots))]
    joined = "".join(f"[s{i}]" for i in range(len(shots)))
    parts.append(f"{joined}concat=n={len(shots)}:v=1:a=0[v0]")
    parts.append(f"[v0]{look}[v]" if look else "[v0]null[v]")

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
        "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf), "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest",
        plan["out"],
    ]
    subprocess.run(cmd, check=True)
    print(f"{plan['out']}: {total}s, {len(shots)} shots, look={plan.get('look', 'good')}")


if __name__ == "__main__":
    main(sys.argv[1])
