"""Read-only extraction of game assets; writes previews only inside IslaMonoMap."""
from pathlib import Path
import struct, io, sys, json
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'IslaMonoMap' / 'research'
OUT.mkdir(parents=True, exist_ok=True)
def tx(p):
    b=p.read_bytes(); _,w,h,m,f,size=struct.unpack('<IIII4sI',b[:24]); data=b[24:24+size]
    if struct.unpack('<I',f)[0]==21: return Image.frombytes('RGBA',(w,h),data,'raw','BGRA')
    hdr=struct.pack('<4sIIIIIII44xII4s20xI16x',b'DDS ',124,0x81007,h,w,size,0,1,32,4,f,0x1000)
    return Image.open(io.BytesIO(hdr+data)).convert('RGBA')
tx(ROOT/'Resource/Textures/Islands/IslaMona/IslaMonaMask.tga.tx').save(OUT/'island_mask.png')
for name in ['Dominica','Barbados']:
    p=ROOT/'Resource/Textures/Interfaces/Maps/russian'/f'{name}.tga.tx'
    im=tx(p); im.save(OUT/f'{name}.png'); print(name,im.size)
p=ROOT/'Resource/foam/islands/IslaMona.tga'
try:
    im=Image.open(p); print('foam',im.size,im.mode); im.save(OUT/'depth.png')
except Exception as e: print('foam error',e)
for rel in ['Resource/Models/Islands/IslaMona/IslaMona.gm','Resource/Models/WorldMap/islands/IslaMona.gm']:
    b=(ROOT/rel).read_bytes(); print(rel,len(b),struct.unpack_from('<11I7f',b),repr(b[72:300]))
