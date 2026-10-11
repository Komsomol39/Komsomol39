#!/usr/bin/env python3
"""Validate staged Castle GIF Library v2: asset integrity, frame metadata and mirror pairs."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageOps

def check(root):
    root=Path(root).resolve()
    cat=json.loads((root/"catalog.json").read_text(encoding="utf-8"))
    if cat.get("schema")!=2 or (cat.get("width"),cat.get("height"))!=(30,32):
        raise ValueError("Expected Castle GIF Library schema 2 (30x32)")
    errors=[];checked=0;pairs=0
    def asset(filename,sha):
        p=(root/filename).resolve()
        if root not in p.parents:raise ValueError("Escaping root: "+filename)
        if not p.is_file():raise ValueError("Missing "+filename)
        data=p.read_bytes()
        if hashlib.sha256(data).hexdigest()!=sha:raise ValueError("Bad sha256 "+filename)
        return p,len(data)
    for item in cat["items"]:
        try:
            preview,_=asset(item["preview"]["file"],item["preview"]["sha256"])
            with Image.open(preview) as image:
                if image.size!=(30,32):raise ValueError("Preview size")
            recorded={}
            for v in item["variants"]:
                p,size=asset(v["file"],v["sha256"])
                if size!=v["sizeBytes"] or size>1_000_000:raise ValueError("Bad GIF size")
                with Image.open(p) as im:
                    if im.format!="GIF" or im.size!=(30,32):raise ValueError("Bad GIF format/dimensions")
                    if im.n_frames!=v["frameCount"]:raise ValueError("Bad frameCount")
                    if item["type"]=="animation" and im.info.get("loop")!=0:
                        raise ValueError("Animation must loop indefinitely")
                    frames=[];duration=0
                    for f in range(im.n_frames):
                        im.seek(f)
                        duration+=int(im.info.get("duration",0))
                        frames.append(im.convert("RGB").tobytes())
                    if duration!=v["durationMs"]:raise ValueError("Bad durationMs")
                    speed=v.get("speedPercent")
                    if item["type"]=="animation" and (speed is None or speed%10 or not 10<=speed<=200):
                        raise ValueError("Bad speedPercent")
                    if item["type"]=="image" and speed is not None:raise ValueError("Static speed option")
                    recorded[(v["orientation"],speed)]=frames
                checked+=1
            for (orientation,speed),frames in recorded.items():
                if orientation=="normal" and ("street",speed) in recorded:
                    mirrored=recorded[("street",speed)]
                    if len(frames)!=len(mirrored):raise ValueError("Mirror count differs")
                    for a,b in zip(frames,mirrored):
                        image=Image.frombytes("RGB",(30,32),a)
                        if ImageOps.mirror(image).tobytes()!=b:raise ValueError("Mirror pixel mismatch")
                    pairs+=1
        except Exception as ex:
            errors.append(item.get("id","?")+": "+str(ex))
    report={"items":len(cat["items"]),"gifVariantsVerified":checked,
            "mirrorPairsVerified":pairs,"errors":errors,"status":"PASS" if not errors else "FAIL"}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--library",required=True)
    check(p.parse_args().library)
