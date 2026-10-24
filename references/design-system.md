# Color-led academic design system

Adjustable defaults. Venue requirements, explicit user preferences, and rendered
readability take priority.

## 1. Inputs and tokens

Accept a HEX color, a named color, an existing palette, or an institutional
identity. For "navy" or "muted purple", resolve to an explicit HEX and state the
assumption in the outline. Ask only when the exact brand color is consequential.
Do not deduce a scientific or emotional meaning from hue alone.

Default identity: primary `#2457C5`, background `#FFFFFF`, body `#172033`,
secondary text `#526174`. `scripts/make_theme.py` produces the complete theme:

| Token | Function |
|---|---|
| preferred | Unmodified user color for identity tracking |
| primary | Adjusted fill/mark color legible on the background |
| primary_ink | Adjusted color for emphasized text |
| on_primary | Dark or light text chosen for contrast on primary |
| surface / primary_soft | Low-saturation tint for restrained grouping |
| primary_dark | Darker identity variant; not automatically text-safe everywhere |
| text / muted_text | Ordinary and secondary readable text |
| baseline | Neutral comparison mark; never intentionally unreadable |
| border | Decorative separator, not the sole carrier of meaning |
| secondary | Optional independent comparison accent, not mandatory |

The bundled helpers apply only `background`, `text`, `muted_text`, and `primary`
by default. The other roles are for project code (grouping fills, tables, chart
series, emphasis); use them deliberately or leave them unused. `semantic_map` is
written empty: fill it in `theme.json` by hand (series or object name → token or
HEX) before building charts that need stable colors.

Keep the original identity color while deriving safer roles. A yellow preference
must not produce yellow body text on white. A black preference should not turn
the whole deck black unless a dark background was requested. The engine records
contrast adjustments; show substantial hue/lightness compromises in the outline.

Use light mode by default. Dark mode is an explicit choice or a venue/template
constraint, not an automatic result of a dark accent. For bright accents, use
neutral backgrounds and small saturated marks; for pale accents, use tinted
surfaces and darker label variants. Freeze palette tokens before full production.

## 2. Contrast and scientific color semantics

Adopt at least 4.5:1 for ordinary text and 3:1 for necessary graphical marks as
engineering targets (from WCAG contrast guidance). Prefer the stronger text
target even for slide titles. Assess each real foreground/background pair,
including text on charts, photos, and imported figures.

Map named series/objects to fixed colors in `semantic_map`. Redundant labels,
markers, line styles, and position must distinguish information without color
alone.

If a scientific image encodes quantities, retain its original color mapping,
legend, and range. Do not hue-shift microscopy, heatmaps, or experimental images
to match a user's preferred color. A newly plotted chart may use the deck palette
only when its underlying numeric data are verified. Choose categorical,
sequential, or diverging scales according to data meaning, not decoration.
For many categories, use explicit labels and appropriate additional colors,
rather than dozens of indistinguishable tints of one accent.

## 3. Typography and Korean

Starting values for a 13.333 × 7.5 inch, 16:9 deck:

| Role | Default | Working range / response to crowding |
|---|---:|---|
| Cover title | 44 pt | Shorten or wrap deliberately |
| Slide title | 34 pt | Usually 30–40; avoid three-line headings |
| Body / explanation | 24 pt | Usually 22–28; move detail to notes |
| Chart labels / annotations | 20 pt | Target 18–22 at final displayed size |
| Citation / nonessential locator | 12 pt | 12–14; essential caveats must be larger |

Figure-label sizes are assessed after scaling onto the slide, not at the original
PDF's nominal size. Never shrink a dense paper panel until the axes vanish.
A citation can be secondary, but a small footnote cannot rescue an overstated
claim. Prefer one family with real regular/bold weights and consistent numerals.

Korean-family candidates, in preference order: Noto Sans CJK KR, Noto Sans KR,
Malgun Gothic, Apple SD Gothic Neo, NanumGothic. Verify the actual selected
family and glyph coverage.
On Fontconfig systems use `fc-list` to check installation; `fc-match` alone can
return a substitute and must not be treated as proof of an exact match. Else
inspect the host's font inventory and perform a render test. For other languages,
select an installed family supporting all required scripts.

`scripts/pptx_helpers.py` writes Latin and East Asian font names on text runs
(names only; see the tool limits in `qa.md`). Keep font names and substitution
risks in the delivery report; provide a PDF fallback. Do not bundle font
binaries. Recheck Hangul syllables,
spacing, mixed-language labels, Greek symbols, minus signs, superscripts, and
line wrapping in the final render. Avoid automatic shrink-to-fit as a fix.

## 4. Layout grammar

Use a common grid: roughly 0.55 inch exterior margins, aligned title/body starts,
and a reserved footer area. Adapt to required templates instead of overriding
them. These layout families are options, not required slides:

- Claim/question with one dominant figure, proof, or quotation.
- Overview pipeline with short steps, followed by component zoom-ins.
- Two-column comparison with aligned measures and shared scales.
- Cohort/sampling flow or compact dataset table.
- Result plot or focused table with the key comparison visibly identified.
- Equation/proof sketch with terms and assumptions explained.
- Qualitative evidence with quotation/context and restrained interpretation.
- Take-home screen containing the contribution, scope, and Q&A prompt.

Use lines, spacing, and typography before boxes. No mandatory card dashboard,
stock-photo background, or decorative AI illustration. A restrained diagram may
clarify a mechanism, but does not replace evidence. Preserve aspect ratios;
use contain-fit for source panels. Intentional overlaps such as a label inside
a box are not automatically defects; accidental obscuring of labels is.

Static sequence slides may replace animation. Do not make an exported PDF lose
an argument that depended on animation state. Use a conceptually appropriate
visual, including a table or equation when it communicates better than a chart.
