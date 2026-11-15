---
name: ref-researcher
description: >-
  Researches UI/UX and landing page references across any web URL, design
  gallery, screenshot, or video for mobile apps, web apps, and websites;
  extracts HTML structure, slices tall images and video keyframes for
  inspection, audits findings against product and brand reality, and outputs
  an actionable execution playbook (.md) with Dos & Don'ts.
---

# Reference Researcher (`ref-researcher`)

## Overview

`ref-researcher` turns raw inspiration (live websites, design galleries, app recordings, UI screenshots, or saved HTML) into an opinionated, execution-ready **`.md` Design & Product Playbook** before design or coding begins.

Use this skill for **mobile app features**, **web app flows**, or **marketing websites** whenever you need to deeply inspect visual craft, motion cues, copy patterns, and anti-patterns from external references—without losing fidelity to your project's real brand tokens, platform rules, and shipping scope.

## Dependencies

Coordinate these installed skills instead of duplicating their responsibilities:

- **`uv`** — Check and invoke Python CLI scripts cleanly via `uv run` (fall back to `python3` only if running strictly offline/stdlib without `uv` installed).
- **`chrome-devtools`** — Render JS-heavy SPAs, inspect live layout/animation behavior, and capture full-page screenshots or interactive browser sessions when static HTTP fetching hits client-side shells (`needs_browser_capture: true`) or gated sites.
- **`frontend-design`** — Guide visual point-of-view, typography pairing, spatial restraint, and anti-template critique when synthesizing **web apps** or **marketing websites**.
- **`apple-hig-designer`** — Validate native iOS/iPadOS/watchOS component fidelity, safe areas, sheets, Dynamic Type, and accessibility when synthesizing **mobile app features** or native Apple device showcases.

## Quick Start

Start either from **live URLs** (fetching public HTML/assets and capturing browser screenshots) or from an **existing local reference folder**:

```bash
# 1. Inspect saved HTML references into structured JSON
uv run ~/.gemini/config/skills/ref-researcher/scripts/ref_researcher.py extract-html \
  --input-dir "./Docs/References & Inspo" \
  --limit 25 \
  --output "/tmp/ref_html_summary.json"

# 2. Slice ultra-tall screenshots + extract video keyframes into scratch (1024px wide)
uv run ~/.gemini/config/skills/ref-researcher/scripts/ref_researcher.py slice-media \
  --input-dir "./Docs/References & Inspo" \
  --scratch-dir "/tmp/ref_slices" \
  --slice-height 1400 \
  --out-width 1024 \
  --max-slices 12 \
  --frames-per-video 3 \
  --output "/tmp/ref_media_manifest.json"
```

## Utility Scripts

All programmatic extraction, slicing, polite HTTP fetching, and link auditing live in [`scripts/ref_researcher.py`](scripts/ref_researcher.py). Every command **requires explicit limits and `--output <file.json>`** (writing concise status only to stdout).

### 1. `fetch-page` — Polite Public URL & Asset Fetcher
Downloads static HTML and top stylesheets/images from public URLs while detecting login walls, bot challenges, and client-side JS shells (`needs_browser_capture: true`).

```bash
uv run ~/.gemini/config/skills/ref-researcher/scripts/ref_researcher.py fetch-page \
  --url "https://example.com" \
  --asset-dir "./refs/example" \
  --max-assets 20 \
  --output "/tmp/fetch_example.json"
```

### 2. `extract-html` — Code, Copy, Typography & Token Extractor
Parses saved `.html` and `.css` files up to `--limit`, outputting titles, nav links, H1–H3 hierarchy, CTAs, body copy samples, hex colors, `font-family` declarations, and animation library cues (`@keyframes`, `framer`, `gsap`, `lottie`).

```bash
uv run ~/.gemini/config/skills/ref-researcher/scripts/ref_researcher.py extract-html \
  --input-dir "./refs" \
  --limit 25 \
  --output "/tmp/html_summary.json"
```

### 3. `slice-media` — Tall Screenshot & Video Keyframe Slicer
Reads real image pixel dimensions (handling misnamed extensions like JPEG saved as `.webp`), splits tall full-page screenshots into sharp `1024px`-wide viewport slices, and extracts evenly spaced MP4/MOV/WebM keyframes via `ffmpeg`.

```bash
uv run ~/.gemini/config/skills/ref-researcher/scripts/ref_researcher.py slice-media \
  --input-dir "./refs" \
  --scratch-dir "<scratch_dir>/slices" \
  --slice-height 1400 \
  --out-width 1024 \
  --max-slices 12 \
  --frames-per-video 3 \
  --output "/tmp/slice_manifest.json"
```

> **Workspace Hygiene:** Always point `--scratch-dir` to your conversation scratch directory (or `/tmp/`), **never** into the user's repository workspace.

### 4. `verify-links` — Playbook Asset Link Auditor
Validates every relative markdown link inside generated `.md` files against disk and exits with code `1` if any path is broken.

```bash
uv run ~/.gemini/config/skills/ref-researcher/scripts/ref_researcher.py verify-links \
  --markdown "./Docs/References & Inspo/PLAYBOOK.md" \
  --markdown "./Docs/References & Inspo/README.md" \
  --output "/tmp/verify_links.json"
```

## Workflow

### 1. Audit Target Product & Constraints First
Before opening a single inspiration link, read the target project's source-of-truth docs (PRD, brand colors/tokens, design system, platform constraints). Record:
- **Target surface:** Mobile App Feature, Web App Flow, or Marketing Website.
- **Visual tokens & contrast traps:** Exact hex values and WCAG AA minimums (e.g., low-contrast dark-mode accents).
- **Product Truth Matrix:** Separate **Shipping Today** vs **Roadmap / Forbidden Claims**.

### 2. Gather References (Live Fetch, Browser Capture, or Existing Folder)
- **Existing local references:** Run `extract-html` and `slice-media` immediately on the provided directory.
- **Public URLs / Research from scratch:**
  1. Run `fetch-page` first for fast, rate-limited static HTML + asset capture.
  2. When `needs_browser_capture` is `true` (React/Next/Vite CSR shell) or full-page visual screenshots are needed, use the **`chrome-devtools`** skill (or browser workflow) to render and capture full-page images/DOM.
  3. **Auth / Blocked Site Protocol (STRICT):** If a site returns HTTP `401`/`403`, redirects to `/login`, or shows a paywall/bot wall:
     - **Ask the user to log in first**, then **retry up to 2 times**.
     - If access still fails after 2 retries, **log the blocked source clearly** and automatically **pivot to accessible public sites/pages** or peer alternatives so momentum never stalls.

### 3. Inspect Visually & Programmatically (Never Skim Tall Captures Blind)
- Full-page captures (`3840w × 15000px+`) downscale to illegible thumbnails if viewed whole. Always inspect sequential viewport slices generated by `slice-media` across **all** collected references plus extracted copy/CSS tokens from `extract-html`.
- Pair visual study with platform guidance:
  - Invoke **`apple-hig-designer`** cues for iOS/iPadOS navigation, sheets, SF Symbols, and touch/Dynamic Type ergonomics.
  - Invoke **`frontend-design`** cues for web typography contrast, intentional whitespace, and cutting AI template defaults.

### 4. Synthesize the `.md` Playbook
Write the deliverable playbook inside the target project's reference folder following [`references/playbook_template.md`](references/playbook_template.md). Adapt the blueprint to the target surface while always including:
1. **Product Truth & Constraints Matrix** (including dark/light contrast traps)
2. **Executive Creative & UX Direction**
3. **Architecture / Screen-Flow Blueprint**
4. **State & Edge-Case Inventory** (empty, loading/streaming, partial/cap-hit, error/permission)
5. **Platform & Responsive Translation Matrix**
6. **Typography, Surface, Motion & Copy Rules**
7. **Strict DOS & DON'TS** citing concrete positive **and** negative examples from your batch
8. **Indexed Reference Asset Lookup Table** (relative markdown links)
9. **Pre-Build Execution & QA Checklist**

Update the directory's `README.md` (if present) to surface the new playbook at the top.

### 5. Verify All Relative Links
Run `verify-links` on the playbook (and updated `README.md`). Fix any non-zero exit before reporting completion to the user.

## Rate Limiting

- `fetch-page` enforces **`1.0` request/second** (`REQUESTS_PER_SECOND = 1.0`) across concurrent agent processes via a file lock (`/tmp/ref_researcher_fetch.lock`) and monotonic timestamps (`time.monotonic()`).
- HTTP `429` triggers exponential backoff (`Retry-After` or `2^attempt`s) logged to `stderr` before raising `RateLimitError`.
- HTTP `5xx` retries with exponential backoff; permanent HTTP errors include the URL and truncated response body for fast diagnosis.

## Common Mistakes

- **Inspecting un-sliced `15,000px`-tall screenshots directly:** Causes blurry guesswork and missed micro-interactions. Always slice first with `slice-media`.
- **Bypassing blocked logins forever or stalling on one paywall:** Ask the user to sign in once, retry at most 2×, then pivot cleanly to accessible sources and log the gap.
- **Trusting competitor marketing claims over your own codebase/PRD:** Copying a peer's "Cloud Sync" or "Mac App" hero blindly creates false marketing claims. Always gate every pattern through the **Product Truth Matrix**.
- **Leaving broken relative links or dumping scratch images inside the project repo:** Always write slices to scratch and run `verify-links` before wrapping up.
