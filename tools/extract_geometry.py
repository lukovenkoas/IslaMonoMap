"""Extract Storm GM triangle surface, clipping at sea level; no game changes."""
from pathlib import Path
import struct, json, math
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'IslaMonoMap/research'
def read_gm(path):
 b=path.read_bytes(); u=struct.unpack_from('<11I',b); o=72+u[2]+u[3]*4+u[4]*4+u[5]*56+u[7]*108
 objects=[]
 for i in range(u[8]):
  q=o+i*104
  objects.append(struct.unpack_from('<6I',b,q+28))
 t=o+104*u[8]; faces=[struct.unpack_from('<3H',b,t+i*6) for i in range(u[9])]; v=t+6*u[9]
 typ,size=struct.unpack_from('<2I',b,v); stride=36+8*(typ&3)
 vertices=[struct.unpack_from('<3f',b,v+8+i*stride) for i in range(size//stride)]
 print(path.name,'objects',objects,'vb',typ,size,'stride',stride,'vertices',len(vertices))
 assert size%stride==0
 polys=[]
 for _,nt,st,nv,sv,mat in objects:
  assert st+nt<=len(faces) and sv+nv<=len(vertices)
  for face in faces[st:st+nt]:
   assert max(face)<nv
   polys.append([vertices[sv+j] for j in face])
 return polys,vertices
polys,verts=read_gm(ROOT/'Resource/Models/Islands/IslaMona/IslaMona.gm')
# Clip each triangle against y=0.05 to exclude the coplanar sea-bed rim.
def clip(poly):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[1]>.05; ib=b[1]>.05
  if ia: out.append(a)
  if ia!=ib:
   t=(.05-a[1])/(b[1]-a[1]); out.append(tuple(a[k]+t*(b[k]-a[k]) for k in range(3)))
 return out
land=[clip(p) for p in polys]; land=[p for p in land if len(p)>2]
# fixed equal-scale projection x east, z up
bounds=[-800,-1800,1700,1900]
def project(p): return (80+(p[0]+800)*.30,80+(1900-p[2])*.30)
im=Image.new('RGB',(910,1270),'#cee0df'); d=ImageDraw.Draw(im)
for p in land:
 h=sum(v[1] for v in p)/len(p); c=(int(181-h*.15),int(189-h*.20),int(133-h*.13))
 d.polygon([project(v) for v in p],fill=c)
for name,x,z in [('75',323.495,164.469),('76',1255.541,-44.396),('77',792.049,1330.770)]:
 q=project((x,0,z)); d.ellipse((q[0]-6,q[1]-6,q[0]+6,q[1]+6),fill='red'); d.text(q,name,fill='black')
im.save(OUT/'geometry_preview.png')
(OUT/'geometry.json').write_text(json.dumps({'land':land,'bounds':bounds}),encoding='utf-8')
print('PASS: all triangle and vertex ranges valid; clipped land triangles',len(land))
