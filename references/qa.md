# Quality gates and honest release status

Use `assets/qa-report.template.md`. Every category is `PASS`, `FAIL`, or `NOT_RUN`.
A passed script is not a passed presentation. Record observed facts and inspected
slide IDs, not generic "all checks passed" boilerplate.

## Gate 1 — Approval and timing

Run `plan_check.py` (production §4); exit `0` is required, and every warning is
reviewed. It checks plan structure, not scientific truth or rehearsal timing.
Verify `slide-plan.json` records actual outline approval or an explicit waiver.
Do not write an approval timestamp or quotation that was not observed. If the
outline changes materially, apply the approval policy again. Record whether the
duration includes Q&A; subtract a known Q&A allocation before budgeting. If
unknown, state the assumption instead of inventing a conference rule.

Sum estimated seconds for main slides only. Target approximately 90% of speaking
time and adjust to the presenter's pace when known. This is planning, not proof
of rehearsal fit. Read titles in sequence: does the contribution follow from
the question, method/argument, and displayed evidence? Title/transition/disclosure
slides need appropriate shorter estimates, not a compulsory minute each.

## Gate 2 — Scientific verification

Independently reopen the exact source version and check every consequential
claim, number, sample count, metric, axis unit, confidence level, test, and
citation against the evidence map. Check percent versus percentage points,
absolute versus relative changes, rounding, evaluation units, external versus
internal testing, and source qualifiers. Make sure notes and visible titles agree.

A mapping to a paper is not enough: the cited page/panel must support the claim.
Inspect any cropped/adapted image against the original. Require visible caveats
where omitting them would mislead. A false value, invented source, materially
misleading crop, or causal overstatement is a blocking `FAIL`.

## Gate 3 — Automated structure

`scripts/check_deck.py` checks readable PPTX packaging, slide count, outer shape
bounds, explicit small fonts, presence of slide notes, and leftover `<...>` or
`[NEEDS SOURCE]`/`[TBD]`/`[TODO]` markers in slides, groups, tables, and notes.
It conservatively marks group-internal geometry as needing manual inspection
and does not resolve rotated shapes, masters, text layout, or chart internals.
`plan_check.py --pptx` confirms titles and planned note text reached the deck.

Its warnings require review, not automatic deletion of intentional design.
Geometry success must not be described as "no text overflow" or "all slides
readable" (see Tool limits).

## Gate 4 — Rendered visual review

Produce a fresh PDF and all slide PNGs from the final PPTX. The QA render
includes hidden slides; confirm the page count equals the slide count.
Open every slide PNG;
contact sheets support global consistency but cannot establish small-label
readability. Specifically inspect:

- Cropped/overlapping text, misplaced objects, margins, title wrapping, and density.
- Figures, uncertainty bars, legends, axes, units, and labels at displayed size.
- Hangul glyphs, Greek symbols, superscripts, minus signs, font substitution,
  equations, and line breaks.
- Foreground/background contrast, stable series colors, and redundant encoding.
- Static slide/PDF comprehensibility, including animation-dependent content.

Fix the editable source, regenerate renders, and reopen each changed slide.
Regenerate the complete final export; confirm slide/page counts and revision
identity. A deck with unreadable primary evidence, broken glyphs, or cropped
essential labels is a blocking `FAIL`.

## Gate 5 — Notes and delivery

Every main slide has notes in the requested language, explanation beyond the
visible words, a transition, timing, and source/caveats. Backup slides have useful
Q&A notes. Verify notes are actually embedded in the delivered PPTX and match
`<deck-stem>.speaker-notes.md`, or explicitly report the absent capability.
Check required files exist and that PDF and PPTX refer to the same final revision.
Verify shared URLs/QR destinations when used.

## Gate 6 — Wording (all languages)

Read every slide's visible text and every note as the audience or presenter
would. Check, in any language:

1. **Concrete, not abstract**: claims say what changed, by how much, against
   what, under which condition; no "significantly improved", "various factors".
2. **No reasoning traces**: no agent reasoning, work memos, self-checks,
   assumptions-in-progress, or instructions to the presenter about the agent's
   own process (e.g. "검토 결과", "가정:", "[메모: ...]", "this slide should emphasize").
3. **Newcomer-readable, not childish**: a researcher new to the topic can follow;
   technical terms stay precise; no infantilizing analogies.
4. **No private words**: no internal IDs (claim/source IDs, `slide-plan` fields,
   file names such as `Fig3a_crop`), no self-coined or undefined abbreviations;
   spell out standard abbreviations at first use.

When slide or notes language is Korean, these four are the mandatory rules of
[`korean-writing.md`](korean-writing.md) §1; also run its §4 self-check list
(format: unit spacing, endings, notes register and pacing). Record checked slide
IDs. Any item 2 or 4 violation in delivered text, or an unsupported concrete
number added to satisfy item 1, is a `FAIL`.

## Release decision

- `READY`: all required gates passed, zero blocking issues, and remaining
  nonblocking exceptions are disclosed.
- `DRAFT — FIXES REQUIRED`: a required gate failed or scientific content is
  unresolved. It may be delivered as a draft, never as presentation-ready.
- `DRAFT — VERIFICATION INCOMPLETE`: a required category is `NOT_RUN`, including
  unavailable rendered inspection or missing source verification.

Native PowerPoint/venue-machine testing is a separately reported check. Lack of
that specific test does not erase a completed LibreOffice visual review, but do
not claim renderer parity or venue readiness. When rendering or source access
fails, state the precise missing step rather than claiming an invisible review.
A final status must be set by the reviewing agent/person, not by the geometry
script automatically.

## Tool limits (state once in the report's limitations section)

Other references point here instead of repeating these caveats.

- python-pptx writes PPTX; it does not render or measure text layout.
- `check_deck.py` checks packaging and outer geometry only: not text fit, figure
  completeness, embedded-image labels, font substitution, or color accessibility.
- A successful PDF/PNG export proves a file was produced, not that it was inspected.
  LibreOffice output is not proof of identical rendering in the venue's PowerPoint.
- Font names written to runs do not install or embed fonts; recipient machines may
  substitute.
- Contrast targets follow WCAG ratios; passing them does not guarantee projector
  readability or certify color-vision accessibility.
- `make_theme.py` tints by deterministic RGB mixing, not perceptual optimization.
- `.source.json` records provenance, not a scientific review of the crop.
- Templates are data contracts; nothing parses a paper automatically.
