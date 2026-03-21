# WCBNW — Whiskey Creek Beach NW

Marketing website for a beach vacation rental property in Port Angeles, WA.

## Project Structure

```
NEW/                  ← source of truth, this is what gets deployed
  *.html              ← one file per page
  js/nav-loader.js    ← dynamically injects shared nav into pages
  partials/nav.html   ← shared nav markup (desktop + mobile)
  images/             ← Website assets (backgrounds, property photos, logo, icons)
    bkgds/            ← section background textures
    properties/       ← property listing photos
    about/            ← about page images
  photos/             ← Photos from local camera/shoots
    outdoor/          ← beach/outdoor shots
    codfish/          ← Codfish Cottage photos
    halibut hole/     ← Halibut Hole photos
    jasper/           ← Jasper Inn photos
OLD/                  ← legacy site (local only, gitignored, do not touch)
Website/              ← original asset source (local only, gitignored)
Photos/               ← full photo library (local only, gitignored)
```

## Deployment

- **Hosting:** Render (static site), auto-deploys on push to `main`
- **Publish directory:** `NEW`
- **Build command:** none (pure HTML/CSS/JS, no build step)
- Config: `render.yaml` in repo root

## Pages

| File | Page |
|------|------|
| `index.html` | Home |
| `accommodations.html` | Accommodations (manual property cards) |
| `accommodations_guesty.html` | Accommodations (Guesty widget version) |
| `about.html` | About Us |
| `contact.html` | Contact |
| `policies.html` | Booking, Cancellation & Pet Policies |
| `other-properties.html` | Other Properties |

## Navigation

The nav is a shared partial at `partials/nav.html`, injected at runtime by `js/nav-loader.js` into a `<div id="site-nav-placeholder">` in each page. Each page includes:

```html
<div id="site-nav-placeholder"></div>
<script src="js/nav-loader.js" defer></script>
```

**Note:** `policies.html` currently has an inline nav (not using the partial) — it should be migrated to the partial pattern when convenient.

## Styles

- No CSS framework — all styles are inline `<style>` blocks per page
- Font: Josefin Sans (Google Fonts) + Copperplate (system) for headings
- Color palette defined as CSS variables:
  - `--navy: #293b4e`
  - `--cream: #f6efe5`
  - `--sage: #b5b8a3`
  - `--brown: #6b452e`

## Images

All images must live inside `NEW/` to be served by Render. Do **not** reference `../Website/` or `../Photos/` — those paths only exist locally and will 404 in production. When adding new images, copy them into `NEW/images/` or `NEW/photos/` first.

## Responsive / Mobile

Mobile traffic is a priority. After every push, check all pages at 375px width (iPhone). Key things to verify:
- Nav collapses to hamburger, no overflow
- Tab bars wrap rather than clip (accommodations page)
- Images fill width, not overflow
- Text is readable, not too small
- Footer stacks cleanly
- Forms are full-width and usable

Use the Claude Preview tool with `preset: mobile` to check before committing.

## Version Number

Every page footer displays a version string (e.g. `v1.0.4`) below the copyright line via `<span class="site-version">`.

**Update this with every push.** It is the primary way to confirm a Render deployment completed successfully. Bump the patch number (third digit) for routine changes, minor for larger changes.

Current version: **v1.0.6**

To update: find `site-version">v1.0.x` across all 7 HTML files and increment.

## Key Business Info

- **Address:** 1385 Whiskey Creek Beach Rd, Port Angeles, WA 98363
- **Phone:** (844) 769-2322
- **Email:** whiskeycreekbeachnw@gmail.com
- **Booking platform:** reservenow.com (also Guesty widget on accommodations_guesty.html)
