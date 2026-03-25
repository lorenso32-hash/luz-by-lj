"""
Upload BTS background images to Cloudinary under bts/ folder.
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

BTS_DIR = Path("/tmp")
FILES = ["bts_25.jpg", "LJBtsBehindCam.jpg", "bts_56.jpg", "bts_66.jpg"]

for filename in FILES:
    img = BTS_DIR / filename
    public_id = f"bts/{Path(filename).stem}"
    print(f"Uploading {filename} ...", end=" ", flush=True)
    res = cloudinary.uploader.upload(
        str(img),
        public_id=public_id,
        overwrite=True,
        resource_type="image",
    )
    print(f"done — {res['secure_url']}")

print("\n✓ Done.")
