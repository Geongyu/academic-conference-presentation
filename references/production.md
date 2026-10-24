# Production route and operational recipes

## 1. Backend decision

Use the user's requested native environment when supported by available tools.
Otherwise this package's default is Python + python-pptx for an editable PPTX,
LibreOffice for PPTX-to-PDF conversion, and PyMuPDF for slide PNGs.

A host-provided PptxGenJS, artifact, or native slides backend may replace authoring
when required by the host or explicitly chosen. Read its actual available API;
do not invent tools, speaker-notes methods, or export support. Record the route.
The evidence map, approval, notes, and QA contract do not change with backend.
If cloud slides were explicitly requested but access fails, disclose failure
before offering a local alternative. Do not silently create a cloud copy.

## 2. Paths and shell

- `SKILL_DIR`: the folder containing `SKILL.md`. Read-only during a job.
- `PROJECT_DIR`: the user's working folder. Job inputs and all outputs live
  here (see the release layout below).

Run every command with `PROJECT_DIR` as the current directory and call bundled
scripts by absolute path. Replace `<SKILL_DIR>` with that absolute path and keep
the double quotes (paths may contain spaces). Each command is a single line with
double-quoted arguments, so it runs unchanged in bash, zsh, PowerShell, and cmd.
Output paths in the examples are relative to `PROJECT_DIR`.

Do not automatically upload source papers or data to conversion services.
Preserve originals and use a new output directory for each revision.

## 3. Preflight and environment

```bash
python "<SKILL_DIR>/scripts/preflight.py" --out "preflight.json"
```

Check Python, package imports, a real renderer, and installed font families.
Optional `--font "<family>"` reports whether that family is installed
(`fonts.requested_found`); `--soffice "<path>"` uses a specific LibreOffice.
Without `--soffice`, the renderer is searched on PATH, then in the standard
Windows (`%ProgramFiles%`, `%ProgramFiles(x86)%`) and macOS application folders.
On Windows the console `soffice.com` next to `soffice.exe` is preferred, also
when `soffice.exe` is given explicitly; an empty version string is recorded as
`unknown`. Fonts are read from Fontconfig, Windows font folders and registry,
or macOS font folders. Renderer status `AVAILABLE_NOT_TESTED` means found, not
yet used.
The requirements file describes the local helper route. Package installation is
a separate authorized environment setup step, not a substitute for preflight:

```bash
python -m pip install -r "<SKILL_DIR>/requirements.txt"
```

To test the helpers themselves on a new machine (outputs only in the given folder):

```bash
python "<SKILL_DIR>/scripts/smoke_test.py" --out-dir "<temp folder>" --render
python "<SKILL_DIR>/scripts/regression_checks.py" --out-dir "<temp folder>"
```

`smoke_test.py` builds a synthetic 3-slide deck (a 2-line title, a PDF crop, a
hidden slide), checks notes and the sidecar, renders it, and re-renders over the
existing output; it accepts `--font`, `--soffice`, and `--overwrite` (rerun in the
same folder). `regression_checks.py` needs python-pptx, PyMuPDF, and Pillow;
`regression_stdlib.py --out-dir "<temp folder>"` covers font/renderer detection,
plan checks, and console output with the standard library only. These test the
helpers, never a real talk.

LibreOffice is an external application and is not installed by pip. Use an
available PowerPoint or platform renderer instead when LibreOffice is absent.
Without a renderer, retain `visual_render: NOT_RUN`; do not claim verification.
If no authoring tool exists, deliver only a clearly labeled plan rather than a
pretend PPTX. Missing user-supplied source files are not a reason to invent data.

## 4. Project inputs

Copy `brief.template.json`, `slide-plan.template.json`, and
`evidence-map.template.json` from `<SKILL_DIR>/assets/` into `PROJECT_DIR` as
`brief.json`, `slide-plan.json`, and `evidence-map.json`, then fill them by
actually reading the sources. Do not leave angle-bracket placeholders in a deck
labeled final. Keep main/backup identity, source IDs, timings, notes, and
approval evidence explicitly in the plan.

| Supplied input | Use |
|---|---|
| PDF paper or manuscript | Read text and captions; inspect pages; crop figures with `crop_pdf.py` (section 5) |
| DOCX / ODT manuscript | Read text and tables directly; take figures from the embedded originals, not page screenshots |
| Existing PPTX (earlier talk, lab deck) | Reuse only content re-verified against the paper; a required venue/lab template goes to the builder |
| LaTeX source / Overleaf export | Equations, numbers, and captions from `.tex`; figures from the files it includes |
| Original figure files (PNG, TIFF, SVG, PDF) | Prefer over PDF crops when labels and resolution are kept; rasterize SVG unless the render path is tested |
| Data tables (CSV, XLSX) | Native table or replot only from these values; locator = file, sheet, range |

Record each input's version or hash in `evidence-map.json`. When several forms of
the same study disagree, ask which one is authoritative.

Check the plan before the approval checkpoint and again after building:

```bash
python "<SKILL_DIR>/scripts/plan_check.py" --plan "slide-plan.json" --evidence "evidence-map.json" --out "plan-check.json"
python "<SKILL_DIR>/scripts/plan_check.py" --plan "slide-plan.json" --evidence "evidence-map.json" --pptx "presentation.pptx" --out "plan-check.json"
```

It checks required fields, duplicate or unknown IDs, `SRC` prefixes of evidence
locators, existence of local sources, assets, and `theme_file`, leftover
`<...>`/`[NEEDS SOURCE]`/`[TBD]`/`[TODO]` markers, approval consistency, and the
main-slide time budget (min of `target_speaking_seconds` and 90% of
`available_speaking_seconds`; backup excluded). With `--pptx` it also compares
slide count, titles, and the planned explanation/transition inside each note.
Asset and source paths resolve relative to the evidence-map folder, `theme_file`
relative to the plan folder. Exit codes: `0` no errors (warnings possible),
`1` validation errors, `2` unreadable or malformed input. `pending` approval
is a warning; `approved` without `instruction_evidence` and an
`approved_revision` equal to `revision` is an error. Notes-length timing is an
approximation (Korean 300–350 syllables/min, English 130–150 words/min, from
explanation + transition only), not rehearsal. List the cover and every backup
slide in `slide-plan.json` in deck order, or the `--pptx` comparison reports a
count/title mismatch.

```bash
python "<SKILL_DIR>/scripts/make_theme.py" --accent "#6D28D9" --mode light --font "<installed family>" --out "theme.json"
```

`make_theme.py` accepts six-digit HEX colors. Convert named color requests into
HEX before invoking it. If `--font` is omitted it uses the first detected Korean
candidate, or warns and writes `sans-serif` when none is found; always confirm
the chosen family against the preflight inventory. `typography.language`
defaults to `ko-KR` and sets the run language; edit it in `theme.json` for other
slide languages.
Inspect scientific charts separately from the palette tokens.

## 5. PDF figure workflow

First inspect the relevant page and caption using the host's PDF/page-view tool.
With only local tools, render a page with PyMuPDF and open the PNG. OCR is a last
resort for image-only sources; do not OCR an already readable digital paper.

A PDF figure may contain vector curves, text, and multiple raster objects.
Extracting a single embedded image is therefore not always extraction of the
complete figure. The default helper renders an explicitly inspected page region
as a single PNG, preserving labels within that region:

```bash
python "<SKILL_DIR>/scripts/crop_pdf.py" --pdf "source/paper.pdf" --page 4 --box 0.08 0.20 0.94 0.72 --dpi 300 --source-id SRC01 --locator "Fig. 2b; caption checked on p. 4" --out "assets/fig-2b.png"
```

`--page` is **one-based**. `--box` is normalized `left top right bottom` relative
to the displayed page rectangle, each value between 0 and 1. Default is the
whole page. The script records the PDF SHA-256, page, region, DPI, and locator
beside the output as `.source.json` (provenance only).
Render at a resolution appropriate to final placement; do not imply upsampling
creates missing detail. Match the original figure and preserve aspect ratio.

When a journal supplies the exact standalone figure, prefer that source if it
retains labels and resolution. Use vector insertion only with a tested backend
and render path; otherwise a high-resolution faithful raster is safer than a
broken SVG. Crop/eliminate whitespace, not interpretive context. Keep the
original source; no destructive edits. For charts, replot only from verified
data with the same values, appropriate scales, units, and uncertainty.

## 6. Build an editable deck

Create `PROJECT_DIR/build_deck.py`. The bundled helpers are a thin skeleton for
native text and shapes, contain-fit images, East Asian font runs, and
embedded/sidecar notes. Adapt or extend layouts to the approved plan instead of
forcing every slide into the example layout. Use native table/chart APIs for
suitable verified data. A minimal runnable example is `scripts/smoke_test.py`.

Start `build_deck.py` with this header. It imports the helpers from `SKILL_DIR`
without writing `__pycache__` there and resolves all outputs in `PROJECT_DIR`:

```python
import json, sys
from pathlib import Path

SKILL_DIR = Path(r"<SKILL_DIR>")          # absolute path of the folder with SKILL.md
PROJECT_DIR = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(SKILL_DIR / "scripts"))
from pptx_helpers import new_deck, add_title_slide, add_slide, add_text, set_notes, save_deck

theme = json.loads((PROJECT_DIR / "theme.json").read_text(encoding="utf-8"))
prs = new_deck(theme)                     # or new_deck(theme, template=PROJECT_DIR / "venue.pptx")
notes = []
cover = add_title_slide(prs, theme, 'Talk title', subtitle='A. Author, B. Author',
                        affiliation='Institution', venue='Conference 2026, Seoul')
notes.append(set_notes(cover, slide_id='S00', title='Talk title', objective='Open the talk.',
                       explanation='Introduce the question in one sentence.', cue='Title.',
                       transition='First, the problem.', seconds=20,
                       source='Author et al., 2026.', language='en'))
slide = add_slide(prs, theme, 'A source-supported slide title', number=1)
add_text(slide, 'Explain one point, then show the evidence.',
         x=0.6, y=slide.content_top, w=12.1, h=1.1, theme=theme)
notes.append(set_notes(slide, slide_id='S01', title='A source-supported slide title',
                       objective='State the research question.',
                       explanation='Replace this example with sourced explanation.',
                       cue='Point to the main evidence.',
                       transition='Next, explain how the question was tested.',
                       seconds=60, source='Author et al., 2026, Fig. 2.', language='en'))
save_deck(prs, PROJECT_DIR / "presentation.pptx", notes)   # overwrite=True to replace
```

Run it from `PROJECT_DIR` with `python "build_deck.py"`.

Helper reference (`scripts/pptx_helpers.py`):

| Helper | Behavior |
|---|---|
| `new_deck(theme, template=None)` | Without a template: blank 16:9 deck from `theme.canvas`. With a `.pptx` template: keeps its masters, layouts, slide size, and existing slides (not deleted automatically; remove or reuse them deliberately) |
| `add_title_slide(prs, theme, title, subtitle='', affiliation='', venue='')` | Cover on the Blank layout: title at `typography.cover_pt`, no accent bar, citation, or number. `subtitle` may hold authors, `venue` the event and date. Warns when the cover may overflow |
| `add_slide(prs, theme, title, number=None, citation='', layout_name=None, override_background=None)` | Content slide. Layout by exact name (`ValueError` if unknown), default `Title Only` → `Blank` → first layout. Uses the layout's title placeholder when present. Background is filled from the theme for plain decks, preserved for templates; `True`/`False` forces either |
| `slide.content_top` | Inches; top of the free body area below the (possibly wrapped) title and accent bar. Place body content from here. Exists only during the build, not after reopening the PPTX. Long titles trigger a warning |
| `add_text`, `add_rich_text(slide, runs, x, y, w, h, theme, size=None, name='body')` | Text boxes with Latin and East Asian fonts and language set. `runs` is a list of dicts: `text` plus optional `bold`, `italic`, `size`, `fill` |
| `style_table(table, theme, size=None)` | Applies theme font, size (default `body_pt`), and language to every cell of a native table |
| `add_picture_contain` | Contain-fit image, aspect ratio preserved |
| `set_notes(slide, *, slide_id, title, objective, explanation, cue, transition, seconds, source, backup=False, language='ko')` | See section 7 |
| `save_deck(prs, path, notes, overwrite=False)` | One notes record per slide (backup included). Refuses with `FileExistsError` when the PPTX or its sidecar exists unless `overwrite=True`. Saves to a temp file, reopens and verifies embedded notes, then replaces the PPTX and writes `<deck-stem>.speaker-notes.md`. Each file is replaced atomically, not both as one transaction |

To hide a backup slide in slideshow mode, set `slide._element.set('show', '0')`;
the QA render still includes hidden slides. No text-autofit shrinking is applied. Set East Asian fonts on any new
runs added by project code, including native chart/table text. If an equation
needs a renderer not available locally, use a faithful source equation image;
retain its editable source expression in the project when available and report
that the placed equation is rasterized.

## 7. Speaker notes

`set_notes` writes to `slide.notes_slide.notes_text_frame.text` and returns the
same text; `save_deck` writes all returned notes to `<deck-stem>.speaker-notes.md`
(`presentation.speaker-notes.md` for `presentation.pptx`). Field order:
explanation, transition, objective, visual cue, source and caveats, then
`Type: main|backup` and estimated seconds. `language='ko'` (default) gives
Korean labels (`유형: 본 발표|백업`); pass `language='en'` for English notes.
`slide_id` and `title` are kept for bookkeeping and are not written into the
note. The helper fails rather than silently dropping notes if a template lacks
the required notes placeholder. For alternative native
backends, verify notes survive export; otherwise deliver the sidecar and report
that embedded notes are missing.

Notes are speech support, not pasted manuscript paragraphs. Include the slide's
purpose, a concise explanation, a visual pointer, the transition, timing, and
source/caveats. Korean slides can have English notes or vice versa when requested.
Korean notes follow `korean-writing.md`. Field contents are what the presenter
says: never agent reasoning, work memos, internal IDs, file paths, or sensitive
comments, in any language. Write `source` as a reader-facing citation
(author, year, figure/page), not an evidence-map ID.

## 8. Render and inspect

```bash
python "<SKILL_DIR>/scripts/check_deck.py" "presentation.pptx" --out "structural-qa.json"
python "<SKILL_DIR>/scripts/render_deck.py" "presentation.pptx" --out-dir "rendered" --dpi 150
```

Outputs in `rendered/`: `<deck-stem>.pdf`, `slide-001.png`…, `contact-sheet-01.png`…,
and `render-report.json`. `--overwrite` deletes only files listed in the previous
`render-report.json` of that folder; other files are kept. If planned output
names already exist without such a report (or without `--overwrite`), it refuses
with an error: use a fresh folder. `check_deck.py` also flags leftover `<...>` and
`[NEEDS SOURCE]`-style markers in slides, groups, tables, and notes.

The renderer uses the same LibreOffice search as preflight (`--soffice "<path>"`
overrides), an isolated profile and conversion folder in the system temp
directory, and exports hidden slides too, so the QA PDF has one page per slide.
It checks that a new PDF was produced, compares slide/page counts, renders all
pages, and makes contact sheets. A temp-folder cleanup failure only prints a
warning. It uses no shell interpolation. Nonzero exits must be handled, not
ignored. For an audience PDF without hidden backup slides, export separately
and say so.

Open each PNG at full inspection size, not only the montage. Fix the source deck
and regenerate its PDF/PNGs; never patch only the preview. The resulting PDF is
an audience-facing slide export, not a speaker-notes PDF. Copy it to the agreed
final destination only after inspecting the final revision. Record renderer
name/version; report renderer limits as listed in `qa.md`.

## 9. Release layout

```text
PROJECT_DIR/
  presentation.pptx
  presentation.pdf          # only when actually exported
  presentation.speaker-notes.md
  outline.md
  qa-report.md
  source/                    # supplied material; exclude private files from public delivery
  build_deck.py
  brief.json
  slide-plan.json
  evidence-map.json
  theme.json
  preflight.json
  plan-check.json
  structural-qa.json
  assets/                    # cropped/adapted figures with their .source.json
  rendered/
```

Keep private sources and full-resolution originals in the working project unless
sharing them is authorized. A reproducibility bundle can contain source locators
and hashes without redistributing papers, patient data, or licensed font files.
