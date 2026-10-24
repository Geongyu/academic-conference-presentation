# Official technical references

These references support the file format and helper APIs. The workflow,
approval policy, presentation pacing, and layout defaults are design decisions
for this skill, not claims of a universal academic standard.

Verified against the official pages on 2026-09-29:

1. Agent Skills specification: required `SKILL.md`, YAML metadata, optional
   scripts/references/assets, relative paths, and progressive loading.
   `https://agentskills.io/specification`
2. python-pptx: working with notes slides, including
   `slide.notes_slide.notes_text_frame.text`.
   `https://python-pptx.readthedocs.io/en/latest/user/notes.html`
3. python-pptx slide API and notes-slide presence checks.
   `https://python-pptx.readthedocs.io/en/latest/api/slides.html`
4. PyMuPDF Page API: page rendering, `get_pixmap`, DPI, and clipping.
   `https://pymupdf.readthedocs.io/en/latest/page.html`
5. LibreOffice command-line parameters: headless mode, conversion, output
   directory, and isolated user profile.
   `https://help.libreoffice.org/latest/en-US/text/shared/guide/start_parameters.html`
6. W3C WCAG 2.2 text contrast: adopted as a design target, not a projection
   readability guarantee.
   `https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html`
7. W3C non-text contrast: the source for the necessary-mark 3:1 design target.
   `https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html`

Consult installed package/runtime versions before extending the helpers. This
package does not assert identical behavior across all slide-authoring products.
