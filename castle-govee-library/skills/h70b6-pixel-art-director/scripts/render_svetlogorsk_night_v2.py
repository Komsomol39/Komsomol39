"""Castle Govee H70B6: Svetlogorsk water tower night, v2 (30x32).
12-second timeline @ 100%:
 window #1 (high-tower gallery, left bay): 0-5 seconds.
 window #2 (high-tower gallery, right bay): 6-11 seconds.
 Never two lit together. Five candidate window positions; three remain dark.
"""
from PIL import Image, ImageDraw
from pathlib import Path
import importlib.util, math, hashlib, json

P=Path(r"D:\Project\CastleGovee")
mod=P/"skills/h70b6-pixel-art-director/scripts/render_svetlogorsk_water_tower.py"
sp=importlib.util.spec_from_file_location("svetlogorsk_arch",mod)
arch=importlib.util.module_from_spec(sp)
sp.loader.exec_module(arch)
out=P/"artwork/svetlogorsk-tower/night-animation-v2"
out.mkdir(parents=True,exist_ok=True)
N,MS=120,100
BASE=arch.art("hybrid")
C=arch.C
OFF=C["off"]

def upright_moon(image):
    d=ImageDraw.Draw(image)
    d.rectangle((22,2,29,10),fill=OFF)
    d.ellipse((23,3,28,9),fill="#ffe09a")
    d.ellipse((25,2,29,7),fill=OFF)
    d.point((23,7),fill="#ffe09a")

upright_moon(BASE)

# A stylized small willow under the bright north-west star. Trunk at x2,
# light drooping branches at x0-6. Exactly three foliage LEDs project over
# the brown shaft on x5-6 (y20-24); no emblem, white gallery or lit windows
# are obscured. Tree is held still so moon/meteor/windows remain the motion.
def willow_at_tower(image):
    d=ImageDraw.Draw(image)
    dark="#163d2c"
    forest="#276c46"
    leaf="#499c63"
    tips="#89bb70"
    bark="#a86a41"
    shadow="#72442b"
    d.line([(2,30),(2,26),(3,22),(3,19)],fill=shadow,width=2)
    d.line([(2,29),(2,25),(3,21)],fill=bark,width=1)
    d.line([(3,21),(1,18),(1,16)],fill=shadow,width=1)
    d.line([(3,20),(5,17),(5,15)],fill=bark,width=1)
    d.line([(3,23),(5,20),(6,19)],fill=shadow,width=1)
    d.polygon([(0,17),(1,15),(3,14),(5,15),(6,17),(5,19),
               (6,21),(4,21),(3,23),(1,22),(0,20)],fill=dark)
    d.line([(1,16),(3,15),(5,16)],fill=forest,width=1)
    d.line([(0,18),(2,17),(4,18),(5,18)],fill=leaf,width=1)
    d.line([(1,20),(3,19),(4,20)],fill=forest,width=1)
    # Thin hanging leaf strands make it willow-like, but avoid sky sparkles.
    for x,top,bottom in [(0,19,23),(1,20,24),(2,20,23),(4,19,24),(5,18,22)]:
        d.line((x,top,x,bottom),fill=forest)
    for x,y in [(1,16),(3,15),(4,17),(0,20),(2,19),(3,21),(4,22),(5,19)]:
        d.point((x,y),fill=leaf)
    for x,y in [(0,21),(2,17),(4,20),(5,21)]:
        d.point((x,y),fill=tips)
    # Gentle contact with the side of the tower: 2-3 leaf pixels, no
    # bright roof arches or white landmark emblem are covered.
    for x,y,c in [(5,23,forest),(6,22,forest),(5,26,dark)]:
        d.point((x,y),fill=c)

willow_at_tower(BASE)

# Five architectural window openings, two occupied for exactly 50 frames each.
# 0 left gallery, 1 right gallery, 2 left attic, 3 right attic, 4 ground floor.
WINDOWS={
 "gallery_left":  [(8,11),(9,11),(8,12),(9,12)],
 "gallery_right": [(11,11),(12,11),(11,12),(12,12)],
 "attic_left":    [(20,22)],
 "attic_right":   [(26,22)],
 "ground_left":   [(19,27),(20,27),(19,28),(20,28)]
}
LIT=[(0,50,"gallery_left"),(60,110,"gallery_right")]
STAR_POINTS=[(2,4),(18,2),(20,11),(28,11),(18,9)]
frames=[]
lit_timeline=[]
for idx in range(N):
    im=BASE.copy()
    d=ImageDraw.Draw(im)
    # Distinctive star in the empty far upper left corner. Five-LED sparkle,
    # halo tones gently change, but center stays bright enough to read at distance.
    tw=(1+math.sin(2*math.pi*idx/24))/2
    main="#ffffff" if tw>.55 else "#fff4b9"
    dim="#6aa2bd" if tw>.55 else "#315c79"
    for x,y in [(2,3),(1,4),(3,4),(2,5)]:
        d.point((x,y),fill=dim)
    d.point((2,4),fill=main)
    for j,(x,y) in enumerate(STAR_POINTS[1:]):
        if 22<=x<=29 and 2<=y<=10:continue
        brightness=(1+math.sin(2*math.pi*idx/(33+j*7)+j*1.9))/2
        d.point((x,y),fill=("#bfdfff" if brightness>.8 else
                            "#5786a8" if brightness>.35 else "#204055"))
    # One light trail crossing the clear patch, away from the roof or moon.
    if 34<=idx<46:
        k=idx-34
        x=16+k
        y=4+k//4
        if not (23<=x<=29 and 2<=y<=10):
            d.point((x,y),fill="#ffffff")
        for trail in (1,2,3):
            xx=x-trail
            yy=y-(trail//3)
            if 16<=xx<29 and 1<=yy<=10 and not(23<=xx<=29 and 2<=yy<=10):
                d.point((xx,yy),fill=("#d5edff" if trail==1 else "#6097bc" if trail==2 else "#244865"))
    # Exactly one of the five windows illuminates, with no rapid flutter.
    chosen=None
    for first,last,name in LIT:
        if first<=idx<last:
            chosen=name
            # 5 second ON interval; gentle edge ramp during first/last 300 ms.
            elapsed=min(idx-first,last-1-idx)
            strength=min(1.0,(elapsed+1)/3.0)
            palette=("#9d560a","#ed9622","#ffbd39")
            light=palette[min(2,max(0,round(strength*3)-1))]
            for point in WINDOWS[name]:
                d.point(point,fill=light)
    lit_timeline.append(chosen)
    im.save(out/f"frame-{idx:03}.png")
    frames.append(im)

# Validate positions remain dark in the OFF windows, as in source architecture.
for i,f in enumerate(frames):
    for name,points in WINDOWS.items():
        expected=lit_timeline[i]==name
        if name in ("gallery_left","gallery_right"):
            changed=any(f.getpixel(p)!=BASE.getpixel(p) for p in points)
            if changed!=expected:raise RuntimeError(f"Window mismatch frame {i} {name}: {changed}/{expected}")
assert lit_timeline.count("gallery_right")==50
assert lit_timeline.count("gallery_left")==50
assert lit_timeline.count(None)==20

colors=sorted(set(pixel for image in frames for pixel in image.get_flattened_data()))
assert len(colors)<=256,len(colors)
flat=[channel for col in colors for channel in col]
pal=flat+[0]*(768-len(flat))
lut={color:i for i,color in enumerate(colors)}
indexed=[]
for frame in frames:
    dst=Image.new("P",(30,32))
    dst.putpalette(pal)
    dst.putdata([lut[color] for color in frame.get_flattened_data()])
    indexed.append(dst)
dest=out/"source.gif"
indexed[0].save(dest,save_all=True,append_images=indexed[1:],
    loop=0,duration=[MS]*N,disposal=2,optimize=False)
with Image.open(dest) as g:
    assert g.size==(30,32) and g.n_frames>=60, (g.size,g.n_frames)
    gif_frames=g.n_frames
    total=0
    for i in range(gif_frames):
        g.seek(i)
        total+=g.info.get("duration",0)
    assert total==N*MS,(total,N*MS)
# 12 sample moments 0..11s for tangible review
sheet=Image.new("RGB",(30*6,32*2),OFF)
for i in range(12):
    sheet.paste(frames[i*10],((i%6)*30,(i//6)*32))
sheet.resize((1080,384),Image.Resampling.NEAREST).save(out/"storyboard.png")
frames[35].resize((420,448),Image.Resampling.NEAREST).save(out/"preview.png")
report={
 "canvas":[30,32],"sourceFrames":N,"gifFrames":gif_frames,"durationMs":N*MS,
 "window1":{"name":"gallery_left","startMs":0,"endMs":5000,"durationMs":5000},
 "window2":{"name":"gallery_right","startMs":6000,"endMs":11000,"durationMs":5000},
 "candidateWindowCount":len(WINDOWS),"maxSimultaneousLitWindows":1,
 "paletteSize":len(colors),"gifBytes":dest.stat().st_size,
 "sha256":hashlib.sha256(dest.read_bytes()).hexdigest()
}
(out/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,ensure_ascii=False))
