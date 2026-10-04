"""Usage: python prepare_media.py "C:\\path\\to\\your\\originals"
Needs: pip install pillow pillow-heif   and ffmpeg on PATH.
Converts HEIC/HEIF -> JPG (max 1800px), MOV/MP4 -> web MP4 (max 720p),
into media/photos and media/videos, with names that match index.html."""
import re, sys, subprocess
from pathlib import Path
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
register_heif_opener()

src = Path(sys.argv[1])
out = Path(__file__).parent / "media"
(out / "photos").mkdir(parents=True, exist_ok=True)
(out / "videos").mkdir(parents=True, exist_ok=True)
clean = lambda stem: re.sub(r"[^A-Za-z0-9_]+", "_", stem).strip("_")

for f in sorted(src.rglob("*")):
    ext = f.suffix.lower()
    if f.name.startswith(("Screenshot", "file_")):
        continue
    name = clean(f.stem)
    if ext in (".heic", ".heif", ".jpg", ".jpeg", ".png"):
        dest = out / "photos" / f"{name}.jpg"
        if dest.exists(): continue
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        im.thumbnail((1800, 1800))
        im.save(dest, "JPEG", quality=82)
        print("photo", dest.name)
    elif ext in (".mp4", ".mov"):
        dest = out / "videos" / f"{name}.mp4"
        if dest.exists(): continue
        subprocess.run(["ffmpeg", "-y", "-i", str(f), "-vf", "scale=-2:'min(720,ih)'",
                        "-c:v", "libx264", "-crf", "26", "-preset", "medium",
                        "-c:a", "aac", "-movflags", "+faststart", str(dest)], check=True)
        print("video", dest.name)
print("Done. Now copy your song to media/song.mp3")