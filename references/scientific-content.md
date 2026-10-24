# Scientific content and evidence mapping

## Scope

The core workflow serves empirical, theoretical, methodological, and qualitative
conference talks. It does not prescribe an IMRaD slide count or assume every
study proposes a predictive model. Use the research question and actual evidence
to choose the structure.

## Extract before summarizing

From the supplied sources, identify the question, gap, contribution, evidence,
methodological assumptions, evaluation or argument, uncertainty, limitations,
and the narrowest defensible conclusion. Read figure captions and supplementary
material needed to interpret selected findings. Record source versions; do not
silently combine an old manuscript's cohort with a newer paper's results.

Maintain `evidence-map.json` with stable source and claim IDs. Each empirical
claim needs its source locator and exact reported quantity/context. Keep the
original value and any displayed rounding separately. A source locator can be
`paper.pdf, p. 8, Fig. 3c` or a source table/range, not merely the paper's title.
A DOI or URL is an identifier, not proof that its contents were inspected.

Unpublished user results can be cited as supplied data, with file/version/range.
Do not invent journal citations for them. Mark abstract-only information as such;
request full methods when a talk depends on unavailable details. External searches
must not expose private data or substitute unrelated studies for missing results.

## Choose a narrative, not a universal checklist

| Study type | Typical argument | Evidence that should remain visible |
|---|---|---|
| Empirical | Question → design → observations → interpretation | Population, evaluation unit, measurement, comparisons where claimed, uncertainty |
| Methodological | Limitation → proposed mechanism → evaluation → scope | Method assumptions, fair comparisons, relevant ablations/failure cases |
| Theoretical | Problem → definitions/assumptions → proposition → proof idea → consequence | Conditions of the theorem, precise claim, decisive derivation |
| Qualitative | Question → context/sampling → analysis → themes → interpretation | Traceable examples/quotations, analytical procedure, scope and reflexivity |
| Mixed methods | Shared question → complementary evidence → synthesis | Which inference each method supports and where evidence disagrees |

A proof sketch or carefully selected quotation can be the dominant visual.
Do not force these talks into charts, sample-size cards, or model comparisons.
A method overview is often useful before dataset details, but reorder when the
audience first needs to understand the measurements or sampling process.

## Quantitative safeguards

Report evaluation units: participants, slides, patches, visits, documents, or
experiments are not interchangeable. Identify repeated measurements and splits
when they affect independence or leakage. Distinguish standard deviation,
standard error, confidence intervals, and fold-to-fold variability; never
rename one as another. Preserve confidence levels and test assumptions as stated.

Use comparative titles only when a comparator was actually evaluated. Show the
baseline and relevant uncertainty when available. Do not require a comparator
for a descriptive result or theorem. Do not infer statistical significance from
numerical ordering or overlapping/nonoverlapping error bars alone.

An improvement from 0.30 to 0.36 is +0.06 absolute, or +20% relative to 0.30;
specify which transformation is displayed. Correlation coefficients are not
percentage-point quantities. Accuracy from 70% to 75% is +5 percentage points.
These are arithmetic examples, not research findings to insert into a deck.

Do not average heterogeneous endpoints, different validation schemes, or
incompatible metrics just to obtain a single headline number. Preserve negative,
null, and contradictory findings necessary for a fair interpretation. Any
assistant-calculated statistic requires verified inputs, its method, and a
clear distinction from author-reported results.

## Figures and other sources

Attribution is required for external scientific material. Use a compact visible
citation; put a full locator/DOI in the source map and notes. Label exact reuse,
cropped/enlarged reuse, adaptation, and redrawing accurately. An author/year
citation is not a substitute for complying with source permissions or licenses.
Check venue and source requirements; do not make a blanket permission claim.

Do not remove unfavorable comparison groups to strengthen the message. Cropping
may focus attention, but retain context needed for honest interpretation.
For quotations, preserve meaning, mark omissions, and provide a locator. Protect
participant identity and user confidentiality. For equations, retain conditions
and define symbols that the audience needs to follow the argument.

## Closing the argument

Discussion explains mechanisms, alternative explanations, scope, or implications;
it should not simply repeat numbers from Results. Include consequential
limitations on the relevant result slide or in a concise dedicated discussion.
A separate limitations slide is not compulsory in a short talk.

The final main slide retains the central contribution and its scope during Q&A.
Include contact/QR information only from supplied or verified destinations.
Required conflicts, funding, ethics, and acknowledgments follow actual venue
rules when available; absence of a disclosure statement is not evidence of
"no conflicts" or ethical approval. Detailed protocol, robustness analyses,
proofs, secondary tables, and likely Q&A material belong in backup when useful.
