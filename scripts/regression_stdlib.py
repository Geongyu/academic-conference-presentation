#!/usr/bin/env python3
"""Run discovery, encoding and plan regressions without optional rendering packages."""
from __future__ import annotations
import argparse
import io
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
from make_theme import make_theme
from plan_check import check_plan, speaking_seconds
from preflight import configure_console, font_inventory, resolve_soffice


def run_checks(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for result in [ValueError('font decoding failed'), subprocess.CompletedProcess([], 0, None, None)]:
        with patch('preflight.shutil.which', return_value='fc-list'), patch(
                'preflight.subprocess.run', side_effect=result if isinstance(result, Exception) else None,
                return_value=result):
            assert 'korean_candidates_found' in font_inventory()
    inventory = font_inventory()
    assert 'Malgun Gothic' in inventory['korean_candidates_found']
    assert Path(resolve_soffice()).is_file()
    with patch('preflight.shutil.which', return_value=None):
        assert Path(resolve_soffice()).is_file()
        assert 'Malgun Gothic' in font_inventory()['korean_candidates_found']
    theme = make_theme()
    assert theme['typography']['family'] in inventory['korean_candidates_found']
    for stream_name in ('stdout', 'stderr'):
        stream = io.TextIOWrapper(io.BytesIO(), encoding='cp949')
        with patch('sys.' + stream_name, stream):
            configure_console()
            print('Fig. 2 — μ ± −', file=stream)
            stream.flush()
    (output / 'theme.json').write_text(json.dumps(theme), encoding='utf-8')
    evidence = {'sources': [], 'claims': [], 'assets': []}
    plan = {'revision': 'v1', 'theme_file': 'theme.json', 'available_speaking_seconds': 100,
            'target_speaking_seconds': 90,
            'approval': {'status': 'approved', 'instruction_evidence': 'fixture', 'approved_revision': 'v1'},
            'slides': [{'id': 'S01', 'main_or_backup': 'main', 'title': 'Fixture', 'purpose': 'test',
                        'claim_ids': [], 'evidence_locators': [], 'layout': 'Blank', 'visual_assets': [],
                        'estimated_seconds': 95, 'notes': {'language': 'en', 'objective': 'Test',
                        'explanation': 'word ' * 140, 'visual_cue': 'None', 'transition': 'End',
                        'source_and_caveats': 'Self-generated'}}]}
    pp, ep = output / 'slide-plan.json', output / 'evidence-map.json'
    ep.write_text(json.dumps(evidence), encoding='utf-8')

    def check():
        pp.write_text(json.dumps(plan), encoding='utf-8')
        return check_plan(pp, ep)

    report = check()
    assert report['status'] == 'PASS' and any('exceeds budget' in w for w in report['warnings'])
    plan['slides'][0]['claim_ids'] = ['C99']
    assert any('C99' in e for e in check()['errors'])
    plan['slides'][0]['claim_ids'] = []
    plan['slides'][0]['visual_assets'] = ['A99']
    assert any('A99' in e for e in check()['errors'])
    plan['slides'][0]['visual_assets'] = []
    evidence['assets'] = [{'id': 'A01', 'source_id': 'SRC99', 'locator': 'line 1',
                           'path': 'missing.png', 'transformation': 'cropped',
                           'caption_checked': False, 'scientific_context_preserved': False}]
    ep.write_text(json.dumps(evidence), encoding='utf-8')
    asset_errors = check()['errors']
    assert any('SRC99' in e for e in asset_errors) and any('missing.png' in e for e in asset_errors)
    evidence['assets'] = []
    ep.write_text(json.dumps(evidence), encoding='utf-8')
    plan['theme_file'] = 'missing.json'
    assert any('local file missing' in e for e in check()['errors'])
    plan['theme_file'] = 'theme.json'
    plan['approval']['approved_revision'] = 'old'
    assert any('approved_revision' in e for e in check()['errors'])
    plan['approval']['approved_revision'] = 'v1'
    plan['slides'][0]['title'] = '<title>'
    assert any('placeholder' in e for e in check()['errors'])
    plan['slides'][0]['title'] = 'Fixture'
    plan['slides'][0]['main_or_backup'] = 'backup'
    assert check()['main_seconds'] == 0
    plan['slides'][0]['main_or_backup'] = 'main'
    plan['slides'][0]['estimated_seconds'] = 80
    assert check()['status'] == 'PASS'
    assert 55 < speaking_seconds('가' * 325, 'ko')[0] < 56
    assert speaking_seconds('word ' * 140, 'en')[1] > 64
    (output / 'stdlib-report.json').write_text(json.dumps({'status': 'PASS',
        'font': theme['typography']['family'], 'soffice': resolve_soffice(),
        'checks': ['font failure and None stdout', 'cp949 output', 'automatic font and soffice',
                   'plan references/assets/approval/placeholders/budget', 'speaking time ranges']},
        ensure_ascii=False, indent=2), encoding='utf-8')


def main() -> int:
    configure_console()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', required=True, type=Path)
    args = parser.parse_args()
    run_checks(args.out_dir)
    print('Standard-library regressions PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
