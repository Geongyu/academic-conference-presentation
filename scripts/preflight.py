#!/usr/bin/env python3
"""Report local authoring/rendering capabilities; never install dependencies."""
from __future__ import annotations
import argparse
import importlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys


def font_inventory() -> dict:
    fc_list = shutil.which('fc-list')
    if not fc_list:
        return {'status': 'NOT_RUN', 'reason': 'fc-list unavailable; inspect host font inventory.',
                'korean_candidates_found': []}
    try:
        proc = subprocess.run([fc_list, '--format', '%{family}\n'], capture_output=True,
                              text=True, timeout=20, check=True)
        families = {part.strip() for line in proc.stdout.splitlines()
                    for part in line.split(',') if part.strip()}
        candidates = ['Noto Sans CJK KR', 'Noto Sans KR', 'Malgun Gothic',
                      'Apple SD Gothic Neo', 'NanumGothic']
        return {'status': 'PASS', 'family_count': len(families),
                'korean_candidates_found': [f for f in candidates if f in families],
                'glyph_coverage': 'NOT_RUN: a real render test is still required.'}
    except (OSError, subprocess.SubprocessError) as exc:
        return {'status': 'NOT_RUN', 'reason': str(exc), 'korean_candidates_found': []}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    packages = {}
    for module, package in [('pptx', 'python-pptx'), ('pymupdf', 'PyMuPDF'), ('PIL', 'Pillow')]:
        try:
            importlib.import_module(module)
            packages[package] = {'status': 'PASS', 'version': importlib.metadata.version(package)}
        except (ImportError, importlib.metadata.PackageNotFoundError) as exc:
            packages[package] = {'status': 'FAIL', 'reason': str(exc)}
    renderer = shutil.which('soffice') or shutil.which('libreoffice')
    version = None
    if renderer:
        try:
            version = subprocess.run([renderer, '--version'], capture_output=True,
                                     text=True, timeout=20, check=True).stdout.strip()
        except (OSError, subprocess.SubprocessError) as exc:
            version = f'Version check failed: {exc}'
    report = {'python': sys.version.split()[0], 'python_supported': sys.version_info >= (3, 10),
              'packages': packages, 'renderer': {'path': renderer, 'version': version,
              'status': 'AVAILABLE_NOT_TESTED' if renderer else 'NOT_RUN'},
              'fonts': font_inventory(), 'visual_qa': 'NOT_RUN', 'scientific_qa': 'NOT_RUN'}
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + '\n', encoding='utf-8')
    return 0 if report['python_supported'] and all(v['status'] == 'PASS' for v in packages.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
