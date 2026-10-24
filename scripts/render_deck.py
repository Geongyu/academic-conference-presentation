#!/usr/bin/env python3
"""Export a PPTX via LibreOffice and render all pages. Does not inspect the images."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import warnings
import pymupdf
from PIL import Image, ImageDraw
from pptx import Presentation
from preflight import resolve_soffice, configure_console


def contact_sheets(pages: list[Path], output: Path) -> list[str]:
    sheet_names = []
    for start in range(0, len(pages), 12):
        subset = pages[start:start + 12]
        columns = min(3, len(subset))
        rows = (len(subset) + columns - 1) // columns
        tw, th, pad, label_h = 480, 270, 14, 26
        sheet = Image.new('RGB', (columns * (tw + pad) + pad,
                                 rows * (th + label_h + pad) + pad), 'white')
        draw = ImageDraw.Draw(sheet)
        for offset, page in enumerate(subset):
            x = pad + (offset % columns) * (tw + pad)
            y = pad + (offset // columns) * (th + label_h + pad)
            with Image.open(page) as img:
                img = img.convert('RGB')
                img.thumbnail((tw, th), Image.Resampling.LANCZOS)
                sheet.paste(img, (x + (tw - img.width) // 2, y + (th - img.height) // 2))
            draw.text((x, y + th + 4), f'Slide {start + offset + 1}', fill='black')
        name = f'contact-sheet-{start // 12 + 1:02d}.png'
        sheet.save(output / name)
        sheet_names.append(name)
    return sheet_names


def render_deck(pptx: Path, out_dir: Path, dpi: int = 150,
                soffice: str | None = None, overwrite: bool = False,
                timeout: int = 180) -> dict:
    pptx, out_dir = pptx.resolve(), out_dir.resolve()
    if not pptx.is_file() or pptx.suffix.lower() != '.pptx':
        raise ValueError(f'A readable .pptx file is required: {pptx}')
    if not 72 <= dpi <= 300:
        raise ValueError('DPI must be between 72 and 300 for full-deck previews.')
    if timeout <= 0:
        raise ValueError('Timeout must be positive.')
    executable = resolve_soffice(soffice)
    slide_count = len(Presentation(str(pptx)).slides)
    if not slide_count:
        raise ValueError('Cannot render a presentation with no slides.')
    pdf_name = pptx.stem + '.pdf'
    products = []
    previous = out_dir / 'render-report.json'
    if previous.is_file():
        old = json.loads(previous.read_text(encoding='utf-8'))
        names = old.get('slide_images', []) + old.get('contact_sheets', []) + [old.get('pdf_file', ''), previous.name]
        for name in names:
            if name and Path(name).name == name and (out_dir / name).is_file():
                products.append(out_dir / name)
    planned = [pdf_name, 'render-report.json']
    planned += [f'slide-{n:03d}.png' for n in range(1, slide_count + 1)]
    planned += [f'contact-sheet-{n:02d}.png' for n in range(1, (slide_count + 11) // 12 + 1)]
    conflicts = [name for name in planned if (out_dir / name).exists() and out_dir / name not in products]
    if conflicts or (products and not overwrite):
        raise FileExistsError('Existing outputs are unowned or --overwrite was not supplied: ' + str(conflicts))
    out_dir.mkdir(parents=True, exist_ok=True)
    version_result = subprocess.run([executable, '--version'], capture_output=True,
                                    text=True, encoding='utf-8', errors='replace', timeout=20, check=True)
    version = (version_result.stdout or '').strip() or (version_result.stderr or '').strip() or 'unknown'
    with tempfile.TemporaryDirectory(prefix='academic-slides-render-', ignore_cleanup_errors=True) as temp:
        temp_root = Path(temp).resolve()
        convert_dir, profile_dir = temp_root / 'converted', temp_root / 'profile'
        convert_dir.mkdir()
        cmd = [executable, f'-env:UserInstallation={profile_dir.as_uri()}',
               '--headless', '--nologo', '--nodefault', '--norestore',
               '--convert-to', 'pdf:impress_pdf_Export:{"ExportHiddenSlides":{"type":"boolean","value":"true"}}', '--outdir', str(convert_dir), str(pptx)]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout, check=False)
        pdf = convert_dir / pdf_name
        if result.returncode != 0 or not pdf.is_file() or pdf.stat().st_size == 0:
            raise RuntimeError(f'PDF export failed (exit {result.returncode}). '
                               f"Stdout: {(result.stdout or '').strip()} Stderr: {(result.stderr or '').strip()}")
        with pymupdf.open(pdf) as doc:
            if len(doc) != slide_count:
                raise RuntimeError(f'Slide/page mismatch: {slide_count} slides, {len(doc)} PDF pages.')
            for page in doc:
                if page.rect.width * page.rect.height * (dpi / 72) ** 2 > 80_000_000:
                    raise ValueError('Slide raster would exceed 80 megapixels; reduce DPI.')
        # Replace only files listed in the previous report, after conversion succeeded.
        for path in products:
            if path.is_file():
                path.unlink()
        final_pdf = out_dir / pdf_name
        shutil.copy2(pdf, final_pdf)
    if temp_root.exists():
        warnings.warn(f'Render temporary directory could not be fully cleaned: {temp_root}')
    page_paths = []
    with pymupdf.open(final_pdf) as doc:
        for number, page in enumerate(doc, 1):
            destination = out_dir / f'slide-{number:03d}.png'
            page.get_pixmap(dpi=dpi, alpha=False).save(destination)
            page_paths.append(destination)
    sheets = contact_sheets(page_paths, out_dir)
    report = {
        'pptx_file': pptx.name, 'pptx_sha256': hashlib.sha256(pptx.read_bytes()).hexdigest(),
        'renderer': version, 'rasterizer': f'PyMuPDF {pymupdf.VersionBind}',
        'pdf_file': final_pdf.name, 'pdf_sha256': hashlib.sha256(final_pdf.read_bytes()).hexdigest(),
        'slide_count': slide_count, 'rendered_pages': len(page_paths), 'dpi': dpi,
        'slide_images': [p.name for p in page_paths], 'contact_sheets': sheets,
        'export_status': 'PASS', 'visual_inspection': 'NOT_RUN',
        'scientific_verification': 'NOT_RUN', 'native_powerpoint_check': 'NOT_RUN',
        'next_step': 'Open every slide image and record the inspection; generation is not verification.'}
    (out_dir / 'render-report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


def main() -> int:
    configure_console()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pptx', type=Path)
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--dpi', type=int, default=150)
    parser.add_argument('--soffice')
    parser.add_argument('--timeout', type=int, default=180)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    try:
        report = render_deck(args.pptx, args.out_dir, args.dpi, args.soffice,
                             args.overwrite, args.timeout)
        print(f"Exported {report['rendered_pages']} slide images to {args.out_dir}. "
              'Visual inspection and scientific verification remain NOT_RUN.')
        return 0
    except Exception as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
