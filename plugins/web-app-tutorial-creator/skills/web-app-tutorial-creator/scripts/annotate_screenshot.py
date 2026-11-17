#!/usr/bin/env python3
"""
Annotate a screenshot with a colored highlight box and a numbered circle callout.

Usage:
    python annotate_screenshot.py \
        --input screenshot.png \
        --output annotated.png \
        --box X,Y,W,H \
        --number N \
        [--color red|orange|green|blue|#hex] \
        [--callout-position top-left|top-right|bottom-left|bottom-right]

The output is the same dimensions as the input, with:
  - A rounded highlight rectangle around the specified region
  - A soft outer glow around the highlight
  - A numbered circle callout overlapping one corner of the highlight
"""
import argparse
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from spec import color as validate_color, SpecError

NAMED_COLORS = {
    "red":    "#FF4D4D",
    "orange": "#FFB800",
    "green":  "#00B894",
    "blue":   "#3B82F6",
}

# Try a sequence of bold fonts; fall back to default if none found.
BOLD_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "C:/Windows/Fonts/arialbd.ttf",
]


def load_bold_font(size: int) -> ImageFont.ImageFont:
    for path in BOLD_FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def parse_color(c: str) -> tuple[int, int, int]:
    """Return RGB tuple from named color or #rrggbb."""
    value = validate_color(c or 'red')[1:]
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))


def validate_box(box, width, height):
    import math
    if len(box) != 4 or any(isinstance(v, bool) or not isinstance(v, (int,float)) or not math.isfinite(v) for v in box):
        raise SpecError('Box needs four finite pixel coordinates')
    x,y,w,h = box
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x+w > width or y+h > height:
        raise SpecError('Highlight/redaction is outside the image or has zero area')
    # Expand fractional edges outward so redaction never leaks border pixels.
    left, top = math.floor(x), math.floor(y)
    return left, top, math.ceil(x+w)-left, math.ceil(y+h)-top


def annotate(
    input_path: str,
    output_path: str,
    box: tuple[int, int, int, int],
    number: int,
    color: str = "red",
    callout_position: str = "top-left",
    redactions=(),
) -> None:
    rgb = parse_color(color)
    img = Image.open(input_path).convert("RGBA")
    W, H = img.size
    x, y, w, h = validate_box(box, W, H)
    if number < 1:
        raise SpecError('number must be positive')
    if callout_position not in ('top-left','top-right','bottom-left','bottom-right'):
        raise SpecError('Invalid callout position')
    draw = ImageDraw.Draw(img)
    for region in redactions:
        rx, ry, rw, rh = validate_box(region, W, H)
        draw.rectangle((rx, ry, rx+rw-1, ry+rh-1), fill=(0,0,0,255))

    # Auto-scale stroke / circle / radius based on image size so things look
    # consistent on small and large screenshots.
    short_side = min(W, H)
    border_width = max(2, short_side // 300)
    corner_radius = max(8, border_width * 2)
    circle_diameter = min(W, H, max(20, min(52, short_side // 20)))
    inner_circle_border = max(3, circle_diameter // 16)

    # ---- Draw the dim layer (grey out everything outside the highlight) ----
    # A semi-transparent dark layer covers the whole image, with a rounded
    # rectangular hole punched out where the highlight box is — so the user's
    # eye lands on the focus area immediately.
    dim_alpha = 64  # 0..255; ~55% darken
    mask = Image.new("L", img.size, 255)  # 255 = dim covers; 0 = transparent
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=corner_radius,
        fill=0,
    )
    dim_solid = Image.new("RGBA", img.size, (0, 0, 0, dim_alpha))
    dim_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dim_layer.paste(dim_solid, (0, 0), mask)

    # ---- Draw the glow (separate layer, then blur) -------------------------
    # NOTE: glow strength reduced ~30% from earlier version. With the dim
    # layer doing the heavy focus-pulling, the glow is just an accent.
    glow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_padding = max(7, int(border_width * 2.1))     # was border_width * 3
    glow_alpha = 126                                    # was 180 (~30% reduction)
    glow_draw.rounded_rectangle(
        [x - glow_padding, y - glow_padding,
         x + w + glow_padding, y + h + glow_padding],
        radius=corner_radius + glow_padding,
        outline=(*rgb, glow_alpha),
        width=glow_padding,
    )
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=glow_padding * 0.6))

    # ---- Draw the highlight box --------------------------------------------
    box_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    box_draw = ImageDraw.Draw(box_layer)
    box_draw.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=corner_radius,
        outline=(*rgb, 255),
        width=border_width,
    )

    # ---- Draw the numbered circle callout ----------------------------------
    # Position so the circle overlaps one corner of the highlight box.
    overlap = circle_diameter // 3
    if callout_position == "top-left":
        cx0 = x - circle_diameter + overlap
        cy0 = y - circle_diameter + overlap
    elif callout_position == "top-right":
        cx0 = x + w - overlap
        cy0 = y - circle_diameter + overlap
    elif callout_position == "bottom-left":
        cx0 = x - circle_diameter + overlap
        cy0 = y + h - overlap
    elif callout_position == "bottom-right":
        cx0 = x + w - overlap
        cy0 = y + h - overlap
    else:
        cx0 = x - circle_diameter + overlap
        cy0 = y - circle_diameter + overlap

    # Prefer outside the target so the number does not obscure its label.
    if y >= circle_diameter + 4:
        cy0 = y - circle_diameter - 4
    elif H - y - h >= circle_diameter + 4:
        cy0 = y + h + 4
    elif x >= circle_diameter + 4:
        cx0 = x - circle_diameter - 4
    elif W - x - w >= circle_diameter + 4:
        cx0 = x + w + 4
    # Keep circle on canvas
    cx0 = max(0, min(cx0, W - circle_diameter))
    cy0 = max(0, min(cy0, H - circle_diameter))

    callout_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    callout_draw = ImageDraw.Draw(callout_layer)
    # Subtle drop-shadow for the circle
    shadow_offset = max(2, circle_diameter // 30)
    shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_draw.ellipse(
        [cx0 + shadow_offset, cy0 + shadow_offset,
         cx0 + circle_diameter + shadow_offset, cy0 + circle_diameter + shadow_offset],
        fill=(0, 0, 0, 110),
    )
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=shadow_offset))

    # White border ring (slightly larger), then colored fill
    callout_draw.ellipse(
        [cx0, cy0, cx0 + circle_diameter, cy0 + circle_diameter],
        fill=(*rgb, 255),
        outline=(255, 255, 255, 255),
        width=inner_circle_border,
    )

    # Number
    text = str(number)
    font_size = int(circle_diameter * 0.55)
    font = load_bold_font(font_size)
    bbox = callout_draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = cx0 + (circle_diameter - text_w) // 2 - bbox[0]
    text_y = cy0 + (circle_diameter - text_h) // 2 - bbox[1]
    callout_draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)

    # ---- Composite layers in order: image + dim + glow + box + shadow + callout
    out = Image.alpha_composite(img, dim_layer)
    out = Image.alpha_composite(out, glow_layer)
    out = Image.alpha_composite(out, box_layer)
    out = Image.alpha_composite(out, shadow_layer)
    out = Image.alpha_composite(out, callout_layer)

    out = out.convert("RGB")
    out.info.clear()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    out.save(output_path, exif=b"" if str(output_path).lower().endswith((".jpg", ".jpeg", ".webp")) else b"")
    print(f"Annotated -> {output_path}  (size {W}x{H}, box {x},{y},{w},{h})")


def main() -> None:
    p = argparse.ArgumentParser(description="Annotate a screenshot.")
    p.add_argument("--input", required=True, help="Path to source screenshot.")
    p.add_argument("--output", required=True, help="Path to write annotated image.")
    p.add_argument("--box", required=True, help="Highlight box as X,Y,W,H in pixels.")
    p.add_argument("--number", type=int, required=True, help="Step number to display.")
    p.add_argument("--color", default="red",
                   help="Color: red | orange | green | blue | #rrggbb")
    p.add_argument("--callout-position", default="top-left",
                   choices=["top-left", "top-right", "bottom-left", "bottom-right"],
                   help="Which corner of the highlight box the circle overlaps.")
    args = p.parse_args()

    parts = [int(v.strip()) for v in args.box.split(",")]
    if len(parts) != 4:
        raise SystemExit("--box must be X,Y,W,H (4 integers).")
    box = (parts[0], parts[1], parts[2], parts[3])

    annotate(args.input, args.output, box, args.number, args.color, args.callout_position)


if __name__ == "__main__":
    main()
