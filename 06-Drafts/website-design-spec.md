# bigquivdigitals.com — Framer Design Specification

> Idotive-inspired dark/bold/modern aesthetic, adapted for Quivira brand.

---

## Color System

| Token | Hex | Usage |
|-------|-----|-------|
| `bg-primary` | `#0A0A0A` | Page background |
| `bg-secondary` | `#111111` | Card backgrounds, sections with contrast |
| `bg-tertiary` | `#1A1A1A` | Hover states, input fields |
| `accent` | `#E63946` | CTAs, highlights, active states, red accents |
| `accent-hover` | `#FF4D5A` | Button hover, link hover |
| `text-primary` | `#FFFFFF` | Headlines, primary text |
| `text-secondary` | `#A0A0A0` | Body text, descriptions |
| `text-muted` | `#666666` | Captions, labels, meta text |
| `border` | `#222222` | Card borders, dividers |
| `border-hover` | `#333333` | Card hover borders |
| `gradient-red` | `linear-gradient(135deg, #E63946, #FF6B6B)` | CTA buttons, accent elements |
| `gradient-dark` | `linear-gradient(180deg, #0A0A0A, #111111)` | Section transitions |

---

## Typography

**Font Family:** Inter (Google Fonts) — fallback: system-ui, -apple-system, sans-serif

| Element | Size (Desktop) | Size (Mobile) | Weight | Line Height | Letter Spacing |
|---------|---------------|---------------|--------|-------------|----------------|
| H1 (Hero) | 72px | 40px | 800 | 1.05 | -0.02em |
| H2 (Section) | 48px | 32px | 700 | 1.15 | -0.01em |
| H3 (Card title) | 24px | 20px | 600 | 1.3 | 0 |
| Body Large | 20px | 18px | 400 | 1.6 | 0 |
| Body | 16px | 16px | 400 | 1.6 | 0 |
| Body Small | 14px | 14px | 400 | 1.5 | 0 |
| Caption | 12px | 12px | 500 | 1.4 | 0.05em |
| Button | 16px | 16px | 600 | 1 | 0.02em |
| Nav Link | 14px | 14px | 500 | 1 | 0.02em |
| Stat Number | 56px | 36px | 800 | 1 | -0.02em |
| Stat Label | 14px | 12px | 500 | 1.4 | 0.05em |

**Rotating keyword in hero:** Same as H1, but with `accent` color and a typewriter/swap animation (300ms ease, 3s interval).

---

## Spacing System (8px Grid)

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | 4px | Inline gaps |
| `sm` | 8px | Tight element spacing |
| `md` | 16px | Default internal padding |
| `lg` | 24px | Card internal padding |
| `xl` | 32px | Section internal gaps |
| `2xl` | 48px | Between content blocks |
| `3xl` | 64px | Between major sections (mobile) |
| `4xl` | 96px | Between major sections (desktop) |
| `5xl` | 128px | Hero top/bottom padding |

**Section padding:** `96px` top/bottom on desktop, `64px` on mobile.
**Container max-width:** `1200px`, centered, with `24px` horizontal padding on mobile.

---

## Responsive Breakpoints

| Name | Width | Columns | Gutter |
|------|-------|---------|--------|
| Mobile | < 768px | 1 | 16px |
| Tablet | 768px – 1024px | 2 | 24px |
| Desktop | > 1024px | 3 (or 4 for grids) | 32px |

**Layout rules:**
- 3-column grids → 2 on tablet → 1 on mobile (stacked)
- Hero text: centered on all breakpoints
- Nav: horizontal on desktop, hamburger on mobile/tablet
- Cards: full-width on mobile, maintain aspect ratio
- Trust bar: horizontal scroll on mobile, grid on desktop
- Pricing tables: horizontal scroll on mobile, full grid on desktop

---

## Component Patterns

### Nav Bar
- **Position:** Fixed top, `bg-primary` with 80% opacity + backdrop blur (12px)
- **Height:** 64px
- **Logo:** Left-aligned, white text "Quivira", 20px, weight 700
- **Links:** Center, `text-secondary`, hover → `text-primary`, 14px weight 500
- **CTA:** Right, red accent button "Book a Call"
- **Mobile:** Hamburger icon right, full-screen overlay menu

### Buttons

**Primary (CTA):**
- Background: `gradient-red`
- Text: `#FFFFFF`, 16px, weight 600
- Padding: `14px 28px`
- Border-radius: `8px`
- Hover: scale 1.02, shadow `0 4px 20px rgba(230, 57, 70, 0.3)`
- Arrow icon (→) right-aligned, 4px gap

**Secondary:**
- Background: transparent
- Border: 1px `border`
- Text: `text-primary`
- Padding: `14px 28px`
- Border-radius: `8px`
- Hover: border `border-hover`, background `bg-tertiary`

### Cards

**Service/Product Card:**
- Background: `bg-secondary`
- Border: 1px `border`
- Border-radius: `12px`
- Padding: `32px`
- Hover: border `border-hover`, translateY(-4px), shadow `0 8px 32px rgba(0,0,0,0.3)`
- Transition: 300ms ease

**Layout inside card:**
1. Icon (24px, `accent` color) or image
2. Title (H3)
3. Description (Body, `text-secondary`)
4. Price (if applicable — Body Large, `text-primary`, weight 700)
5. CTA link (accent color, arrow icon)

### Stat Card (Trust Bar)
- Background: `bg-secondary`
- Border-radius: `12px`
- Padding: `24px`
- Number: `Stat Number` style, `text-primary`
- Label: `Stat Label` style, `text-secondary`
- Subtle red glow on number: `text-shadow: 0 0 20px rgba(230, 57, 70, 0.2)`

### Testimonial Card
- Background: `bg-secondary`
- Border-left: 3px `accent`
- Border-radius: `8px`
- Padding: `32px`
- Quote: Body Large, italic, `text-primary`
- Attribution: Body Small, `text-secondary`

### CTA Banner
- Background: `bg-secondary` or subtle gradient
- Full-width section
- Centered text
- Headline: H2
- Subtext: Body Large, `text-secondary`
- Button: Primary CTA, centered
- Optional: subtle red accent line above (3px, centered, 80px wide)

### FAQ Accordion
- Background: `bg-secondary`
- Border: 1px `border`
- Border-radius: `8px`
- Question: H3, `text-primary`, click to expand
- Answer: Body, `text-secondary`, expandable
- Chevron icon right, rotates 180° on open
- Transition: 200ms ease

### Contact Form
- Input background: `bg-tertiary`
- Border: 1px `border`
- Border-radius: `8px`
- Padding: `14px 16px`
- Focus: border `accent`, subtle glow
- Label: Caption, `text-muted`
- Dropdown: same style as inputs
- Submit: Primary CTA button

### Footer
- Background: `bg-primary`
- Top border: 1px `border`
- Padding: `64px` top, `32px` bottom
- 4-column grid on desktop (Logo + tagline | Pages | Socials | Contact)
- 1-column stacked on mobile
- Social icons: 20px, `text-secondary`, hover → `text-primary`
- Copyright: Caption, `text-muted`, centered bottom

---

## Animation Specs

### Scroll Reveal (All Sections)
- **Type:** Fade up + slight blur
- **Initial state:** opacity 0, translateY(24px), filter blur(4px)
- **Animate to:** opacity 1, translateY(0), filter blur(0)
- **Duration:** 600ms
- **Easing:** cubic-bezier(0.16, 1, 0.3, 1)
- **Trigger:** When element enters viewport (threshold: 20%)
- **Stagger:** Cards within a grid stagger 100ms each

### Hero Keyword Rotation
- **Type:** Vertical swap with fade
- **Words cycle:** Trading → AI → Web3 → Education
- **Interval:** 3 seconds
- **Transition:** 300ms ease, fade out up + fade in up
- **Color:** `accent` for the rotating word only

### Button Hover
- **Scale:** 1.02
- **Shadow:** `0 4px 20px rgba(230, 57, 70, 0.3)` (primary only)
- **Duration:** 200ms ease

### Card Hover
- **TranslateY:** -4px
- **Border:** `border-hover`
- **Shadow:** `0 8px 32px rgba(0,0,0,0.3)`
- **Duration:** 300ms ease

### Nav on Scroll
- **Backdrop blur:** activates after 50px scroll
- **Background opacity:** transitions from 0% to 80%
- **Duration:** 200ms ease

### Page Load
- **Hero elements:** Staggered fade-in (headline → subheadline → CTAs → image)
- **Stagger:** 150ms between elements
- **Duration:** 600ms each

---

## Page-by-Page Section Layout

### HOME
1. Nav (fixed)
2. Hero — full viewport height, centered content, image right (or below on mobile)
3. Trust Bar — 4 stat cards in a row, `4xl` padding
4. What I Do — 3-column card grid
5. Featured Products — 3-column product cards
6. Results/Social Proof — stat cards + testimonial carousel
7. CTA Banner — full-width, centered
8. Footer

### SERVICES
1. Nav
2. Hero — half-height, centered text
3. Consulting Services — 5 cards, 3-column grid (last row centered)
4. Education Products — 5 cards, 3-column grid
5. AI Products — 3 featured product cards (larger, more detail)
6. CTA Banner
7. Footer

### PRICING
1. Nav
2. Hero — half-height, centered text
3. Personal Services — table or card list
4. Quivira OS Tiers — 3 product sections, each with 3-column comparison
5. FAQ — accordion list
6. CTA Banner
7. Footer

### ABOUT
1. Nav
2. Hero — character portrait left, text right (stacked on mobile)
3. Story — single column, max-width 720px centered
4. Mission — centered text block
5. Values — 3-column cards
6. Brands/Pillars — 4-column grid (2x2 on mobile)
7. Footer

### PORTFOLIO
1. Nav
2. Hero — half-height
3. Case Studies — 4-column card grid (2x2 on tablet, 1-col mobile)
4. Testimonials — horizontal carousel, auto-scroll
5. CTA Banner
6. Footer

### CONTACT
1. Nav
2. Hero — half-height
3. Contact Options — 3 cards side by side
4. Social Links — horizontal icon row
5. Contact Form — centered, max-width 600px
6. Footer

---

## Asset Checklist

| Asset | Format | Size | Notes |
|-------|--------|------|-------|
| Hero image (home) | PNG/WebP | 800x1000px | Low-angle character shot, dark bg, red accent |
| Character portrait (about) | PNG/WebP | 600x800px | Confident, composed, dark bg |
| Service icons (6) | SVG | 24x24px | Minimal line style, white, accent on hover |
| Product mockups (3) | PNG/WebP | 800x600px | SignalOS dashboard, ContentBrain interface, Quivira OS |
| Trust bar stats | Built in Framer | — | No image needed, use stat card component |
| Social proof cards | Built in Framer | — | Testimonial card component |
| OG image | PNG | 1200x630px | Brand name + tagline + dark bg + red accent |
| Favicon | ICO/SVG | 32x32px | "Q" lettermark, red on dark |

---

## Framer-Specific Notes

1. **CMS Collections:** Create collections for Testimonials, Case Studies, and FAQ items so they're editable without touching layout
2. **Components:** Build reusable components for Card, Button, Stat Card, Testimonial Card, CTA Banner, Section Wrapper
3. **Variables:** Store all colors, fonts, and spacing as Framer design tokens for easy global changes
4. **SEO:** Set meta title, description, and OG image per page
5. **Forms:** Use Framer's native form component or embed Tally/Typeform for the contact form
6. **Analytics:** Add Google Analytics or Plausible tracking code in site settings
7. **Custom domain:** After build, connect bigquivdigitals.com via Framer's domain settings (DNS instructions below)

---

## Domain Connection: Namecheap → Framer

### Step 1: Get Framer DNS Records
1. In Framer, go to Site Settings → Custom Domain
2. Add `bigquivdigitals.com`
3. Framer will provide DNS records (typically an A record and/or CNAME)

### Step 2: Update Namecheap DNS
1. Log into Namecheap → Domain List → bigquivdigitals.com → Manage
2. Go to Advanced DNS tab
3. Delete existing A records and CNAME for @ and www
4. Add the records Framer provides:
   - **A Record:** Host `@`, Value: Framer's IP (e.g., `75.2.70.75`)
   - **CNAME:** Host `www`, Value: `proxy.framer.app`
5. Save changes

### Step 3: Verify
- DNS propagation takes 1-48 hours (usually under 1 hour)
- Return to Framer's Custom Domain settings and click "Verify"
- Framer auto-provisions SSL certificate

### Step 4: Disable WordPress Hosting (Optional)
- If you want to stop paying for Namecheap hosting, you can cancel the hosting plan separately
- The domain registration stays active regardless of hosting

---

*End of design specification.*
