"""Original engraved-style illustration; coastline from the extracted game geometry.
No reference-map pixels are used. Symbols and vegetation are decorative.
"""
from pathlib import Path
import json, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
OUT=Path(__file__).resolve().parents[1]
G=json.loads((OUT/'research/geometry.json').read_text())
D=json.loads((OUT/'data.json').read_text(encoding='utf-8'))
W,H=2400,2700
rng=random.Random(1729)
INK='#433b29'; RED='#895139'; PAPER='#e3d5ac'
im=Image.new('RGB',(W,H),PAPER); dr=ImageDraw.Draw(im)
def font(s,italic=False,bold=False):
 return ImageFont.truetype('C:/Windows/Fonts/georgia'+('b' if bold else 'i' if italic else '')+'.ttf',s)
def txt(x,y,t,s=36,italic=False,bold=False,anchor='ma'):
 dr.text((x,y),t,font=font(s,italic,bold),fill=INK,anchor=anchor,stroke_width=2,stroke_fill=PAPER)
def ln(p,c=INK,w=2): dr.line(p,fill=c,width=w,joint='curve')
def P(x,z): return (650+(x+680)*.50,430+(1732-z)*.50)
def T(p): return (650+(p[0]-400)/.39*.50,430+(p[1]-390)/.39*.50)
mask=Image.new('L',(W,H)); md=ImageDraw.Draw(mask)
for poly in G['land']: md.polygon([P(v[0],v[2]) for v in poly],fill=255)
# Sea rhumbs and ornamental frame: intentionally no invented geographic grid.
for ox,oy in [(310,760),(2080,2120)]:
 for a in range(0,360,15):
  r=math.radians(a); ln([(ox+math.cos(r)*70,oy+math.sin(r)*70),(ox+math.cos(r)*3500,oy+math.sin(r)*3500)],'#a8a181',1)
for x in range(200,2400,350): ln([(x,64),(x,H-64)],'#b8ad88',1)
for y in range(350,2600,350): ln([(64,y),(W-64,y)],'#b8ad88',1)
def spread(size, inward=False):
 small=mask.resize((W//3,H//3),Image.Resampling.NEAREST)
 n=max(3,(size//3)|1)
 return small.filter(ImageFilter.MinFilter(n) if inward else ImageFilter.MaxFilter(n)).resize((W,H),Image.Resampling.BILINEAR)
# Concentric engraved waterline, sand coast, inner wash. Original mask is unchanged.
for size,col in [(65,'#bcc1a5'),(49,'#a4b29b'),(31,'#7e9587'),(15,'#506c62')]:
 im.paste(col,(0,0),spread(size))
# Thin broken tidal hatching outside coast.
outer=spread(77); inner=spread(19)
water=ImageChops.subtract(outer,inner)
hatch=Image.new('L',(W,H)); hd=ImageDraw.Draw(hatch)
for y in range(0,H,7): hd.line([(0,y),(W,y)],fill=120,width=1)
im.paste('#46665f',(0,0),ImageChops.multiply(water,hatch))
im.paste('#ae7652',(0,0),mask)
im.paste('#d3ae77',(0,0),spread(13,True))
im.paste('#c8c28c',(0,0),spread(35,True))
# Soft ochre highland washes from actual vertex elevations, not triangle edges.
washes=Image.new('RGBA',(W,H)); wd=ImageDraw.Draw(washes)
for poly in G['land'][::7]:
 h=sum(v[1] for v in poly)/len(poly)
 if h>45:
  x,y=P(sum(v[0] for v in poly)/len(poly),sum(v[2] for v in poly)/len(poly))
  wd.ellipse((x-22,y-18,x+22,y+18),fill=(140,117,63,24))
washes=washes.filter(ImageFilter.GaussianBlur(18)); washes.putalpha(ImageChops.multiply(washes.getchannel('A'),mask))
im=Image.alpha_composite(im.convert('RGBA'),washes).convert('RGB'); dr=ImageDraw.Draw(im)
coords={k:P(*v) for k,v in D['layout'].items() if isinstance(v,list)}
coords.update({s['id']:P(s['x'],s['z']) for s in D['shores']})
j1,j2,town,fac=[coords[k] for k in ('J1','J2','Town','Factoria')]
roads=[[coords['Shore75'],T((832,962)),j1],[j1,T((975,880)),town],[j1,T((940,815)),T((925,735)),j2],[j2,T((985,625)),coords['Shore77']],[j2,fac],[coords['Shore76'],coords['CaveEntrance'],coords['Cave']]]
reserved=[(town[0]-100,town[1]-125,town[0]+210,town[1]+100),(fac[0]-115,fac[1]-100,fac[0]+115,fac[1]+125)]
def segdist(p,a,b):
 v=(b[0]-a[0],b[1]-a[1]); t=max(0,min(1,((p[0]-a[0])*v[0]+(p[1]-a[1])*v[1])/(v[0]**2+v[1]**2 or 1)))
 return math.dist(p,(a[0]+t*v[0],a[1]+t*v[1]))
def free(x,y,r=35):
 if not (r<x<W-r and r<y<H-r): return False
 if any(mask.getpixel((int(x+dx),int(y+dy)))==0 for dx,dy in [(0,0),(-r,0),(r,0),(0,-r),(0,r)]): return False
 if any(a-r<x<c+r and b-r<y<d+r for a,b,c,d in reserved): return False
 return all(segdist((x,y),a,b)>r+14 for road in roads for a,b in zip(road,road[1:]))
def tree(x,y,s):
 # Individually inked canopies and forked trunks, with coloured shadow.
 dr.ellipse((x-s*.6,y-3,x+s*.7,y+5),fill='#aba777')
 ln([(x,y+3),(x,y-s*.9)],'#625637',2)
 ln([(x,y-s*.3),(x-s*.35,y-s*.8)],'#625637',2)
 for dx,dy,r in [(-.32,-.95,.43),(.25,-1.02,.47),(0,-1.35,.45)]:
  dr.ellipse((x+(dx-r)*s,y+(dy-r)*s,x+(dx+r)*s,y+(dy+r)*s),fill=rng.choice(['#7d8a56','#8d965e','#9ca26b']),outline='#5b6342',width=2)
 ln([(x-s*.27,y-s*1.4),(x,y-s*1.6)],'#c2c28b',2)
def mountain(x,y,s):
 # Broken ridgelines and contour hatching, rather than identical triangular peaks.
 ridge=[(-1.28,.32),(-.91,.13),(-.72,-.15),(-.57,-.20),(-.38,-.53),(-.24,-.58),(-.08,-1.03),(.04,-.93),(.19,-.69),(.29,-.62),(.47,-.34),(.64,-.24),(.77,.06),(1.17,.30)]
 ridge=[(x+s*a,y+s*(b+rng.uniform(-.065,.065))) for a,b in ridge]
 base=[(x+s*.73,y+s*.47),(x+s*.12,y+s*.37),(x-s*.52,y+s*.43)]
 dr.polygon(ridge+base,fill=rng.choice(['#b29b64','#bba572','#c0aa78']))
 peak=ridge[6]
 fold=[peak,(x+s*.10,y-s*.45),(x-s*.03,y-s*.13),(x+s*.22,y+s*.07),(x+s*.12,y+s*.37)]
 dr.polygon(fold+ridge[7:]+base[:2],fill='#967748')
 ln(ridge,'#705735',2); ln(fold,'#775f3b',2)
 for i in range(13):
  t=i/13; ax=x+s*(.09+t*.67); ay=y+s*(-.83+t*.96)
  ln([(ax,ay),(ax+s*.08,ay+s*.13),(ax+s*.13,ay+s*.23),(ax+s*.28,ay+s*.30)],'#735b39',1)
 for i in range(6):
  ax=x-s*(.64-i*.085); ay=y+s*(.10-i*.12)
  ln([(ax,ay),(ax-s*.16,ay+s*.21),(ax-s*.29,ay+s*.26)],'#e1cc94',2)
 for i in range(3):
  ln([(x-s*(1.12-i*.12),y+s*(.45+i*.07)),(x+s*(.9-i*.16),y+s*(.43+i*.07))],'#9c8c5e',1)
# Highlands sampled from the model, then sparse original engraved symbols.
peaks=[]
for poly in sorted(G['land'],key=lambda p:-sum(v[1] for v in p)/len(p)):
 h=sum(v[1] for v in poly)/len(poly)
 if h<45: break
 x,y=P(sum(v[0] for v in poly)/len(poly),sum(v[2] for v in poly)/len(poly))
 if free(x,y,62) and all(math.dist((x,y),p)>110 for p in peaks): peaks.append((x,y))
 if len(peaks)>=20: break
for x,y in sorted(peaks,key=lambda p:p[1]): mountain(x,y,rng.uniform(42,68))
for _ in range(1800):
 x,y=rng.randrange(700,2000),rng.randrange(430,2370)
 if free(x,y,22) and all(math.dist((x,y),p)>85 for p in peaks): tree(x,y,rng.uniform(11,20))
# The roads remain readable over ornament; doubled ink edges resemble old map tracks.
for path in roads:
 ln(path,'#6e6746',17); ln(path,'#eee0ae',12)
 for a,b in zip(path,path[1:]):
  dist=math.dist(a,b)
  for k in range(0,int(dist),19):
   t=k/dist; u=min((k+9)/dist,1)
   ln([(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t),(a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u)],'#7d704b',2)
# Subterranean route is explicitly dashed, never a surface road.
path=[coords['Cave'],T((1120,960)),T((1130,875)),town]
for a,b in zip(path,path[1:]):
 dist=math.dist(a,b)
 for k in range(0,int(dist),24):
  t=k/dist; u=min((k+11)/dist,1); ln([(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t),(a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u)],RED,3)
def house(x,y,s=22):
 dr.polygon([(x-s,y),(x,y-s*.4),(x+s,y),(x+s,y+s),(x,y+s*1.35),(x-s,y+s)],fill='#dfcda2',outline=INK)
 dr.polygon([(x-s*1.15,y),(x,y-s),(x+s*1.15,y),(x,y+s*.3)],fill='#9b6344',outline=INK)
 ln([(x,y+s*.3),(x,y+s*1.35)],INK,2)
 dr.rectangle((x+s*.35,y+s*.4,x+s*.62,y+s*.9),fill='#665439')
x,y=town
for dx,dy in [(-42,-25),(15,-42),(60,-3),(-10,20),(40,45)]: house(x+dx,y+dy,20)
txt(x+15,y+82,'Посёлок',38,italic=True)
x,y=fac
for i in range(6):
 ln([(x-65+i*17,y-35),(x-42+i*17,y+22)],'#637249',3)
 ln([(x-62+i*17,y-36),(x-39+i*17,y+21)],'#b1b57c',2)
house(x+40,y-50,27); txt(x,y+65,'Фактория*',34,italic=True)
x,y=coords['Cave']
dr.pieslice((x-25,y-30,x+25,y+20),180,360,fill='#8c7954',outline=INK,width=3)
dr.ellipse((x-13,y-16,x+13,y+3),fill='#403d2e'); txt(x-20,y+30,'Пещера',30,italic=True)
# Mooring anchors are drawn, not font glyphs, for predictable output.
def anchor(x,y):
 dr.ellipse((x-6,y-36,x+6,y-24),outline=INK,width=3)
 ln([(x,y-24),(x,y+25)],INK,4); ln([(x-17,y-15),(x+17,y-15)],INK,3)
 dr.arc((x-26,y-15,x+26,y+34),0,180,fill=INK,width=4)
 ln([(x-26,y+9),(x-29,y-3),(x-16,y+4)],INK,3); ln([(x+26,y+9),(x+29,y-3),(x+16,y+4)],INK,3)
# Decorative sandy landing accents are clipped inside the unaltered coastline.
beach=Image.new('RGB',(W,H),'#ead7a1'); bm=Image.new('L',(W,H)); bmd=ImageDraw.Draw(bm)
for s in D['shores']:
 x,y=coords[s['id']]; bmd.ellipse((x-42,y-42,x+42,y+42),fill=255)
im.paste(beach,(0,0),ImageChops.multiply(bm,mask)); dr=ImageDraw.Draw(im)
for sid,apos,lpos,lines in [('Shore75',(660,1270),(445,1350),['Бухта','Губернатора']),('Shore77',(1510,665),(1800,530),['Бухта Вьекес']),('Shore76',(1800,1380),(2010,1450),['Мыс','Утопленника*'])]:
 q=coords[sid]; anchor(*apos); ln([q,apos],'#7b6847',2)
 for i,t in enumerate(lines): txt(lpos[0],lpos[1]+i*43,t,38,italic=True)
# Compass and original decorative vignette in the empty sea.
cx,cy=345,1900
for i in range(16):
 a=i*math.pi/8; r=108 if i%4==0 else 77 if i%2==0 else 52
 pts=[(cx,cy),(cx+math.cos(a-.12)*28,cy+math.sin(a-.12)*28),(cx+math.cos(a)*r,cy+math.sin(a)*r),(cx+math.cos(a+.12)*28,cy+math.sin(a+.12)*28)]
 dr.polygon(pts,fill=RED if i%2==0 else '#667c65',outline=INK)
dr.ellipse((cx-33,cy-33,cx+33,cy+33),fill=PAPER,outline=INK,width=3)
for dx,dy,t in [(0,-150,'С'),(150,-18,'В'),(0,120,'Ю'),(-150,-18,'З')]: txt(cx+dx,cy+dy,t,28)
# Frame and title cartouche, no false scale bar or fabricated coordinates.
for inset,c,w in [(38,INK,4),(52,RED,8),(66,INK,2),(80,INK,1)]: dr.rectangle((inset,inset,W-inset,H-inset),outline=c,width=w)
for x in range(85,W-85,38): ln([(x,43),(x+18,43)],'#e8d5a7',3)
txt(1200,115,'Карта тайного острова',38,italic=True)
txt(1200,178,'ИСЛА МОНА',102,bold=True)
txt(1200,310,'18°42′ с. ш.     ·     72°09′ з. д.',34)
ln([(850,375),(1550,375)],RED,2)
txt(1200,2440,'CARIBBEAN LEGEND',26)
txt(1200,2490,'Берег — по модели острова; дороги и внутренние объекты — условно.',25,italic=True)
txt(1200,2532,'Горы и деревья — художественные знаки. Пунктир — подземный путь.',25,italic=True)
txt(1200,2574,'* Доступность зависит от квеста. Повороты — на технической карте.',25,italic=True)
# Fine deterministic paper grain and broad uneven wash; generated, not sampled.
noise=Image.effect_noise((W,H),11).convert('RGB'); im=Image.blend(im,noise,.055)
cloud=Image.effect_noise((300,338),35).resize((W,H),Image.Resampling.BICUBIC).convert('RGB')
im=Image.blend(im,cloud,.035)
im.save(OUT/'Isla_Mona_art.png',dpi=(240,240))
im.resize((960,1080),Image.Resampling.LANCZOS).save(OUT/'art_preview.jpg',quality=94)
print('PASS: original illustrated PNG 2400x2700; model-derived coast; 3 landing anchors')
