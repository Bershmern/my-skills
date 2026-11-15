# {Project / Feature Name} Design & Execution Playbook

> **Target Surface:** `{Mobile App Feature | Web App Flow | Marketing Website}`  
> **Corpus Studied:** `{N}` reference sites / apps / captures (`{urls / folders / videos}`)  
> **Source-of-Truth Project Docs Checked:** `{design tokens, PRD, HIG/platform rules, API capabilities}`
>
> **Greenfield Principle:** Borrow *structural craft, motion pacing, and interaction clarity* from top references—never copy competitor branding verbatim, and never invent unshipped capabilities.

---

## 1. Product Truth & Constraints Matrix

### 1.1 Official Visual Tokens & Contrast Traps
| Token Role | Light Mode | Dark Mode | Guardrail / Minimum Contrast |
| :--- | :--- | :--- | :--- |
| Canvas | `{#HEX}` | `{#HEX}` | `{Note system auto vs fixed brand sections}` |
| Elevated Surface | `{#HEX}` | `{#HEX}` | `{Border vs shadow discipline}` |
| Primary Text | `{#HEX}` | `{#HEX}` | `>= 7:1` preferred (`4.5:1` WCAG AA floor) |
| Secondary Text | `{#HEX}` | `{#HEX}` | `{Subhead / metadata limits}` |
| Action / Link Accent | `{#HEX}` | `{#HEX}` | **Check dark-mode accent readability** (`>= 4.5:1` text, `>= 3:1` UI) |

### 1.2 Shipping Truth vs. Forbidden Claims
| Area / Feature | Shipping Truth (Design & Copy Allowed) | Roadmap / Forbidden Today (Do NOT Fake) |
| :--- | :--- | :--- |
| Supported Platforms | `{e.g., iPhone + iPad / Web Desktop + Mobile}` | `{e.g., Native Mac / Watch / Android if unbuilt}` |
| Data & Sync | `{Local / Live Cloud / Auth method}` | `{Any unimplemented sync or real-time claim}` |
| Core Functionality | `{Verified implemented behaviors}` | `{Placeholder / Coming Soon integrations}` |
| Pricing / Entitlements | `{Real free tier, trial rules, paid caps}` | `{Fake urgency timers or invented social proof}` |

---

## 2. Executive Creative & UX Direction

- **Core Aesthetic Thesis:** `{1-sentence design thesis combining emotional user transformation + visual medium}`
- **North-Star Reference Synthesis:**
  - **What to absorb from top peers:**
    - **`{Ref 1}`:** `{Exact pattern borrowed — e.g., Hero interactive proof}`
    - **`{Ref 2}`:** `{Exact pattern borrowed — e.g., Color polarity & border discipline}`
    - **`{Ref 3}`:** `{Exact pattern borrowed — e.g., Native gesture/navigation craft}`

---

## 3. Architecture / Screen-Flow Blueprint

*(Use **Section Cadence** for Websites; **Screen & Navigation Flow** for Mobile/Web App Features.)*

1. **Entry / Step 0 (`{Navbar / Trigger}`):** `{Purpose, max items, primary action}`
2. **Step 1 (`{Hero / Entry Screen}`):** `{3-second clarity hook + primary visual proof}`
3. **Step 2 (`{Core Loop / Problem -> Solution Proof}`):** `{Interactive demo or step progression}`
4. **Step 3 (`{Primary Workspace / Deep Feature}`):** `{Native/web controls, visual rhythm}`
5. **Step 4 (`{Trust / Pricing / Confirmation / Summary}`):** `{Clean decision UI + objection handling}`

---

## 4. State & Edge-Case Inventory

| State | Visual Treatment | Copy / Action |
| :--- | :--- | :--- |
| **Empty / First-Run** | `{Inviting single-action prompt, never dead blank space}` | `{Action-oriented CTA + sample hint}` |
| **Loading / Streaming / Processing** | `{Skeleton, waveform, or determinate % progress}` | `{Clear active verb; disable conflicting actions cleanly}` |
| **Partial / Offline / Cap Hit** | `{Calm inline banner + non-blocking fallback}` | `{Preserve user data; offer manual or retry path}` |
| **Error / Permission Denied** | `{Direct explanation + recovery button, never generic apology}` | `{Exact next action}` |

---

## 5. Platform & Responsive Translation Matrix

| Surface Aspect | Mobile (`390px` / iOS / Android) | Tablet / Web Desktop (`1280px–1440px`) |
| :--- | :--- | :--- |
| **Navigation & Chrome** | `{Bottom bar / Sheet / Safe-area clearances}` | `{Top pill nav / Sidebar / Split view}` |
| **Primary Proof / Workspace** | `{Vertical card stack / Gesture-friendly slider}` | `{Multi-column split panel / Corner QR or shortcut}` |
| **Input & Ergonomics** | `{44pt+ tap targets, Dynamic Type / thumb zone}` | `{Keyboard shortcuts, hover clarity, 62ch prose cap}` |

---

## 6. Typography, Surface, Motion & Copy Rules

- **Typography Pairing:** Display `{font + tracking}`, Body `{font + measure}`, Numeric/Code `{tabular-nums / monospace}`.
- **Surface & Framing:** `{Container radius, 1px borders vs glass, photography/background pairing}`.
- **Motion Choreography:** `{GPU-only properties (transform/opacity/stroke-dashoffset), durations, prefers-reduced-motion fallback}`.
- **Copy Guidelines:** `{Headline formula, microcopy ceiling, forbidden words}`.

---

## 7. Strict DOS & DON'TS (From Studied References)

### DO ✅
1. `{Concrete winner pattern tied to specific reference}`
2. `{Concrete winner pattern tied to specific reference}`
3. `{Concrete winner pattern tied to specific reference}`

### DON'T ❌
1. `{Concrete anti-pattern tied to negative reference — e.g., hype urgency bars, sprawl, low-contrast tokens}`
2. `{Concrete anti-pattern tied to negative reference}`
3. `{Concrete anti-pattern tied to negative reference}`

---

## 8. Indexed Reference Asset Lookup

| Target Section / Flow | Top Reference Files / Paths | Key Takeaway |
| :--- | :--- | :--- |
| `{Area 1}` | `[Ref Name](relative/path)` | `{Why open this asset during build}` |
| `{Area 2}` | `[Ref Name](relative/path)` | `{Why open this asset during build}` |

---

## 9. Pre-Build Execution & QA Checklist

- [ ] **Contrast & Tokens:** Verified in Light & Dark modes (`>= 4.5:1` text, `>= 3:1` controls/borders).
- [ ] **Product Truth:** Zero unshipped features, fake metrics, or contradictory labels advertised.
- [ ] **Above-the-Fold Check:** Primary clarity + visual proof visible cleanly on both mobile and desktop viewports.
- [ ] **States & Accessibility:** All empty/loading/error/reduced-motion/keyboard/VoiceOver paths covered.
- [ ] **Verified Links:** `ref_researcher.py verify-links` passed with `0` broken references.
