# Package validation record

Package: academic-conference-presentation v1.0.0
Validation dates: 2026-09-29 (initial record); 2026-10-25 (Korean Windows, see below)
Scope: package structure, helper execution, and a synthetic three-slide fixture.
No real research presentation was created or scientifically validated for this test.

## Environment actually used (2026-09-29)

- Python 3.13.5
- python-pptx 1.0.2
- PyMuPDF 1.26.7
- Pillow 12.3.0
- LibreOffice 25.2.3.2
- Installed font: Noto Sans CJK KR

These are observed test versions, not a claim of exhaustive cross-platform support.
Font files and third-party application binaries are not included in the package.

## Checks actually performed

| Check | Result | Scope |
|---|---|---|
| Python syntax | PASS | All bundled scripts compiled |
| Skill metadata | PASS | Locally checked YAML, name/directory match, field lengths, string metadata |
| Relative links | PASS | All SKILL.md reference targets exist |
| JSON templates | PASS | All bundled JSON templates parsed |
| Palette tests | PASS | Eight input colors in light and dark modes; 16 combinations passed defined token contrasts |
| Invalid color handling | PASS | A non-HEX input was rejected with an actionable error |
| Invalid PDF crop inputs | PASS | Page zero, unavailable page, and reversed box were rejected |
| Rotated PDF crop | PASS | Crop matched the corresponding full-render region of a 90-degree rotated synthetic page |
| Editable PPTX creation | PASS | Three-slide synthetic fixture produced and reopened |
| Speaker notes | PASS | Three embedded note records matched the sidecar content after reopening |
| Outer shape bounds | PASS | No outer-bound errors in the synthetic fixture |
| PDF export and page count | PASS | Fresh LibreOffice PDF contained three pages |
| PNG and contact sheet | PASS | All three slide images generated |
| Final rendered visual inspection | PASS | All three final PNGs opened individually and inspected |
| Missing renderer handling | PASS | Invalid renderer path reported failure, not successful verification |
| Overwrite guard | PASS | Existing renderer output was not replaced without an explicit overwrite request |

## Visual observations and correction

The initial render showed theme-inherited shadows on native rectangles. The
helper was corrected to suppress inherited shape effects. A new final fixture
was built and rendered; all three final slide images were reopened.

The tested Hangul, Latin text, Greek symbols, minus/plus-minus signs, figure
labels, synthetic panel caption, and footers were visible without observed
clipping. The source-panel image retained its aspect ratio. No statement here
certifies untested fonts, equations, charts, or arbitrary future deck layouts.

## Not performed / limitations

- The official `skills-ref` CLI was not run; metadata checks were local.
- Installation/auto-trigger behavior in individual agent products was not tested.
- Native Microsoft PowerPoint and the eventual venue computer were not tested.
- No cloud-slides connector or alternative authoring backend was exercised.
- No real paper's claims, statistics, licensing, or source selection were reviewed.
- Contrast tests do not certify all color-vision conditions or projector readability.
- Complex native charts, equation objects, arbitrary templates, and animations
  require deck-specific testing beyond this smoke fixture.

## Korean Windows validation (2026-10-25)

Run by the orchestrator after the script revision. Earlier sections describe the
2026-09-29 record of the previous helper version.

Environment: Korean Windows 11 (console code page cp949), Python 3.12.10,
python-pptx 1.0.2, PyMuPDF 1.28.2, LibreOffice 26.8.1 (not on PATH).

Before the fix, `preflight.py` crashed on this system with a cp949 decoding
error.

| Check | Result | Scope |
|---|---|---|
| `preflight.py` | PASS | Malgun Gothic and LibreOffice detected automatically (via `soffice.com`); version string populated |
| `smoke_test.py --render` without `--font` / `--soffice` | PASS | Synthetic fixture built and rendered |
| `smoke_test.py --render --overwrite` rerun in the same folder | PASS | Re-render over existing output |
| 2-line title | PASS | Accent bar rendered below the title, no overlap, in the smoke fixture |
| Hidden slide | PASS | Included in the exported PDF |
| `regression_checks.py` | PASS | Bundled regression fixtures |

Scope: the synthetic smoke fixture only. No real talk, scientific content,
native PowerPoint, or other Windows configuration was tested.

## Reproduce the smoke fixture

With the required packages, renderer, and Korean font, write outputs outside the
skill folder (`<SKILL_DIR>` is this package's absolute path):

```bash
python "<SKILL_DIR>/scripts/preflight.py"
python "<SKILL_DIR>/scripts/smoke_test.py" --out-dir "smoke-validation" --render
python "<SKILL_DIR>/scripts/regression_checks.py" --out-dir "regression-validation"
```

Open every resulting PNG. The scripts deliberately retain visual/scientific
review statuses as `NOT_RUN`; a reviewer must record the inspection separately.
The smoke-test files are diagnostic artifacts, not a ready-made conference deck.
