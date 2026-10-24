#!/usr/bin/env python3
"""Create deterministic academic-slide design tokens from a preferred HEX color."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re


def normalize_hex(value: str) -> str:
    value = value.strip().lstrip('#')
    if not re.fullmatch(r'[0-9a-fA-F]{6}', value):
        raise ValueError('Use a six-digit HEX color, such as #2457C5; resolve color names first.')
    return '#' + value.upper()


def rgb(value: str) -> tuple[int, int, int]:
    value = normalize_hex(value)[1:]
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def mix(a: str, b: str, fraction_b: float) -> str:
    if not 0 <= fraction_b <= 1:
        raise ValueError('Mix fraction must be between 0 and 1.')
    channels = [round(x * (1 - fraction_b) + y * fraction_b) for x, y in zip(rgb(a), rgb(b))]
    return '#' + ''.join(f'{c:02X}' for c in channels)


def luminance(value: str) -> float:
    vals = [x / 255 for x in rgb(value)]
    linear = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in vals]
    return sum(w * x for w, x in zip((0.2126, 0.7152, 0.0722), linear))


def contrast(a: str, b: str) -> float:
    lo, hi = sorted((luminance(a), luminance(b)))
    return (hi + 0.05) / (lo + 0.05)


def accessible(seed: str, background: str, minimum: float) -> str:
    seed = normalize_hex(seed)
    if contrast(seed, background) >= minimum:
        return seed
    target = max(('#000000', '#FFFFFF'), key=lambda c: contrast(c, background))
    for step in range(1, 101):
        candidate = mix(seed, target, step / 100)
        if contrast(candidate, background) >= minimum:
            return candidate
    raise ValueError(f'Could not obtain contrast {minimum} against {background}.')


def make_theme(accent: str = '#2457C5', mode: str = 'light',
               font: str = 'Noto Sans CJK KR', secondary: str | None = None) -> dict:
    if mode not in ('light', 'dark'):
        raise ValueError('Mode must be light or dark.')
    if not font.strip():
        raise ValueError('A font-family name is required; verify installation separately.')
    preferred = normalize_hex(accent)
    bg = '#FFFFFF' if mode == 'light' else '#101722'
    primary = accessible(preferred, bg, 3.0)
    tokens = {
        'preferred': preferred, 'background': bg,
        'primary': primary, 'primary_ink': accessible(preferred, bg, 4.5),
        'on_primary': max(('#000000', '#FFFFFF'), key=lambda c: contrast(c, primary)),
        'primary_soft': mix(preferred, bg, 0.94), 'surface': mix(preferred, bg, 0.97),
        'primary_dark': mix(preferred, '#000000', 0.28),
        'text': accessible('#172033' if mode == 'light' else '#F4F7FB', bg, 4.5),
        'muted_text': accessible('#526174' if mode == 'light' else '#C3CDD9', bg, 4.5),
        'baseline': accessible('#596579' if mode == 'light' else '#A8B5C8', bg, 3.0),
        'border': '#D9DEE7' if mode == 'light' else '#394354',
        'secondary': accessible(secondary, bg, 3.0) if secondary else None,
        'secondary_ink': accessible(secondary, bg, 4.5) if secondary else None,
    }
    tests = [('text', 'background', 4.5), ('muted_text', 'background', 4.5),
             ('primary_ink', 'background', 4.5), ('primary', 'background', 3.0),
             ('on_primary', 'primary', 4.5), ('baseline', 'background', 3.0)]
    if secondary:
        tests += [('secondary', 'background', 3.0), ('secondary_ink', 'background', 4.5)]
    checks = [{'foreground': a, 'background': b, 'minimum': minimum,
               'ratio': contrast(tokens[a], tokens[b]),
               'pass': contrast(tokens[a], tokens[b]) >= minimum}
              for a, b, minimum in tests]
    return {
        'version': '1.0.0', 'mode': mode, 'tokens': tokens,
        'canvas': {'width_in': 13.333333, 'height_in': 7.5, 'margin_in': 0.55},
        'typography': {'family': font, 'east_asian_family': font,
                       'cover_pt': 44, 'title_pt': 34, 'body_pt': 24,
                       'annotation_pt': 20, 'citation_pt': 12},
        'semantic_map': {}, 'contrast_checks': checks,
        'adjustments': {key: value for key, value in tokens.items()
                        if key in ('primary', 'primary_ink') and value != preferred},
        'font_verified': False,
        'limitations': ['Font existence and glyph coverage are not verified by this script.',
                        'Tint mixing is RGB interpolation, not perceptual palette optimization.',
                        'Contrast tests do not certify color-vision or projection readability.',
                        'Inspect actual text/mark pairs on images, surfaces, and charts separately.'],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--accent', default='#2457C5')
    parser.add_argument('--secondary')
    parser.add_argument('--mode', choices=('light', 'dark'), default='light')
    parser.add_argument('--font', default='Noto Sans CJK KR')
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    try:
        theme = make_theme(args.accent, args.mode, args.font, args.secondary)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(theme, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'Wrote {args.out}. Font and final-slide visual checks remain required.')
        return 0
    except (ValueError, OSError) as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
