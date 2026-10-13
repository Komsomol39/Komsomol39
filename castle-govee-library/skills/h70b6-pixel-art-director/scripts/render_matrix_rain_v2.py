#!/usr/bin/env python3
"""Matrix 2.0: separated vertical code streams on a real 30x32 LED curtain.

Physical-led design: 7 wider 3x3 pseudo-symbol columns, irregular staggered
showers actually descending from off-screen to below the curtain, tapering
green trails, two occasionally pale almost-white heads and black negative space.
Deterministic loop, no film frames and no font rasterization.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import math, hashlib, json
BASE=Path(r"D:\Project\CastleGovee")
OUT=BASE/"artwork/matrix-digital-rain-v2"
OUT.mkdir(parents=True,exist_ok=True)
W,H=30,32
N=96; DT=100
BLACK=(0,0,0)
GLYPHS=(
 ((0,0),(1,0),(2,0),(2,1),(1,2)),
 ((0,0),(0,1),(1,1),(2,2)),
 ((2,0),(1,0),(1,1),(0,1),(0,2)),
 ((0,0),(1,0),(2,1),(1,2)),
 ((2,0),(2,1),(1,1),(0,2)),
 ((0,0),(1,1),(2,2),(0,2)),
 ((2,0),(0,1),(1,1),(2,2)),
 ((0,0),(2,0),(1,1),(1,2)),
 ((0,0),(0,1),(0,2),(1,2),(2,2)),
 ((0,0),(2,0),(1,1),(2,1)),
 ((0,0),(1,0),(2,1),(2,2)),
 ((2,0),(1,1),(0,2),(1,2)),
 ((0,0),(1,1),(2,1),(0,2)),
 ((1,0),(2,0),(0,1),(1,2)),
 ((0,0),(1,1),(2,2)),
)
COLORS={
 "head":(200,255,209),"head_soft":(158,239,177),
 "glow":(49,240,92),"green":(12,204,65),
 "mid":(4,151,46),"tail":(2,93,27),
 "dim":(1,55,14),"faint":(1,29,7),
}
# X is fixed in real LED columns; the stream start frame is staggered.
# durations 59..84 frames create independent fall rates and blank gaps.
STREAMS=[
 {"x":0, "start":-29,"duration":73,"length":5,"tone":0},
 {"x":4, "start":7,  "duration":80,"length":6,"tone":1},
 {"x":9, "start":-10,"duration":61,"length":7,"tone":0},
 {"x":13,"start":31, "duration":83,"length":6,"tone":2},
 {"x":18,"start":-45,"duration":72,"length":7,"tone":0},
 {"x":22,"start":52, "duration":64,"length":5,"tone":1},
 {"x":27,"start":-3, "duration":77,"length":6,"tone":0},
]
BRIGHT={2,5}
def frame_at(frame):
    im=Image.new("RGB",(W,H),BLACK)
    draw=ImageDraw.Draw(im)
    for col,s in enumerate(STREAMS):
        age=(frame-s["start"])%N
        if age>=s["duration"]:continue
        # Head enters naturally from above; full tail vanishes at bottom before reset.
        travel=H+4*(s["length"]-1)+6
        head=-4+(age/s["duration"])*travel
        # One one-pixel-wide code gap between neighboring streams is deliberate.
        for trail in range(s["length"]):
            yy=math.floor(head-4*trail+0.5)
            if yy < -3 or yy>H-1:continue
            # Stable per "material" glyph, occasionally rewritten: no random flicker.
            code_tick=int(age//13)
            pat=GLYPHS[(col*17+trail*7+code_tick*(2+(col%3)))%len(GLYPHS)]
            if trail==0:
                color=COLORS["head"] if col in BRIGHT else COLORS["glow"]
            elif trail==1:
                color=COLORS["green"] if s["tone"]!=2 else COLORS["mid"]
            elif trail==2:
                color=COLORS["mid"]
            elif trail==3:
                color=COLORS["tail"]
            elif trail==4:
                color=COLORS["dim"]
            else:
                color=COLORS["faint"]
            # Slow light variation happens in the glyph body, not across entire screen.
            if trail==0 and col in BRIGHT and (age//8)%3==2:
                color=COLORS["head_soft"]
            for dx,dy in pat:
                px=s["x"]+dx
                py=yy+dy
                if 0<=px<W and 0<=py<H:draw.point((px,py),fill=color)
    return im

if __name__=="__main__":
    frames=[frame_at(i) for i in range(N)]
    for i,f in enumerate(frames): f.save(OUT/f"frame-{i:03}.png")
    colors=sorted(set(c for im in frames for c in im.get_flattened_data()))
    assert len(colors)<=16,len(colors)
    palette=[component for c in colors for component in c]+[0]*(768-3*len(colors))
    lookup={v:i for i,v in enumerate(colors)}
    indexed=[]
    for im in frames:
        p=Image.new("P",(W,H));p.putpalette(palette)
        p.putdata([lookup[c] for c in im.get_flattened_data()])
        indexed.append(p)
    dest=OUT/"source.gif"
    indexed[0].save(dest,save_all=True,append_images=indexed[1:],
                    loop=0,duration=[DT]*N,disposal=2,optimize=False)
    with Image.open(dest) as gif:
        count=gif.n_frames;duration=0
        for i in range(count):
            gif.seek(i);duration+=gif.info.get("duration",0)
    assert duration==N*DT,(duration,N*DT)
    assert dest.stat().st_size < 1_000_000
    sheet=Image.new("RGB",(W*6,H*2),BLACK)
    for i in range(12):sheet.paste(frames[i*8],((i%6)*W,(i//6)*H))
    sheet.resize((1080,384),Image.Resampling.NEAREST).save(OUT/"contact-sheet.png")
    frames[27].resize((450,480),Image.Resampling.NEAREST).save(OUT/"preview.png")
    lit=[sum(px!=BLACK for px in im.get_flattened_data())/960 for im in frames]
    # Model the head trajectories to ensure genuine downward motion (no modulo row wrap).
    diagnostics=[]
    for s in STREAMS:
        positions=[-4+((frame-s["start"])%N/s["duration"])*(H+4*(s["length"]-1)+6)
                   for frame in range(N) if (frame-s["start"])%N<s["duration"]]
        diagnostics.append({"x":s["x"],"length":s["length"],"durationFrames":s["duration"],
                            "speedPxPerSecond":round((H+4*(s["length"]-1)+6)/s["duration"]*10,2)})
    report={"resolution":[W,H],"streams":len(STREAMS),"sourceFrames":N,"gifFrames":count,
            "durationMs":duration,"colors":len(colors),"averageLit":round(sum(lit)/N,3),
            "minLit":round(min(lit),3),"maxLit":round(max(lit),3),
            "sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),"bytes":dest.stat().st_size,
            "streamPhysics":diagnostics}
    (OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(report,ensure_ascii=False))
