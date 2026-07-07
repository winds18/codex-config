# Style Directions

Use these as fast-start direction cards when browsing is unavailable. They are condensed from Refero style pages and should be adapted to the project, not copied.

## Dark Precision Instrument

Inspired by: Linear, Integrated Biosciences.

Use for:
- Command centers, admin consoles, technical dashboards, security, devtools, AI ops.

Core grammar:
- Near-black canvas with one small electric accent.
- Hairline borders and geometry instead of shadows.
- Crisp type, tight tracking, low-to-medium font weights.
- Compact cards, small radii, restrained labels.
- Accent appears on active controls, indicators, dots, arrows, or one primary action only.

Avoid:
- Large decorative gradients.
- Multiple saturated status colors.
- Heavy shadows or soft glass effects.
- Bold marketing typography.

Token sketch:

```css
:root {
  --surface-canvas: #08090a;
  --surface-card: #101214;
  --text-strong: #ffffff;
  --text-muted: #8a8f98;
  --border-hairline: #23252a;
  --accent-signal: #e4f222;
  --radius-card: 12px;
  --radius-control: 6px;
}
```

## Warm Editorial Notebook

Inspired by: Notion, Monad.

Use for:
- Content-heavy SaaS, onboarding, knowledge tools, creator workflows, documentation, calm mobile product surfaces.

Core grammar:
- Warm off-white canvas, never clinical pure white.
- Paper-like cards with 1px borders and little/no shadow.
- Editorial headings: serif or expressive sans at restrained weights.
- Sparse accent color, used like punctuation.
- Feature cards can use soft sticky-note-like accent surfaces.

Avoid:
- Blue-on-white default SaaS pages.
- Overusing the accent on every icon or button.
- Heavy elevation.
- Dense enterprise table visuals unless softened.

Token sketch:

```css
:root {
  --surface-canvas: #f6f5f4;
  --surface-card: #ffffff;
  --text-strong: #111111;
  --text-muted: #615d59;
  --border-hairline: #d8d3ce;
  --accent-primary: #0075de;
  --accent-warm: #ffb110;
  --radius-card: 12px;
  --radius-pill: 9999px;
}
```

## Frosted SaaS Ledger

Inspired by: Dub.

Use for:
- B2B dashboards, analytics, link/workflow tools, settings, account management.

Core grammar:
- Near-white or rice-paper canvas.
- Dense monochrome typography.
- 1px borders create structure; surfaces stay flat.
- One electric brand color for key links/metrics/actions.
- Small feature-pill accents can segment content without visual noise.
- Components are compact: 8px gaps, 12px card radius, ghost controls.

Avoid:
- Large colorful cards as the main system.
- Gradients on functional UI.
- Excess whitespace that makes dashboards feel empty.
- Decorative icons that compete with data.

Token sketch:

```css
:root {
  --surface-canvas: #fafafa;
  --surface-card: #ffffff;
  --text-strong: #171717;
  --text-muted: #525252;
  --border-hairline: #e5e5e5;
  --accent-primary: #2563eb;
  --accent-primary-strong: #1e40af;
  --radius-card: 12px;
  --radius-pill: 9999px;
}
```

## Bioluminescent Laboratory

Inspired by: Integrated Biosciences.

Use for:
- Science, biotech, medical research, high-trust technical products, premium lab-like data interfaces.

Core grammar:
- Abyssal ink or dark green-black canvas.
- White typography, green-lime micro accents.
- Single-weight typography; hierarchy through size and tracking.
- Roboto Mono or equivalent for technical labels.
- Flat surfaces; no gradients and no shadows.
- Hairline borders define cards and sections.

Avoid:
- Making lime the main button background everywhere.
- Thick borders, glossy cards, neumorphism.
- Multiple type weights.
- Decorative color noise.

Token sketch:

```css
:root {
  --surface-canvas: #222f30;
  --surface-light: #f7f7f5;
  --surface-card: #ffffff;
  --text-strong: #ffffff;
  --text-dark: #222f30;
  --text-muted: #4d5757;
  --border-hairline: #c9cbbe;
  --accent-bio: #cef79e;
  --radius-card: 20px;
  --radius-large: 40px;
}
```

## Direction Selection Matrix

- Admin console with operational density: choose Frosted SaaS Ledger or Dark Precision Instrument.
- Consumer mobile/H5 with trust and warmth: choose Warm Editorial Notebook, then add project accent colors.
- Technical/AI/security product: choose Dark Precision Instrument.
- Healthcare/biotech/high-trust science: choose Bioluminescent Laboratory.
- Marketing landing page: start from Warm Editorial Notebook or Bioluminescent Laboratory depending on tone, then add a stronger hero concept.
- Existing design system already exists: use Refero only to sharpen spacing, typography, and component grammar; do not replace the system wholesale.
