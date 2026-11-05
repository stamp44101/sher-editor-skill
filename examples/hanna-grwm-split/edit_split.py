# Split-screen GRWM edit used for hanna-grwm-split (5 Nov 2026). Expects L0.png/R0.png stills, clips c2-c8.mp4 and music.mp3 in the working folder.
# Each 9:16 clip is cropped to the centre 540px; T lists (duration, left, right) per beat: a clip, a still, or a frozen frame.
import subprocess, os
F = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
HALF = "scale=-2:1920,crop=540:1920,setsar=1,fps=24,format=yuv420p"

def seg_clip(src, ss, dur, out):
    subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",str(ss),"-t",str(dur),"-i",src,
                    "-an","-vf",HALF,out], check=True)

def seg_still(src, dur, out, ss=None):
    if ss is None:  # png still
        cmd = ["ffmpeg","-y","-loglevel","error","-loop","1","-t",str(dur),"-i",src]
    else:           # freeze a frame from a clip
        cmd = ["ffmpeg","-y","-loglevel","error","-ss",str(ss),"-i",src,"-frames:v","1","-f","image2pipe","-vcodec","png","-"]
        png = subprocess.run(cmd, capture_output=True, check=True).stdout
        tmp = out + ".png"; open(tmp,"wb").write(png)
        cmd = ["ffmpeg","-y","-loglevel","error","-loop","1","-t",str(dur),"-i",tmp]
    subprocess.run(cmd + ["-vf",HALF,out], check=True)

# (duration, left, right)  left/right = ("clip",src,ss) | ("still",src) | ("freeze",src,t)
T = [
 (1.8, ("still","L0.png"),        ("still","R0.png")),
 (1.6, ("clip","c2.mp4",0.0),     ("still","R0.png")),
 (1.8, ("clip","c3.mp4",0.6),     ("still","R0.png")),
 (1.8, ("clip","c4.mp4",0.0),     ("still","R0.png")),
 (1.8, ("freeze","c4.mp4",1.75),  ("clip","c5.mp4",0.5)),
 (2.0, ("freeze","c4.mp4",1.75),  ("clip","c6.mp4",1.0)),
 (2.1, ("clip","c7.mp4",0.5),     ("freeze","c6.mp4",2.95)),
 (2.1, ("freeze","c7.mp4",2.55),  ("clip","c8.mp4",0.6)),
]
os.makedirs("seg", exist_ok=True)
parts = []
for i,(d,l,r) in enumerate(T):
    sides = []
    for side,spec in (("l",l),("r",r)):
        o = f"seg/{i}{side}.mp4"
        if spec[0]=="clip": seg_clip(spec[1], spec[2], d, o)
        elif spec[0]=="still": seg_still(spec[1], d, o)
        else: seg_still(spec[1], d, o, ss=spec[2])
        sides.append(o)
    o = f"seg/{i}.mp4"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",sides[0],"-i",sides[1],"-filter_complex",
        "[0][1]hstack=inputs=2,drawbox=x=538:y=0:w=4:h=ih:color=white@0.9:t=fill[v]",
        "-map","[v]","-t",str(d),"-r","24","-pix_fmt","yuv420p",o], check=True)
    parts.append(o)
open("seg/list.txt","w").write("".join(f"file '{os.path.basename(p)}'\n" for p in parts))
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i","seg/list.txt","-c","copy","seg/video.mp4"], check=True)
total = sum(t[0] for t in T)
txt = "drawtext=fontfile=%s:text='coffee date':fontsize=46:fontcolor=white:shadowcolor=black@0.55:shadowx=2:shadowy=2:x=270-tw/2:y=250:enable='between(t,0.15,%s)'," \
      "drawtext=fontfile=%s:text='dinner date':fontsize=46:fontcolor=white:shadowcolor=black@0.55:shadowx=2:shadowy=2:x=810-tw/2:y=250:enable='between(t,0.15,%s)'," \
      "drawtext=fontfile=%s:text='which one are you?':fontsize=58:fontcolor=white:shadowcolor=black@0.6:shadowx=2:shadowy=3:x=(w-tw)/2:y=160:enable='between(t,0.15,2.6)'" % (F,total,F,total,F)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i","seg/video.mp4","-i","music.mp3","-filter_complex",
    f"[0:v]{txt}[v];[1:a]atrim=0:{total},afade=t=in:d=0.15,afade=t=out:st={total-0.8}:d=0.8[a]",
    "-map","[v]","-map","[a]","-c:v","libx264","-preset","veryfast","-crf","20","-c:a","aac","-b:a","160k",
    "-shortest","hanna_grwm_coffee_vs_dinner.mp4"], check=True)
print("total", total)
