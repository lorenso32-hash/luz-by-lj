"""
1. Download levi web-sized photos from Google Drive
2. Upload them to Cloudinary
3. Rewrite index.html — all photos use Cloudinary URLs
   - Gallery/band imgs: w_800,f_auto,q_auto  (fast thumbnails)
   - CSS backgrounds:   w_1920,f_auto,q_auto (full width)
   - Lightbox JS:       w_1920,f_auto,q_auto (on click)
"""

import os, re, urllib.request, tempfile, cloudinary, cloudinary.uploader
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

CLOUD  = os.getenv("CLOUDINARY_CLOUD_NAME")
BASE   = f"https://res.cloudinary.com/{CLOUD}/image/upload"
THUMB  = "w_800,f_auto,q_auto"
FULL   = "w_1920,f_auto,q_auto"

# ─── Levi web-sized Drive IDs ─────────────────────────────────────────────────
LEVI_IDS = {
    "Untitled.jpg":    "1JJVk_rY8mPUceAluO1BShV6DmW-9CiCZ",
    "Untitled-2.jpg":  "1eUhDqiA0pViPNl4k0ABwrShi7ydb5N9x",
    "Untitled-3.jpg":  "1TjO1WbJ5uY9aBnVKfozs-WhWt6-xlY7e",
    "Untitled-4.jpg":  "1lGdFyYcIBSvfKjwkxQNBSSnkrz6K6RvK",
    "Untitled-5.jpg":  "1paTQdczFgjGz1tuLcqeFqP8Jj-IpYEgd",
    "Untitled-6.jpg":  "1JG_ZHHFz8rPwldpwHoF2QCcm87qBA36e",
    "Untitled-7.jpg":  "1naVPPPMhMYPUAt6FojO1UA1KoFUy2fjP",
    "Untitled-8.jpg":  "16M9Vf8Zd0OzybVBtP9tIj-ygF_-ePVqJ",
    "Untitled-9.jpg":  "1h-2hIDqJdKH6Zgo2b5LY1cL8QaYHpD8u",
    "Untitled-10.jpg": "1SvrIyhLOKVEjuMdgb7lPbk2pQYt_gxff",
    "Untitled-11.jpg": "1QInnZVlmdOC6EJrhqjuDdKzIplVRLr5_",
    "Untitled-12.jpg": "1h4x-TVWC17qhSi9hzng-mCARhvSKJorh",
    "Untitled-13.jpg": "10nj5eGjUuKqyxs4arDLGoYk334Aen_tb",
    "Untitled-14.jpg": "12XhcOPPu3CNnBMSC1gtzEIT-Dw7_7CiZ",
    "Untitled-15.jpg": "19KFwfTw3qbL3BvSSUVUI5wNj1T0Z7Lfc",
    "Untitled-16.jpg": "19kzTxGxFndcoaTv_YTGAPYKdqGeGaNnk",
    "Untitled-17.jpg": "1oF70BQIt461q4v79w7j80ttJf_ZJXPns",
    "Untitled-18.jpg": "1hJMhmqhqFRqEyqOU0qEMtNi1EXj7BXBa",
    "Untitled-19.jpg": "1B6ab-BcsZGE0FfVE2yu58XiZgia5b-h6",
    "Untitled-20.jpg": "1dqzYzplggTitHH747D8JHR9veRCXuY3n",
    "Untitled-21.jpg": "1oLQXp5eO8s_1rjszLQXThpsEja2g9lhs",
    "Untitled-22.jpg": "1P1iwmsoDdSyYbfuULx2i9RmohR4jt3x8",
    "Untitled-23.jpg": "1KgpsRNuKmXTrIkqG783ZVIxQulAeDFGS",
    "Untitled-24.jpg": "11Ya93EkDuwl3QnGypD3phO-qp4xRipKR",
    "Untitled-25.jpg": "1n7yMsLrIgN_qJODLRdIA6elXshqHm23A",
    "Untitled-26.jpg": "1fjZIiRLu5IFWzE34rFxy3OWhJT9bbUQU",
    "Untitled-27.jpg": "1P1ah25JaJ_hxJi2oMnF_jW_TR9io2Se4",
    "Untitled-28.jpg": "1iLYjt-0rjopHBFPJi30O3pm4dOucAnEO",
    "Untitled-29.jpg": "1Gpo6fYpIcM-2dJODYxGRkZR1BDXfaa6L",
    "Untitled-30.jpg": "1TPm_-isF-wK2jxiC5C04_UjDEXajovvV",
    "Untitled-31.jpg": "1SZMWIe6cz5hCASQxqwu5pRc1lnZ0-uIr",
    "Untitled-32.jpg": "116o5bqBCwEb8-k_90gE1hiHA7uTDC8ui",
    "Untitled-33.jpg": "1qj6gftlb-fnKRliX-ztfFy2yjSEBXQm7",
    "Untitled-34.jpg": "10OEZifpOaBjE6PhQOfz0pv_XVo00KSTt",
    "Untitled-35.jpg": "13JFhyvlyvfRp5mLomCAFrBq-4kGzVctd",
}

def drive_dl(file_id):
    return f"https://drive.google.com/uc?export=download&id={file_id}"

def cld_url(public_id, transform):
    return f"{BASE}/{transform}/{public_id}.jpg"

# ─── 1. Upload levi photos from Drive → Cloudinary ───────────────────────────
print("=== Uploading levi photos from Drive to Cloudinary ===")
levi_cld = {}
with tempfile.TemporaryDirectory() as tmp:
    for filename, drive_id in LEVI_IDS.items():
        public_id = f"photos/levi/{Path(filename).stem}"
        tmp_path = os.path.join(tmp, filename)
        print(f"  Downloading {filename} ...", end=" ", flush=True)
        try:
            urllib.request.urlretrieve(drive_dl(drive_id), tmp_path)
            res = cloudinary.uploader.upload(
                tmp_path,
                public_id=public_id,
                overwrite=True,
                resource_type="image",
            )
            levi_cld[filename] = public_id
            print(f"uploaded ✓")
        except Exception as e:
            print(f"FAILED: {e}")

# ─── 2. Rewrite index.html ────────────────────────────────────────────────────
print("\n=== Rewriting index.html ===")
html = Path("index.html").read_text()

# CSS backgrounds — full width
css_bg_map = {
    "photos/Tattoo mirror.jpg":   "photos/Tattoo mirror",
    "photos/Enrique-27.jpg":      "photos/Enrique-27",
    "photos/levi/LeviPlayingBackground.jpg": None,  # deleted — remove
    "photos/leah-live/Blurry Artsy Band Pic.jpg": None,  # deleted — remove
    "photos/doug-live/DSC00738.jpg": None,  # deleted — remove
}

for local_path, public_id in css_bg_map.items():
    pattern = f"url('{local_path}')"
    if public_id:
        replacement = f"url('{cld_url(public_id, FULL)}')"
    else:
        replacement = "none"
    html = html.replace(pattern, replacement)

# Gallery <img src="photos/..."> — thumbnails
def replace_gallery_src(m):
    local = m.group(1)  # e.g. photos/Tattoo mirror.jpg
    public_id = local.rsplit(".", 1)[0]  # strip .jpg
    return f'src="{cld_url(public_id, THUMB)}"'

html = re.sub(
    r'src="(photos/(?!levi/)[^"]+\.jpg)"',
    replace_gallery_src,
    html
)

# Levi band <img src="photos/levi/..."> — thumbnails from Cloudinary
def replace_levi_src(m):
    filename = m.group(1)  # e.g. Untitled-3.jpg
    if filename in levi_cld:
        return f'src="{cld_url(levi_cld[filename], THUMB)}"'
    return m.group(0)  # fallback unchanged

html = re.sub(
    r'src="photos/levi/([^"]+\.jpg)"',
    replace_levi_src,
    html
)

# Lightbox — swap w_800 for w_1920 when opening
old_lb = "document.getElementById('lightbox-img').src = photo.src;"
new_lb = "document.getElementById('lightbox-img').src = photo.src.replace('/w_800,', '/w_1920,');"
html = html.replace(old_lb, new_lb)

Path("index.html").write_text(html)
print("index.html updated ✓")
print(f"\nDone. {len(levi_cld)} levi photos uploaded, all src attributes rewritten.")
