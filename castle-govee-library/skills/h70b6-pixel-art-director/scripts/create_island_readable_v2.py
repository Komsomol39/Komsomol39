#!/usr/bin/env python3
"""High-contrast tropical island for a REAL 30×32 LED curtain.
Art direction: unlit sky, clear sunshine, bold palm / sand silhouette, large flying gull.
Output: deterministic master GIF, frame strips, overview PNG, QA JSON.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import math, json, hashlib
W,H=30,32
N=56
DT=110
C={
 "off":(0,0,0), "sea":(0,38,60), "sea2":(0,108,155),
 "wave":(23,222,230),"foam":(140,255,235),
 "sunrim":(245,107,19),"sun":(255,215,38),"suncore":(255,246,118),
 "sandshade":(179,69,6),"sand":(255,151,23),"sandhi":(255,225,88),
 "trunkshade":(104,39,12),"trunk":(255,129,30),"trunkhi":(255,183,49),
 "leafshade":(0,93,50),"leaf":(9,213,70),"leafhi":(121,255,85),
 "gull":(246,253,255),"gullshade":(94,228,252), "beak":(255,180,35)
}
def I(x):return int(round(x))
def polygon(d,points,col):d.polygon(points,fill=C[col])
def line(d,points,col,w=1):d.line(points,fill=C[col],width=w,joint="curve")
def render(i):
 f=Image.new("RGB",(W,H),C["off"]);d=ImageDraw.Draw(f)
 # Highly controlled lit-pixel budget: no neon-blue sky wash.
 # Sun: isolated, high-contrast disc in top right.
 d.ellipse((22,2,28,8),fill=C["sunrim"])
 d.ellipse((23,3,27,7),fill=C["sun"])
 d.line((24,4,26,4),fill=C["suncore"])
 d.point((25,5),fill=C["suncore"])
 # Water becomes four discrete dark/bright lines rather than a luminous blanket.
 d.rectangle((0,26,29,31),fill=C["sea"])
 k=i%N
 # Very small 1px wave motion.
 for y,start,end,phase in [(27,0,7,0),(27,17,28,6),(29,1,10,7),(29,17,26,13),(31,4,15,2),(31,22,29,9)]:
     shift=I(math.sin(2*math.pi*k/N+phase)*1)
     d.line((start+shift,y,end+shift,y),fill=C["sea2"],width=1)
 # Two-pixel travelling water glimmer: preserves all unique frames.
 glint=i%30
 d.line((glint,30,min(29,glint+1),30),fill=C["wave"])
 # Island: one unmistakable golden triangle with broad bright upper edge.
 polygon(d,[(3,26),(6,24),(11,23),(19,23),(24,24),(27,26),(25,28),(5,28)],"sandshade")
 polygon(d,[(5,25),(10,23),(20,23),(25,25),(23,27),(7,27)],"sand")
 d.line((9,23,20,23),fill=C["sandhi"],width=2)
 d.line((10,26,19,26),fill=C["sandhi"],width=1)
 # Palm: lit warm-orange crooked trunk at x13-16, conspicuous against OFF background.
 # slight movement only in canopy, trunk remains fixed.
 line(d,[(12,24),(12,21),(13,18),(14,16),(15,13)],"trunkshade",4)
 line(d,[(12,24),(12,21),(13,18),(14,16),(15,13)],"trunk",2)
 d.line((13,21,14,17),fill=C["trunkhi"],width=1)
 # Palm's recognizable 'star' crown with downward dangling end-pixels.
 sway=I(math.sin(2*math.pi*k/N)*1)
 xx=15+sway
 def frond(path):
     line(d,path,"leafshade",2)
     line(d,path,"leaf",1)
     d.point(path[-1],fill=C["leafhi"])
 # Create a 14 to 20 px canopy; no frond intersects bird flight lane.
 frond([(xx,13),(xx-3,11),(xx-7,11),(xx-10,13)])
 frond([(xx,13),(xx-5,14),(xx-8,16),(xx-9,18)])
 frond([(xx,13),(xx-3,15),(xx-4,18)])
 frond([(xx,13),(xx+4,11),(xx+8,11),(xx+10,13)])
 frond([(xx,13),(xx+5,14),(xx+8,16),(xx+9,18)])
 frond([(xx,13),(xx+3,15),(xx+4,18)])
 # Two coconuts make palm distinct from random green star.
 d.point((xx-1,14),fill=C["sandshade"])
 d.point((xx+1,14),fill=C["sandshade"])
 # Clear animated gull, 12-14 px across, crossing top third rightward.
 # Starts outside left boundary, ends outside right; no seam teleports.
 x=-10+i  # 56 steps from -10 to 45 inclusive
 y=9+I(math.sin(2*math.pi*i/N)*1)
 pose=i%8
 # joint up/down flaps, each wing is 2px thick.
 lift=[-3,-3,-2,-1,0,0,-1,-2][pose]
 # spread wings
 line(d,[(x-1,y),(x-3,y+lift),(x-6,y+lift-1)],"gullshade",3)
 line(d,[(x+1,y),(x+3,y+lift),(x+6,y+lift-1)],"gullshade",3)
 line(d,[(x-1,y-1),(x-3,y+lift-1),(x-6,y+lift-2)],"gull",2)
 line(d,[(x+1,y-1),(x+3,y+lift-1),(x+6,y+lift-2)],"gull",2)
 # head and bird core: contrasting cream and amber beak
 d.rectangle((x-1,y-1,x+1,y+1),fill=C["gull"])
 d.point((x+2,y),fill=C["beak"])
 # Distinctive seagull tail feathers
 d.point((x-1,y+2),fill=C["gullshade"])
 return f

def go(output):
 out=Path(output);out.mkdir(parents=True,exist_ok=True)
 src=out/"frames";src.mkdir(exist_ok=True)
 frames=[]
 for i in range(N):
     f=render(i);f.save(src/f"frame-{i:03d}.png");frames.append(f)
 # preserve pixel-palette RGB by encoder mapping all 18 colors exactly.
 palette=[ch for rgb in C.values() for ch in rgb]+[0]*(768-len(C)*3)
 lookup={rgb:n for n,rgb in enumerate(C.values())}
 pframes=[]
 for f in frames:
     assert set(f.get_flattened_data()).issubset(set(lookup))
     p=Image.new("P",(W,H))
     p.putpalette(palette)
     p.putdata([lookup[x] for x in f.get_flattened_data()])
     pframes.append(p)
 master=out/"source.gif"
 pframes[0].save(master,format="GIF",save_all=True,append_images=pframes[1:],loop=0,
                 duration=[DT]*N,disposal=2,optimize=False)
 with Image.open(master) as test:
    if test.n_frames!=N:raise RuntimeError(f"Frame collapse {test.n_frames}!={N}")
 def diff(a,b):return sum(p!=q for p,q in zip(a.get_flattened_data(),b.get_flattened_data()))
 occupancy=[sum(any(v>0 for v in pix) for pix in f.get_flattened_data())/(W*H) for f in frames]
 # render storyboard without blur
 overview=Image.new("RGB",(30*5*4,32*5*2),C["off"])
 for j,at in enumerate((0,8,16,24,32,40,48,55)):
     overview.paste(frames[at].resize((150,160),Image.Resampling.NEAREST),((j%4)*150,(j//4)*160))
 overview.save(out/"storyboard.png")
 frames[20].resize((450,480),Image.Resampling.NEAREST).save(out/"preview-final.png")
 report={"size":[W,H],"frames":N,"delayMs":DT,"durationMs":N*DT,"palette":len(C),
         "sourceBytes":master.stat().st_size,"sourceSha256":hashlib.sha256(master.read_bytes()).hexdigest(),
         "litRatioAvg":round(sum(occupancy)/len(occupancy),3),"litRatioRange":[round(min(occupancy),3),round(max(occupancy),3)],
         "loopEdgeDiff":diff(frames[0],frames[-1]),"uniqueFrames":len({hashlib.sha256(f.tobytes()).digest() for f in frames})}
 (out/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
 print(json.dumps(report,indent=2))
if __name__=="__main__":
 import argparse
 ap=argparse.ArgumentParser()
 ap.add_argument("--output",default=r"D:\Project\CastleGovee\artwork\island-readable-v2")
 go(ap.parse_args().output)
