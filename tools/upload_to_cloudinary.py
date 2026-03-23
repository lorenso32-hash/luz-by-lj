"""
Upload all portfolio photos to Cloudinary.
Run from the Luz By LJ root directory.
"""

import os, cloudinary, cloudinary.uploader
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

PHOTOS_DIR = Path("photos")
FOLDERS = [
    PHOTOS_DIR,
    PHOTOS_DIR / "leah-live",
    PHOTOS_DIR / "doug-live",
]

results = {}

for folder in FOLDERS:
    for img in sorted(folder.glob("*.jpg")):
        # public_id mirrors the local path: photos/tattoo-mirror, photos/leah-live/LeahLive3, etc.
        public_id = str(img.with_suffix(""))
        print(f"Uploading {img} ...", end=" ", flush=True)
        res = cloudinary.uploader.upload(
            str(img),
            public_id=public_id,
            overwrite=True,
            resource_type="image",
        )
        results[str(img)] = res["secure_url"]
        print(f"done — {res['secure_url']}")

print(f"\n✓ Uploaded {len(results)} photos.")
