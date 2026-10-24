# Production route and operational recipes

## 1. Backend decision

Use the user's requested native environment when supported by available tools.
Otherwise this package's default is Python + python-pptx for an editable PPTX,
LibreOffice for PPTX-to-PDF conversion, and PyMuPDF for slide PNGs. This makes
the fallback path explicit; it is not a claim that python-pptx renders slides.

A host-provided PptxGenJS, artifact, or native slides backend may replace authoring
when required by the host or explicitly chosen. Read its actual available API;
do not invent tools, speaker-notes methods, or export support. Record the route.
The evidence map, approval, notes, and QA contract do not change with backend.
If cloud slides were explicitly requested but access fails, disclose failure
before offering a local alternative. Do not silently create a cloud copy.

Keep all paths relative to the skill root or supplied project directory. The
helpers contain no private agent installation paths. Do not automatically upload
source papers or data to conversion services. Preserve originals and use a new
output directory for each revision.

## 2. Preflight and environment

Run from the skill directory:

```bash
python scripts/preflight.py
```

Check Python, package imports, a real renderer, and installed font families.
The requirements file describes the local helper route. Package installation is
a separate authorized environment setup step, not a substitute for preflight:

```bash
python -m pip install -r requirements.txt
```

LibreOffice is an external application and is not installed by pip. Use an
available PowerPoint or platform renderer instead when LibreOffice is absent.
Without a renderer, retain `visual_render: NOT_RUN`; do not claim verification.
If no authoring tool exists, deliver only a clearly labeled plan rather than a
pretend PPTX. Missing user-supplied source files are not a reason to invent data.

## 3. Project inputs

Copy and fill `assets/brief.template.json`, `assets/slide-plan.template.json`,
and `assets/evidence-map.template.json` into a new working project. Do not leave
angle-bracket placeholders in a deck labeled final. Keep main/backup identity,
source IDs, timings, notes, and approval evidence explicitly in the plan.
A slide-plan template is a data contract for the agent, not an automatic parser
for arbitrary academic papers. The agent must actually read sources and design
the layouts.

```bash
python scripts/make_theme.py --accent '#6D28D9'   --mode light --font 'Noto Sans CJK KR' --out work/theme.json
```

`make_theme.py` accepts six-digit HEX colors. Convert named color requests into
HEX before invoking it. Font inventory verification remains a separate step.
Its RGB tint mixing is deterministic, not perceptually uniform palette
optimization. Inspect scientific charts separately.

## 4. PDF figure workflow

First inspect the relevant page and caption using the host's PDF/page-view tool.
With only local tools, render a page with PyMuPDF and open the PNG. OCR is a last
resort for image-only sources; do not OCR an already readable digital paper.

A PDF figure may contain vector curves, text, and multiple raster objects.
Extracting a single embedded image is therefore not always extraction of the
complete figure. The default helper renders an explicitly inspected page region
as a single PNG, preserving labels within that region:

```bash
python scripts/crop_pdf.py --pdf source/paper.pdf --page 4   --box 0.08 0.20 0.94 0.72 --dpi 300   --source-id SRC01 --locator 'Fig. 2b; caption checked on p. 4'   --out work/assets/fig-2b.png
```

`--page` is **one-based**. `--box` is normalized `left top right bottom` relative
to the displayed page rectangle, each value between 0 and 1. Default is the
whole page. The script records the PDF SHA-256, page, region, DPI, and locator
beside the output as `.source.json`; this provenance is not a scientific review.
Render at a resolution appropriate to final placement; do not imply upsampling
creates missing detail. Match the original figure and preserve aspect ratio.

When a journal supplies the exact standalone figure, prefer that source if it
retains labels and resolution. Use vector insertion only with a tested backend
and render path; otherwise a high-resolution faithful raster is safer than a
broken SVG. Crop/eliminate whitespace, not interpretive context. Keep the
original source; no destructive edits. For charts, replot only from verified
data with the same values, appropriate scales, units, and uncertainty.

## 5. Build an editable deck

Create a project-specific `build_deck.py`. The bundled helpers provide a thin
production skeleton, not a universal layout engine. They support native text
and shapes, contain-fit images, East Asian font runs, and embedded/sidecar notes.
Adapt or extend layouts to the approved plan instead of forcing every slide
into the example layout. Use native table/chart APIs for suitable verified data.

A minimal runnable authoring example is `scripts/smoke_test.py`. Typical usage:

```python
import json
from pathlib import Path
from pptx_helpers import new_deck, add_slide, add_text, set_notes, save_deck

theme = json.loads(Path('work/theme.json').read_text(encoding='utf-8'))
prs = new_deck(theme)
slide = add_slide(prs, theme, 'A source-supported slide title', number=1)
add_text(slide, 'Explain one point, then show the evidence.',
         x=0.6, y=1.7, w=12.1, h=1.1, theme=theme)
notes = set_notes(slide, slide_id='S01', title='A source-supported slide title',
                  objective='State the research question.',
                  explanation='Replace this example with sourced explanation.',
                  cue='Point to the main evidence.',
                  transition='Next, explain how the question was tested.',
                  seconds=60, source='Replace with a verified source locator.')
save_deck(prs, Path('work/presentation.pptx'), [notes])
```

Place `scripts/` on the Python module path or import it explicitly from the
skill directory. Helpers never assert that text fits merely because a textbox
exists. No text-autofit shrinking is applied. Set East Asian fonts on any new
runs added by project code, including native chart/table text. If an equation
needs a renderer not available locally, use a faithful source equation image;
retain its editable source expression in the project when available and report
that the placed equation is rasterized.

## 6. Speaker notes

`set_notes` writes to `slide.notes_slide.notes_text_frame.text` and returns the
same content for `speaker-notes.md`. The helper fails rather than silently dropping
notes if a template lacks the required notes placeholder. For alternative native
backends, verify notes survive export; otherwise deliver the sidecar and report
that embedded notes are missing.

Notes are speech support, not pasted manuscript paragraphs. Include the slide's
purpose, a concise explanation, a visual pointer, the transition, timing, and
source/caveats. Korean slides can have English notes or vice versa when requested.
Do not hide sensitive internal comments in notes of a distributable deck.

## 7. Render and inspect

```bash
python scripts/check_deck.py work/presentation.pptx   --out work/structural-qa.json
python scripts/render_deck.py work/presentation.pptx   --out-dir work/rendered --dpi 150
```

For a new revision, use a fresh output directory or pass `--overwrite` to
replace only the renderer-owned PDF, PNGs, and render report in that directory.

The renderer invokes LibreOffice with an isolated temporary profile and a fresh
conversion directory, checks that a new PDF was produced, compares slide/page
counts, renders all pages, and makes contact sheets. Supply `--soffice PATH` when
needed. It uses no shell interpolation. Nonzero exits must be handled, not ignored.

Open each PNG at full inspection size, not only the montage. Fix the source deck
and regenerate its PDF/PNGs; never patch only the preview. The resulting PDF is
an audience-facing slide export, not a speaker-notes PDF. Copy it to the agreed
final destination only after inspecting the final revision. Record renderer
name/version and note that different PowerPoint installations can render fonts
or equations differently.

## 8. Release layout

```text
project/
  presentation.pptx
  presentation.pdf          # only when actually exported
  speaker-notes.md
  outline.md
  qa-report.md
  source/                    # supplied material; exclude private files from public delivery
  build_deck.py
  brief.json
  slide-plan.json
  evidence-map.json
  theme.json
  assets/
  rendered/
```

Keep private sources and full-resolution originals in the working project unless
sharing them is authorized. A reproducibility bundle can contain source locators
and hashes without redistributing papers, patient data, or licensed font files.
