#!/usr/bin/env python3
"""Geometry Masters: eight public-domain geometric-art interpretations, 30x32.
Source for Castle Lights / Govee H70B6. No third-party images are embedded.
Each component enters along a deterministic curved trajectory and rotates/scales
into its final coordinate. Prior artwork simultaneously flies apart.
"""
from __future__ import annotations
import json, math, random
from pathlib import Path
from PIL import Image, ImageDraw
W,H=30,32
STEP=16
FRAME_MS=280
ROOT=Path(__file__).resolve().parent
DARK=(2,3,8)
PAPER=(126,122,107)
RED=(227,44,37)
BLUE=(28,68,194)
GOLD=(230,179,36)
BLACK=(8,12,24)
WHITE=(189,188,171)
TEAL=(30,141,131)
ORANGE=(224,91,36)
PINK=(182,85,117)
GREEN=(77,144,87)
PURPLE=(97,64,163)
NAVY=(21,36,81)

def poly(points,color):
    return {"pts":[(float(x),float(y)) for x,y in points],"color":color}
def rec(x,y,w,h,c,ang=0):
    cx,cy=x+w/2,y+h/2
    ps=[(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
    return rotate_poly(ps,cx,cy,ang,c)
def rotate_poly(pts,cx,cy,ang,color):
    a=math.radians(ang);co=math.cos(a);si=math.sin(a)
    return poly([(cx+(x-cx)*co-(y-cy)*si,cy+(x-cx)*si+(y-cy)*co) for x,y in pts],color)
def disk(x,y,r,c,n=24):
    return poly([(x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n)) for i in range(n)],c)
def tri(points,c):
    return poly(points,c)
def bar(x1,y1,x2,y2,width,c):
    dx=x2-x1;dy=y2-y1;L=max(0.01,math.hypot(dx,dy))
    px=-dy/L*width/2;py=dx/L*width/2
    return poly([(x1+px,y1+py),(x2+px,y2+py),(x2-px,y2-py),(x1-px,y1-py)],c)
def ring(cx,cy,r1,r2,start,end,c,n=None):
    if n is None:n=max(4,int(abs(end-start)/11)+1)
    a=[math.radians(start+(end-start)*i/n) for i in range(n+1)]
    ps=[(cx+r2*math.cos(t),cy+r2*math.sin(t)) for t in a]
    ps += [(cx+r1*math.cos(t),cy+r1*math.sin(t)) for t in reversed(a)]
    return poly(ps,c)
def base(c,seed=0):
    # Small independent squares coalesce into one large bounded panel.
    tiles=[]
    for y in range(5):
        for x in range(5):
            factor=((x*7+y*11+seed)%9-4)
            col=tuple(max(0,min(255,v+factor)) for v in c)
            tiles.append(rec(2+x*5.2,2+y*5.6,5.5,5.9,col))
    return tiles
def make_scenes():
    scenes=[]
    # Mondrian 1930: dominant red rectangle, blue and yellow small corners.
    s=base((132,130,115),1)
    s += [rec(10,3,18,19,RED),rec(2,24,8,6,BLUE),rec(26,27,2,3,GOLD)]
    s += [rec(9,2,1.8,28,BLACK),rec(2,22,26,1.8,BLACK),
          rec(2,10,8,1.8,BLACK),rec(25,23,1.8,8,BLACK),
          rec(2,2,26,1,BLACK),rec(2,30,26,1,BLACK)]
    scenes.append(("Piet Mondrian","Composition with Red, Blue and Yellow (1930)",s))
    # Malevich 1916: several bold, tilted suprematist planes.
    s=base((145,144,132),2)
    s += [bar(2,23,28,23,3.2,(29,27,31)),rec(3,2,2.8,12,BLACK,26),
          rec(9,6,5,20,GREEN,22),rec(16,15,12,12,BLUE,32),
          rec(22,5,2,10,GOLD,26),rec(24,6,3.3,4,GOLD,22),
          rec(2,17,2.4,7,BLACK,-29),rec(4,28,5,2.2,ORANGE,26),
          rec(16,3,2,3,BLACK,20),rec(19,4,3,2,BLUE,27),
          bar(13,26,22,8,1.1,ORANGE),rec(13,26,3,2,PINK,-25),
          rec(23,27,6,1.5,GOLD,-10)]
    scenes.append(("Kazimir Malevich","Suprematist Composition (1916)",s))
    # Kandinsky 1923: precise circles, line diagonals and a triangle.
    s=base((125,127,111),3)
    s += [tri([(2,20),(11,30),(2,30)],(89,140,181)),
          bar(2,27,29,7,1.0,BLACK),bar(3,14,29,25,.9,BLACK),
          bar(17,2,21,30,.75,BLACK),bar(3,28,26,4,.65,ORANGE),
          tri([(12,7),(19,2),(17,10)],BLACK),
          tri([(17,11),(22,9),(19,5)],GOLD),
          disk(9,10,3.8,BLACK),disk(9,10,2.6,(175,165,139)),disk(9,10,1.55,RED),
          disk(22,14,5.2,BLACK),disk(22,14,3.9,(212,168,69)),
          disk(22,14,2.9,BLUE),disk(22,14,1.55,BLACK),
          disk(7,27,3.4,GOLD),disk(7,27,2.2,BLUE),
          disk(16,20,2.8,PURPLE),disk(25,26,2.2,(97,104,112)),
          ring(13,13,5.6,6.2,35,167,BLACK),
          bar(2,17,29,17,.7,BLACK),
          rec(25,4,2,2,GOLD),rec(25,4,1,1,BLACK),
          disk(5,7,1,RED)]
    scenes.append(("Wassily Kandinsky","Composition VIII (1923)",s))
    # Klee 1928: mosaic blocks/rooftops with a floating glowing sun.
    s=base((88,36,35),4)
    pal=[(226,129,56),(191,48,49),(222,177,75),(88,142,141),
         (183,104,95),(163,117,61),(51,62,66),(218,91,54),
         (141,93,122),(209,138,89),(209,175,131)]
    rng=random.Random(1912)
    for yy in (14,18,22,26):
        for xx in (3,8,13,18,23):
            s.append(rec(xx,yy,5,4,pal[(xx*3+yy*7)//5%len(pal)]))
    # Tall ramparts
    s += [rec(4,6,5,9,pal[5]),rec(11,3,5,12,pal[2]),rec(21,9,5,7,pal[6]),
          tri([(3,15),(7,11),(11,15)],pal[2]),
          tri([(9,14),(14,8),(19,14)],pal[0]),
          tri([(20,17),(24,12),(28,17)],pal[9]),
          disk(21,6,4.2,(238,173,50))]
    for j in range(10):
        x=3+(j*7)%23;y=13+(j*9)%17
        s.append(rec(x,y,2.2,2.1,pal[j%len(pal)]))
    scenes.append(("Paul Klee","Castle and Sun (1928)",s))
    # Delaunay 1913: slices of concentric suns and overlapping lunar discs.
    s=base((13,30,40),5)
    s += [disk(14,15,14,(26,121,136))]
    cols=[ORANGE,(223,155,52),GOLD,(41,103,177),(94,162,156),(177,58,72),(140,114,143)]
    for j in range(12):
        s.append(ring(14,15,8.7,13.1,j*30,j*30+30,cols[(j*3+1)%len(cols)]))
    for j in range(10):
        s.append(ring(14,15,4.4,8.7,j*36,j*36+36,cols[(j*2+4)%len(cols)]))
    s += [disk(14,15,3.9,(224,201,136)),disk(14,15,2.5,(73,158,151)),
          disk(8,7,5,(210,70,42)),disk(8,7,3.5,GOLD),disk(8,7,2.1,(196,197,175)),
          disk(23,24,5,(237,169,52)),disk(23,24,3.4,(29,95,163)),
          disk(23,24,1.7,ORANGE),disk(24,5,3.2,BLACK)]
    scenes.append(("Robert Delaunay","Circular Forms, Sun and Moon (1913)",s))
    # El Lissitzky 1919: red wedge stabs an open white circular form.
    s=base((123,120,106),6)
    s += [disk(21,19,11,BLACK),disk(21,19,7.5,(172,169,146)),
          tri([(1,9),(5,5),(24,21)],RED),
          tri([(3,8),(5,7),(21,19)],(248,88,45)),
          bar(3,29,14,29,1.0,RED),bar(3,27,12,27,.7,BLACK),
          rec(3,3,2,3,BLACK,-22),rec(7,5,2,1,BLACK,19),
          rec(16,4,3,3,BLACK,45),
          tri([(26,4),(29,4),(28,11)],BLACK),
          bar(19,29,26,28,1.1,RED)]
    scenes.append(("El Lissitzky","Beat the Whites with the Red Wedge (1919)",s))
    # Popova 1917: overlapping constructivist planes.
    s=base((132,113,114),7)
    s += [tri([(2,5),(29,14),(11,31)],(220,64,33)),
          tri([(8,2),(26,2),(19,26)],(39,42,42)),
          tri([(3,26),(7,11),(14,18)],BLACK),
          tri([(15,18),(25,11),(28,23)],(176,172,159)),
          tri([(18,3),(27,3),(22,14)],(91,91,87)),
          tri([(4,6),(12,5),(3,18)],(199,105,128)),
          tri([(17,15),(26,18),(26,26)],(225,218,192)),
          rec(24,4,8,3,(151,35,38),25),
          rec(19,25,11,4,(209,121,133),-12),
          bar(3,29,14,2,3,BLACK)]
    scenes.append(("Lyubov Popova","Painterly Architectonic (1917)",s))
    # Kupka 1912: interlocking red and blue curving ribbons.
    s=base((132,132,126),8)
    s += [disk(26,2,7,BLACK),disk(3,30,9,BLACK)]
    for k in range(12):
        a=k*30
        c=BLUE if k%2==0 else RED
        s.append(ring(13,18,6.3,10.8,a,a+27,c))
    for k in range(8):
        a=k*45
        c=RED if k%2==0 else BLUE
        s.append(ring(23,12,3.1,6.4,a,a+40,c))
    s += [ring(12,20,11.5,13,100,310,RED),
          ring(9,12,8.8,10.3,-110,115,BLUE),
          ring(20,20,8,9.5,-90,120,RED),
          ring(19,16,5.5,7.1,50,300,BLUE),
          tri([(8,30),(14,14),(19,31)],RED),
          tri([(14,5),(20,3),(17,24)],BLUE)]
    scenes.append(("Frantisek Kupka","Amorpha: Fugue in Two Colors (1912)",s))
    return scenes

SCENES=make_scenes()
def lerp(a,b,t):return a+(b-a)*t
def ease(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
def center(pts):
    return sum(x for x,y in pts)/len(pts),sum(y for x,y in pts)/len(pts)
def draw_fragments(draw,frags,scene_idx,phase,exit=False):
    for j,obj in enumerate(frags):
        # Independence and stagger ensure fragments move at the SAME TIME, not in sequence.
        rng=random.Random(scene_idx*20003+j*179+31)
        cx,cy=center(obj["pts"])
        angle=rng.uniform(-170,170)
        radius=rng.uniform(10,25)
        direction=rng.uniform(0,math.tau)
        dx,dy=radius*math.cos(direction),radius*math.sin(direction)
        # Move through a gentle curved path. Retain exact integer target geometry.
        local=max(0,min(1,(phase-(j%7)*0.017)/(.9-(j%7)*0.017)))
        q=ease(local)
        if exit:q=1-q
        scale=.25+.75*q
        rot=math.radians(angle*(1-q))
        cc,ss=math.cos(rot),math.sin(rot)
        ox=dx*(1-q)+math.sin(q*math.pi)*2.3*(j%3-1)
        oy=dy*(1-q)+math.sin(q*math.pi)*2.1*((j+1)%3-1)
        ps=[]
        for x,y in obj["pts"]:
            a=(x-cx)*scale;b=(y-cy)*scale
            ps.append((round(cx+ox+a*cc-b*ss),round(cy+oy+a*ss+b*cc)))
        if len(set(ps))>=3:
            draw.polygon(ps,fill=obj["color"])
def render():
    out=ROOT
    frames_dir=out/"frames"
    frames_dir.mkdir(parents=True,exist_ok=True)
    all_frames=[]
    for index in range(len(SCENES)):
        artist,title,shapes=SCENES[index]
        prev=SCENES[(index-1)%len(SCENES)][2]
        for step in range(STEP):
            im=Image.new("RGB",(W,H),DARK)
            dr=ImageDraw.Draw(im)
            if step<8:
                p=step/7
                draw_fragments(dr,prev,(index-1)%8,p,exit=True)
                draw_fragments(dr,shapes,index,p,exit=False)
            else:
                # Hold artwork perfectly still; no noisy twinkling or "wobble".
                draw_fragments(dr,shapes,index,1.0,exit=False)
            all_frames.append(im)
            im.save(frames_dir/f"frame-{index*STEP+step:03d}.png")
    path=out/"geometry-masters-source.gif"
    all_frames[0].save(path,save_all=True,append_images=all_frames[1:],
        format="GIF",duration=[FRAME_MS]*len(all_frames),loop=0,
        disposal=2,optimize=True)
    # At full scale LED 30x32, and enlarged preview.
    finals=[all_frames[i*STEP+12] for i in range(len(SCENES))]
    sheet=Image.new("RGB",(30*8,32))
    for i,im in enumerate(finals):
        sheet.paste(im,(30*i,0))
        im.save(out/f"painting-{i+1:02d}.png")
    sheet.resize((960,128),Image.Resampling.NEAREST).save(out/"eight-paintings-contact-sheet.png")
    storyboard=Image.new("RGB",(30*8,32*4))
    for i in range(8):
        for row,step in enumerate((0,3,7,12)):
            storyboard.paste(all_frames[i*STEP+step],(i*30,row*32))
    storyboard.resize((960,512),Image.Resampling.NEAREST).save(out/"motion-storyboard.png")
    with Image.open(path) as check:
        assert 8*STEP/2 <= check.n_frames <= 8*STEP, (check.n_frames,8*STEP)
        assert check.size == (W,H)
    manifest={"id":"geometry-masters","artists":[{"artist":a,"work":w,"shapes":len(s)} for a,w,s in SCENES],
      "frames":len(all_frames),"frameMs":FRAME_MS,"durationMs":len(all_frames)*FRAME_MS,
      "artwork":"30x32 LED-friendly geometric reinterpretations",
      "motion":"simultaneous affine translation, rotation and scale with overlap",
      "source":str(path)}
    (out/"geometry-masters.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(manifest,ensure_ascii=False))
if __name__=="__main__":render()
