# Design System Master File

> **LOGIC:** When building a specific page, first check `design-system/pages/[page-name].md`.
> If that file exists, its rules **override** this Master file.
> If not, strictly follow the rules below.

---

**Project:** Quivira
**Generated:** 2026-03-28 16:03:24
**Category:** Fintech/Crypto

---

## Global Rules

### Color Palette

| Role | Hex | CSS Variable |
|------|-----|--------------|
| Primary Background | `#0A0A0A` | `--color-bg-primary` |
| Secondary Background | `#111111` | `--color-bg-secondary` |
| Tertiary Background | `#1A1A1A` | `--color-bg-tertiary` |
| CTA/Accent | `#E63946` | `--color-cta` |
| CTA Hover | `#FF4D5A` | `--color-cta-hover` |
| Text Primary | `#FFFFFF` | `--color-text` |
| Text Secondary | `#A0A0A0` | `--color-text-secondary` |
| Text Muted | `#666666` | `--color-text-muted` |
| Border | `#222222` | `--color-border` |
| Border Hover | `#333333` | `--color-border-hover` |

**Color Notes:** Dark theme with red accent — matches Quivira brand identity. No light backgrounds.

### Typography

- **Heading Font:** Inter (weight 700-800 for bold, modern, clean aesthetic)
- **Body Font:** Inter (weight 400 for readability)
- **Mood:** Bold, modern, authoritative, clean, dark, premium
- **Google Fonts:** [Inter](https://fonts.google.com/share?selection.family=Inter:wght@400;500;600;700;800)

**CSS Import:**
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
```

### Spacing Variables

| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | `4px` / `0.25rem` | Tight gaps |
| `--space-sm` | `8px` / `0.5rem` | Icon gaps, inline spacing |
| `--space-md` | `16px` / `1rem` | Standard padding |
| `--space-lg` | `24px` / `1.5rem` | Section padding |
| `--space-xl` | `32px` / `2rem` | Large gaps |
| `--space-2xl` | `48px` / `3rem` | Section margins |
| `--space-3xl` | `64px` / `4rem` | Hero padding |

### Shadow Depths

| Level | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle lift |
| `--shadow-md` | `0 4px 6px rgba(0,0,0,0.1)` | Cards, buttons |
| `--shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | Modals, dropdowns |
| `--shadow-xl` | `0 20px 25px rgba(0,0,0,0.15)` | Hero images, featured cards |

---

## Component Specs

### Buttons

```css
/* Primary Button */
.btn-primary {
  background: linear-gradient(135deg, #E63946, #FF6B6B);
  color: #FFFFFF;
  padding: 14px 28px;
  border-radius: 8px;
  font-weight: 600;
  transition: all 200ms ease;
  cursor: pointer;
}

.btn-primary:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 20px rgba(230, 57, 70, 0.3);
}

/* Secondary Button */
.btn-secondary {
  background: transparent;
  color: #FFFFFF;
  border: 1px solid #222222;
  padding: 14px 28px;
  border-radius: 8px;
  font-weight: 600;
  transition: all 200ms ease;
  cursor: pointer;
}

.btn-secondary:hover {
  border-color: #333333;
  background: #1A1A1A;
}
```

### Cards

```css
.card {
  background: #111111;
  border: 1px solid #222222;
  border-radius: 12px;
  padding: 32px;
  transition: all 300ms ease;
  cursor: pointer;
}

.card:hover {
  border-color: #333333;
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
```

### Inputs

```css
.input {
  background: #1A1A1A;
  color: #FFFFFF;
  padding: 14px 16px;
  border: 1px solid #222222;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 200ms ease;
}

.input:focus {
  border-color: #E63946;
  outline: none;
  box-shadow: 0 0 0 3px rgba(230, 57, 70, 0.15);
}
```

### Modals

```css
.modal-overlay {
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
}

.modal {
  background: #111111;
  border: 1px solid #222222;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  max-width: 500px;
  width: 90%;
}
```

---

## Style Guidelines

**Style:** Exaggerated Minimalism

**Keywords:** Bold minimalism, oversized typography, high contrast, negative space, loud minimal, statement design

**Best For:** Fashion, architecture, portfolios, agency landing pages, luxury brands, editorial

**Key Effects:** font-size: clamp(3rem 10vw 12rem), font-weight: 900, letter-spacing: -0.05em, massive whitespace

### Page Pattern

**Pattern Name:** Trust & Authority

- **CTA Placement:** Above fold
- **Section Order:** Hero > Features > CTA

---

## Anti-Patterns (Do NOT Use)

- ❌ Playful design
- ❌ Unclear fees
- ❌ AI purple/pink gradients

### Additional Forbidden Patterns

- ❌ **Emojis as icons** — Use SVG icons (Heroicons, Lucide, Simple Icons)
- ❌ **Missing cursor:pointer** — All clickable elements must have cursor:pointer
- ❌ **Layout-shifting hovers** — Avoid scale transforms that shift layout
- ❌ **Low contrast text** — Maintain 4.5:1 minimum contrast ratio
- ❌ **Instant state changes** — Always use transitions (150-300ms)
- ❌ **Invisible focus states** — Focus states must be visible for a11y

---

## Pre-Delivery Checklist

Before delivering any UI code, verify:

- [ ] No emojis used as icons (use SVG instead)
- [ ] All icons from consistent icon set (Heroicons/Lucide)
- [ ] `cursor-pointer` on all clickable elements
- [ ] Hover states with smooth transitions (150-300ms)
- [ ] Light mode: text contrast 4.5:1 minimum
- [ ] Focus states visible for keyboard navigation
- [ ] `prefers-reduced-motion` respected
- [ ] Responsive: 375px, 768px, 1024px, 1440px
- [ ] No content hidden behind fixed navbars
- [ ] No horizontal scroll on mobile
