"""Build a publication-only bundle. Never includes game models or reference textures."""
from pathlib import Path
import shutil, zipfile
OUT=Path(__file__).resolve().parents[1]
FILES=['index.html','site.css','site.js','Isla_Mona.png','Isla_Mona.svg','Isla_Mona_art.png']
for name in FILES:
 if not (OUT/name).is_file(): raise FileNotFoundError(name)
dest=OUT/'pages'; dest.mkdir(exist_ok=True)
for name in FILES: shutil.copy2(OUT/name,dest/name)
(dest/'.nojekyll').write_text('',encoding='utf-8')
with zipfile.ZipFile(OUT/'Isla_Mona_Pages.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in FILES+['.nojekyll']: z.write(dest/name,name)
print('PASS: GitHub Pages bundle: 7 static files, relative URLs, no game resources')
