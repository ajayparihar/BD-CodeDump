import os
from PIL import Image, ImageOps

# ============================================================
# USER-CONFIGURABLE CONSTANTS (TWEAK HERE ONLY)
# ============================================================
# All values below control the final album look.
# Change ONLY these to customize output in the future.
# ============================================================

# -----------------------
# PRINT SETTINGS
# -----------------------

# Print resolution in dots per inch.
# 300 DPI is industry standard for high-quality photo prints.
DPI = 300

# Final photo size in inches (4x6 album print).
# Swapping these will NOT break anything — orientation is auto-handled.
CANVAS_WIDTH_IN = 6
CANVAS_HEIGHT_IN = 4


# -----------------------
# OUTPUT FORMAT
# -----------------------

# Output image quality.
# 100 = maximum quality (recommended for wedding albums).
JPEG_QUALITY = 100


# -----------------------
# COLORS
# -----------------------

# Background color of the album page.
# White is standard for wedding and portrait albums.
BACKGROUND_COLOR = (255, 255, 255)

# Color of the thin outline around each photo.
# Pure black is the classic studio look.
BORDER_COLOR = (0, 0, 0)


# -----------------------
# ALBUM DESIGN TUNING
# -----------------------

# White margin between photo and album edge.
# Expressed as a percentage of the shorter canvas edge.
# 0.015 = 1.5% → tight, premium wedding album look.
WHITE_MARGIN_RATIO = 0.015

# Thickness of the black outline around the photo.
# Scales automatically with print size.
# 0.004 ≈ visually ~1–2px at 300 DPI.
BLACK_BORDER_RATIO = 0.004


# ============================================================
# DERIVED VALUES (DO NOT EDIT)
# ============================================================

# Convert canvas size from inches to pixels using DPI
CANVAS_WIDTH_PX = CANVAS_WIDTH_IN * DPI
CANVAS_HEIGHT_PX = CANVAS_HEIGHT_IN * DPI


# ============================================================
# PATH SETUP
# ============================================================

# Root directory = location of this script
ROOT_DIR = os.getcwd()

# Output directory where processed images will be stored
OUTPUT_DIR = os.path.join(ROOT_DIR, "processed")

# Create output directory if it does not already exist
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# IMAGE PROCESSING
# ============================================================

for file_name in os.listdir(ROOT_DIR):

    # Process only supported image formats
    if not file_name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        continue

    input_path = os.path.join(ROOT_DIR, file_name)

    try:
        # ----------------------------------------------------
        # Load image
        # ----------------------------------------------------
        img = Image.open(input_path)

        # Fix orientation using EXIF metadata (critical for camera photos)
        img = ImageOps.exif_transpose(img)

        # ----------------------------------------------------
        # Determine best orientation for maximum image size
        # ----------------------------------------------------
        img_w, img_h = img.size
        canvas_w, canvas_h = CANVAS_WIDTH_PX, CANVAS_HEIGHT_PX

        # Rotate canvas if it allows better utilization of space
        if (img_w > img_h and canvas_h > canvas_w) or \
           (img_h > img_w and canvas_w > canvas_h):
            canvas_w, canvas_h = canvas_h, canvas_w

        # ----------------------------------------------------
        # Create blank album canvas
        # ----------------------------------------------------
        canvas = Image.new("RGB", (canvas_w, canvas_h), BACKGROUND_COLOR)

        # ----------------------------------------------------
        # Calculate margins and borders
        # ----------------------------------------------------
        short_edge = min(canvas_w, canvas_h)

        # Fixed minimal white margin for clean album framing
        white_margin = int(short_edge * WHITE_MARGIN_RATIO)

        # Thin black outline (never smaller than 1px)
        black_border = max(1, int(short_edge * BLACK_BORDER_RATIO))

        # Maximum area available for the image (no cropping)
        available_w = canvas_w - 2 * (white_margin + black_border)
        available_h = canvas_h - 2 * (white_margin + black_border)

        # ----------------------------------------------------
        # Resize image while preserving full photo
        # ----------------------------------------------------
        img.thumbnail((available_w, available_h), Image.LANCZOS)

        # ----------------------------------------------------
        # Center image on the canvas
        # ----------------------------------------------------
        x = (canvas_w - img.width) // 2
        y = (canvas_h - img.height) // 2

        # ----------------------------------------------------
        # Draw black outline behind the image
        # ----------------------------------------------------
        border_box = (
            x - black_border,
            y - black_border,
            x + img.width + black_border,
            y + img.height + black_border
        )

        border_layer = Image.new(
            "RGB",
            (border_box[2] - border_box[0], border_box[3] - border_box[1]),
            BORDER_COLOR
        )

        # Paste border first, then photo on top
        canvas.paste(border_layer, (border_box[0], border_box[1]))
        canvas.paste(img, (x, y))

        # ----------------------------------------------------
        # Save processed image
        # ----------------------------------------------------
        output_name = f"processed_{os.path.splitext(file_name)[0]}.jpg"
        output_path = os.path.join(OUTPUT_DIR, output_name)

        canvas.save(
            output_path,
            "JPEG",
            quality=JPEG_QUALITY,
            dpi=(DPI, DPI),
            subsampling=0
        )

        print(f"✔ Processed: {file_name}")

    except Exception as e:
        print(f"✖ Failed: {file_name} | {e}")
