# Quality gates and honest release status

Use `assets/qa-report.template.md`. Every category is `PASS`, `FAIL`, or `NOT_RUN`.
A passed script is not a passed presentation. Record observed facts and inspected
slide IDs, not generic "all checks passed" boilerplate.

## Gate 1 — Approval and timing

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
bounds, explicit small fonts, and presence of slide notes. It conservatively
marks group-internal geometry as needing manual inspection and does not claim
to resolve rotated shapes, masters, text layout, or chart internals.

Its warnings require review, not automatic deletion of intentional design.
It cannot prove that text fits, that a scientific figure is complete, or that
colors are accessible. Embedded image labels and font substitution cannot be
validated from text runs alone. Geometry success must not be described as
"no text overflow" or "all slides readable".

## Gate 4 — Rendered visual review

Produce a fresh PDF and all slide PNGs from the final PPTX. A successful file
export establishes only that an exporter produced a file. Open every slide PNG;
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
Q&A notes. Verify notes are actually embedded in the delivered PPTX or explicitly
report the absent capability. Check required files exist and that PDF and PPTX
refer to the same final revision. Verify shared URLs/QR destinations when used.

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
