#!/usr/bin/env python3
"""Report local authoring/rendering capabilities; never install dependencies."""
from __future__ import annotations
import argparse
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')


def resolve_soffice(requested: str | None = None) -> str:
    def preferred(path: str) -> str:
        candidate = Path(path)
        console = candidate.with_suffix('.com')
        if sys.platform == 'win32' and candidate.name.lower() == 'soffice.exe' and console.is_file():
            return str(console)
        return path

    if requested:
        found = shutil.which(requested)
        if found:
            return preferred(found)
        if Path(requested).expanduser().is_file():
            return preferred(str(Path(requested).expanduser().resolve()))
        raise FileNotFoundError(f'LibreOffice executable not found: {requested}')
    found = shutil.which('soffice') or shutil.which('libreoffice')
    if found:
        return preferred(found)
    candidates = [Path(os.environ.get(key, default)) / 'LibreOffice/program/soffice.exe'
                  for key, default in [('ProgramFiles', 'C:/Program Files'),
                                       ('ProgramFiles(x86)', 'C:/Program Files (x86)')]]
    candidates.append(Path('/Applications/LibreOffice.app/Contents/MacOS/soffice'))
    for candidate in candidates:
        if candidate.is_file():
            return preferred(str(candidate.resolve()))
    raise FileNotFoundError('No LibreOffice renderer; supply --soffice PATH.')


def font_inventory() -> dict:
    families, diagnostics = set(), []
    fc_list = shutil.which('fc-list')
    try:
        if fc_list:
            proc = subprocess.run([fc_list, '--format', '%{family}\n'], capture_output=True,
                                  text=True, encoding='utf-8', errors='replace', timeout=20, check=True)
            families.update(part.strip() for line in (proc.stdout or '').splitlines()
                            for part in line.split(',') if part.strip())
    except (OSError, subprocess.SubprocessError, ValueError, AttributeError) as exc:
        diagnostics.append(str(exc))
    names = []
    folders = [Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts',
               Path(os.environ.get('LOCALAPPDATA', '~')).expanduser() / 'Microsoft/Windows/Fonts',
               Path('/System/Library/Fonts'), Path('/Library/Fonts'), Path.home() / 'Library/Fonts']
    for folder in folders:
        try:
            if folder.is_dir():
                names.extend(p.stem for p in folder.rglob('*') if p.suffix.lower() in ('.ttf', '.otf', '.ttc'))
        except OSError as exc:
            diagnostics.append(str(exc))
    if sys.platform == 'win32':
        import winreg
        for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                with winreg.OpenKey(root, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts') as key:
                    for index in range(winreg.QueryInfoKey(key)[1]):
                        name, value, _ = winreg.EnumValue(key, index)
                        names.extend([name, Path(str(value)).stem])
            except OSError as exc:
                diagnostics.append(str(exc))
    aliases = {'Malgun Gothic': ['malgun', '맑은고딕'], 'Noto Sans KR': ['notosanskr'],
               'Noto Sans CJK KR': ['notosanscjkkr', 'notosanscjk-'],
               'Pretendard': ['pretendard'], 'Apple SD Gothic Neo': ['applesdgothicneo'],
               'NanumGothic': ['nanumgothic', '나눔고딕']}
    for family, hints in aliases.items():
        if any(hint in name.lower().replace(' ', '') for hint in hints for name in names):
            families.add(family)
    return {'status': 'PASS' if families else 'NOT_RUN', 'family_count': len(families),
            'families': sorted(families), 'korean_candidates_found': [f for f in aliases if f in families],
            'diagnostics': diagnostics, 'glyph_coverage': 'NOT_RUN: render verification required.'}


def main() -> int:
    configure_console()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--soffice')
    parser.add_argument('--font')
    args = parser.parse_args()
    packages = {}
    for module, package in [('pptx', 'python-pptx'), ('pymupdf', 'PyMuPDF'), ('PIL', 'Pillow')]:
        try:
            importlib.import_module(module)
            packages[package] = {'status': 'PASS', 'version': importlib.metadata.version(package)}
        except (ImportError, importlib.metadata.PackageNotFoundError) as exc:
            packages[package] = {'status': 'FAIL', 'reason': str(exc)}
    try:
        renderer = resolve_soffice(args.soffice)
        renderer_error = None
    except FileNotFoundError as exc:
        renderer = None
        renderer_error = str(exc)
    version = None
    if renderer:
        try:
            proc = subprocess.run([renderer, '--version'], capture_output=True,
                                  text=True, encoding='utf-8', errors='replace', timeout=20, check=True)
            version = (proc.stdout or '').strip() or (proc.stderr or '').strip() or 'unknown'
        except (OSError, subprocess.SubprocessError) as exc:
            version = f'Version check failed: {exc}'
    report = {'python': sys.version.split()[0], 'python_supported': sys.version_info >= (3, 10),
              'packages': packages, 'renderer': {'path': renderer, 'version': version,
              'status': 'AVAILABLE_NOT_TESTED' if renderer else 'NOT_RUN', 'reason': renderer_error},
              'fonts': font_inventory(), 'visual_qa': 'NOT_RUN', 'scientific_qa': 'NOT_RUN'}
    if args.font:
        report['fonts'].update(requested=args.font, requested_found=args.font in report['fonts']['families'])
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + '\n', encoding='utf-8')
    return 0 if report['python_supported'] and all(v['status'] == 'PASS' for v in packages.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
