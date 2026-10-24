# Changelog

## 1.1.0 — 2026-10-25

Reviewed by three models (Claude, Codex, Gemini 3.8 Flash) with cross-verification, then refined by the same three; validated on Korean Windows 11.

### Fixed
- `preflight.py` / `smoke_test.py` crashed on Korean Windows (cp949 decode of `fc-list` output). All subprocess calls now use UTF-8 with replacement; console output is UTF-8.
- LibreOffice not found when installed but not on PATH; Windows Program Files and macOS app paths are searched, and `soffice.com` is preferred on Windows (version string was empty with `soffice.exe`).
- Korean fonts not detected without `fc-list`; Windows Fonts folders/registry and macOS font folders are scanned. `make_theme.py` defaults to the first detected Korean font.
- Two-line titles overlapped the accent bar and body; title height and `slide.content_top` are computed from estimated line count.
- Hidden backup slides caused a slide/page mismatch; QA PDF export includes hidden slides.
- `crop_pdf.py` reported failure after successful writes when printing μ, —, − on cp949 consoles.
- `check_deck.py` missed unresolved markers in notes, groups, tables and `<...>` placeholders.
- Notes round-trip failed on CRLF / `_x000D_`.
- `render_deck.py --overwrite` deleted any `slide-*.png`; it now replaces only files listed in the previous render report. Temporary LibreOffice profile lives in system temp.
- Notes no longer contain internal slide IDs.

### Added
- `scripts/plan_check.py`: cross-checks slide plan, evidence map and (optionally) the built PPTX — IDs, required fields, asset existence, approval state, timing budget, estimated speaking time.
- Helpers: `add_title_slide`, `new_deck(template=)`, `add_slide(layout_name=, override_background=)`, `add_rich_text`, `style_table`, run `lang` attribute (ko-KR default).
- `references/korean-writing.md` (authored by Gemini): mandatory Korean wording rules — no abstraction, no model reasoning traces in slides/notes, newcomer-readable but not childish, no private words/internal IDs/undefined abbreviations.
- QA Gate 6 (wording, all languages); `regression_checks.py`, `regression_stdlib.py`; `smoke_test.py --overwrite`.

### Changed
- Notes sidecar is now `<deck-stem>.speaker-notes.md`; `save_deck` refuses to overwrite unless `overwrite=True`.
- Skill folder and project folder are separated (`SKILL_DIR` / `PROJECT_DIR`); shell examples work in bash, PowerShell and cmd.
- Description now covers seminars, invited talks, thesis defenses and journal-club talks.

### Known issues (planned for 1.2.0)
- QA relies on self-reporting; a model can mark every gate PASS (observed with Gemini) and cite sources it never opened.
- Wording gate can be skipped (observed with Codex); abstract title patterns are not listed as banned examples.
- `plan_check.py` warns on `waived` approval.
- Running scripts can create `scripts/__pycache__` in the skill folder.

## 1.0.0 — 2026-09-29
Initial draft.
