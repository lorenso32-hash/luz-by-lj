"""
Generate a signed Cloudinary "Download All" archive (zip) URL for a client gallery page.
Run from the Luz By LJ root directory.

Usage:
    python3 tools/generate_archive_url.py <target_public_id> <expires_at> <public_id_1> <public_id_2> ...

    target_public_id : name for the downloaded zip file
    expires_at       : unix timestamp the link stops working, or "never"
"""

import os, sys, time, cloudinary, cloudinary.utils
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    target_public_id = sys.argv[1]
    expires_at_arg = sys.argv[2]
    public_ids = sys.argv[3:]

    expires_at = 9999999999 if expires_at_arg == "never" else int(expires_at_arg)

    url = cloudinary.utils.download_archive_url(
        public_ids=public_ids,
        target_format="zip",
        target_public_id=target_public_id,
        mode="download",
        expires_at=expires_at,
        timestamp=int(time.time()),
    )
    print(url)

if __name__ == "__main__":
    main()
