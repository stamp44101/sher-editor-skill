#!/usr/bin/env python3
"""reel-teardown: cut detection, shot timing, keyframe contact sheet, hook strip, audio extract, rough BPM.
Usage: python3 teardown.py VIDEO [OUTDIR] [--thresh 0.3]
Needs ffmpeg/ffprobe, numpy, Pillow."""
import sys, os, json, subprocess, re, argparse
import numpy as np
from PIL import Image, ImageDraw

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def probe(v):
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", v])
    d = json.loads(r.stdout)
    vs = next(s for s in d["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in d["streams"])
    num, den = vs.get("avg_frame_rate", "0/1").split("/")
    fps = float(num) / float(den) if float(den) else 0
    return dict(duration=float(d["format"]["duration"]), width=vs["width"], height=vs["height"],
                fps=round(fps, 2), has_audio=has_audio)

def cuts(v, thresh):
    r = run(["ffmpeg", "-hide_banner", "-i", v, "-vf", f"select='gt(scene,{thresh})',showinfo",
             "-an", "-f", "null", "-"])
    return sorted({round(float(m), 2) for m in re.findall(r"pts_time:([\d.]+)", r.stderr)})

def frame(v, t, path, w=360):
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", v, "-frames:v", "1",
         "-vf", f"scale={w}:-2", path])
    return path if os.path.exists(path) else None

def board(paths, labels, out, cols):
    ims = [Image.open(p) for p in paths]
    w, h = ims[0].size
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * (h + 28)), "white")
    d = ImageDraw.Draw(sheet)
    for i, (im, lab) in enumerate(zip(ims, labels)):
        x, y = (i % cols) * w, (i // cols) * (h + 28)
        sheet.paste(im.resize((w, h)), (x, y + 28))
        d.text((x + 6, y + 8), lab, fill="black")
    sheet.save(out, quality=88)

def bpm(wav):
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", wav, "-ac", "1", "-ar", "11025",
                        "-f", "s16le", "-"], capture_output=True)
    x = np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32)
    if len(x) < 11025 * 4:
        return None
    hop = 256
    env = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    onset = np.maximum(np.diff(env), 0)
    onset -= onset.mean()
    ac = np.correlate(onset, onset, "full")[len(onset) - 1:]
    fr = 11025 / hop
    lo, hi = int(fr * 60 / 180), int(fr * 60 / 70)
    lag = lo + int(np.argmax(ac[lo:hi]))
    return round(60 * fr / lag)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("out", nargs="?", default="teardown")
    ap.add_argument("--thresh", type=float, default=0.3)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    m = probe(a.video)
    c = [t for t in cuts(a.video, a.thresh) if 0.15 < t < m["duration"] - 0.15]
    edges = [0.0] + c + [m["duration"]]
    shots, paths, labels = [], [], []
    for i in range(len(edges) - 1):
        s, e = edges[i], edges[i + 1]
        mid = (s + e) / 2
        p = frame(a.video, mid, os.path.join(a.out, f"shot_{i:02d}.jpg"))
        shots.append(dict(n=i, start=round(s, 2), end=round(e, 2), dur=round(e - s, 2), keyframe=p))
        if p:
            paths.append(p); labels.append(f"#{i} {s:.1f}-{e:.1f}s ({e - s:.1f}s)")
    if paths:
        board(paths, labels, os.path.join(a.out, "contact_sheet.jpg"), cols=min(6, len(paths)))
    hook = [frame(a.video, t, os.path.join(a.out, f"hook_{t:.1f}.jpg"))
            for t in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0) if t < m["duration"]]
    hook = [p for p in hook if p]
    if hook:
        board(hook, [os.path.basename(p)[5:-4] + "s" for p in hook],
              os.path.join(a.out, "hook_strip.jpg"), cols=len(hook))
    wav = None
    if m["has_audio"]:
        wav = os.path.join(a.out, "audio.mp3")
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.video, "-vn", "-ac", "1", "-b:a", "128k", wav])
    durs = [s["dur"] for s in shots]
    summary = dict(**m, shots=len(shots), avg_shot=round(float(np.mean(durs)), 2),
                   min_shot=min(durs), max_shot=max(durs),
                   cuts_in_first_3s=sum(1 for t in c if t < 3),
                   bpm_rough=bpm(wav) if wav else None, audio=wav, shot_list=shots)
    json.dump(summary, open(os.path.join(a.out, "teardown.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != "shot_list"}, indent=1))
    for s in shots:
        print(f"#{s['n']:02d} {s['start']:6.2f}-{s['end']:6.2f}  {s['dur']:.2f}s")

if __name__ == "__main__":
    main()
