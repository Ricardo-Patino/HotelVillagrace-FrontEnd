
from pathlib import Path
import zipfile, shutil

# Usage:
# 1) Put your original 'Hotel.zip' next to this script.
# 2) Run:  python populate_static_from_original.py
# 3) It will copy images/videos/etc. into static/ keeping the same structure.

MEDIA_EXTS = {'.jpg','.jpeg','.png','.gif','.svg','.webp','.avif','.mp4','.webm','.ogg','.pdf'}

base = Path(__file__).parent
src_zip = base / 'Hotel.zip'
static_dir = base / 'static'

assert src_zip.exists(), "Coloque su Hotel.zip junto a este script."
static_dir.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(src_zip, 'r') as z:
    for info in z.infolist():
        if info.is_dir(): 
            continue
        ext = Path(info.filename).suffix.lower()
        if ext in MEDIA_EXTS:
            target = static_dir / info.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as src, open(target, 'wb') as dst:
                shutil.copyfileobj(src, dst)

print("✔ Listo. Los assets pesados fueron copiados a static/ con su misma estructura.")
