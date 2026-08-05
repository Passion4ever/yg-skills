# Optional Figure Mode Design

**Date:** 2026-08-05  
**Scope:** `sci-read-paper` figure handoff and report output only

## Goal

Keep ordinary deep-reading reports focused on understanding and evaluating the paper. Scientific-figure material must not appear unless the user requests it, while preserving a clean handoff to the future `sci-ai-figure` skill.

## Interface

Use one independent three-state parameter:

```text
figure=off | brief | generate
```

- `off` is the default. Generate no brief, image, heading, empty disclosure, or other figure placeholder in the final HTML.
- `brief` generates at most three collapsed scientific-figure briefs after Section 8. It does not invoke a figure-generation skill.
- `generate` invokes `sci-ai-figure`, embeds at most three resulting images with captions and evidence IDs, and does not expose the internal handoff brief by default.

The paper-reading mode remains independent:

```text
mode=standard|audit, figure=off|brief|generate
```

Natural-language requests map as follows:

- Requests for a figure plan, visual brief, or drawing proposal select `figure=brief`.
- Requests to create, draw, or generate the scientific figure select `figure=generate`.
- A normal deep-read request selects `figure=off` without asking.

## Degraded Generate Behavior

If `figure=generate` cannot run because `sci-ai-figure` is unavailable or fails before producing a usable image:

1. Continue and finish the paper reading.
2. Fall back to `figure=brief`.
3. State the reason for the fallback once in the figure disclosure.
4. Do not treat figure failure as a `partial` paper-reading result unless paper evidence is also incomplete.

## HTML Contract

Replace the template's always-visible figure disclosure with one output slot:

```html
<main id="main-content">
  {{REPORT_BODY}}
  {{FIGURE_OUTPUT}}
  {{AUDIT_PANELS}}
</main>
```

Render the slot by mode:

- `off`: empty string.
- `brief`: one collapsed `<details id="figure-briefs">` containing at most three briefs. Each brief records purpose/reader, figure type, entities and relationships, evidence IDs, visual hierarchy, and content that must not be invented.
- `generate`: at most three semantic `<figure>` elements with embedded data-URI images, concise captions, alt text, and evidence IDs. Keep the report offline and self-contained.

Do not add a figure link to the fixed sidebar. Figure output is supplementary and must not compete with the eight-chapter reading path.

## Skill and Example Changes

- Change `SKILL.md` from heuristic brief generation to explicit `figure` selection with `off` as default.
- Update `references/output-contract.md` with the parameter, natural-language mapping, conditional HTML, and fallback behavior.
- Change `assets/report-template.html` from an always-visible Brief disclosure to `{{FIGURE_OUTPUT}}`.
- Remove the existing optional figure Brief from the SiamProm acceptance example because it represents the default `figure=off` path.
- Keep `sci-ai-figure` optional; do not declare a hard dependency.

## Verification

Tests must establish that:

1. The default template has no fixed `可选科研绘图 Brief` disclosure and exposes only `{{FIGURE_OUTPUT}}`.
2. The output contract defines all three states, defaults to `off`, and documents natural-language selection and downgrade behavior.
3. The SiamProm default example contains neither a figure Brief heading nor a `figure-briefs` element.
4. Existing eight-section structure, evidence ledger, offline HTML, audit mode, and scientific-depth checks still pass.

## Non-Goals

- Implementing `sci-ai-figure`.
- Generating an image for the current SiamProm example.
- Adding figure controls to the report UI.
- Changing the eight primary sections, evidence policy, standard/audit modes, or report visual design.
