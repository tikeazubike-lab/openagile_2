---
type: FR
id: F-028
title: Landing Page Redesign — Kidza-Style Playful Education Theme
status: ACTIVE
version: 1.0
updated: 2026-08-16
author: OpenCode (Builder)
---

# F-028 — Landing Page Redesign (Kidza-Style)

## 1. Purpose

Redesign the public landing page of `tutor-connect-hub` to match the visual language of the target design image (`website_redesign_2.png`). The target is a playful, early-childhood/education theme ("Kidza") with rounded shapes, bold friendly colors, and a warm, approachable feel.

**Content stays the same** — the site still sells tutoring services. Only the visual design, layout, colors, typography, and component styling change.

## 2. Scope

### In Scope
- Global design tokens (colors, fonts, radii, shadows)
- `index.html` title, meta, and font imports
- `Header` — top contact bar + playful nav
- `Footer` — multi-column footer with brand colors
- `HeroSection` — two-column hero with badge, headline, CTAs, decorative illustration
- `SubjectsSection` — pastel rounded subject cards
- `HowItWorksSection` — numbered step cards with playful icons
- `TestimonialsSection` — rounded testimonial cards with avatars
- `CTASection` — orange/wavy call-to-action

### Out of Scope
- Dashboard pages (owner, tutor, student)
- Authentication flows
- Payment logic
- Backend API changes
- New images/photography assets (use CSS/SVG/icons)

## 3. Design Tokens

### Color Palette (extracted from target image)

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-primary-500` | `#6C5CE7` | Main purple (header bar, sections, buttons) |
| `--color-primary-600` | `#5B4BD4` | Primary hover |
| `--color-primary-100` | `#E8E5FC` | Light primary backgrounds |
| `--color-secondary-500` | `#FF8C42` | Orange CTA buttons |
| `--color-secondary-600` | `#F07A2D` | Orange hover |
| `--color-accent-yellow` | `#FFD93D` | Highlights, badges, hero bg accents |
| `--color-accent-pink` | `#FFB7C5` | Soft pink card accents |
| `--color-accent-mint` | `#B8F2E6` | Soft mint card accents |
| `--color-accent-cyan` | `#A0E7E5` | Soft cyan card accents |
| `--color-cream` | `#FFFBEB` | Hero/section background |
| `--color-background` | `#FFFFFF` | Page background |
| `--color-foreground` | `#1F2937` | Body text |
| `--color-muted` | `#F9FAFB` | Muted backgrounds |
| `--color-muted-foreground` | `#6B7280` | Secondary text |
| `--color-border` | `#E5E7EB` | Borders |

### Typography

| Element | Font | Weight | Size |
|---------|------|--------|------|
| Headings | Nunito | 700-800 | H1: 3rem / H2: 2.25rem |
| Body | Nunito | 400-600 | Base: 1rem |
| Badges | Nunito | 700 | 0.75rem |
| Buttons | Nunito | 700 | 0.875rem |

### Shapes

- Buttons: `rounded-full` (pill shape) for primary CTAs, `rounded-2xl` for cards
- Cards: `rounded-2xl` to `rounded-3xl` with soft shadows
- Icons: circular colored badges with white icons
- Decorative: hand-drawn-style doodles (SVG) and blobs

## 4. Section-by-Section Design

### Header
- Top purple bar with contact email/phone on the left, social links on the right
- Main nav: logo (GraduationCap icon + "TutorConnect" text), nav links, orange pill "Get Started" CTA
- Mobile: hamburger menu with same links

### HeroSection
- Background: soft cream `#FFFBEB` with decorative blobs/doodles
- Left: small purple badge ("Trusted by 500+ students"), large friendly headline, subheadline, two CTAs (orange primary + outline secondary)
- Right: stylized illustration — large rounded card or image placeholder with floating subject cards, star ratings, and decorative elements

### SubjectsSection
- White background
- Centered section title + subtitle
- 12 subject cards in a 4-column grid (2 on mobile, 3 on tablet)
- Each card: rounded-2xl, soft pastel background, large circular icon, subject name, tutor count, hover lift

### HowItWorksSection
- Light purple/cream background
- Centered title + subtitle
- 4 step cards with large numbered badges (1-4), circular icon, title, description
- Connected with a subtle dashed line on desktop

### TestimonialsSection
- White background
- Centered title + subtitle
- 3 testimonial cards: rounded-2xl, light pastel backgrounds alternating, 5-star rating, quote, avatar + name + role

### CTASection
- Orange background with wavy top/bottom divider or rounded corners
- Centered headline, subtext, two CTAs (white primary + orange outline)

### Footer
- Purple background
- 4 columns: brand + tagline, Platform links, Subjects, Contact
- Bottom bar with copyright
- White/light text on purple

## 5. Responsive Behavior

- Desktop (≥1024px): full multi-column layouts
- Tablet (768-1023px): 2-3 column grids, stacked hero
- Mobile (<768px): single column, hamburger menu, full-width cards, smaller hero text

## 6. Acceptance Criteria

- [ ] `npm run build` passes with no TypeScript or Tailwind errors
- [ ] All five home sections use the new Kidza color palette and rounded shapes
- [ ] Header includes purple top bar and orange pill CTA
- [ ] Footer uses purple background with white text
- [ ] Buttons are pill-shaped where appropriate
- [ ] Text remains readable (WCAG AA contrast on primary text)
- [ ] Mobile layout is usable and visually consistent
- [ ] No functional regressions in navigation, auth, or routing

## 7. Verification Steps

```bash
cd /home/zubbyik/openagile_2/frappe_docker/tutor-connect-hub
npm run build
```

Expected: build completes, `dist/` folder is generated with no errors.

## 8. Rollback

Restore the previous commit on `test` branch if visual regressions are found:

```bash
git checkout test
git log --oneline -5
git revert <commit-hash>
```
