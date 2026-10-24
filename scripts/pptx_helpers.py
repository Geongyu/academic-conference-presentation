"""Thin editable-PPTX primitives. They do not guarantee layout or source accuracy."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import math
import os
import tempfile
import unicodedata
import warnings
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt


def color(value: str) -> RGBColor:
    return RGBColor.from_string(value.lstrip('#'))


def set_run_font(run: Any, family: str, east_asian_family: str | None = None,
                 lang: str = 'ko-KR') -> None:
    """Set Latin and East Asian OOXML typefaces; does not install/embed fonts."""
    run.font.name = family
    rpr = run._r.get_or_add_rPr()
    set_font_properties(rpr, family, east_asian_family, lang)


def set_font_properties(rpr: Any, family: str, east_asian_family: str | None = None,
                         lang: str = 'ko-KR') -> None:
    """Apply typefaces/language to run or paragraph-default properties."""
    rpr.set('lang', lang)
    for tag, face in [('a:latin', family), ('a:ea', east_asian_family or family), ('a:cs', family)]:
        child = rpr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}' + tag.split(':')[1])
        if child is None:
            child = OxmlElement(tag)
            rpr.append(child)
        child.set('typeface', face)


def new_deck(theme: dict, template: Path | str | None = None) -> Any:
    prs = Presentation(str(template)) if template else Presentation()
    prs._academic_template = template is not None
    if template is None:
        prs.slide_width = Inches(theme['canvas']['width_in'])
        prs.slide_height = Inches(theme['canvas']['height_in'])
    return prs


def estimate_lines(text: str, width: float, size: float) -> int:
    """Conservative width estimate, not a font shaping engine."""
    capacity = max(1, (width - 0.04) * 72 / size)
    return sum(max(1, math.ceil(sum(1 if unicodedata.east_asian_width(c) in ('W', 'F')
                                  else 0.55 for c in line) / capacity))
               for line in text.split('\n'))


def add_text(slide: Any, text: str, x: float, y: float, w: float, h: float,
             theme: dict, size: float | None = None, bold: bool = False,
             fill: str | None = None, align: Any = PP_ALIGN.LEFT,
             name: str = 'body', vertical: Any = MSO_ANCHOR.TOP) -> Any:
    if w <= 0 or h <= 0:
        raise ValueError('Text box width and height must be positive.')
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    box.name = name
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = Inches(0.02)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = vertical
    for index, line in enumerate(str(text).split('\n')):
        paragraph = tf.paragraphs[0] if index == 0 else tf.add_paragraph()
        paragraph.alignment = align
        paragraph.space_after = Pt(4)
        run = paragraph.add_run()
        run.text = line
        run.font.size = Pt(size or theme['typography']['body_pt'])
        run.font.bold = bold
        run.font.color.rgb = color(fill or theme['tokens']['text'])
        set_run_font(run, theme['typography']['family'], theme['typography']['east_asian_family'],
                     theme['typography'].get('language', 'ko-KR'))
    return box


def add_rect(slide: Any, x: float, y: float, w: float, h: float, fill: str,
             line: str | None = None, name: str = 'shape') -> Any:
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.name = name
    # Override any default theme shadow; keep scientific layouts flat.
    sppr = shape._element.spPr
    if sppr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}effectLst') is None:
        sppr.append(OxmlElement('a:effectLst'))
    style = shape._element.find('{http://schemas.openxmlformats.org/presentationml/2006/main}style')
    if style is not None:
        effect = style.find('{http://schemas.openxmlformats.org/drawingml/2006/main}effectRef')
        if effect is not None:
            effect.set('idx', '0')
    shape.fill.solid()
    shape.fill.fore_color.rgb = color(fill)
    if line:
        shape.line.color.rgb = color(line)
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape


def add_slide(prs: Any, theme: dict, title: str, number: int | None = None,
              citation: str = '', layout_name: str | None = None,
              override_background: bool | None = None) -> Any:
    layouts = list(prs.slide_layouts)
    if layout_name:
        layout = next((item for item in layouts if item.name == layout_name), None)
        if layout is None:
            raise ValueError(f'Unknown layout: {layout_name}')
    else:
        layout = next((item for item in layouts if item.name == 'Title Only'), None)
        layout = layout or next((item for item in layouts if item.name == 'Blank'), layouts[0])
    slide = prs.slides.add_slide(layout)
    if override_background is True or (override_background is None and not getattr(prs, '_academic_template', False)):
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = color(theme['tokens']['background'])
    width, height = prs.slide_width / Inches(1), prs.slide_height / Inches(1)
    margin = theme['canvas']['margin_in']
    size = theme['typography']['title_pt']
    lines = estimate_lines(title, width - 2 * margin, size)
    title_height = max(1.02, lines * (size * 1.25 + 4) / 72 + 0.04)
    if lines > 2 or title_height > height * 0.35:
        warnings.warn(f'Title needs about {lines} lines; shorten it and inspect rendering.')
    box = add_text(slide, title, margin, 0.40, width - 2 * margin, title_height, theme,
                   size=size, bold=True, name='title')
    placeholder = slide.shapes.title
    if placeholder is not None:
        placeholder.left, placeholder.top = box.left, box.top
        placeholder.width, placeholder.height = box.width, box.height
        old = placeholder._element.find('{http://schemas.openxmlformats.org/presentationml/2006/main}txBody')
        from copy import deepcopy
        placeholder._element.replace(old, deepcopy(box._element.txBody))
        box._element.getparent().remove(box._element)
        placeholder.name = 'title'
    accent_y = 0.40 + title_height + 0.06
    add_rect(slide, margin, accent_y, 0.62, 0.045, theme['tokens']['primary'], name='title-accent')
    slide.content_top = max(1.85, accent_y + 0.25)
    if citation:
        add_text(slide, citation, margin, height - 0.40, width - 2 * margin - 0.70,
                 0.28, theme, size=theme['typography']['citation_pt'],
                 fill=theme['tokens']['muted_text'], name='citation')
    if number is not None:
        add_text(slide, str(number), width - margin - 0.50, height - 0.40,
                 0.50, 0.28, theme, size=12, fill=theme['tokens']['muted_text'],
                 align=PP_ALIGN.RIGHT, name='slide-number')
    return slide


def add_title_slide(prs: Any, theme: dict, title: str, subtitle: str = '',
                    affiliation: str = '', venue: str = '') -> Any:
    """Add an undecorated cover; subtitle may contain authors, venue may include date."""
    layout = next((item for item in prs.slide_layouts if item.name == 'Blank'), prs.slide_layouts[0])
    slide = prs.slides.add_slide(layout)
    for placeholder in list(slide.placeholders):
        placeholder._element.getparent().remove(placeholder._element)
    if not getattr(prs, '_academic_template', False):
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = color(theme['tokens']['background'])
    width, height = prs.slide_width / Inches(1), prs.slide_height / Inches(1)
    margin = theme['canvas']['margin_in']
    size = theme['typography']['cover_pt']
    title_h = max(1.2, estimate_lines(title, width - 2 * margin, size) * (size * 1.25 + 4) / 72 + 0.04)
    y = height * 0.18
    add_text(slide, title, margin, y, width - 2 * margin, title_h, theme,
             size=size, bold=True, name='title')
    y += title_h + 0.30
    for name, text in [('subtitle', subtitle), ('affiliation', affiliation), ('venue', venue)]:
        if text:
            size = theme['typography']['body_pt']
            h = max(0.5, estimate_lines(text, width - 2 * margin, size) * (size * 1.25 + 4) / 72 + 0.04)
            add_text(slide, text, margin, y, width - 2 * margin, h, theme, size=size, name=name)
            y += h + 0.16
    if y > height - margin:
        warnings.warn('Cover text may exceed slide height; shorten it and inspect rendering.')
    return slide


def add_picture_contain(slide: Any, image: Path, x: float, y: float,
                        w: float, h: float, name: str = 'source-figure') -> Any:
    image = Path(image)
    if not image.is_file():
        raise FileNotFoundError(f'Figure not found: {image}')
    with Image.open(image) as img:
        iw, ih = img.size
    if min(iw, ih, w, h) <= 0:
        raise ValueError('Image and target dimensions must be positive.')
    scale = min(w / iw, h / ih)
    fw, fh = iw * scale, ih * scale
    shape = slide.shapes.add_picture(str(image), Inches(x + (w - fw) / 2),
                                     Inches(y + (h - fh) / 2), Inches(fw), Inches(fh))
    shape.name = name
    return shape


def set_notes(slide: Any, *, slide_id: str, title: str, objective: str,
              explanation: str, cue: str, transition: str, seconds: int | float,
              source: str, backup: bool = False, language: str = 'ko') -> str:
    if seconds < 0:
        raise ValueError('Speaking-time estimate must be nonnegative.')
    if language not in ('ko', 'en'):
        raise ValueError('Notes language must be ko or en.')
    labels = (['설명', '연결', '목적', '가리킬 부분', '출처와 주의점', '유형', '예상 발화 시간(초)']
              if language == 'ko' else
              ['Explanation', 'Transition', 'Objective', 'Visual cue', 'Source and caveats', 'Type', 'Estimated seconds'])
    notes = '\n\n'.join(f'{label}\n{text}' for label, text in zip(labels[:5],
                         [explanation, transition, objective, cue, source]))
    # slide_id stays a parameter for plan bookkeeping but is not written: notes are read by the presenter.
    kind = ('백업' if backup else '본 발표') if language == 'ko' else ('backup' if backup else 'main')
    notes += f'\n\n{labels[5]}: {kind}\n{labels[6]}: {seconds:g}'
    notes = notes.replace('\r\n', '\n').replace('\r', '\n')
    frame = slide.notes_slide.notes_text_frame
    if frame is None:
        raise RuntimeError('No notes text placeholder. Supply a valid notes master or repair the template.')
    frame.text = notes
    return notes


def save_deck(prs: Any, destination: Path, notes: list[str], overwrite: bool = False) -> None:
    destination = Path(destination)
    if destination.suffix.lower() != '.pptx':
        raise ValueError('Presentation output must end with .pptx.')
    if len(notes) != len(prs.slides):
        raise ValueError('Provide one notes record per slide, including backup slides.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    sidecar = destination.with_name(destination.stem + '.speaker-notes.md')
    if not overwrite and (destination.exists() or sidecar.exists()):
        raise FileExistsError('Deck or notes sidecar exists; use overwrite=True to replace.')
    with tempfile.TemporaryDirectory(prefix='deck-save-', dir=destination.parent) as temp:
        staged = Path(temp) / destination.name
        prs.save(str(staged))
        verify_notes(staged, notes)
        staged_notes = Path(temp) / sidecar.name
        staged_notes.write_text('# Speaker notes\n\n' + '\n\n---\n\n'.join(notes) + '\n', encoding='utf-8')
        os.replace(staged, destination)
        os.replace(staged_notes, sidecar)


def normalize_notes(text: str) -> str:
    return text.replace('_x000D_', '\r').replace('\r\n', '\n').replace('\r', '\n')


def verify_notes(destination: Path, notes: list[str]) -> None:
    # Reopen to confirm actual packaging and embedded notes, not visual correctness.
    reopened = Presentation(str(destination))
    if len(reopened.slides) != len(notes):
        raise RuntimeError('Saved presentation slide count mismatch.')
    for index, (slide, expected) in enumerate(zip(reopened.slides, notes), 1):
        frame = slide.notes_slide.notes_text_frame if slide.has_notes_slide else None
        if frame is None or normalize_notes(frame.text) != normalize_notes(expected):
            raise RuntimeError(f'Embedded notes mismatch on slide {index}.')


def style_table(table: Any, theme: dict, size: float | None = None) -> Any:
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(size or theme['typography']['body_pt'])
                set_font_properties(paragraph._p.get_or_add_pPr().get_or_add_defRPr(),
                                    theme['typography']['family'], theme['typography']['east_asian_family'],
                                    theme['typography'].get('language', 'ko-KR'))
                for run in paragraph.runs:
                    run.font.size = paragraph.font.size
                    set_run_font(run, theme['typography']['family'], theme['typography']['east_asian_family'],
                                 theme['typography'].get('language', 'ko-KR'))
    return table


def add_rich_text(slide: Any, runs: list[dict], x: float, y: float, w: float, h: float,
                  theme: dict, size: float | None = None, name: str = 'body') -> Any:
    box = add_text(slide, '', x, y, w, h, theme, size=size, name=name)
    paragraph = box.text_frame.paragraphs[0]
    for item in runs:
        run = paragraph.add_run()
        run.text = item['text']
        run.font.size = Pt(item.get('size', size or theme['typography']['body_pt']))
        run.font.bold, run.font.italic = item.get('bold', False), item.get('italic', False)
        run.font.color.rgb = color(item.get('fill', theme['tokens']['text']))
        set_run_font(run, theme['typography']['family'], theme['typography']['east_asian_family'],
                     theme['typography'].get('language', 'ko-KR'))
    return box
