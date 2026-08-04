# `sci-read-paper` HTML UI Refinement Design

## Goal

Make the single-file paper report feel like a compact scientific long-read: the paper title should orient rather than dominate, provenance should remain available without occupying the cover, and the table of contents should behave as a nearby reading rail rather than a separate centered card.

This revision changes presentation only. It does not change the eight-section report structure, scientific content, evidence IDs, offline requirement, or audit-mode contract.

## Chosen Direction

Use a left reading rail. On desktop, the report group starts closer to the viewport edge and gives unused width to the right of the article instead of distributing it symmetrically. The TOC remains visually distinct through a quiet background and accent rule, but loses the complete bordered-card treatment and prominent shadow.

Two alternatives were rejected:

- Merely reducing the existing gap leaves the entire TOC/article group too centered.
- Pinning the TOC to the viewport edge makes the report resemble an application dashboard rather than a scientific publication.

## Hero and Title

- Reduce the desktop title maximum from `4.5rem` to approximately `3.2rem` using a responsive `clamp()`.
- Keep the serif face, strong weight, and restrained line length; slightly relax line height for long English titles.
- Reduce the hero's vertical padding so the three summary cards enter the first screen sooner.
- Keep the compact metadata row: report mode/status, journal identity, DOI or stable ID, and access date.

## Provenance and Version Information

Remove the wide `报告与版本信息` disclosure from the hero. Its content remains required because paper version, code commit, unresolved artifacts, and completion status determine how claims should be interpreted.

Move the complete information to a collapsed footer disclosure named `来源、版本与未解决问题`, placed immediately before the embedded evidence ledger. The hero status badge and metadata row provide the only top-level provenance summary.

## Desktop Reading Layout

- Give the page shell a wide bounded canvas of approximately `1360px`, with `32–48px` effective left inset on a 1440px viewport.
- Use a TOC column of approximately `225px`, a fixed `28–32px` article gap, and an article column of approximately `900px`.
- Align the grid to the start of the bounded canvas instead of centering the two-column group.
- Give remaining width to the article's right side.
- Keep the TOC sticky, keyboard accessible, numbered, and scrollable when taller than the viewport.
- Replace the full border/shadow with a subtle tinted surface and left accent rule. Reduce internal horizontal padding without crowding link text.

## Responsive and Print Behavior

Below `900px`, preserve the existing single-column flow. The TOC becomes a normal in-flow navigation block and the summary cards stack. At narrow phone widths, the title remains readable and metadata wraps naturally. Print output continues to hide the TOC and expose collapsed provenance and evidence content.

## Acceptance Criteria

- At 1440px, the title no longer occupies most of the first screen.
- The hero has no `报告与版本信息` disclosure.
- Full provenance is reachable in the footer under `来源、版本与未解决问题`.
- The desktop TOC begins substantially closer to the left viewport edge than before.
- The visual gap between TOC and article is no more than `32px`.
- The TOC has no complete card border or prominent shadow.
- The eight section anchors, evidence links, responsive layout, print behavior, and offline single-file guarantee continue to pass automated checks.
