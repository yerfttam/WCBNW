# WCBNW Redesign — "Where the Forest Meets the Sea"

## Design Vision

A cinematic, scroll-driven experience that sells the *feeling* of being at Whiskey Creek Beach before a guest ever books. The current site is informational — the redesign is **emotional**. Every section pulls visitors deeper into the Pacific Northwest: mist on the Strait, driftwood on the shore, firelight in a cabin window.

---

## Visual Identity

### Color Palette (evolved from current)
| Token | Hex | Usage |
|-------|-----|-------|
| `--midnight` | `#1a2634` | Primary dark — nav, hero overlays, footer |
| `--drift` | `#f4ede4` | Warm off-white backgrounds |
| `--stone` | `#8c8677` | Secondary text, subtle borders |
| `--moss` | `#6b7f5e` | Accent — buttons, highlights, badges |
| `--copper` | `#b87944` | Warm accent — prices, CTAs, hover states |
| `--fog` | `#d5dbe0` | Light cool gray — card backgrounds, dividers |
| `--white` | `#ffffff` | Cards, contrast panels |

**Rationale:** The current navy/cream/sage is pleasant but safe. This palette leans into the PNW's natural material palette — driftwood, moss, copper-tinged sunsets, morning fog over the Strait.

### Typography
| Role | Font | Weight | Style |
|------|------|--------|-------|
| Display headings | **Playfair Display** | 700, 900 | Serif — editorial, premium feel |
| Body / UI | **Inter** | 300, 400, 500, 600 | Sans-serif — crisp, modern readability |
| Accent / labels | **Inter** | 500 | Uppercase, wide letter-spacing |

**Rationale:** Copperplate feels dated. Playfair Display gives the same "premium lodge" feel but in a modern editorial context. Inter is the gold standard for web UI text.

### Photography Treatment
- **Hero images**: Full-bleed, edge-to-edge, slight desaturation + warm tone for cohesion
- **Property photos**: Clean, no filters — guests want to see what they're booking
- **Ambient overlays**: Subtle gradient overlays (not flat color blocks) — dark at top for nav readability, fading to transparent
- **Parallax**: Gentle parallax on section background images (CSS `background-attachment: fixed` or scroll-driven)

---

## Tech Stack

**Astro** (static site generator) — compiles to pure HTML/CSS/JS with zero client-side runtime by default.

**Why Astro:**
- Components without the framework tax — reusable nav, footer, property cards as `.astro` files
- Markdown/JSON content loading built in — `listings.json` becomes a first-class data source
- Islands architecture — only ship JS where interactive (carousels, modals, filters)
- Output is plain static HTML — deploys to Render identically to today
- No React/Vue/Svelte required — can use vanilla JS for interactions

**CSS:** Tailwind CSS via Astro integration — utility-first for rapid iteration, purged in production for tiny CSS bundles.

**Animations:** CSS scroll-driven animations + Intersection Observer for entrance effects. No heavy libraries.

---

## Site Architecture

### Pages

| Route | Content | New vs. Existing |
|-------|---------|-------------------|
| `/` | Home — cinematic landing + property highlights | **Reimagined** |
| `/properties` | All properties — filterable grid + map | **New** (replaces accommodations) |
| `/properties/[category]` | Category view (Beach Front Cabins, etc.) | **New** |
| `/properties/[slug]` | Individual property detail page | **New** (replaces modal popups) |
| `/experiences` | Curated collections — "Romantic Getaway", "Family Adventure", etc. | **New** |
| `/about` | Our story | **Reimagined** |
| `/contact` | Contact form + info | **Reimagined** |
| `/policies` | Booking, cancellation, pet policies | **Reimagined** |

### What Changes
- **Accommodations + Other Properties merge** into a single `/properties` hub with filtering
- **Property modals become full pages** — better for SEO, sharing, and the browsing experience
- **Experiences page** is new — curated property bundles for different trip types
- **Guesty widget page dropped** — the JSON-driven approach is superior and customizable

---

## Page-by-Page Design

### Home Page (`/`)

**Goal:** Make someone feel the pull of the Pacific Northwest in 5 seconds.

#### Section 1: Hero (100vh)
- **Full-screen video or animated photo sequence** of the Strait at golden hour
- Minimal text centered: logo mark + "Where the Forest Meets the Sea"
- Single ghost button: "Explore Our Properties"
- Subtle scroll indicator (animated chevron)
- Nav is transparent over hero, transitions to solid on scroll

#### Section 2: The Setting (scroll-triggered)
- **Two-column split**: Left is a tall vertical photo of the shoreline. Right has staggered text blocks that fade in on scroll:
  > "On the shores of the Strait of Juan de Fuca, where the Olympic Mountains meet the Pacific, a string of handcrafted cabins, cottages, and hideaways wait."
- Animated stat counters: "32 unique stays · 6 property styles · Steps from the beach"

#### Section 3: Property Showcase (interactive)
- **Horizontal scroll carousel** of featured/highlighted properties (large cards)
- Each card: full-bleed photo, property name, category badge, price, guest count
- Hover: subtle lift + second photo crossfade
- "View All Properties →" link

#### Section 4: Experiences Triptych
- Three large panels side by side (stacks on mobile):
  1. **"Romantic Escape"** — moody cabin interior photo, overlay text
  2. **"Family Adventure"** — beach/outdoor photo with kids
  3. **"Solo Retreat"** — A-frame with forest backdrop
- Each links to `/experiences` filtered view

#### Section 5: The Place
- **Full-width map illustration or aerial photo** of the property grounds
- Callout pins for key areas: "Beach Access", "Fire Pit", "Check-in"
- Brief paragraph about the location, proximity to Port Angeles, Olympic National Park

#### Section 6: Guest Testimonials (if available, placeholder for now)
- Rotating quote cards with subtle animation
- Star ratings, guest photos (placeholder avatars)

#### Section 7: Newsletter / CTA Band
- Warm copper-toned banner
- "Get 10% off your first stay" (or whatever offer applies)
- Email capture input + submit
- If no newsletter yet, make this a strong booking CTA instead

#### Section 8: Footer
- Rich footer: site map, contact info, social links, property categories
- Subtle background texture (driftwood grain pattern)

---

### Properties Page (`/properties`)

**Goal:** Make it effortless to find the perfect stay.

#### Layout
- **Sticky filter bar** at top (below nav):
  - Category pills: All | Beach Front Cabins | Cottages | A-Frames | Tent Sites | RV Sites
  - Guest count dropdown
  - Price range slider
  - "Pet Friendly" toggle
  - Sort: Featured / Price Low→High / Price High→Low / Guest Count
- **Grid view** (default): 3-column responsive card grid
- **Toggle to list view**: Horizontal cards with more detail
- Property count indicator: "Showing 32 properties"

#### Property Cards (Grid View)
- **Photo**: Top portion, 3:2 ratio, hover triggers subtle zoom
- **Photo dots**: Small indicators for multiple photos (carousel on click/swipe)
- **Category badge**: Small pill in top-left corner (e.g., "A-Frame", "Beachfront")
- **Name**: Playfair Display, bold
- **Snippet**: 2-line description
- **Details bar**: Icons + text — guests · beds · baths
- **Price**: "From $XX / night" in copper accent
- **CTA**: "View Details →" (whole card is clickable)

#### Category Sections
When "All" is selected, properties group by category with section headers:
- Category name (large, Playfair)
- Brief category description
- Property grid
- Subtle divider between categories

---

### Property Detail Page (`/properties/[slug]`)

**Goal:** This is the money page — convince the guest to book.

**This replaces the current modal popups.** Full dedicated pages are better for:
- SEO (each property gets its own URL)
- Shareability (guests can text a link to their travel partner)
- Space to breathe (more room for photos, details, and booking CTAs)

#### Layout

**Photo Gallery (top)**
- Hero-sized primary photo (full width, 60vh)
- Thumbnail strip below: 4-5 thumbnails visible, scroll for more
- Click any photo → fullscreen lightbox with arrow navigation
- On mobile: swipeable photo carousel

**Property Info (below gallery)**
- Two-column layout:
  - **Left (65%)**:
    - Property name + category badge
    - Quick stats row: guests · bedrooms · bathrooms
    - Full description (rendered from listings.json)
    - Amenities grid (icon + label for each amenity, grouped by type)
  - **Right (35%) — Sticky booking card**:
    - Price per night (large)
    - Cleaning fee note
    - "Check Availability" button → links to Guesty booking page
    - "Or call us: (844) 769-2322"
    - Small trust signals: "Free cancellation" (if applicable), "Instant booking"

**Below the fold:**
- "You might also like" — 3 related property cards (same category or similar)
- Location section with property address context
- Link to policies page

---

### Experiences Page (`/experiences`)

**Goal:** Help undecided visitors find their ideal trip type.

This is a **new concept** — curated collections that cross-cut categories.

#### Collections (defined in a JSON config)
| Collection | Properties Included | Vibe |
|-----------|-------------------|------|
| Romantic Escape | Select cabins + cottages with fireplaces/hot tubs | Warm, intimate |
| Family Adventure | Larger cabins + cottages (4+ guests) | Fun, spacious |
| Solo Retreat | A-Frames + small cabins | Quiet, reflective |
| Budget Friendly | Tent sites + RV sites + affordable cabins | Accessible, outdoorsy |
| Pet Friendly | All pet-friendly properties | Filter from amenities |
| Beachfront Living | All waterfront properties | Premium, scenic |

#### Layout
- Large hero card per collection (photo + overlay text + property count)
- Click into a collection → filtered property grid (reuses `/properties` grid component)

---

### About Page (`/about`)

**Goal:** Build trust and emotional connection with the place and people behind it.

#### Layout
- **Hero**: Cinematic landscape shot, text overlay: "Our Story"
- **Timeline or scroll-story**: Key moments in the property's history
  - How it started
  - The land and its history
  - The vision for guests
- **Photo grid**: Mix of property shots, nature, family/community
- **Values section**: 3 cards — "Sustainability", "Community", "Authenticity" (or whatever fits)
- **CTA**: "Come see for yourself → View Properties"

---

### Contact Page (`/contact`)

**Goal:** Make it dead simple to reach out.

#### Layout
- **Split layout**: Left = contact info card (address, phone, email, check-in/check-out times). Right = form.
- **Form fields** (same as today): First name, Last name, Email, Subject, Property interest dropdown, Message
- **Formspree integration** preserved (same endpoint)
- **Below form**: Embedded map (optional — Google Maps or a styled illustration)
- Clean, generous whitespace — the form should feel calm, not like a corporate intake form

---

### Policies Page (`/policies`)

**Goal:** Make policies clear and scannable without feeling like a legal document.

#### Layout
- **Accordion-style sections** (one open at a time):
  - Booking Policies
  - Cancellation Policies
  - Pet Policies
- **Each section**: Clean typography, bulleted lists, highlight boxes for key rules
- **Friendly tone**: "We want your stay to be perfect. Here's what to know."
- **Quick-reference sidebar** (desktop): Jump links to each policy section
- **CTA at bottom**: "Questions? Contact us" → link to contact page

---

## Navigation

### Desktop
- **Fixed top bar**, transparent on hero pages, solid `--midnight` on scroll
- **Logo** (left) — links to home
- **Links** (center): Properties · Experiences · About · Contact · Policies
- **CTA button** (right): "Book Now" in `--moss` green

### Mobile
- **Fixed top bar** with logo (left) + hamburger (right)
- **Full-screen overlay menu** on open (slides down, `--midnight` background)
- Large tap targets, category sub-links visible
- "Book Now" as a prominent button at bottom of menu

---

## Interactions & Micro-animations

| Element | Animation |
|---------|-----------|
| Hero text | Fade up on load (300ms delay) |
| Section content | Fade up + slight translate when scrolling into view |
| Property cards | Subtle lift on hover (translateY -4px + shadow) |
| Photo carousel | Crossfade transition between images |
| Nav background | Opacity transition from transparent → solid on scroll |
| Filter pills | Scale + color transition on active |
| Buttons | Background color shift on hover (200ms ease) |
| Page transitions | Subtle fade between pages (if using View Transitions API) |

**No heavy animation libraries.** CSS transitions + Intersection Observer only.

---

## Responsive Strategy

| Breakpoint | Behavior |
|-----------|----------|
| ≥1200px | Full desktop layout — 3-col grids, side-by-side sections |
| 768–1199px | Tablet — 2-col grids, slightly reduced spacing |
| <768px | Mobile — single column, stacked layout, hamburger nav |
| <480px | Small mobile — tighter padding, larger tap targets |

**Mobile-first CSS** — base styles are mobile, media queries add complexity for larger screens.

---

## Data & Integration

### listings.json (unchanged)
- Continue using the nightly Guesty sync via GitHub Actions
- Astro reads `listings.json` at build time to generate property pages
- Each property gets a static page at `/properties/[slug]`

### Experiences (new)
- New file: `data/experiences.json` — defines collections with:
  - Name, description, hero image
  - Array of property IDs or filter criteria (e.g., `amenities includes "Pet friendly"`)

### Contact Form
- Same Formspree endpoint: `https://formspree.io/f/xkoqaqjr`
- Same fields, modernized styling

### Booking Links
- All "Book Now" / "Check Availability" buttons → Guesty booking URLs (from listings.json)
- Main "Book Now" nav button → Guesty landing page

---

## What's Preserved from Today

Everything that works stays. Specifically:
- All 32 properties and 6 categories from listings.json
- Guesty booking URLs and integration
- Nightly sync workflow (GitHub Actions)
- Formspree contact form
- All existing photos and images (copied into new project)
- Business info (address, phone, email)
- Render deployment (just point publish dir to Astro's `dist/`)
- Booking, cancellation, and pet policies content

## What's New

- **Individual property pages** (SEO + shareability)
- **Experiences page** (curated collections for different trip types)
- **Advanced filtering** (guests, price, pet-friendly, category)
- **Modern design system** (Playfair + Inter, PNW color palette, editorial photography)
- **Component architecture** (Astro components for reuse)
- **Scroll-driven storytelling** on home page
- **View Transitions** for smooth page navigation
- **Better mobile experience** (full-screen menu, swipeable carousels, touch-optimized)

---

## Project Setup

New project directory alongside the existing one:
```
WCBNW/           ← existing repo (untouched)
WCBNW-redesign/  ← new project
  src/
    pages/        ← Astro pages
    components/   ← Shared components (Nav, Footer, PropertyCard, etc.)
    layouts/      ← Page layouts
    data/         ← listings.json, experiences.json
    styles/       ← Global CSS, design tokens
  public/
    images/       ← Copied from NEW/images/
    photos/       ← Copied from NEW/photos/
  astro.config.mjs
  package.json
```

---

## Summary

The redesign transforms WCBNW from a straightforward listing site into an **immersive destination brand**. The shift from modals to full property pages, the addition of experience-based browsing, the cinematic scroll storytelling, and the refined PNW-inspired design system all work together to make one thing happen: **guests picture themselves there and click "Book Now."**
