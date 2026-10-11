from PIL import Image, ImageDraw
from pathlib import Path

ROOT = Path(r"D:\Project\CastleGovee\artwork\svetlogorsk-tower")
ROOT.mkdir(parents=True,exist_ok=True)
W,H = 30,32
C = {'off':'#02050b','air':'#091426','roof_dark':'#51291f','roof':'#df7042','roof_light':'#ffa261','ridge':'#ffd19a','stone_dark':'#303235','stone':'#79756b','stone_light':'#c0b7a5','white':'#f3efe3','glass':'#131f2a','glass_light':'#79b8c1','gold':'#f9d27b','foliage':'#246a4a','grass':'#466f50','sand':'#68634c','heart':'#f88f71','wall_edge':'#ad6045','moon':'#ffe4a0','star':'#d7edff','dim_star':'#6099be'}

def art(style='outline'):
    im=Image.new('RGB',(W,H),C['off']); d=ImageDraw.Draw(im)
    def poly(pts,fill,outline=None):d.polygon(pts,fill=C[fill] if fill else None,outline=C[outline] if outline else None,width=1)
    def line(pts,color,width=1):d.line(pts,fill=C[color],width=width)
    def rect(box,color):d.rectangle(box,fill=C[color])
    if style=='hybrid':
        # Deep night remains largely unlit; tiny stars read as isolated LEDs through tulle.
        for x,y,col in [(18,2,'star'),(27,1,'dim_star'),(20,11,'dim_star'),(28,11,'star'),(18,9,'dim_star')]:
            d.point((x,y),fill=C[col])
        # Crescent in the free upper-right area. Pixel-drawn, not resized photography.
        d.ellipse((22,3,28,9),fill=C['moon'])
        d.ellipse((24,1,29,7),fill=C['off'])
        d.point((23,8),fill=C['moon'])
    poly([(5,14),(15,14),(15,30),(5,30)],'stone_dark' if style in ('outline','hybrid') else 'stone','wall_edge' if style=='hybrid' else 'stone_light')
    if style=='mosaic':
        rect((7,16,9,28),'stone_dark');rect((12,16,13,28),'stone_dark')
    # Warm brown high-tower side piers free the white architectural gallery to stand out.
    side_color='wall_edge' if style=='hybrid' else 'stone_light'
    line([(6,17),(6,27)],side_color);line([(14,16),(14,26)],side_color)
    d.ellipse((8,17,12,21),outline=C['white'],width=1); d.point((10,19),fill=C['gold'])
    line([(10,17),(10,16)],'white');line([(5,14),(15,14)],'white')
    for x in (6,9,12,14):d.arc((x-1,13,x+1,16),0,180,fill=C['white'])
    rect((5,9,15,13),'glass')
    line([(5,9),(15,9)],'white');line([(5,13),(15,13)],'white')
    for x in (5,7,10,13,15):line([(x,9),(x,13)],'white')
    d.point((11,10),fill=C['glass_light'])
    poly([(4,8),(5,6),(7,4),(9,3),(11,3),(13,5),(16,8),(16,9),(4,9)],'roof_dark' if style=='outline' else 'roof','roof_light')
    line([(5,8),(8,5),(10,4),(13,6),(15,8)],'roof_light')
    line([(10,3),(10,1)],'white');d.point((10,0),fill=C['gold']);line([(4,9),(16,9)],'ridge')
    poly([(16,22),(18,19),(20,17),(23,16),(26,18),(29,22),(29,25),(16,25)],'roof_dark' if style=='outline' else 'roof','roof_light')
    line([(16,22),(18,19),(20,17),(23,16),(26,18),(29,22)],'roof_light')
    line([(23,16),(23,13)],'white');d.point((23,12),fill=C['gold'])
    d.arc((18,20,22,23),180,360,fill=C['white']); d.arc((24,20,28,23),180,360,fill=C['white'])
    d.point((20,22),fill=C['glass_light']);d.point((26,22),fill=C['glass_light'])
    poly([(16,25),(29,25),(29,30),(15,30)],'stone_dark' if style in ('outline','hybrid') else 'stone','stone_light')
    line([(17,25),(28,25)],'ridge')
    for x in (20,26):
        d.arc((x-2,25,x+2,29),180,360,fill=C['white'])
        line([(x-2,27),(x-2,29)],'white');line([(x+2,27),(x+2,29)],'white')
        line([(x,26),(x,29)],'white');line([(x-2,29),(x+2,29)],'white')
        d.point((x-1,28),fill=C['glass_light'])
    poly([(13,27),(17,26),(27,26),(29,27),(29,29),(13,29)],'roof_dark' if style=='outline' else 'roof','roof_light')
    line([(14,28),(28,28)],'ridge')
    line([(16,29),(16,31)],'stone_light');line([(27,29),(27,31)],'stone_light')
    rect((21,29,23,31),'glass')
    line([(3,31),(29,31)],'stone_dark' if style=='outline' else 'stone_light')
    return im

if __name__=='__main__':
    for style in ('outline','mosaic','hybrid'):
        im=art(style)
        im.save(ROOT/f'tower_{style}_30x32.png')
        im.resize((420,448),Image.Resampling.NEAREST).save(ROOT/f'tower_{style}_preview.png')
        print('CREATED',style,'distinct colors',len(set(im.get_flattened_data())))
