#!/usr/bin/env python3
"""Render an inspected PDF region; one-based page, normalized displayed-page box."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import pymupdf


def crop_pdf(pdf: Path, page_number: int, box: list[float], dpi: int,
             output: Path, source_id: str = '', locator: str = '') -> dict:
    pdf, output = pdf.resolve(), output.resolve()
    if not pdf.is_file():
        raise FileNotFoundError(f'Source PDF not found: {pdf}')
    if output.suffix.lower() != '.png':
        raise ValueError('Output must be a .png file.')
    if pdf == output:
        raise ValueError('Output must not overwrite the source.')
    if not (72 <= dpi <= 600):
        raise ValueError('DPI must be between 72 and 600.')
    if len(box) != 4 or not all(math.isfinite(x) for x in box):
        raise ValueError('Box requires four finite normalized coordinates.')
    left, top, right, bottom = box
    if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
        raise ValueError('Box must satisfy 0 <= left < right <= 1 and 0 <= top < bottom <= 1.')
    with pymupdf.open(pdf) as doc:
        if doc.needs_pass:
            raise ValueError('Password-protected PDF: obtain an authorized readable copy first.')
        if not (1 <= page_number <= len(doc)):
            raise ValueError(f'Page must be 1..{len(doc)}; pages are one-based.')
        page = doc[page_number - 1]
        rect = page.rect
        clip = pymupdf.Rect(rect.x0 + left * rect.width, rect.y0 + top * rect.height,
                            rect.x0 + right * rect.width, rect.y0 + bottom * rect.height)
        if clip.width * clip.height * (dpi / 72) ** 2 > 80_000_000:
            raise ValueError('Requested raster exceeds 80 megapixels; reduce DPI or region.')
        pix = page.get_pixmap(dpi=dpi, clip=clip, alpha=False)
        output.parent.mkdir(parents=True, exist_ok=True)
        pix.save(output)
        manifest = {'source_id': source_id, 'source_file': pdf.name,
                    'source_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
                    'page_one_based': page_number, 'page_rotation': page.rotation,
                    'normalized_display_box': box, 'clip_points': list(clip), 'dpi': dpi,
                    'pixels': [pix.width, pix.height], 'locator': locator,
                    'transformation': 'rendered displayed-page region',
                    'output_file': output.name, 'caption_checked': False,
                    'scientific_context_preserved': None,
                    'review_required': 'Compare crop and caption with the original source.'}
    output.with_suffix('.source.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', required=True, type=Path)
    parser.add_argument('--page', required=True, type=int)
    parser.add_argument('--box', nargs=4, type=float, default=[0.0, 0.0, 1.0, 1.0])
    parser.add_argument('--dpi', type=int, default=300)
    parser.add_argument('--source-id', default='')
    parser.add_argument('--locator', default='')
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    try:
        report = crop_pdf(args.pdf, args.page, args.box, args.dpi, args.out,
                          args.source_id, args.locator)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, RuntimeError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
