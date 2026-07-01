# DermAssist-AI — Introductory Presentation Spec

This document fully defines a **5-slide introductory presentation** for DermAssist-AI: content, copy, layout, and visual design. It is self-contained — hand it to a slide generator (PowerPoint/Google Slides/Marp/Reveal.js/Canva) or a human designer and no extra context is needed.

---

## 0. Global Design System

| Aspect | Spec |
|---|---|
| **Theme** | Clean clinical-tech — trustworthy medical product meets modern AI/ML tool |
| **Aspect ratio** | 16:9 (1920×1080 px) |
| **Color palette** | Primary: `#0E7C7B` (teal, medical/trust) · Secondary: `#1B3A4B` (deep navy, text/headers) · Accent: `#E8743B` (coral, for warnings/highlights/CTAs) · Background: `#FFFFFF` / `#F7FAFA` (alt slides) · Neutral text: `#33424B` |
| **Typography** | Headings: **Poppins SemiBold** (or Sora/Inter if unavailable) · Body: **Inter Regular** · Code/mono (if needed): **JetBrains Mono** |
| **Font sizes** | Slide title: 40–44pt · Section subhead: 24–26pt · Body bullets: 18–20pt · Footnotes/citations: 12–14pt |
| **Spacing/grid** | 12-column grid, 80px outer margin, 40px gutter. Title block fixed top 15% of slide. Content area = remaining 85% minus 10% bottom margin for footer. |
| **Iconography** | Line-style icons (Lucide/Feather style), 2px stroke, teal or navy fill — never photographic clipart |
| **Imagery** | Use abstract medical/AI motifs only where noted (skin texture macro shot, neural-net node graph). No stock "doctor with stethoscope" clichés. |
| **Footer (every slide)** | Bottom-left: "DermAssist-AI" in 11pt gray `#9AA5AB` · Bottom-right: slide number `X / 5` |
| **Transitions** | Simple fade or none — this is an introductory/academic deck, not a marketing reel |
| **Disclaimer styling** | Any disclaimer text (e.g., "not a diagnostic device") rendered in coral `#E8743B` italic, small caps, 14pt — must be visually distinct as a callout, not buried in body text |

---

## Slide 1 — Title

**Layout:** Centered hero. Background: subtle full-bleed gradient teal→navy (`#0E7C7B` → `#1B3A4B`, diagonal 135°) with a faint abstract pattern (skin-cell or neural-node texture at 8% opacity) in the bottom-right corner. All text white/off-white, centered vertically and horizontally.

**Content:**
- **Title (44pt, bold):** DermAssist-AI
- **Subtitle (22pt, regular, 70% opacity white):** Explainable Multimodal Skin Cancer Detection & Clinical Decision Support System
- **Tagline strip (16pt, coral accent underline):** AI-Assisted Pre-Screening for Skin Conditions
- **Footer block (14pt):** Team/Author name(s) · Course/Project name · Date

**Visual element:** Small icon row beneath the tagline — magnifying glass + skin/lesion icon + neural-network icon, evenly spaced, white line-icons.

---

## Slide 2 — Purpose & Motivation

**Layout:** Two-column 40/60 split. Left column (40%): large stat callout. Right column (60%): heading + bullets.

**Heading (32pt, navy):** Why DermAssist-AI?

**Left column — stat callout card** (teal background card, white text, rounded corners 16px):
- Big number (48pt bold): **1.9B+**
- Caption (14pt): people affected by skin conditions worldwide (WHO, 2023)
- Secondary stat below, smaller card or just stacked text (24pt bold / 14pt caption): **20% → 99%** / melanoma 5-year survival rate, Stage IV vs. Stage I, when caught early

**Right column — bullets (18-20pt, navy text, coral bullet markers, icon per bullet):**
- 🔍 Early detection of melanoma dramatically improves survival outcomes
- 🌍 Access to certified dermatologists is limited in many regions
- 🤖 AI pre-screening can flag high-risk lesions and direct patients to care faster
- 💡 Explainable AI (Grad-CAM) builds trust by showing *why* the model decided

**Footer disclaimer callout (coral, italic, small):** *Designed as a screening aid — not a replacement for professional diagnosis.*

---

## Slide 3 — Scope

**Layout:** Two side-by-side cards, equal width (48% each, 4% gutter), same height. Left card = "In Scope" (teal left border, light teal tint background `#EAF6F6`). Right card = "Out of Scope" (coral left border, light coral tint background `#FDF1EC`).

**Heading (32pt, navy, full width above cards):** Project Scope

**Left card — "✅ In Scope" (heading 20pt teal):**
- Image upload & 4-class skin condition classification (Acne, Eczema, Psoriasis, Melanoma-like)
- Grad-CAM explainability heatmap overlay on predictions
- User authentication (registration/login) and prediction history
- Admin panel for managing users and reviewing data
- Flask REST API + Streamlit interactive demo UI

**Right card — "🚫 Out of Scope" (heading 20pt coral):**
- Clinical/legal diagnostic certification
- Real-time video or dermoscopy hardware integration
- Treatment recommendation or prescription guidance
- Storage of personally identifiable health data long-term

**Bottom strip (full width, centered, 14pt gray):** Target users: patients seeking pre-screening guidance · clinicians as a decision-support aid · researchers studying explainable medical AI

---

## Slide 4 — Functional Requirements

**Layout:** Single column heading, then a horizontal 5-step pipeline diagram (icon + label boxes connected by arrows), left to right, spanning full width. Below the pipeline, a compact 2-column table for FR-ID mapping.

**Heading (32pt, navy):** Functional Requirements — System Pipeline

**Pipeline diagram (5 boxes, teal outline, navy text, connected by coral arrows →):**
1. **Upload** — user submits JPEG/PNG skin image
2. **Preprocess** — resize 224×224, normalize, augment
3. **Classify** — EfficientNet-B0 CNN → 4-class softmax
4. **Explain** — Grad-CAM heatmap on suspicious region
5. **Display** — prediction + confidence + heatmap in UI

**Requirements table below (14-16pt, alternating row tint `#F7FAFA`):**

| ID | Requirement |
|---|---|
| FR-1 | User registration, login, and session management |
| FR-2 | Image upload with format/size validation |
| FR-3 | CNN-based classification across 4 skin condition classes |
| FR-4 | Grad-CAM visual explanation generated per prediction |
| FR-5 | Confidence score / probability bar chart displayed to user |
| FR-6 | Admin panel: view/manage users and prediction logs |
| FR-7 | REST API (Flask) for programmatic inference access |

---

## Slide 5 — Non-Functional Requirements & Tech Stack

**Layout:** Two-column split (55/45). Left column: NFR bullet list grouped by category with small icon per category. Right column: vertical tech-stack badge list (logo-style pill chips).

**Heading (32pt, navy):** Non-Functional Requirements & Stack

**Left column — NFRs (18pt, grouped, bold category label in teal):**
- **Performance** — inference response < 3 seconds per image; ≥85% test accuracy target
- **Security & Privacy** — authenticated access; images discarded after inference; no long-term PII storage
- **Usability** — intuitive upload-to-result flow; clear visual confidence indicators
- **Reliability** — graceful handling of invalid/corrupt image input
- **Scalability** — stateless inference layer, deployable on low-end/cloud free-tier hardware
- **Ethics & Transparency** — mandatory disclaimer on every result; documented dataset bias mitigation

**Right column — Tech stack pills (rounded chip badges, teal/navy alternating, 14pt):**
`Python 3.10+` `PyTorch` `EfficientNet-B0` `OpenCV` `Keras` `Flask` `Streamlit` `SQLAlchemy` `Grad-CAM` `Jupyter`

**Closing line (bottom, centered, 16pt italic navy):** "Bridging the dermatology access gap with transparent, AI-assisted pre-screening."

---

## Build Notes (for whoever generates this deck)

- Source-of-truth content pulled from `docs/generate_proposal.py` (existing project proposal generator) — keep numbers (1.9B, 20%→99%, 85% accuracy target) consistent with that doc.
- If using **Marp/Reveal.js**: implement the two-column layouts with CSS grid (`grid-template-columns: 40% 60%` etc.) matching the ratios specified per slide.
- If using **PowerPoint/python-pptx**: use Slide Master with the color palette above; reuse the same teal/coral/navy theme colors across all 5 slides for consistency.
- Keep total bullet count per slide ≤ 6 — this is a 5-minute intro talk, not a reference document.
- Every slide must visually reinforce that this is a **screening aid, not a diagnostic tool** — the disclaimer styling in §0 is mandatory wherever claims about detection/classification appear.
