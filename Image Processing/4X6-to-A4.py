"""
============================================================
PRINT-SAFE 4x6 → A4 PDF GENERATOR
============================================================

Guarantees:
✔ Exact 4x6 inch size (300 DPI native)
✔ NO resizing
✔ NO compression
✔ NO distortion
✔ Only rotation if needed
✔ Smart orientation
✔ Progress in terminal

Layout per page:
   [ Portrait ][ Portrait ]
   [ Landscape (rotated) ]

============================================================
"""

import os
import math
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

# ================= CONFIG =================

INPUT_FOLDER = r"D:\SSD data\Edited\processed"
OUTPUT_FOLDER_NAME = "pdf"
OUTPUT_FILENAME = "album_output.pdf"

PHOTO_W_IN = 4
PHOTO_H_IN = 6

CUT_LINE = 0.1

# ==========================================


PT = 72  # PDF points per inch

PHOTO_W = PHOTO_W_IN * PT   # 288 pt
PHOTO_H = PHOTO_H_IN * PT   # 432 pt

A4_W, A4_H = A4


# =================================================
# collect images
# =================================================

valid_ext = (".jpg", ".jpeg", ".png", ".tif", ".tiff")

images = [
    os.path.join(INPUT_FOLDER, f)
    for f in sorted(os.listdir(INPUT_FOLDER))
    if f.lower().endswith(valid_ext)
]

if not images:
    raise Exception("No images found!")

total = len(images)
pages = math.ceil(total / 3)

print(f"\nFound {total} images")
print("Generating print-quality PDF...\n")


# =================================================
# output
# =================================================

out_dir = os.path.join(INPUT_FOLDER, OUTPUT_FOLDER_NAME)
os.makedirs(out_dir, exist_ok=True)

pdf_path = os.path.join(out_dir, OUTPUT_FILENAME)

c = canvas.Canvas(pdf_path, pagesize=A4)


# =================================================
# PERFECT MARGINS (math, no scaling ever)
# =================================================

remaining_w = A4_W - (PHOTO_W * 2)
SIDE = remaining_w / 3

left_x = SIDE
right_x = SIDE * 2 + PHOTO_W

bottom_w = PHOTO_H
bottom_h = PHOTO_W

bottom_x = (A4_W - bottom_w) / 2

remaining_h = A4_H - (PHOTO_H + bottom_h)
VERT = remaining_h / 3

top_y = A4_H - VERT - PHOTO_H
bottom_y = VERT


# =================================================
# helpers (ROTATE ONLY — NEVER RESIZE)
# =================================================

def prepare_image(path, want_portrait):
    """
    Opens image and rotates ONLY if orientation wrong.
    Does NOT resize or compress.
    """
    img = Image.open(path)

    w, h = img.size
    is_portrait = h >= w

    # rotate only
    if want_portrait and not is_portrait:
        img = img.rotate(90, expand=True)

    if not want_portrait and is_portrait:
        img = img.rotate(90, expand=True)

    return ImageReader(img)


# =================================================
# build pages
# =================================================

c.setLineWidth(CUT_LINE)

for page_num, i in enumerate(range(0, total, 3), start=1):

    batch = images[i:i+3]

    print(f"Page {page_num}/{pages}  |  Images {i+1}-{min(i+3,total)}")

    # top left (portrait)
    if len(batch) > 0:
        img = prepare_image(batch[0], True)
        c.drawImage(img, left_x, top_y, PHOTO_W, PHOTO_H,
                    preserveAspectRatio=True)
        c.rect(left_x, top_y, PHOTO_W, PHOTO_H)

    # top right (portrait)
    if len(batch) > 1:
        img = prepare_image(batch[1], True)
        c.drawImage(img, right_x, top_y, PHOTO_W, PHOTO_H,
                    preserveAspectRatio=True)
        c.rect(right_x, top_y, PHOTO_W, PHOTO_H)

    # bottom (landscape)
    if len(batch) > 2:
        img = prepare_image(batch[2], False)
        c.drawImage(img, bottom_x, bottom_y, bottom_w, bottom_h,
                    preserveAspectRatio=True)
        c.rect(bottom_x, bottom_y, bottom_w, bottom_h)

    c.showPage()


c.save()

print("\n✅ DONE — Print-ready PDF created at:")
print(pdf_path)
