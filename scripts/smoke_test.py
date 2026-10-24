#!/usr/bin/env python3
"""Build a three-slide Korean/English fixture, not a research presentation."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import pymupdf
from make_theme import make_theme
from crop_pdf import crop_pdf
from pptx_helpers import (new_deck, add_slide, add_text, add_rect,
                          add_picture_contain, set_notes, save_deck)
from check_deck import check_deck
from render_deck import render_deck
from preflight import font_inventory


def fixture_pdf(path: Path) -> None:
    doc = pymupdf.open()
    page = doc.new_page(width=720, height=405)
    page.insert_text((45, 30), 'SYNTHETIC FIXTURE - NOT RESEARCH EVIDENCE', fontsize=16)
    for x, label in [(80, 'Input'), (290, 'Transform'), (500, 'Output')]:
        page.draw_rect(pymupdf.Rect(x, 110, x + 140, 240), color=(0.1, 0.1, 0.1), width=2)
        page.insert_text((x + 14, 180), label, fontsize=20)
    for left, right in [(220, 290), (430, 500)]:
        page.draw_line(pymupdf.Point(left, 175), pymupdf.Point(right, 175), width=2)
        page.draw_line(pymupdf.Point(right - 10, 168), pymupdf.Point(right, 175), width=2)
        page.draw_line(pymupdf.Point(right - 10, 182), pymupdf.Point(right, 175), width=2)
    page.insert_text((70, 320), 'Fig. 1 | Synthetic vector panel for extraction only.', fontsize=18)
    doc.save(path)
    doc.close()


def main() -> int:
    from preflight import configure_console
    configure_console()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', required=True, type=Path)
    parser.add_argument('--font')
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--soffice')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    try:
        output = args.out_dir.resolve()
        output.mkdir(parents=True, exist_ok=True)
        if not args.overwrite and any((output / name).exists() for name in
                                      ('smoke-test.pptx', 'smoke-test.speaker-notes.md')):
            raise FileExistsError('Use a fresh smoke-test output directory or --overwrite.')
        font = args.font
        if not font:
            candidates = font_inventory().get('korean_candidates_found', [])
            if not candidates:
                raise RuntimeError('No verified Korean font candidate found; supply --font after checking inventory.')
            font = candidates[0]
        theme = make_theme('#6D28D9', font=font)
        (output / 'theme.json').write_text(json.dumps(theme, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        source = output / 'synthetic-source.pdf'
        fixture_pdf(source)
        crop = output / 'synthetic-panel.png'
        crop_pdf(source, 1, [0.07, 0.16, 0.94, 0.86], 200, crop,
                 'FIXTURE01', 'Synthetic Fig. 1; not scientific evidence')
        prs, notes = new_deck(theme), []
        slide = add_slide(prs, theme, '학회 발표 스킬 · 출력 점검', 1,
                          citation='기능 점검용 예시입니다. 실제 연구 결과가 아닙니다.')
        add_text(slide, '편집 가능한 텍스트와 도형', 0.58, 1.85, 12.1, 0.8,
                 theme, size=32, bold=True, fill=theme['tokens']['primary_ink'])
        add_text(slide, '한글과 English · μ ± − Δ α β', 0.58, 2.80, 12.1, 0.8, theme, size=28)
        for x, label in [(0.65, '논지 개요'), (4.75, '제작'), (8.85, '검수')]:
            add_rect(slide, x, 4.15, 3.65, 1.1, theme['tokens']['primary_soft'],
                     line=theme['tokens']['primary'], name='workflow-step')
            add_text(slide, label, x + 0.22, 4.39, 3.18, 0.62, theme, size=28, bold=True)
        notes.append(set_notes(slide, slide_id='S01', title='학회 발표 스킬 · 출력 점검',
             objective='기본 글꼴과 네이티브 편집 요소의 출력을 확인한다.',
             explanation='이 슬라이드는 연구 내용이 아니라 도구 점검용 자료입니다. 한글과 기호를 확인합니다.',
             cue='두 번째 줄의 한글·영어·그리스 문자와 하단 도형을 확인한다.',
             transition='다음 장에서 PDF 패널 삽입을 확인합니다.', seconds=30,
             source='자체 생성한 기능 점검 자료. 연구 결과가 아님.'))
        slide = add_slide(prs, theme, 'PDF 패널을 비율 그대로\n삽입합니다', 2,
                          citation='출처: 자체 생성 synthetic-source.pdf, Fig. 1. 연구 근거가 아닙니다.')
        assert slide.content_top > 1.85
        add_picture_contain(slide, crop, 0.65, slide.content_top, 12.0, 6.8 - slide.content_top)
        notes.append(set_notes(slide, slide_id='S02', title='PDF 패널을 비율 그대로\n삽입합니다',
             objective='벡터 PDF 패널의 래스터 추출 및 비율 보존을 확인한다.',
             explanation='원본에 있던 도형, 연결선, 레이블과 캡션이 유지되어야 합니다.',
             cue='입력·변환·출력 레이블과 하단 캡션을 확인한다.',
             transition='마지막으로 Q&A용 화면을 확인합니다.', seconds=30,
             source='FIXTURE01, synthetic-source.pdf, p. 1, synthetic Fig. 1.'))
        slide = add_slide(prs, theme, '핵심 메시지를 남긴 채 질문을 받습니다', 3,
                          citation='기능 점검용 take-home 화면 · 실제 학술 내용은 원자료에 근거해야 합니다.')
        slide._element.set('show', '0')
        add_text(slide, '근거는 크게, 설명은 발표 노트로', 0.58, 2.05, 12.0, 1.0,
                 theme, size=36, bold=True, fill=theme['tokens']['primary_ink'])
        add_text(slide, '결과 파일 생성과 검수 완료를 구분합니다.', 0.58, 3.45, 12.0, 0.8,
                 theme, size=28)
        add_text(slide, 'Questions?', 0.58, 5.35, 12.0, 0.8, theme, size=30)
        notes.append(set_notes(slide, slide_id='S03', title='핵심 메시지를 남긴 채 질문을 받습니다',
             objective='최종 화면과 발표 노트 저장을 확인한다.',
             explanation='슬라이드 렌더링이 끝나도 시각 검수와 과학적 검수는 별도로 수행합니다.',
             cue='핵심 문장과 Questions를 확인한다.', transition='질문을 받는다.',
             seconds=20, source='기능 점검 예시. 실제 발표자료의 검증을 대신하지 않음.'))
        destination = output / 'smoke-test.pptx'
        save_deck(prs, destination, notes, overwrite=args.overwrite)
        assert destination.with_name('smoke-test.speaker-notes.md').is_file()
        from regression_checks import run_checks
        run_checks(output / 'regression', theme, overwrite=args.overwrite)
        structural = check_deck(destination)
        (output / 'structural-qa.json').write_text(json.dumps(structural, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        if structural['errors']:
            raise RuntimeError(f"Structural errors: {structural['errors']}")
        if args.render:
            rendered = output / 'rendered'
            rendered.mkdir(exist_ok=True)
            sentinel = rendered / 'slide-user.png'
            sentinel.write_bytes(b'unrelated file')
            report = render_deck(destination, rendered, soffice=args.soffice, overwrite=args.overwrite)
            assert report['rendered_pages'] == 3
            render_deck(destination, rendered, soffice=args.soffice, overwrite=True)
            assert sentinel.read_bytes() == b'unrelated file'
        print(f'Created {destination} with three embedded notes records. '
              'Open the rendered images before claiming visual QA.')
        return 0
    except Exception as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
