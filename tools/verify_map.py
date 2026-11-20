"""Independent contract checks against installed game assets."""
from pathlib import Path
import json, struct, sys, xml.etree.ElementTree as ET
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'IslaMonoMap'
d=json.loads((OUT/'data.json').read_text(encoding='utf-8'))
def labels(rel):
 b=(ROOT/rel).read_bytes(); u=struct.unpack_from('<11I',b); pool=b[72:72+u[2]]
 def name(i): return pool[i:pool.index(b'\0',i)].decode('latin1')
 o=72+u[2]+4*u[3]+4*u[4]+56*u[5]+76*u[6]
 result={}
 for i in range(u[7]):
  q=o+i*108; group,nm,flags=struct.unpack_from('<3I',b,q)
  result[name(nm)]=struct.unpack_from('<3f',b,q+12+48)
 return result
loc=labels('Resource/Models/Islands/IslaMona/IslaMona_locators.gm')
for s in d['shores']:
 x,y,z=loc[s['reload']]; assert abs(x-s['x'])<.001 and abs(z-s['z'])<.001
print('PASS: 3 shore positions match GM locator matrices')
# Relative left/right is invariant under translating/rotating a three-way scene.
def side(a,b,c):
 cx=(a[0]+b[0]+c[0])/3; cz=(a[2]+b[2]+c[2])/3
 vx,vz=cx-a[0],cz-a[2]; wx,wz=c[0]-cx,c[2]-cz
 return vx*wz-vz*wx
for folder,file,entry,left,right in [('Jungle3','jungle3_locators','reload1','reload3','reload2'),('Jungle5','jungle5_locators','reload1','reload2','reload3'),('jungle13','jungle13L_locators','reload1','reload3','reload2')]:
 l=labels(f'Resource/Models/Locations/Outside/Jungles/{folder}/{file}.gm')
 assert side(l[entry],l[right],l[left])>0
print('PASS: turn handedness matches Jungle3, Jungle5 and late-stage Jungle13L')
src=(ROOT/'Program/locations/init/IslaMona.c').read_text(encoding='utf-8-sig')
for a,b in [('Shore75','IslaMona_Jungle_01'),('IslaMona_Jungle_01','IslaMona_town'),('IslaMona_Jungle_02','Shore77'),('IslaMona_Jungle_02','IslaMona_factoria')]:
 block=src.split('locations[n].id = "'+a+'";')[1].split('n = n + 1;')[0]
 assert '"'+b+'"' in block
print('PASS: primary surface connections exist in game source')
with Image.open(OUT/'Isla_Mona.png') as im: assert im.size==(2600,2100); im.verify()
tree=ET.parse(OUT/'Isla_Mona.svg'); ns={'s':'http://www.w3.org/2000/svg'}
texts=' '.join(t.text or '' for t in tree.findall('.//s:text',ns))
for term in ['ИСЛА МОНА','Губернатора','Бухта Вьекес','Утопленника*','Посёлок','Фактория*','18°42′','72°09′']: assert term in texts,term
for el in tree.findall('.//s:image',ns): assert el.attrib['href'].startswith('data:image/png;base64,')
print('PASS: PNG integrity, required labels, coordinates and self-contained SVG')
