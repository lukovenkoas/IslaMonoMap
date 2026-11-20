from pathlib import Path
import struct
p=Path('Resource/Models/Islands/IslaMona/IslaMona.gm')
b=p.read_bytes()
u=struct.unpack_from('<11I',b)
o=72+u[2]+4*u[3]+4*u[4]+56*u[5]+4+108*u[7]
print('objects start',o,'counts',u)
for q in range(o,o+700,16):
 print(q,struct.unpack_from('<4I',b,q),tuple(round(x,4) for x in struct.unpack_from('<4f',b,q)))
print('vertex header',struct.unpack_from('<8I',b,48259))
for q in range(48267,48443,44): print('vertex?',q,struct.unpack_from('<11f',b,q))
print('last 160')
for q in range(len(b)-160,len(b),16): print(q,struct.unpack_from('<4I',b,q),struct.unpack_from('<4f',b,q))
