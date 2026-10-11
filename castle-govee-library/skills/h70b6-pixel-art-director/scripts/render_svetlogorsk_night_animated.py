from PIL import Image, ImageDraw
from pathlib import Path
import importlib.util, math, hashlib, json
P=Path(r"D:\Project\CastleGovee")
f=P/"skills/h70b6-pixel-art-director/scripts/render_svetlogorsk_water_tower.py"
sp=importlib.util.spec_from_file_location("tower_art",f);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
out=P/"artwork/svetlogorsk-tower/night-animation"
out.mkdir(parents=True,exist_ok=True)
N=64; MS=120
base=m.art("hybrid")
# Replace original moon with a neat crescent oriented upright (left lit arc, dark inset).
# Keep moon within x=23..28,y=3..10; no collision with upper roof.
def moon(im):
 d=ImageDraw.Draw(im)
 # Blank original region without touching stars at x18..20.
 d.rectangle((22,2,29,10),fill=m.C["off"])
 # Standing crescent: gold disk carved at slightly rightward x-coordinate.
 d.ellipse((23,3,28,9),fill="#ffe09a")
 d.ellipse((25,2,29,7),fill=m.C["off"])
 d.point((23,7),fill="#ffe09a")
 return im
base=moon(base)
# Position windows only: lit under roof in round side building, and tall tower's gallery.
# For each pixel mask, avoid changing prominent white architectural lines.
windows=[(20,22),(26,22),(20,27),(26,27),(7,11),(10,11),(13,11),(10,19)]
states=[
 (range(4,17), [0,4]),
 (range(18,31), [1,3,6]),
 (range(31,42), [2,5]),
 (range(44,58), [0,1,7]),
]
stars=[(18,2),(27,1),(20,11),(28,11),(18,9)]
for idx in range(N):
 im=base.copy();d=ImageDraw.Draw(im)
 t=idx/N
 # subtle slow twinkling; at least one star dim at a time
 for j,(x,y) in enumerate(stars):
  if 22<=x<=29 and 2<=y<=10:continue
  levels=["#183450","#437b9a","#b4ddff","#f4fbff"]
  v=(idx*0.105 + j*.53)%4
  level=int((1+math.sin(v*math.pi/2))*1.5)
  d.point((x,y),fill=levels[level])
 # a tiny shooting meteor in upper sky, only 12 frames, once per 7.68s loop.
 # upper free zone right of central spire, moves to the far right and down.
 if 20<=idx<32:
  k=idx-20
  x=16+k
  y=4+k//4
  d.point((x,y),fill="#f8f9d6")
  for trail in range(1,4):
   xx=x-trail
   yy=y-(trail//3)
   if xx>=16 and 0<=yy<12 and xx!=18:
    d.point((xx,yy),fill=["#a4d5f2","#5587a9","#18354a"][trail-1])
 # The animation never changes the main architectural silhouette.
 for interval,lit in states:
  if idx in interval:
   for wi in lit:
    x,y=windows[wi]
    d.point((x,y),fill="#ffd984" if (idx+wi)%5 else "#ffeab3")
 frame_path=out/f"frame-{idx:03}.png"
 im.save(frame_path)
# indexed palette after all frames to ensure exact unaliased colors
frames=[Image.open(out/f"frame-{i:03}.png").convert("RGB") for i in range(N)]
colors=sorted(set(p for im in frames for p in im.get_flattened_data()))
assert len(colors)<=256
pal=[v for c in colors for v in c]+[0]*(768-3*len(colors))
lookup={c:i for i,c in enumerate(colors)}
converted=[]
for im in frames:
 q=Image.new("P",(30,32));q.putpalette(pal);q.putdata([lookup[p] for p in im.get_flattened_data()]);converted.append(q)
target=out/"source.gif"
converted[0].save(target,save_all=True,append_images=converted[1:],loop=0,duration=[MS]*N,disposal=2,optimize=False)
with Image.open(target) as g:
 assert g.size==(30,32) and g.n_frames>=32,(g.size,g.n_frames)
 actual_frames=g.n_frames
preview=frames[24].resize((420,448),Image.Resampling.NEAREST)
preview.save(out/"preview.png")
sheet=Image.new("RGB",(30*8,32*8))
for ix,fr in enumerate(frames):
 sheet.paste(fr,((ix%8)*30,(ix//8)*32))
sheet.resize((960,1024),Image.Resampling.NEAREST).save(out/"contact-sheet.png")
r={"sourceFrames":N,"gifFrames":actual_frames,"durationMs":N*MS,"colors":len(colors),"bytes":target.stat().st_size,
"unique":len(set(hashlib.sha256(im.tobytes()).digest() for im in frames)),
"sha256":hashlib.sha256(target.read_bytes()).hexdigest()}
(out/"report.json").write_text(json.dumps(r,indent=2),encoding="utf8")
print(json.dumps(r))
