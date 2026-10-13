#!/usr/bin/env python3
"""Matrix 2.1 - WHITE RABBIT: 24s, a proper pixel-art character with a pause.

30x32 LED curtain. Old Matrix 2.0 rain stays unchanged. During the finale a
large recognizable rabbit walks in from left, pauses to look around, then
runs into the distance and becomes one fading white point.
No reused movie footage or character sprites.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import importlib.util, json, hashlib, math

ROOT=Path(r"D:\Project\CastleGovee")
OUT=ROOT/"artwork/matrix-white-rabbit"
OUT.mkdir(parents=True, exist_ok=True)
source=ROOT/"skills/h70b6-pixel-art-director/scripts/render_matrix_rain_v2.py"
spec=importlib.util.spec_from_file_location("matrix_v2_rain",source)
rain=importlib.util.module_from_spec(spec)
spec.loader.exec_module(rain)

W,H=30,32
N,MS=240,100
FUR=(247,254,250)
HI=(255,255,255)
LIGHT=(199,220,211)
SHADE=(105,151,136)
EAR=(249,153,177)
NOSE=(255,174,179)
EYE=(3,24,15)
BACKGROUND=(0,0,0)

def smoothstep(t):
    t=min(1.0,max(0.0,t))
    return t*t*(3-2*t)

def rabbit_sprite(look="right",stride=0):
    """Natural 21x22 rabbit silhouette: curved haunch, tapering thorax, long ears.

    Every mark is intentional native pixel art. This is a side-on white rabbit,
    not a humanoid mascot or a filled rectangle with four stick legs.
    """
    im=Image.new("RGBA",(21,22),(0,0,0,0))
    d=ImageDraw.Draw(im)
    transparent=(0,0,0,0)
    # Rounded hindquarters and a sloping back: the silhouette has three
    # differentiated masses (hindquarter, thorax, and delicate head).
    d.polygon([(2,16),(3,13),(4,11),(6,10),(9,10),(11,11),
               (13,13),(14,15),(13,17),(11,19),(8,20),
               (5,20),(3,18)],fill=FUR)
    d.ellipse((4,11,12,20),fill=FUR)
    d.line([(3,15),(4,13),(6,11),(8,10),(10,11)],fill=HI,width=1)
    # Not all white: clear round thigh and soft shaded underbelly.
    d.arc((4,12,11,20),start=265,end=120,fill=LIGHT,width=1)
    d.line([(7,18),(10,19),(12,18)],fill=LIGHT,width=1)
    d.point((6,15),fill=(231,241,235))
    d.point((8,13),fill=(231,241,235))
    # Narrow chest: follows the slope of the neck; avoid squared body.
    d.polygon([(11,14),(13,11),(14,10),(16,12),(16,16),
               (15,19),(13,18),(12,16)],fill=FUR)
    d.line([(13,12),(14,11),(15,13)],fill=HI)
    d.line([(15,15),(14,17),(13,18)],fill=LIGHT)
    # Side view of true rabbit head, narrower than its hips, almond-shaped.
    if look=="front":
        d.ellipse((13,8,18,13),fill=HI)
        d.ellipse((15,11,19,14),fill=FUR)
        d.point((15,10),fill=EYE)
        d.point((18,10),fill=EYE)
        d.point((17,13),fill=NOSE)
        d.point((15,13),fill=LIGHT)
    else:
        d.polygon([(13,11),(14,9),(16,8),(18,9),(19,11),
                   (20,12),(19,14),(16,14),(14,13)],fill=FUR)
        d.line([(15,9),(17,9),(18,10)],fill=HI)
        d.point((17,10),fill=EYE)
        d.point((20,12),fill=NOSE)
        d.point((18,13),fill=LIGHT)
        d.point((19,13),fill=SHADE)
        if look=="sniff":
            d.point((20,11),fill=NOSE)
            d.point((20,12),fill=FUR)
    # Two LOOONG separated ears that taper to 1 LED (not square pillars).
    # Their base sits just behind head, naturally slanted back.
    if look=="listen":
        d.polygon([(13,10),(11,5),(10,1),(11,0),(13,3),(15,9)],fill=FUR)
        d.polygon([(16,9),(17,3),(18,0),(19,2),(18,9)],fill=HI)
        d.line([(12,3),(13,7)],fill=EAR)
        d.line([(18,3),(17,7)],fill=EAR)
    elif look=="front":
        d.polygon([(13,10),(12,3),(12,0),(14,1),(15,9)],fill=FUR)
        d.polygon([(16,9),(17,2),(19,0),(19,4),(18,10)],fill=HI)
        d.line([(13,2),(14,7)],fill=EAR)
        d.line([(18,3),(17,8)],fill=EAR)
    else:
        d.polygon([(13,10),(12,5),(12,2),(13,0),(14,2),(15,9)],fill=HI)
        d.polygon([(16,9),(16,4),(18,1),(19,3),(18,10)],fill=FUR)
        d.line([(13,3),(14,8)],fill=EAR)
        d.line([(18,3),(17,8)],fill=EAR)
    # Powder-puff small tail on the BACK, not a second head.
    d.ellipse((0,13,4,17),fill=FUR)
    d.point((1,13),fill=HI)
    d.point((1,17),fill=LIGHT)
    # Massive folded hind leg, knee curving forward.
    d.ellipse((4,15,10,20),fill=FUR)
    d.arc((5,15,10,20),90,280,fill=LIGHT,width=1)
    d.polygon([(5,18),(5,20),(4,21),(11,21),(12,20),(9,19)],fill=FUR)
    d.line([(7,21),(11,21)],fill=LIGHT)
    # A gap between front and rear feet enhances real anatomy at 30x32.
    d.rectangle((12,20,13,21),fill=transparent)
    # Short foreleg, separate from hind paw, with a small front foot.
    d.line([(15,16),(16,18),(16,20),(18,20)],fill=FUR,width=2)
    d.point((19,20),fill=LIGHT)
    d.point((15,18),fill=LIGHT)
    # Only entrance / running cycle articulates the legs; standing stays poised.
    if stride:
        v=stride%4
        if v==1:
            d.rectangle((4,19,11,21),fill=transparent)
            d.line([(7,17),(5,19),(3,19)],fill=FUR,width=2)
            d.line([(15,17),(17,18),(19,19)],fill=FUR,width=2)
        elif v==2:
            d.rectangle((4,19,11,21),fill=transparent)
            d.line([(7,17),(9,19),(12,19)],fill=FUR,width=2)
            d.rectangle((16,20,20,21),fill=transparent)
            d.line([(15,17),(16,19),(19,18)],fill=FUR,width=2)
        elif v==3:
            d.rectangle((4,19,11,21),fill=transparent)
            d.line([(7,18),(4,20),(2,20)],fill=FUR,width=2)
            d.line([(15,18),(18,19),(20,20)],fill=FUR,width=2)
    return im

def overlay(base,sprite,left,top,scale=1.0):
    width=max(2,round(sprite.width*scale))
    height=max(2,round(sprite.height*scale))
    if (width,height)!=sprite.size:
        sprite=sprite.resize((width,height),Image.Resampling.NEAREST)
    # Protect against matrix code bleeding through gaps in rabbit silhouette.
    mask=sprite.getchannel("A")
    outer=mask.filter(ImageFilter.MaxFilter(3))
    shadow=Image.new("RGB",sprite.size,BACKGROUND)
    base.paste(shadow,(left,top),outer)
    base.paste(sprite.convert("RGB"),(left,top),mask)

def composited(index):
    im=rain.frame_at(index%rain.N)
    # 0.0-11.6s: rain only; 11.6-14s: enters; 14-18.1s: stops and looks around;
    # 18.1-22.4s: runs away into depth; 22.4-23.3s: single fading point;
    # 23.3-24s: rain only before seamless-ish loop.
    if index<116 or index>=233:return im,"rain",0
    if index<140:
        progress=smoothstep((index-116)/23)
        left=round(-21+25*progress)
        foot=30-(1 if (index//4)%3==1 else 0)
        pose=rabbit_sprite("right",stride=(index//4)%4)
        overlay(im,pose,left,foot-pose.height)
        return im,"entrance",pose.width
    if index<181:
        # Fixed ground position makes the rabbit recognizable; no body shrink.
        if index<153:look="right"
        elif index<166:look="front"
        elif index<175:look="listen"
        else:look="sniff"
        pose=rabbit_sprite(look)
        overlay(im,pose,4,30-pose.height)
        return im,"look_around",pose.width
    if index<224:
        p=(index-181)/43
        # First a running start, then rapid perspective shrinking.
        spatial=smoothstep(p)
        cx=14+12*spatial
        foot=30-13*spatial
        scale=1-0.88*smoothstep(max(0,(p-.12)/.88))
        pose=rabbit_sprite("right",stride=((index-181)//3)%4)
        width=max(2,round(pose.width*scale))
        height=max(2,round(pose.height*scale))
        hop=1 if width>=8 and ((index-181)//3)%4 in (1,2) else 0
        overlay(im,pose,round(cx-width/2),round(foot-height-hop),scale)
        return im,"run_away",width
    # By here figure vanishes into an unambiguous single bright LED.
    point_idx=index-224
    spot=(26,17)
    im.putpixel(spot,FUR if point_idx<4 else (142,204,161) if point_idx<7 else (37,83,48))
    return im,"point",1

def main():
    frames=[]
    phases={}
    for i in range(N):
        f,phase,width=composited(i)
        phases[phase]=phases.get(phase,0)+1
        frames.append(f)
        f.save(OUT/f"frame-{i:03}.png")
    assert phases=={"rain":123,"entrance":24,"look_around":41,"run_away":43,"point":9},phases
    assert all(frames[i].tobytes()==rain.frame_at(i%rain.N).tobytes() for i in list(range(116))+list(range(233,N)))
    assert all(composited(i)[2]==21 for i in range(140,181))
    # At least one whole second of genuinely stationary silhouette for recognition.
    assert all(frames[i].getpixel((18,10))==frames[145].getpixel((18,10)) for i in range(140,151))
    colors=sorted({c for f in frames for c in f.get_flattened_data()})
    assert len(colors)<64,len(colors)
    lut={c:i for i,c in enumerate(colors)}
    pal=[v for rgb in colors for v in rgb]+[0]*(768-3*len(colors))
    indexed=[]
    for f in frames:
        p=Image.new("P",(W,H));p.putpalette(pal)
        p.putdata([lut[c] for c in f.get_flattened_data()])
        indexed.append(p)
    gif=OUT/"source.gif"
    indexed[0].save(gif,format="GIF",save_all=True,append_images=indexed[1:],
                    loop=0,duration=[MS]*N,disposal=2,optimize=False)
    with Image.open(gif) as data:
        count=data.n_frames;total=0
        for j in range(count):
            data.seek(j);total+=int(data.info.get("duration",0))
        assert data.size==(W,H) and total==N*MS,(data.size,total)
    assert gif.stat().st_size<1_000_000
    # 3 rows: entrance, three poses while surveying, escape & vanishing point.
    moments=[116,120,126,133,139,143,155,161,169,177,182,186,192,199,207,216,223,225,230,235]
    sheet=Image.new("RGB",(W*5,H*4))
    for j,idx in enumerate(moments):
        sheet.paste(frames[idx],((j%5)*W,(j//5)*H))
    sheet.resize((900,768),Image.Resampling.NEAREST).save(OUT/"storyboard.png")
    frames[158].resize((420,448),Image.Resampling.NEAREST).save(OUT/"rabbit-preview.png")
    report={"canvas":[W,H],"durationSeconds":N*MS/1000,
            "requestedFrames":N,"encodedFrames":count,"phases":phases,
            "timeline":{"entersSec":11.6,"stopsSec":14.0,"looksUntilSec":18.1,
                        "fleesUntilSec":22.4,"pointUntilSec":23.3},
            "colors":len(colors),"bytes":gif.stat().st_size,
            "sha256":hashlib.sha256(gif.read_bytes()).hexdigest()}
    (OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(report,ensure_ascii=False))

if __name__=="__main__":
    main()
