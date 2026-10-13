#!/usr/bin/env python3
"""White Rabbit v3, 24-second Matrix rain film for 30x32 H70B6.
Keyframed body, head, ear, haunch and foot poses. Native LED pixel art;
preserves original 21x22 character scale and Matrix 2.0 rain.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import hashlib, importlib.util, json, math

ROOT=Path(r"D:\Project\CastleGovee")
OUT=ROOT/"artwork/matrix-rabbit-v3"
OUT.mkdir(parents=True,exist_ok=True)
source=ROOT/"skills/h70b6-pixel-art-director/scripts/render_matrix_rain_v2.py"
spec=importlib.util.spec_from_file_location("matrix_rain_v2",source)
rain=importlib.util.module_from_spec(spec);spec.loader.exec_module(rain)

W,H=30,32
N,DT=240,100
OFF=(0,0,0)
FUR=(251,254,250); PURE=(255,255,255); LIGHT=(193,221,210)
SHADE=(96,141,124); DEEP=(40,74,61); PINK=(249,153,174)
EYE=(4,31,18); NOSE=(255,163,171)

def ease(t):
    t=max(0,min(1,t));return t*t*(3-2*t)

def sprite(action="stand", blink=False, ears="up", step=0):
    """21x22 rabbit with a full ear/eye/muzzle, separate haunch and four paws."""
    im=Image.new("RGBA",(21,22),(0,0,0,0));d=ImageDraw.Draw(im)
    is_leap=action in ("bound","flight")
    # Ear poses: noticeable but never scale/blur the silhouette.
    backward=action=="glance_back"
    if backward:
        d.polygon([(9,10),(7,3),(8,1),(10,2),(12,10)],fill=FUR)
        d.polygon([(12,10),(12,2),(14,1),(16,3),(15,10)],fill=PURE)
        d.line((9,3,10,7),fill=PINK)
        d.line((14,3,14,7),fill=PINK)
    elif ears=="listen":
        d.polygon([(12,9),(10,2),(12,0),(14,1),(15,10)],fill=PURE)
        d.polygon([(16,9),(18,2),(20,2),(19,5),(18,10)],fill=FUR)
        d.line((12,2,13,7),fill=PINK)
        d.line((18,4,17,7),fill=PINK)
    elif ears=="fold":
        d.polygon([(12,9),(9,6),(7,5),(7,7),(11,11)],fill=FUR)
        d.polygon([(16,9),(15,4),(17,2),(18,4),(18,10)],fill=PURE)
        d.line((9,7,12,9),fill=PINK)
    else:
        d.polygon([(12,9),(12,2),(13,0),(15,1),(15,10)],fill=PURE)
        d.polygon([(16,9),(16,3),(18,1),(19,3),(18,10)],fill=FUR)
        d.line((13,2,13,7),fill=PINK)
        d.line((17,4,17,8),fill=PINK)
    # Full haunch and sculpted body: 3D shape from dark edge and white highlights.
    d.polygon([(4,13),(5,11),(7,10),(11,11),(13,12),(15,14),
               (14,17),(11,18),(6,18),(4,16)],fill=FUR)
    d.line([(5,13),(6,11),(9,11)],fill=PURE)
    d.line([(6,16),(9,17),(11,16)],fill=LIGHT)
    d.line([(9,12),(8,13),(9,15),(8,17)],fill=SHADE)
    d.line([(11,17),(13,16),(14,15)],fill=SHADE)
    d.point((6,15),fill=LIGHT)
    # Fluffy bob tail has a definite notch where it meets the rear.
    d.ellipse((0,12,5,16),fill=PURE)
    d.point((1,13),fill=LIGHT)
    d.point((3,16),fill=SHADE)
    # Flexible neck and muzzle; separate cheek defines head.
    if backward:
        d.polygon([(12,13),(11,11),(10,9),(7,10),(7,14),(10,16),(13,15)],fill=FUR)
        d.ellipse((6,9,13,14),fill=PURE)
        d.point((7,12),fill=NOSE)
        d.point((9,10),fill=EYE)
        d.point((11,14),fill=SHADE)
    else:
        d.polygon([(12,13),(13,10),(16,9),(18,11),(17,16),(15,17)],fill=FUR)
        d.ellipse((12,8,18,13),fill=PURE)
        d.ellipse((16,11,19,14),fill=FUR)
        d.point((20,13),fill=NOSE)
        d.point((19,13),fill=PURE)
        d.point((17,14),fill=SHADE)
        if action=="look_front":
            d.point((15,10),fill=EYE if not blink else LIGHT)
            d.point((18,10),fill=EYE if not blink else LIGHT)
            d.point((17,12),fill=PINK)
        else:
            d.point((18,10),fill=EYE if not blink else LIGHT)
        if action=="sniff":
            d.point((19,12),fill=PINK)
            d.point((18,14),fill=DEEP)
    # Hind leg and foreleg in detached, expressive key poses.
    d.ellipse((5,15,9,19),fill=FUR)
    d.point((6,16),fill=LIGHT)
    d.rectangle((11,19,13,21),fill=(0,0,0,0))
    if action in ("stand","look_front","glance_back","sniff","prepare"):
        if action=="prepare":
            d.line([(7,17),(5,20),(9,20)],fill=FUR,width=2)
            d.line([(15,16),(16,19),(19,20)],fill=FUR,width=2)
        else:
            d.line([(7,17),(6,19),(4,20),(9,20)],fill=FUR,width=2)
            d.line([(15,16),(15,19),(17,20),(19,20)],fill=FUR,width=2)
        d.point((7,18),fill=SHADE)
    elif action=="walk":
        poses=[
          ([(7,17),(4,20),(8,20)],[(15,16),(16,20),(19,20)]),
          ([(7,17),(5,19),(3,18)],[(15,16),(18,20),(20,19)]),
          ([(7,17),(9,20),(12,20)],[(15,16),(14,19),(17,20)]),
          ([(7,17),(4,19),(4,20)],[(15,16),(18,18),(20,17)])
        ]
        h,f=poses[step%4]
        d.line(h,fill=FUR,width=2);d.line(f,fill=FUR,width=2)
    elif action=="bound":
        d.line([(7,17),(5,18),(2,17)],fill=FUR,width=2)
        d.line([(8,17),(7,20),(10,20)],fill=FUR,width=2)
        d.line([(15,16),(17,16),(19,15)],fill=FUR,width=2)
        d.line([(14,16),(16,19)],fill=FUR,width=2)
    elif action=="flight":
        d.line([(7,17),(4,16),(2,15)],fill=FUR,width=2)
        d.line([(8,17),(6,20),(4,20)],fill=FUR,width=2)
        d.line([(15,16),(17,16),(20,15)],fill=FUR,width=2)
        d.line([(14,17),(17,20)],fill=FUR,width=2)
    elif action=="land":
        d.line([(7,17),(7,20),(10,20)],fill=FUR,width=2)
        d.line([(15,17),(14,20),(19,21)],fill=FUR,width=2)
    else: raise ValueError(action)
    # Tucked chest highlight, clear negative gap between fore/hind paws.
    d.point((14,16),fill=LIGHT)
    return im

def paste_rabbit(im,r,left,top,scale=1.0):
    w=max(2,round(r.width*scale));h=max(2,round(r.height*scale))
    if (w,h)!=r.size:r=r.resize((w,h),Image.Resampling.NEAREST)
    alpha=r.getchannel("A")
    # Contiguous black halo stops matrix symbols turning the rabbit into a blob.
    matte=alpha.filter(ImageFilter.MaxFilter(3))
    im.paste(Image.new("RGB",(w,h),OFF),(left,top),matte)
    im.paste(r.convert("RGB"),(left,top),alpha)

def animate(i):
    base=rain.frame_at(i%rain.N)
    if i<120 or i>=233:return base,"rain",0
    # Rabbit appears gradually from outside x=-21; two small natural hops.
    if i<151:
        p=ease((i-120)/30)
        left=round(-21+25*p)
        cycle=(i-120)%12
        lift=round(2.5*math.sin(math.pi*cycle/12))
        if cycle in (0,1):action="prepare"
        elif cycle in (2,3,4):action="bound"
        elif cycle in (5,6,7):action="flight"
        elif cycle in (8,9):action="land"
        else:action="walk"
        ears="fold" if action=="flight" else "up"
        r=sprite(action,ears=ears,step=cycle//3)
        paste_rabbit(base,r,left,30-r.height-lift)
        return base,"entrance",r.width
    # Rabbit holds position at x4 for 3.9s and inspects surroundings.
    if i<190:
        if i<164:look,ears="stand","up"
        elif i<175:look,ears="look_front","listen"
        elif i<185:look,ears="glance_back","up"
        else:look,ears="sniff","listen"
        blink=i in (162,163,172,173,185)
        r=sprite(look,blink=blink,ears=ears)
        # Real 1px breath on two frames, otherwise body remains dignified.
        bob=1 if i in (169,170) else 0
        paste_rabbit(base,r,4,30-r.height+bob)
        return base,"look_around",r.width
    # Escape: crouch, accelerate, 2 leap cycles, shrink toward upper-right.
    if i<224:
        t=(i-190)/34
        dist=ease(t)
        center_x=14+12*dist
        ground_y=30-13*dist
        scale=1-0.88*ease(max(0,(t-.11)/.89))
        cyc=(i-190)%10
        if i<193:action="prepare"
        elif cyc in (0,1,2):action="bound"
        elif cyc in (3,4,5,6):action="flight"
        else:action="land"
        r=sprite(action,ears="fold" if action=="flight" else "up")
        w=max(2,round(r.width*scale));h=max(2,round(r.height*scale))
        hop=round(3*math.sin(math.pi*cyc/10)*min(1,scale*1.1))
        paste_rabbit(base,r,round(center_x-w/2),round(ground_y-h-hop),scale)
        return base,"run_away",w
    p=i-224
    base.putpixel((26,17),FUR if p<4 else (158,219,172) if p<7 else (44,101,53))
    return base,"point",1

def render():
    frames=[];counts={}
    for i in range(N):
        image,phase,width=animate(i)
        counts[phase]=counts.get(phase,0)+1
        frames.append(image)
        image.save(OUT/f"frame-{i:03}.png")
    assert counts=={"rain":127,"entrance":31,"look_around":39,"run_away":34,"point":9},counts
    assert all(frames[i].tobytes()==rain.frame_at(i%rain.N).tobytes() for i in list(range(120))+list(range(233,N)))
    assert all(animate(i)[2]==21 for i in range(151,190))
    # Pixel-exact PNG and GIF, no antialias.
    colors=sorted({pixel for f in frames for pixel in f.get_flattened_data()})
    assert len(colors)<64,len(colors)
    lookup={pix:i for i,pix in enumerate(colors)}
    pal=[v for rgb in colors for v in rgb]+[0]*(768-len(colors)*3)
    indexed=[]
    for f in frames:
        p=Image.new("P",(W,H));p.putpalette(pal);p.putdata([lookup[q] for q in f.get_flattened_data()])
        indexed.append(p)
    output=OUT/"source.gif"
    indexed[0].save(output,format="GIF",save_all=True,append_images=indexed[1:],duration=[DT]*N,loop=0,disposal=2,optimize=False)
    with Image.open(output) as gif:
        decoded=gif.n_frames;duration=0
        for k in range(decoded):gif.seek(k);duration+=gif.info.get("duration",0)
    assert duration==DT*N and output.stat().st_size<1_000_000
    stages=[119,123,127,132,138,145,151,156,164,169,177,183,189,190,193,197,202,207,213,219,223,225,230,234]
    sheet=Image.new("RGB",(W*6,H*4),OFF)
    for j,index in enumerate(stages):
        sheet.paste(frames[index],((j%6)*W,(j//6)*H))
    sheet.resize((1080,768),Image.Resampling.NEAREST).save(OUT/"storyboard.png")
    frames[162].resize((420,448),Image.Resampling.NEAREST).save(OUT/"rabbit-preview.png")
    report={"durationSeconds":N*DT/1000,"requestedFrames":N,"gifFrames":decoded,
            "phases":counts,"canvas":[W,H],"palette":len(colors),"bytes":output.stat().st_size,
            "sha256":hashlib.sha256(output.read_bytes()).hexdigest()}
    (OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))

if __name__=="__main__":render()
