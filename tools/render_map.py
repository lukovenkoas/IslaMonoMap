"""Reproducible map: model-derived relief, editable vector annotations, PNG export."""
from pathlib import Path
import json, math, random, html, base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'IslaMonoMap'
D=json.loads((OUT/'data.json').read_text(encoding='utf-8'))
G=json.loads((OUT/'research/geometry.json').read_text())
W,H=2600,2100
INK='#3d382c'; SEA='#d5dfd2'; LAND='#babd85'; RED='#914e35'; ROAD='#875b35'
im=Image.new('RGB',(W,H),'#e8dfc4'); draw=ImageDraw.Draw(im)
svg=[]
def font(size,bold=False,italic=False):
 name='georgia'+('b' if bold else 'i' if italic else '')+'.ttf'
 return ImageFont.truetype('C:/Windows/Fonts/'+name,size)
def line(points,fill=INK,width=2,dash=False):
 if not dash: draw.line(points,fill=fill,width=width,joint='curve')
 else:
  for a,b in zip(points,points[1:]):
   dist=math.dist(a,b)
   for k in range(0,int(dist),22):
    t=k/dist; u=min((k+12)/dist,1)
    draw.line([(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t),(a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u)],fill=fill,width=width)
 svg.append(f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in points)}" fill="none" stroke="{fill}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"'+(' stroke-dasharray="12 10"' if dash else '')+'/>')
def text(x,y,t,size=28,bold=False,italic=False,fill=INK,anchor='la'):
 f=font(size,bold,italic); draw.text((x,y),t,font=f,fill=fill,anchor=anchor,stroke_width=0)
 # PIL ascender anchor differs from SVG baseline: use text bbox for reliable placement.
 box=draw.textbbox((x,y),t,font=f,anchor=anchor)
 svg.append(f'<text x="{box[0]}" y="{box[1]+f.getbbox(t)[3]-f.getbbox(t)[1]}" font-family="Georgia" font-size="{size}" font-weight="{"bold" if bold else "normal"}" font-style="{"italic" if italic else "normal"}" fill="{fill}">{html.escape(t)}</text>')
def circle(x,y,r,fill,outline=INK,width=2):
 draw.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=outline,width=width)
 svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{outline}" stroke-width="{width}"/>')
def rect(box,fill,outline=None,width=1):
 draw.rectangle(box,fill=fill,outline=outline,width=width)
 x,y,x2,y2=box; svg.append(f'<rect x="{x}" y="{y}" width="{x2-x}" height="{y2-y}" fill="{fill}" stroke="{outline or "none"}" stroke-width="{width}"/>')
def P(x,z): return (400+(x+680)*.39,390+(1732-z)*.39)
# Map field, real equal-scale relief and coastline.
base=Image.new('RGB',(W,H),SEA); bd=ImageDraw.Draw(base)
mask=Image.new('L',(W,H)); md=ImageDraw.Draw(mask)
for poly in G['land']:
 pts=[P(p[0],p[2]) for p in poly]
 h=sum(v[1] for v in poly)/len(poly)
 a,b,c=poly[:3]; ux,uy,uz=[b[k]-a[k] for k in range(3)]; vx,vy,vz=[c[k]-a[k] for k in range(3)]
 nx,ny,nz=uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx
 if ny<0: nx,ny,nz=-nx,-ny,-nz
 norm=math.sqrt(nx*nx+ny*ny+nz*nz) or 1
 shade=(nx*-.5+ny*.7+nz*.5)/norm
 col=tuple(max(0,min(255,int(q-h*.13+shade*20))) for q in (173,178,120))
 bd.polygon(pts,fill=col); md.polygon(pts,fill=255)
# Only mask coastline edges: no triangulation lines in finished art.
outer=mask.filter(ImageFilter.MaxFilter(25)); halo=Image.new('RGB',(W,H),'#a6c1b5'); base.paste(halo,(0,0),outer); 
# Restore land from second relief render (halo operation covered it).
for poly in G['land']:
 pts=[P(p[0],p[2]) for p in poly]; h=sum(v[1] for v in poly)/len(poly)
 a,b,c=poly[:3]; u=[b[k]-a[k] for k in range(3)]; v=[c[k]-a[k] for k in range(3)]
 n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
 if n[1]<0: n=[-q for q in n]
 norm=math.sqrt(sum(q*q for q in n)) or 1; shade=sum(q*s for q,s in zip(n,[-.5,.7,.5]))/norm
 bd.polygon(pts,fill=tuple(max(0,min(255,int(q-h*.13+shade*20))) for q in (173,178,120)))
edge=Image.eval(mask.filter(ImageFilter.MaxFilter(5)),lambda a:a)
# coast outline from morphological mask difference
from PIL import ImageChops
edge=ImageChops.subtract(edge,mask.filter(ImageFilter.MinFilter(3)))
base.paste('#6b7151',(0,0),edge)
# Map only occupies left field; image embedded as a separate layer in SVG.
base=base.crop((120,320,1670,1830)); base.save(OUT/'island_base.png')
im.paste(base,(120,320))
svg.append('<image id="model-derived-coast-and-relief" x="120" y="320" width="1550" height="1510" href="data:image/png;base64,'+base64.b64encode((OUT/'island_base.png').read_bytes()).decode()+'"/>')
# Border / typography
rect((42,42,W-42,H-42),'none' if False else '#e8dfc4') if False else None
for inset,width in [(40,4),(54,1),(78,2)]: line([(inset,inset),(W-inset,inset),(W-inset,H-inset),(inset,H-inset),(inset,inset)],width=width)
text(125,104,'КАРТА ТАЙНОЙ БАЗЫ',25,bold=True,fill=RED)
text(120,150,'ИСЛА МОНА',100,bold=True)
text(125,270,'18°42′ с. ш.   ·   72°09′ з. д.',32)
text(2450,142,'CARIBBEAN LEGEND',27,anchor='ra')
text(2450,191,'Берег — по модели острова',25,anchor='ra',italic=True)
text(2450,232,'Названия и переходы — по ресурсам игры',25,anchor='ra',italic=True)
# Very restrained rhumb lines in water only, not over the land.
for y in (470,850,1230,1610):
 line([(140,y),(340,y)],fill='#adb4a1',width=1)
# Compass
a,b=265,530
for dx,dy in [(0,-100),(60,0),(0,80),(-60,0)]: line([(a,b),(a+dx,b+dy)],width=2)
line([(a-13,b-42),(a,b-100),(a+13,b-42),(a,b-55),(a-13,b-42)],fill=RED,width=3)
circle(a,b,13,'#e8dfc4'); text(a,b-142,'С',29,bold=True,anchor='ma');text(a+82,b-13,'В',24,anchor='ma');text(a,b+88,'Ю',24,anchor='ma');text(a-82,b-13,'З',24,anchor='ma')
# Roads: location graph embedded schematically on model surface.
coords={k:P(*v) for k,v in D['layout'].items() if isinstance(v,list)}
coords.update({s['id']:P(s['x'],s['z']) for s in D['shores']})
def road(points,underground=False):
 if not underground: line(points,fill='#e9d5a3',width=15)
 line(points,fill=RED if underground else ROAD,width=4,dash=underground)
j1=coords['J1']; j2=coords['J2']; town=coords['Town']; fac=coords['Factoria']
road([coords['Shore75'],(832,962),j1]);road([j1,(975,880),town]);road([j1,(940,815),(925,735),j2]);road([j2,(985,625),coords['Shore77']]);road([j2,fac])
road([coords['Shore76'],coords['CaveEntrance'],coords['Cave']]);road([coords['Cave'],(1120,960),(1130,875),town],True)
for name,q in [('1',j1),('2',j2)]: circle(*q,20,'#f0e4c4',ROAD,3);text(q[0],q[1]-19,name,27,bold=True,anchor='ma')
def settlement(q):
 x,y=q
 for dx,dy in [(-22,-15),(12,-10),(-4,20)]:
  rect((x+dx-10,y+dy-8,x+dx+10,y+dy+12),'#eee0bc',INK,2)
  line([(x+dx-14,y+dy-8),(x+dx,y+dy-21),(x+dx+14,y+dy-8)],fill=RED,width=4)
settlement(town)
text(town[0]+42,town[1]-23,'Посёлок',33,bold=True);text(town[0]+42,town[1]+21,'Форт в джунглях',22,italic=True)
# Factor fields
x,y=fac
for i in range(5): line([(x-28+i*12,y-25),(x-28+i*12,y+25)],fill='#66744b',width=4)
text(x-80,y+42,'Фактория*',29,bold=True)
# Cave glyph
x,y=coords['Cave'];circle(x,y,13,'#454336');text(x-62,y+26,'Пещера',27,bold=True)
# Shore labels and leader lines, the points are mooring locators, not fabricated beach centres.
for sid,labelpos,lines in [('Shore75',(200,1050),['Бухта','Губернатора']),('Shore77',(1140,470),['Бухта Вьекес']),('Shore76',(1260,1120),['Мыс','Утопленника*'])]:
 q=coords[sid];circle(*q,8,'#f5ead0',RED,3)
 x,y=labelpos; line([q,(x+25,y-10)],fill=RED,width=2)
 for i,t in enumerate(lines):text(x,y+i*40,t,33,bold=True)
text(160,1740,'Береговой контур и рельеф извлечены из 3D-модели.',22)
text(160,1775,'Дороги и положение внутренних объектов — условная схема.',22)
# Right-hand navigation panel
line([(1700,350),(1700,1840)],fill='#94856a',width=2)
text(1760,350,'ПУТИ К ПОСЁЛКУ',36,bold=True)
text(1760,415,'От бухты Губернатора',31,bold=True)
text(1760,465,'На развилке 1 — налево.',29,fill=RED)
text(1760,525,'От бухты Вьекес',31,bold=True)
text(1760,575,'На развилке 2 — налево,',29,fill=RED)
text(1760,617,'на развилке 1 — направо.',29,fill=RED)
text(1760,696,'СХЕМЫ РАЗВИЛОК',28,bold=True)
# Inset diagrams are rotated so arrival from the named bay is at bottom.
def junction(cx,cy,num,left,right,bottom):
 line([(cx,cy+92),(cx,cy),(cx-160,cy-85)],fill=ROAD,width=7)
 line([(cx,cy),(cx+160,cy-85)],fill=ROAD,width=7)
 circle(cx,cy,21,'#f0e4c4',ROAD,3);text(cx,cy-20,str(num),29,bold=True,anchor='ma')
 text(cx-165,cy-138,left,23,anchor='ma');text(cx+165,cy-138,right,23,anchor='ma')
 text(cx,cy+106,bottom,24,anchor='ma',italic=True)
junction(2100,930,1,'К посёлку','К развилке 2','Вход от бухты Губернатора')
junction(2100,1210,2,'К развилке 1','К фактории*','Вход от бухты Вьекес')
text(1760,1380,'От мыса Утопленника*',29,bold=True)
text(1760,1430,'Пещера — подвал — дом в посёлке.',25)
text(1760,1470,'Это подземный путь, не лесная дорога.',24,italic=True)
line([(1760,1540),(1840,1540)],fill=ROAD,width=5);text(1870,1523,'Наземные переходы',25)
line([(1760,1600),(1840,1600)],fill=RED,width=4,dash=True);text(1870,1583,'Подземный проход',25)
text(1760,1660,'* Доступность зависит от этапа квестов.',23)
text(1760,1710,'Повороты восстановлены по моделям',23)
text(1760,1745,'локаторов; прохождение в игре',23)
text(1760,1780,'отдельно не проверялось.',23)
# Footer: explicit accuracy without fake cartographic grid values.
line([(125,1880),(2475,1880)],fill='#94856a',width=2)
text(125,1920,'ТРИ МЕСТА ВЫСАДКИ · ДВЕ ЛЕСНЫЕ РАЗВИЛКИ · ТАЙНАЯ БАЗА',30,bold=True)
text(125,1980,'Координаты — из квестового журнала. Карта показывает связи локаций, а не длину пути.',24)
im.save(OUT/'Isla_Mona.png',dpi=(200,200))
# SVG keeps every label, route and symbol editable; base relief is an embedded image.
(OUT/'Isla_Mona.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="2600" height="2100" viewBox="0 0 2600 2100"><title>Исла Мона — карта острова и маршруты</title><rect width="2600" height="2100" fill="#e8dfc4"/>'+''.join(svg)+'</svg>',encoding='utf-8')
im.resize((1300,1050),Image.Resampling.LANCZOS).save(OUT/'preview.jpg',quality=94)
print('PASS: PNG 2600x2100; SVG self-contained; preview 1300x1050')
