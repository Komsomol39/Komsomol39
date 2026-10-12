#!/usr/bin/env python3
"""Matrix (1999)-inspired digital rain for 30x32 physical Govee H70B6.

Original pixel art, not film frames. Fixed glyph cells; new glyphs are printed
down the column, old glyphs dim. Two of ten columns carry pale-green leaders.
Each 2x3 stylized mirrored katakana-like glyph uses real LEDs; no blur.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import random, hashlib, json, math

BASE=Path(r"D:\Project\CastleGovee")
OUT=BASE/"artwork/matrix-digital-rain"
OUT.mkdir(parents=True,exist_ok=True)
W,H=30,32
FRAMES=96
DURATION_MS=100
BG=(0,0,0)
# Hand-drawn 2x3 pseudo-Katakana-inspired geometric glyphs.
# Coordinates are (x,y), with x 0..1, y 0..2, and a blank LED between cells.
GLYPHS=(
 ((0,0),(1,0),(1,1),(0,2)),
 ((0,0),(0,1),(1,1),(1,2)),
 ((1,0),(0,1),(1,1),(0,2)),
 ((0,0),(1,0),(0,1),(1,2)),
 ((0,0),(1,1),(0,2),(1,2)),
 ((0,0),(1,0),(1,2)),
 ((1,0),(0,1),(0,2),(1,2)),
 ((0,0),(0,2),(1,1)),
 ((0,0),(1,0),(1,1),(1,2)),
 ((1,0),(0,1),(1,2)),
 ((0,0),(0,1),(0,2),(1,2)),
 ((0,0),(1,1),(1,2)),
 ((1,0),(1,1),(0,2)),
 ((0,0),(1,0),(0,2)),
 ((0,1),(1,0),(1,2))
)
# Each stream completes 1-3 full screen-height scans per loop. All cycles
# divide the overall loop, so the wrapped transitions remain coherent.
STREAMS=[
 {"phase":2,"cycles":2,"length":6,"depth":0},
 {"phase":6,"cycles":1,"length":5,"depth":2},
 {"phase":0,"cycles":3,"length":7,"depth":1},
 {"phase":5,"cycles":2,"length":6,"depth":0},
 {"phase":3,"cycles":2,"length":5,"depth":2},
 {"phase":7,"cycles":3,"length":5,"depth":1},
 {"phase":1,"cycles":2,"length":7,"depth":0},
 {"phase":4,"cycles":1,"length":6,"depth":2},
 {"phase":6,"cycles":3,"length":7,"depth":1},
 {"phase":0,"cycles":2,"length":4,"depth":0}
]
LEADERS={2,7}  # 20% have near-white leading glyphs, as in the original.
BODY={
 "dim":(2,32,10),
 "faint":(1,51,15),
 "low":(3,77,23),
 "mid":(5,127,35),
 "main":(8,181,54),
 "bright":(31,223,80),
 "tip":(200,255,211),
 "tip2":(185,248,201)
}
def paint(frame):
    im=Image.new("RGB",(W,H),BG)
    d=ImageDraw.Draw(im)
    for col, s in enumerate(STREAMS):
        step=(frame*8*s["cycles"])//FRAMES
        head=(s["phase"]+step)%8
        # fixed grid and fixed glyph positions; only state is updated
        for depth in range(s["length"]):
            row=(head-depth)%8
            # Tiny quasi-random occlusions occur in tail, not the leading edge
            pattern_index=(col*19+row*7+((step//3)*5)+depth*3)%len(GLYPHS)
            g=GLYPHS[pattern_index]
            if depth==0:
                if col in LEADERS:
                    color=BODY["tip"] if frame%2==0 else BODY["tip2"]
                else:
                    color=BODY["bright"] if s["depth"]!=2 else BODY["main"]
            elif depth==1:
                color=BODY["bright"] if s["depth"]==0 else BODY["main"]
            elif depth==2:
                color=BODY["main"] if s["depth"]!=2 else BODY["mid"]
            elif depth==3:
                color=BODY["mid"] if s["depth"]!=2 else BODY["low"]
            elif depth==4:
                color=BODY["low"] if s["depth"]==0 else BODY["faint"]
            else:
                color=BODY["faint"] if s["depth"]!=2 else BODY["dim"]
            x=col*3
            y=row*4
            for dx,dy in g:
                d.point((x+dx,y+dy),fill=color)
    return im

rendered=[paint(k) for k in range(FRAMES)]
for n,f in enumerate(rendered):
    f.save(OUT/f"frame-{n:03}.png")
palette=sorted({c for im in rendered for c in im.get_flattened_data()})
assert len(palette)<256
lookup={c:i for i,c in enumerate(palette)}
flat=[component for c in palette for component in c]+[0]*(768-3*len(palette))
indexed=[]
for im in rendered:
    p=Image.new("P",(W,H));p.putpalette(flat)
    p.putdata([lookup[c] for c in im.get_flattened_data()])
    indexed.append(p)
output=OUT/"source.gif"
indexed[0].save(output,format="GIF",save_all=True,append_images=indexed[1:],
                duration=[DURATION_MS]*FRAMES,loop=0,disposal=2,optimize=False)
with Image.open(output) as gif:
    frames=gif.n_frames
    actual_duration=0
    for i in range(frames):
        gif.seek(i);actual_duration+=gif.info.get("duration",0)
assert actual_duration==FRAMES*DURATION_MS,(actual_duration,FRAMES*DURATION_MS)
assert output.stat().st_size<1000000
# 12 time samples, 6 columns x 2 rows for visual QA.
sheet=Image.new("RGB",(W*6,H*2),BG)
for idx in range(12):
    source=rendered[idx*8]
    sheet.paste(source,((idx%6)*W,(idx//6)*H))
sheet.resize((1080,384),Image.Resampling.NEAREST).save(OUT/"contact-sheet.png")
rendered[17].resize((450,480),Image.Resampling.NEAREST).save(OUT/"preview.png")
lit=[sum(px!=BG for px in im.get_flattened_data())/960 for im in rendered]
report={
 "canvas":[W,H],"requestedFrames":FRAMES,"gifFrames":frames,
 "durationMs":actual_duration,"paletteColors":len(palette),
 "litMin":round(min(lit),3),"litMax":round(max(lit),3),
 "averageLit":round(sum(lit)/len(lit),3),
 "sourceBytes":output.stat().st_size,
 "sourceSha256":hashlib.sha256(output.read_bytes()).hexdigest()
}
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report))
