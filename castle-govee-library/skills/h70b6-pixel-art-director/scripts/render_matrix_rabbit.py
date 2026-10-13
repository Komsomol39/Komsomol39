#!/usr/bin/env python3
"""Matrix 2.1: 19.2s digital rain + a hand-pixelled white rabbit at the end.

A 30x32 Govee curtain has 960 independent LEDs. Keep the original Matrix 2.0
rain intact; stage a clearly readable white rabbit sprinting in from the left,
then jumping away from the viewer and shrinking into a single vanishing dot.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import importlib.util, json, hashlib, math

BASE=Path(r"D:\Project\CastleGovee")
OUT=BASE/"artwork/matrix-white-rabbit"
OUT.mkdir(parents=True,exist_ok=True)
mod=BASE/"skills/h70b6-pixel-art-director/scripts/render_matrix_rain_v2.py"
spec=importlib.util.spec_from_file_location("matrix_v2_rain",mod)
rain=importlib.util.module_from_spec(spec)
spec.loader.exec_module(rain)

W,H=30,32
COUNT,MS=192,100
WHITE=(248,255,249)
SHADOW=(129,167,156)
LIGHT=(217,236,228)
EAR=(255,197,208)
EYE=(11,35,24)
NOSE=(255,172,180)

def rabbit_sprite(pose:int):
    """18x17 hand-pixelled right-facing rabbit with ears, eye and four running feet."""
    im=Image.new("RGBA",(19,18),(0,0,0,0))
    d=ImageDraw.Draw(im)
    # Hindquarters and body; larger connected silhouette reads through tulle.
    d.ellipse((3,8,13,14),fill=WHITE)
    d.ellipse((3,8,12,12),fill=LIGHT)
    d.rectangle((5,11,11,13),fill=WHITE)
    # Two long ears extending clearly above head.
    d.polygon([(11,8),(10,1),(11,0),(13,1),(13,8)],fill=WHITE)
    d.polygon([(14,8),(14,2),(15,1),(16,3),(16,9)],fill=WHITE)
    d.line((12,2,12,6),fill=EAR,width=1)
    d.line((15,4,15,7),fill=EAR,width=1)
    # Head and muzzle on right.
    d.ellipse((11,6,17,12),fill=WHITE)
    d.point((16,9),fill=EYE)
    d.point((18,11),fill=NOSE)
    d.point((17,11),fill=WHITE)
    # Fluffy tail, unmistakably rabbit rather than a cat.
    d.ellipse((1,9,5,12),fill=WHITE)
    d.point((2,9),fill=LIGHT)
    # Running leap: alternating leg positions and lift.
    poses=[
      (((5,13),(2,16)),((9,13),(8,16)),((12,12),(14,15)),((15,11),(17,14))),
      (((5,13),(3,14)),((9,13),(11,17)),((12,12),(14,14)),((15,11),(17,12))),
      (((5,13),(3,16)),((9,13),(7,15)),((12,12),(16,15)),((15,11),(18,13))),
      (((5,13),(4,15)),((9,13),(10,16)),((12,12),(13,14)),((15,11),(17,15))),
    ]
    for a,b in poses[pose%4]:
        d.line((a[0],a[1],b[0],b[1]),fill=WHITE,width=2)
        d.point((b[0],b[1]),fill=LIGHT)
    return im

def smoothstep(x):
    x=max(0,min(1,x))
    return x*x*(3-2*x)

def place_rabbit(background:Image.Image,index:int):
    # From 12.4s: emerges from x=-18, visible large; 16s recedes into depth.
    # By 18.2s is a point; at 18.9s disappears, before the 19.2s loop resets.
    if index<124 or index>=189:
        return background, "hidden", 0
    p=min(1,(index-124)/60)
    # Position of the rabbit's centre. Body moves right and upwards.
    cx=-10+35*p
    foot=30-15*smoothstep(p)
    if index>=181:
        x=round(cx);y=round(foot)
        if 0<=x<W and 0<=y<H:
            background.putpixel((x,y),WHITE if index<185 else (123,175,134))
        return background,"point",1
    scale=1-smoothstep(max(0,(p-0.10)/0.86))
    width=max(2,round(19*scale))
    height=max(2,round(18*scale))
    pose=(index//3)%4
    # Very light hopping while large; shrinking height itself communicates distance.
    bounce=(1 if pose in (1,2) and width>=9 else 0)
    bitmap=rabbit_sprite(pose).resize((width,height),Image.Resampling.NEAREST)
    left=round(cx-width/2)
    top=round(foot-height-bounce)
    background.paste(bitmap,(left,top),bitmap)
    return background, "rabbit",width

frames=[]
phases={}
for i in range(COUNT):
    # Two 9.6s digital-rain passes; no artificial full-frame flicker.
    base=rain.frame_at(i%rain.N)
    result,phase,width=place_rabbit(base,i)
    frames.append(result)
    phases[phase]=phases.get(phase,0)+1
    result.save(OUT/f"frame-{i:03}.png")

# Explicit tests: first half never features a rabbit, ending has a disappearing dot.
assert all(frames[i].tobytes()==rain.frame_at(i%rain.N).tobytes() for i in range(124))
assert phases.get("rabbit",0)>45 and phases.get("point",0)==8
assert frames[189].tobytes()==rain.frame_at(189%rain.N).tobytes()
assert frames[191].tobytes()==rain.frame_at(191%rain.N).tobytes()
colors=sorted({p for im in frames for p in im.get_flattened_data()})
assert len(colors)<=32, len(colors)
lut={p:i for i,p in enumerate(colors)}
palette=[c for p in colors for c in p]+[0]*(768-len(colors)*3)
indexed=[]
for im in frames:
    dst=Image.new("P",(W,H))
    dst.putpalette(palette)
    dst.putdata([lut[p] for p in im.get_flattened_data()])
    indexed.append(dst)
dest=OUT/"source.gif"
indexed[0].save(dest,format="GIF",save_all=True,append_images=indexed[1:],
                loop=0,duration=[MS]*COUNT,disposal=2,optimize=False)
with Image.open(dest) as gif:
    total=0
    for i in range(gif.n_frames):
        gif.seek(i);total+=gif.info.get("duration",0)
    assert gif.size==(W,H) and total==COUNT*MS
    actual=gif.n_frames
assert dest.stat().st_size<1_000_000
# Storyboard samples: first row shows rain; second row follows the rabbit.
times=[10,45,75,105,121,128,134,142,150,158,166,174,181,184,188,190]
sheet=Image.new("RGB",(W*8,H*2))
for j,k in enumerate(times):sheet.paste(frames[k],((j%8)*W,(j//8)*H))
sheet.resize((1200,320),Image.Resampling.NEAREST).save(OUT/"storyboard.png")
frames[148].resize((450,480),Image.Resampling.NEAREST).save(OUT/"rabbit-preview.png")
report={"canvas":[W,H],"totalSeconds":COUNT*MS/1000,"sourceFrames":COUNT,
        "gifFrames":actual,"rabbitStartSeconds":12.4,"rabbitDotSeconds":18.1,
        "rabbitDisappearsSeconds":18.9,"rabbitPhases":phases,
        "paletteColors":len(colors),"bytes":dest.stat().st_size,
        "sha256":hashlib.sha256(dest.read_bytes()).hexdigest()}
(OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(report,ensure_ascii=False))
