# WCBNW — Whiskey Creek Beach NW

Marketing website for a beach vacation rental property in Port Angeles, WA.

## Keeping HANDOFF.md Current

`HANDOFF.md` is the primary reference document for anyone maintaining this site. Keep it up to date as the project evolves. Any time you make a change that affects how the site works — new integrations, changed services, new pages, updated workflows, removed features — update `HANDOFF.md` to reflect the current state. When `HANDOFF.md` changes, also re-run `generate_pdf.py` to regenerate `WCBNW-Website-Guide.pdf`.

## Project Structure

```
NEW/                  ← source of truth, this is what gets deployed
  *.html              ← one file per page
  js/nav-loader.js    ← dynamically injects shared nav into pages
  js/footer-loader.js ← dynamically injects shared footer into pages
  partials/nav.html   ← shared nav markup (desktop + mobile)
  partials/footer.html← shared footer markup (links, contact, version)
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

## Branching & Staging

All changes should be made on the `staging` branch first, then merged to `main` when verified.

| Branch | Render URL | Purpose |
|--------|-----------|---------|
| `main` | https://wcbnw.onrender.com (also www.whiskeycreekbeachnw.com) | Production — live site |
| `staging` | https://wcbnw-stage.onrender.com | Staging — verify before going live |

**Workflow:**
1. Make sure you're on the `staging` branch before making changes
2. Push changes to `staging` — Render auto-deploys to the staging URL within ~2 minutes
3. Review at https://wcbnw-stage.onrender.com
4. When satisfied, merge `staging` → `main` and push — production updates automatically

**To merge staging to main:**
```
git checkout main
git merge staging
git push
git checkout staging
```

## Pages

| File | Page |
|------|------|
| `index.html` | Home |
| `accommodations.html` | Accommodations (dynamic cards from listings.json) |
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

All pages now use the shared nav partial, including `policies.html` (migrated v2.2.1).

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

Current version: **v2.2.4**

**The footer is now a shared partial.** To update the version, edit ONE file only:
```
NEW/partials/footer.html  ← change the site-version span here
```
Also update the `Current version` line above in this file.

**Commit message format:** Always lead the commit message with the version number so it is visible on the Render dashboard. Example:
```
v2.0.0 fix: correct nav anchor IDs for dynamic sections
```

## Third-Party Services

### Formspree (Contact Form)
- **Account login:** yerfttam@icloud.com
- **Form endpoint:** `https://formspree.io/f/xkoqaqjr`
- **Used on:** `contact.html`
- Submissions are emailed to `whiskeycreekbeachnw@gmail.com`
- Free tier: 50 submissions/month

### Guesty (Property Listings)
- **Account:** app.guesty.com
- **Open API client ID:** `0oatpyo652QA9S4Av5d7`
- **Booking base URL:** `https://whiskeycreekbeachnw.guestybookings.com`
- **Listings data:** `NEW/data/listings.json` (generated by `scripts/sync-guesty.py`)
- **Property map:** `NEW/property-map.txt` (owner-defined categories + Guesty IDs)
- **Daily sync:** GitHub Actions workflow at `.github/workflows/sync-guesty.yml` — runs at 9am Pacific (17:00 UTC) every day, commits updated `listings.json` if changed, triggers Render redeploy
- **GitHub Secrets configured:** `GUESTY_CLIENT_ID`, `GUESTY_CLIENT_SECRET`, and `NTFY_TOPIC` — set 2026-03-22

### ntfy.sh (Sync Notifications)
- **App:** ntfy.sh — free push notification service, no account required
- **Used for:** Guesty sync job success/failure alerts
- **Topic:** stored as GitHub secret `NTFY_TOPIC` (treat like a password — don't hardcode it)
- **Setup:** Install the ntfy app on your phone and subscribe to the topic name stored in `NTFY_TOPIC`
- Success sends a green checkmark notification; failure sends a high-priority alert
- Configured 2026-03-26

### Newsletter Section (visual divider, no text)
- As of v2.0.0 the newsletter section is present on all pages as an **empty visual divider** — sage panel left, `wcb-4.jpg` rocks photo right, no text or form
- The original text ("Sign Up for Our Newsletter" / "20% Off" deal) has been removed
- To restore text/form: add content back inside `.newsletter-left` and `.newsletter-right` in each page and wire the email input to Mailchimp or similar
- CSS: `.newsletter-section { min-height: 100px; }` — intentionally short as a decorative band

### Render (Hosting)
- Auto-deploys on push to `main`
- Publish directory: `NEW`
- Confirm deploys by checking the version number in any page footer

## Page Hero Notes

Each inner page has a hero banner with a background photo. Overlays have been intentionally **removed** on all inner pages as of v2.0.0 — the photos show through cleanly.

| Page | Hero Image | Overlay | Subtitle text |
|------|-----------|---------|---------------|
| `index.html` | `photos/outdoor/DSC_0020.JPG` | yes (navy, for readability) | none |
| `about.html` | `photos/outdoor/DSC_0318.JPG` | **none** | none |
| `contact.html` | inherited from page design | n/a | n/a |
| `policies.html` | `photos/outdoor/DSC_0397.jpg` | **none** | none |
| `other-properties.html` | `images/properties/Other_Properties_main_photo.jpg` | **none** | none |

Background images that use `bkgd1.jpg` (no crab icon baked in):
- `about.html` `.story-section`
- `contact.html` `.contact-section`

Do **not** use `bkgds/bkgd1-icon.jpg` — it has a crab illustration baked into the texture.

## Key Business Info

- **Address:** 1385 Whiskey Creek Beach Rd, Port Angeles, WA 98363
- **Phone:** (844) 769-2322
- **Email:** whiskeycreekbeachnw@gmail.com
- **Booking platform:** Guesty (app.guesty.com)
