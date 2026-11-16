#!/usr/bin/env python3
"""Add a photo to the Photography page.

Usage:
    python3 scripts/add_photo.py PATH_TO_ORIGINAL [-t "Title"] [--tags birds,wildlife] [-n file-name]

Anything you leave out (title, tags) is asked for interactively.

What it does:
  1. makes a web-size copy   -> assets/images/photography/<name>.jpg           (1800 px long edge, shown in the viewer)
  2. makes a thumbnail       -> assets/images/photography/thumbs/<name>.jpg    (700 px long edge)
  3. keeps the full original -> assets/images/photography/originals/<name>.jpg (the "Download original" link)
  4. appends an entry        -> _data/photos.yml  (with the thumbnail's width/height)

Camera metadata (EXIF, including GPS location) is removed from every copy. For the original
this is done without re-encoding, so its quality is untouched.
Then review with `bundle exec jekyll serve`, and commit + push.

Needs Pillow:  python3 -m pip install Pillow
"""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is required:  python3 -m pip install Pillow")

ROOT = Path(__file__).resolve().parent.parent
PHOTO_DIR = ROOT / "assets" / "images" / "photography"
THUMB_DIR = PHOTO_DIR / "thumbs"
ORIG_DIR = PHOTO_DIR / "originals"
DATA_FILE = ROOT / "_data" / "photos.yml"

FULL_EDGE, FULL_QUALITY = 1800, 85
THUMB_EDGE, THUMB_QUALITY = 700, 80


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def existing_names():
    if not DATA_FILE.exists():
        return set()
    return set(re.findall(r"^- file:\s*(\S+)\s*$", DATA_FILE.read_text(), flags=re.M))


def existing_tags():
    if not DATA_FILE.exists():
        return []
    tags = set()
    for group in re.findall(r"^\s*tags:\s*\[(.*?)\]", DATA_FILE.read_text(), flags=re.M):
        tags.update(t.strip() for t in group.split(",") if t.strip())
    return sorted(tags)


def save_resized(img, edge, quality, dest):
    """Save a copy no longer than `edge` px on its long side (never upscaled).
    Pillow does not carry EXIF over unless told to, so metadata is dropped.
    The colour profile is kept so colours stay correct. Returns (width, height)."""
    out = img.copy()
    out.thumbnail((edge, edge), Image.LANCZOS)
    kwargs = {"quality": quality, "optimize": True, "progressive": True}
    if img.info.get("icc_profile"):
        kwargs["icc_profile"] = img.info["icc_profile"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, "JPEG", **kwargs)
    return out.size


def strip_jpeg_metadata(data):
    """Return the JPEG bytes without EXIF/XMP (APP1), IPTC (APP13) and comment segments,
    without touching the image data. The colour profile (APP2) is kept."""
    out, i = bytearray(data[:2]), 2
    while i + 4 <= len(data):
        if data[i] != 0xFF:
            break
        marker = data[i + 1]
        if marker == 0xDA:                      # start of scan: the rest is image data
            break
        length = int.from_bytes(data[i + 2:i + 4], "big")
        if marker not in (0xE1, 0xED, 0xFE):
            out += data[i:i + 2 + length]
        i += 2 + length
    return bytes(out + data[i:])


def save_original(src, img, dest):
    """Write the full-resolution original with metadata removed.
    A JPEG with normal orientation is copied losslessly; anything else (PNG, TIFF, a JPEG that
    relies on an EXIF rotation flag) is saved as a high-quality JPEG instead."""
    data = src.read_bytes()
    with Image.open(src) as im:
        plain_jpeg = im.format == "JPEG" and im.getexif().get(274, 1) == 1
    dest.parent.mkdir(parents=True, exist_ok=True)
    if plain_jpeg:
        dest.write_bytes(strip_jpeg_metadata(data))
        return img.size
    kwargs = {"quality": 95, "optimize": True}
    if img.info.get("icc_profile"):
        kwargs["icc_profile"] = img.info["icc_profile"]
    img.save(dest, "JPEG", **kwargs)
    return img.size


def main():
    ap = argparse.ArgumentParser(description="Add a photo to the Photography page.")
    ap.add_argument("image", help="path to the original image (JPEG, PNG, TIFF, ...)")
    ap.add_argument("-t", "--title", help="caption shown on hover and in the viewer")
    ap.add_argument("--tags", help="comma-separated tags, e.g. birds,wildlife")
    ap.add_argument("-n", "--name", help="file name without extension (default: made from the title)")
    args = ap.parse_args()

    src = Path(args.image).expanduser()
    if not src.is_file():
        sys.exit(f"No such file: {src}")

    title = args.title or input("Title (caption): ").strip()
    if not title:
        sys.exit("A title is required.")

    tags = args.tags
    if tags is None:
        known = existing_tags()
        if known:
            print("Existing tags: " + ", ".join(known))
        tags = input("Tags (comma-separated): ")
    tag_list = [t.strip().lower() for t in tags.split(",") if t.strip()]
    if not tag_list:
        sys.exit("At least one tag is required (the filter buttons are built from tags).")

    name = slugify(args.name or title)
    if not name:
        sys.exit("Could not make a file name; pass one with --name.")
    if name in existing_names():
        sys.exit(f"'{name}' is already in {DATA_FILE.relative_to(ROOT)}. Pick another with --name.")
    full_path, thumb_path = PHOTO_DIR / f"{name}.jpg", THUMB_DIR / f"{name}.jpg"
    orig_path = ORIG_DIR / f"{name}.jpg"
    if full_path.exists() or thumb_path.exists() or orig_path.exists():
        sys.exit(f"{full_path.name} already exists in the photography folder. Pick another with --name.")

    with Image.open(src) as im:
        img = ImageOps.exif_transpose(im)  # apply the camera's rotation before EXIF is dropped
        if img.mode != "RGB":
            img = img.convert("RGB")
        orig_size = save_original(src, img, orig_path)
        full_size = save_resized(img, FULL_EDGE, FULL_QUALITY, full_path)
        width, height = save_resized(img, THUMB_EDGE, THUMB_QUALITY, thumb_path)

    entry = (
        f"- file: {name}\n"
        f"  title: {json.dumps(title, ensure_ascii=False)}\n"
        f"  tags: [{', '.join(tag_list)}]\n"
        f"  width: {width}\n"
        f"  height: {height}\n"
    )
    text = DATA_FILE.read_text() if DATA_FILE.exists() else ""
    if text and not text.endswith("\n"):
        text += "\n"
    DATA_FILE.write_text(text + entry)

    kb = lambda p: p.stat().st_size // 1024
    print(f"\nAdded '{title}'")
    print(f"  {full_path.relative_to(ROOT)}   {full_size[0]}x{full_size[1]}, {kb(full_path)} KB")
    print(f"  {thumb_path.relative_to(ROOT)}   {width}x{height}, {kb(thumb_path)} KB")
    print(f"  {orig_path.relative_to(ROOT)}   {orig_size[0]}x{orig_size[1]}, {kb(orig_path)} KB")
    print(f"  entry appended to {DATA_FILE.relative_to(ROOT)}")
    print("\nNext: preview with `bundle exec jekyll serve`, then commit and push.")


if __name__ == "__main__":
    main()
