"""Static publication checks; independent of game install for the finished bundle."""
from pathlib import Path
from html.parser import HTMLParser
from PIL import Image
import zipfile,hashlib
OUT=Path(__file__).resolve().parents[1]
class Links(HTMLParser):
 def __init__(self): super().__init__(); self.links=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ('href','src') and v: self.links.append(v)
p=Links(); p.feed((OUT/'index.html').read_text(encoding='utf-8'))
for ref in p.links:
 assert '://' not in ref and not ref.startswith('/'),ref
 assert (OUT/ref).is_file(),ref
print('PASS: all HTML assets and download links exist; relative URLs only')
for name,size in [('Isla_Mona_art.png',(2400,2700)),('Isla_Mona.png',(2600,2100))]:
 with Image.open(OUT/name) as im: assert im.size==size; im.verify()
print('PASS: both PNG images have expected dimensions and valid image data')
allowed={'index.html','site.css','site.js','Isla_Mona.png','Isla_Mona.svg','Isla_Mona_art.png','.nojekyll'}
with zipfile.ZipFile(OUT/'Isla_Mona_Pages.zip') as z:
 assert set(z.namelist())==allowed
 for name in allowed:
  assert z.read(name)==(OUT/'pages'/name).read_bytes()
  if name!='.nojekyll': assert z.read(name)==(OUT/name).read_bytes(),name
 assert z.testzip() is None
print('PASS: ZIP contains exactly 7 approved files, identical to current originals')
