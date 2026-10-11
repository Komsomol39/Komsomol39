#!/usr/bin/env python3
"""Render a declarative, pixel-perfect 30x32 art scene to PNGs and GIF."""
import argparse,hashlib,json,math,random
from pathlib import Path
from PIL import Image,ImageDraw

W,H=30,32
def rgb(spec,n):
    v=spec["palette"].get(n[1:],n) if n.startswith("@") else n
    if len(v)!=7 or not v.startswith("#"):raise ValueError("bad color "+v)
    return tuple(int(v[i:i+2],16) for i in (1,3,5))

def draw_scene(spec,index):
    n=spec["frames"];t=2*math.pi*index/n
    im=Image.new("RGB",(W,H));d=ImageDraw.Draw(im)
    R=lambda v:rgb(spec,v)
    for layer in spec["layers"]:
        typ=layer["type"]
        c=R(layer.get("color","@ink"))
        if typ=="bands":
            bands=layer["rows"]
            for j,(y,col) in enumerate(bands):
                end=bands[j+1][0]-1 if j<len(bands)-1 else H-1
                d.rectangle((0,y,W-1,end),fill=R(col))
        elif typ=="polygon":
            d.polygon(layer["points"],fill=c)
        elif typ=="rect":
            d.rectangle(layer["bounds"],fill=c)
        elif typ=="sun":
            x,y,r=layer["x"],layer["y"],layer.get("r",3)
            d.ellipse((x-r,y-r,x+r,y+r),fill=c)
        elif typ=="cloud":
            x=round(layer["x"]+layer.get("drift",1)*math.sin(t))
            y=layer["y"]
            d.rectangle((x,y+1,x+8,y+2),fill=c)
            d.rectangle((x+2,y,x+5,y+3),fill=c)
        elif typ=="stars":
            rng=random.Random(spec.get("seed",2026)+layer.get("seed",0))
            for k in range(layer.get("count",10)):
                x,y=rng.randrange(W),rng.randrange(layer.get("maxY",16))
                if math.sin(t*layer.get("cycles",2)+k*1.7)>-0.15:d.point((x,y),fill=c)
        elif typ=="aurora":
            for x in range(W):
                y=layer.get("y",5)+round(2*math.sin(x*.3+t))
                for offset in range(layer.get("height",7)):
                    yy=y+offset
                    if 0<=yy<H:
                        shade=layer["shades"][min(2,offset*3//max(1,layer.get("height",7)))]
                        d.point((x,yy),fill=R(shade))
        elif typ=="waves":
            yy=layer.get("y",21)
            d.rectangle((0,yy,W-1,H-1),fill=c)
            tint=R(layer["highlight"])
            for y in range(yy+1,H,3):
                for k in range(5):
                    x=round(k*9-4+3*math.sin(t+y*.5+k))
                    d.line((x,y,x+3,y),fill=tint)
        elif typ=="island":
            x,y=layer.get("x",14),layer.get("y",22)
            d.polygon([(x-9,y+3),(x-6,y),(x+4,y-1),(x+8,y+3)],fill=c)
            d.line((x-6,y,x+3,y-1),fill=R(layer["grass"]))
        elif typ=="palm":
            x,y=layer["x"],layer["y"];z=layer.get("height",10)
            head=x+3+round(layer.get("sway",1)*math.sin(t))
            d.line((x,y,x+1,y-4,head,y-z),fill=c,width=2)
            for dx,dy in [(-8,1),(-6,-3),(-2,-5),(4,-5),(8,-2),(8,2)]:
                d.line((head,y-z,head+dx,y-z+dy),fill=R(layer["leaves"]))
        elif typ=="bird":
            x=round(layer["x"]+layer.get("range",5)*math.sin(t))
            y=round(layer["y"]+layer.get("bob",2)*math.sin(2*t))
            wing=round(2*math.sin(3*t))
            d.line((x-3,y-1-wing,x-1,y,x+1,y,x+3,y-1-wing),fill=c)
        else:raise ValueError("unknown layer: "+typ)
    return im

def run(scene_path,output):
    spec=json.loads(Path(scene_path).read_text(encoding="utf-8-sig"))
    if spec.get("schema")!=1 or (spec.get("width"),spec.get("height"))!=(30,32):
        raise ValueError("Expected schema 1, 30x32")
    n=spec["frames"];delay=spec.get("frameMs",150)
    if not 12<=n<=240 or not 50<=delay<=1000:raise ValueError("Bad timing")
    if not 1<=len(spec["palette"])<=48:raise ValueError("Palette must have <=48 colors")
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    folder=output/"frames";folder.mkdir(exist_ok=True)
    frames=[]
    for i in range(n):
        f=draw_scene(spec,i)
        f.save(folder/f"frame-{i:03d}.png")
        frames.append(f)
    all_colors=list(dict.fromkeys(rgb(spec,"@"+k) for k in spec["palette"]))
    if any(set(f.get_flattened_data())-set(all_colors) for f in frames):raise ValueError("Unknown palette color")
    pal=[x for c in all_colors for x in c]+[0]*(768-3*len(all_colors))
    lut={c:i for i,c in enumerate(all_colors)}
    indexed=[]
    for f in frames:
        z=Image.new("P",(30,32));z.putpalette(pal);z.putdata([lut[c] for c in f.get_flattened_data()])
        indexed.append(z)
    gif=output/"source.gif"
    indexed[0].save(gif,save_all=True,append_images=indexed[1:],
                    duration=[delay]*n,loop=0,disposal=2,optimize=False)
    frames[0].resize((360,384),Image.Resampling.NEAREST).save(output/"preview.png")
    sheet=Image.new("RGB",(240,32*math.ceil(n/8)))
    for i,f in enumerate(frames):sheet.paste(f,((i%8)*30,(i//8)*32))
    sheet.resize((sheet.width*4,sheet.height*4),Image.Resampling.NEAREST).save(output/"contact-sheet.png")
    with Image.open(gif) as source:decoded=source.n_frames
    diff=lambda a,b:sum(p!=q for p,q in zip(a.get_flattened_data(),b.get_flattened_data()))
    report={"canvas":[30,32],"requestedFrames":n,"gifFrames":decoded,
        "uniqueFrames":len(set(hashlib.sha256(f.tobytes()).digest() for f in frames)),
        "paletteColors":len(all_colors),"gifBytes":gif.stat().st_size,
        "loopBoundaryChangedPixels":diff(frames[-1],frames[0]),
        "avgChangedPixels":round(sum(diff(frames[i],frames[(i+1)%n]) for i in range(n))/n,2)}
    (output/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    if decoded!=n or gif.stat().st_size>1_000_000:raise ValueError("GIF failed device size/frame QA")
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--scene",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();run(a.scene,a.output)
