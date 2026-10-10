#!/usr/bin/env python3
"""Castle GIF Library v2 authoring pipeline, executed on PC/CI, never Android.

Example:
 python tools/add_effect_v2.py --input demo.gif --id demo --title "Demo" --output library-publish
 python tools/add_effect_v2.py --input demo.gif --id demo --title "Demo" --speeds 50,100,150 --orientations normal --replace

Produces finished GIF variants and schema-2 metadata. Upload the changed GIF
files and catalog.json in ONE commit. Requires Pillow.
"""
import argparse
import hashlib
import io
import json
import re
from pathlib import Path
from PIL import Image, ImageOps

WIDTH,HEIGHT=30,32
MAX_GIF=1_000_000
PALETTE=[]
for i in range(256):
    PALETTE.extend(((i>>5&7)*255//7, (i>>2&7)*255//7, (i&3)*255//3))

def digest(data):return hashlib.sha256(data).hexdigest()

def frame_to_rgb(frame):
    image=frame.convert("RGBA")
    image=ImageOps.contain(image,(WIDTH,HEIGHT),method=Image.Resampling.LANCZOS)
    bg=Image.new("RGBA",(WIDTH,HEIGHT),(0,0,0,255))
    bg.alpha_composite(image,((WIDTH-image.width)//2,(HEIGHT-image.height)//2))
    return bg.convert("RGB")

def to_palette(image):
    rgb=image.convert("RGB")
    indices=bytearray(WIDTH*HEIGHT)
    for j,(r,g,b) in enumerate(rgb.getdata()):
        indices[j]=(r&0xE0)|((g&0xE0)>>3)|(b>>6)
    p=Image.frombytes("P",(WIDTH,HEIGHT),bytes(indices))
    p.putpalette(PALETTE)
    return p

def gif_bytes(pixels,durations,loop):
    palette_frames=[to_palette(p) for p in pixels]
    out=io.BytesIO()
    palette_frames[0].save(out,format="GIF",save_all=True,
        append_images=palette_frames[1:],duration=durations,
        loop=0 if loop else None,disposal=1,optimize=False)
    encoded=out.getvalue()
    if not (35<len(encoded)<=MAX_GIF):
        raise ValueError("GIF file exceeds 1,000,000-byte safe limit")
    with Image.open(io.BytesIO(encoded)) as im:
        if im.size!=(WIDTH,HEIGHT) or im.n_frames!=len(pixels):
            raise ValueError("GIF dimensions/count changed on encoding")
        actual_delays=[]
        for index in range(im.n_frames):
            im.seek(index)
            actual_delays.append(im.info.get("duration",0))
            if im.convert("RGB").size!=(WIDTH,HEIGHT):
                raise ValueError("Frame dimensions changed")
    return encoded,actual_delays

def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input",required=True,type=Path)
    ap.add_argument("--id",required=True)
    ap.add_argument("--title",required=True)
    ap.add_argument("--description",default="")
    ap.add_argument("--output",type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument("--speeds",default="all",help="all or comma-separated 10..200 multiples of 10")
    ap.add_argument("--orientations",default="normal,street",help="normal,street / normal / street")
    ap.add_argument("--base-frame-ms",type=int,default=0,help="Override input GIF delays (e.g. 250)")
    ap.add_argument("--replace",action="store_true")
    args=ap.parse_args()
    if not args.input.is_file():ap.error("Input not found")
    if not re.fullmatch(r"[a-z0-9-]{2,48}",args.id):ap.error("Invalid id")
    if not (0<len(args.title)<=80):ap.error("Invalid title")
    orientations=[x.strip() for x in args.orientations.split(",")]
    if not orientations or any(x not in ("normal","street") for x in orientations) or len(set(orientations))!=len(orientations):
        ap.error("Only normal/street orientations")
    if args.speeds=="all":
        speeds=list(range(10,201,10))
    else:
        try:speeds=[int(v.strip()) for v in args.speeds.split(",")]
        except ValueError:ap.error("Invalid speed list")
        if not speeds or len(speeds)!=len(set(speeds)) or any(v<10 or v>200 or v%10 for v in speeds):
            ap.error("Speeds must be unique 10..200 multiples of 10")
    with Image.open(args.input) as image:
        count=getattr(image,"n_frames",1)
        if count>60000:ap.error("Too many frames")
        original=[frame_to_rgb(image.copy()) for i in range(count) if not image.seek(i)]
        image.seek(0)
        src_delays=[]
        for i in range(count):
            image.seek(i)
            duration=args.base_frame_ms if args.base_frame_ms else image.info.get("duration",100)
            src_delays.append(max(20,int(duration or 100)))
    animated=count>1
    if not animated:speeds=[100]
    if not original:raise ValueError("No input frames")
    dst=args.output
    manifest_path=dst/"catalog.json"
    if manifest_path.exists():
        catalog=json.loads(manifest_path.read_text(encoding="utf8"))
        if catalog.get("schema")!=2:ap.error("Output must be schema v2, not legacy v1")
    else:
        catalog={"schema":2,"format":"castle-govee-native-gif-v2",
                 "width":WIDTH,"height":HEIGHT,"items":[]}
    if any(x["id"]==args.id for x in catalog["items"]) and not args.replace:
        ap.error("Already exists; use --replace")
    preview=io.BytesIO()
    original[0].save(preview,format="PNG",optimize=True)
    preview_bytes=preview.getvalue()
    preview_path=(f"animations/{args.id}/frame-00.png" if animated else f"images/{args.id}.png")
    entry={"id":args.id,"title":args.title,"description":args.description[:200],
        "type":"animation" if animated else "image",
        "preview":{"file":preview_path,"sha256":digest(preview_bytes)},
        "variants":[]}
    if animated:entry["loop"]=True
    binaries={preview_path:preview_bytes}
    for orientation in orientations:
        visual=original if orientation=="normal" else [ImageOps.mirror(v) for v in original]
        for speed in speeds:
            delays=[max(20,min(655350,round(ms*100/speed/10)*10)) for ms in src_delays]
            data,verified=gif_bytes(visual,delays,animated)
            rel=(f"gifs/{args.id}/{orientation}/{speed:03d}.gif" if animated else
                 f"gifs/{args.id}/{orientation}.gif")
            variant={"orientation":orientation,"file":rel,"sha256":digest(data),
                     "sizeBytes":len(data),"frameCount":count,
                     "durationMs":sum(verified)}
            if animated:variant["speedPercent"]=speed
            entry["variants"].append(variant)
            binaries[rel]=data
    if args.replace:
        catalog["items"]=[i for i in catalog["items"] if i["id"]!=args.id]
    catalog["items"].append(entry)
    if len(catalog["items"])>48:ap.error("More than 48 catalog items")
    # Write all binaries first; manifest last. This is local staging only.
    for rel,data in binaries.items():
        p=dst/rel
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(data)
    manifest_path.parent.mkdir(parents=True,exist_ok=True)
    tmp=manifest_path.with_name("catalog.json.tmp")
    tmp.write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    tmp.replace(manifest_path)
    print("READY",entry["id"],"frames",count,"variants",len(entry["variants"]),
          "bytes",sum(len(v) for k,v in binaries.items() if k.endswith(".gif")))
    print("PUBLISH atomically to GitHub: all GIFs, previews, and catalog.json")

if __name__=="__main__":
    main()
