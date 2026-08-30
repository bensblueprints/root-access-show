#!/usr/bin/env python3
"""Character reference images from the existing 4-side renders:
  <slug>-standing.png  — full body with the base cropped off
  <slug>-portrait.png  — face close-up (top ~20% of the body, upscaled)
Usage: python3 crop_ref.py <render_dir> <out_dir>
"""
from PIL import Image
import numpy as np
import sys, os, glob

BASE_FRAC = 0.09   # base ≈ 7.5% of the body height (bottom)
HEAD_FRAC = 0.18    # face close-up = top 20% of the body height

def alpha_bbox(a):
    ys, xs = np.where(a > 10)
    return xs.min(), xs.max(), ys.min(), ys.max()

def process(src, out_dir, slug):
    img = Image.open(src).convert("RGBA")
    a = np.array(img)[:, :, 3]
    x0, x1, y0, y1 = alpha_bbox(a)
    h = y1 - y0
    # standing: crop off the base (bottom)
    body_bottom = y1 - int(h * BASE_FRAC)
    standing = img.crop((x0, y0, x1, body_bottom))
    standing.save(os.path.join(out_dir, slug + "-standing.png"))
    # portrait: head close-up = top HEAD_FRAC of the body, upscaled
    head_bottom = y0 + int(h * HEAD_FRAC)
    portrait = img.crop((x0, y0, x1, head_bottom))
    # upscale head crop to a square-ish reference
    w = portrait.width
    portrait = portrait.resize((1024, 1024), Image.LANCZOS)
    portrait.save(os.path.join(out_dir, slug + "-portrait.png"))
    print(f"{slug}: h={h} base_cut={h-int(h*BASE_FRAC)} -> standing + portrait")

def main():
    src = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "/tmp"
    os.makedirs(out_dir, exist_ok=True)
    if os.path.isdir(src):
        for f in sorted(glob.glob(os.path.join(src, "*-front.png"))):
            slug = os.path.basename(f).replace("-front.png", "")
            process(f, out_dir, slug)
    else:
        slug = os.path.basename(src).replace("-front.png", "")
        process(src, out_dir, slug)

if __name__ == "__main__":
    main()
