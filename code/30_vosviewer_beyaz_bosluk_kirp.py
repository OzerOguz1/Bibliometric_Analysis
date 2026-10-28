# -*- coding: utf-8 -*-
"""Crop outer white margins from VOSviewer PNG exports.

Retains network coordinates, colours, labels and the VOSviewer mark. A threshold
identifies near-white outer pixels; a 30-pixel margin is retained on each side."""

from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "06_SONUC" / "sekiller"
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = {
    ROOT / "05_VOSVIEWER/CIKTI/V1_V2_esolusum/V1_esolusum_DE_minocc5_38terim.png":
        OUT / "Sekil6_VOSviewer_kirp.png",
    ROOT / "05_VOSVIEWER/CIKTI/V1_V2_esolusum/V2_overlay_avgpubyear_2016-2026.png":
        OUT / "Sekil7_VOSviewer_kirp.png",
    ROOT / "05_VOSVIEWER/CIKTI/V3_donemsel/V3a_P1_1999-2016_minocc2_23terim.png":
        OUT / "Sekil8a_VOSviewer_kirp.png",
    ROOT / "05_VOSVIEWER/CIKTI/V3_donemsel/V3b_P2_2017-2020_minocc2_32terim.png":
        OUT / "Sekil8b_VOSviewer_kirp.png",
    ROOT / "05_VOSVIEWER/CIKTI/V3_donemsel/V3c_P3_2021-2026_minocc4_36terim.png":
        OUT / "Sekil8c_VOSviewer_kirp.png",
}

THRESHOLD = 12
PADDING = 30


for source, target in SOURCES.items():
    image = Image.open(source).convert("RGB")
    white = Image.new("RGB", image.size, "white")
    difference = ImageChops.difference(image, white).convert("L")
    mask = difference.point(lambda value: 255 if value > THRESHOLD else 0)
    box = mask.getbbox()
    if box is None:
        raise RuntimeError(f"Görsel içeriği saptanamadı: {source}")
    left, top, right, bottom = box
    box_with_padding = (
        max(0, left - PADDING),
        max(0, top - PADDING),
        min(image.width, right + PADDING),
        min(image.height, bottom + PADDING),
    )
    cropped = image.crop(box_with_padding)
    cropped.save(target, optimize=True)
    print(f"{target.name}: {image.size} -> {cropped.size}")
