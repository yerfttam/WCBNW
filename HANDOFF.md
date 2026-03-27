# "If I Get Hit by a Beer Truck"
## Technical Handoff — Whiskey Creek Beach NW (WCBNW)

> This document is for the person who inherits technical ownership of this website.
> It covers everything you need to understand, maintain, and update the site.

---

## What Is This?

A marketing and booking website for a beach vacation rental property in Port Angeles, WA.
The live site is at **[www.whiskeycreekbeachnw.com](https://www.whiskeycreekbeachnw.com)**.

**The site is intentionally simple** — pure HTML, CSS, and JavaScript. No build tools, no
frameworks, no Node.js, no database. If you can edit a text file, you can update this site.

---

## Where the Code Lives

**GitHub repository:** (check with owner for the repo URL)

```
WCBNW/
  NEW/                   ← THIS is what gets deployed — the entire website
    *.html               ← One file per page
    js/
      nav-loader.js      ← Injects the shared nav into every page at runtime
      footer-loader.js   ← Injects the shared footer into every page at runtime
    partials/
      nav.html           ← Shared navigation markup (desktop + mobile hamburger)
      footer.html        ← Shared footer markup — also contains the version number
    images/              ← Website assets (backgrounds, logos, property photos)
      bkgds/             ← Texture backgrounds used in page sections
      properties/        ← Property listing photos
      about/             ← About page images
    photos/              ← Photography from shoots
      outdoor/           ← Beach and outdoor shots
      codfish/           ← Codfish Cottage photos
      halibut hole/      ← Halibut Hole photos
      jasper/            ← Jasper Inn photos
    data/
      listings.json      ← Auto-generated from Guesty daily (DO NOT hand-edit)
    property-map.txt     ← Owner-defined list of properties + Guesty IDs + booking URLs
  scripts/
    sync-guesty.py       ← Python script that pulls data from Guesty API
  .github/workflows/
    sync-guesty.yml      ← GitHub Actions job that runs sync-guesty.py every day
  render.yaml            ← Render hosting config (one line: publish NEW/)
  CLAUDE.md              ← AI assistant instructions (also useful reference for developers)
  HANDOFF.md             ← This file
```

> **⚠ Important:** `OLD/`, `Website/`, and `Photos/` directories exist locally only
> (gitignored). They are legacy/source material. Never reference them in code —
> those paths will 404 in production.

---

## How the Site Works

### Pages

| URL | File |
|-----|------|
| `/` | `index.html` |
| `/accommodations` | `accommodations.html` |
| `/about` | `about.html` |
| `/contact` | `contact.html` |
| `/policies` | `policies.html` |
| `/other-properties` | `other-properties.html` |

### Shared Nav & Footer

Rather than copy/pasting the nav into every page, it lives in one place:
`partials/nav.html`. Each page has a `<div id="site-nav-placeholder"></div>` and
loads `js/nav-loader.js`, which fetches the partial and injects it at runtime.
Same pattern for the footer via `js/footer-loader.js` + `partials/footer.html`.

**To change the nav or footer, edit the partial — one file, all pages update.**

### Styles

No CSS framework. Each page has its own `<style>` block. The design uses:
- **Fonts:** Josefin Sans (Google Fonts), Copperplate (system) for headings
- **Colors:**
  - `--navy: #293b4e`
  - `--cream: #f6efe5`
  - `--sage: #b5b8a3`
  - `--brown: #6b452e`

### Accommodations / Property Listings

The accommodations page (`accommodations.html`) dynamically renders property cards
from `NEW/data/listings.json`. That JSON file is generated every day by the Guesty
sync job (see below) and committed back to the repo if anything changed.

**The property catalog is controlled by `NEW/property-map.txt`** — this is the
owner-maintained list of which properties exist, what category they belong to,
and their Guesty IDs and booking URLs. If a property is added or removed from
Guesty, update `property-map.txt` accordingly.

---

## Hosting

**Host:** [Render](https://render.com) — static site, free tier

**How deploys work:**
1. You push a commit to the `main` branch on GitHub
2. Render detects the push and automatically redeploys within ~1-2 minutes
3. No build step — Render just serves the `NEW/` directory as static files

**Confirming a deploy worked:** Every page footer shows a version number (e.g. `v2.1.0`).
After a push, reload the site and check that the version number updated.

**Render config:** `render.yaml` in the repo root — it's three lines, just tells
Render to serve the `NEW/` folder.

**Render dashboard:** render.com — log in to see deploy history and logs if
something goes wrong.

---

## How to Update the Site

### Making a simple change (e.g. edit text, fix a typo)

1. Edit the relevant `.html` file in `NEW/`
2. Bump the version number in `NEW/partials/footer.html` (patch version, e.g. `v2.1.0` → `v2.1.1`)
3. Commit and push to `main`
4. Wait ~2 minutes, reload the site, confirm the new version number appears

### Adding a new image

1. Copy the image into `NEW/images/` or `NEW/photos/` (appropriate subfolder)
2. Reference it in HTML with a path like `photos/outdoor/myimage.jpg`
3. **Never** reference `../Website/` or `../Photos/` — those paths only exist locally

### Commit message format

Always start with the version number — it shows up on the Render dashboard:
```
v2.1.1 fix: correct typo on about page
```

### Version numbering

- **Patch** (third number): routine edits, typo fixes, content updates
- **Minor** (second number): new features, new pages, significant redesigns
- Update version in **one place only:** `NEW/partials/footer.html`

---

## Third-Party Services

### 1. Render (Hosting)
- **URL:** render.com
- **Plan:** Free static site
- **Auto-deploys:** Yes, on every push to `main`
- **Action needed:** Log in to Render to see deploy status or troubleshoot errors

---

### 2. Guesty (Property Management / Booking)
- **URL:** [app.guesty.com](https://app.guesty.com)
- **What it does:** Manages the property listings, availability, and bookings
- **Open API Client ID:** `0oatpyo652QA9S4Av5d7`
- **Client Secret:** Stored as GitHub secret `GUESTY_CLIENT_SECRET` (ask owner)
- **Booking base URL:** `https://whiskeycreekbeachnw.guestybookings.com`

**The sync flow:**
1. GitHub Actions runs `scripts/sync-guesty.py` every day at 9am Pacific
2. The script authenticates with Guesty's OAuth2 API, fetches all listings
3. It combines Guesty data with owner categories from `property-map.txt`
4. Writes the result to `NEW/data/listings.json`
5. If the file changed, commits and pushes it — which triggers a Render redeploy

**To run manually:** Go to GitHub → Actions → "Sync Guesty Listings" → "Run workflow"

**To add/remove a property:** Edit `NEW/property-map.txt` — follow the existing format
(category header, then `Name | GuestyID | BookingURL` lines)

---

### 3. ntfy.sh (Sync Notifications)
- **URL:** [ntfy.sh](https://ntfy.sh) — free, no account needed
- **What it does:** Sends push notifications to the owner's phone after each sync
- **Success:** ✅ "Listings synced successfully at [time]"
- **Failure:** 🚨 High-priority alert to check GitHub Actions

**Setup (if you need to receive these on a new phone):**
1. Install the ntfy app (iOS or Android)
2. Subscribe to the topic name stored in the GitHub secret `NTFY_TOPIC`
3. Get the topic name from the repo owner or GitHub → Settings → Secrets → `NTFY_TOPIC`

> **Treat `NTFY_TOPIC` like a password** — anyone who knows it can send notifications
> to that phone. Don't hardcode it anywhere; keep it in GitHub Secrets only.

---

### 4. Formspree (Contact Form)
- **URL:** [formspree.io](https://formspree.io)
- **Account login:** yerfttam@icloud.com
- **Form endpoint:** `https://formspree.io/f/xkoqaqjr`
- **Used on:** `contact.html`
- **What it does:** Receives contact form submissions and emails them to `whiskeycreekbeachnw@gmail.com`
- **Free tier:** 50 submissions/month — upgrade if volume increases

---

### 5. Google Fonts
- **What it does:** Loads Josefin Sans font on all pages
- **No account needed** — referenced via `<link>` tag in each page's `<head>`
- If Google Fonts goes down (rare), pages fall back to system sans-serif

---

## GitHub Actions (Automation)

Located in `.github/workflows/sync-guesty.yml`

**Schedule:** Daily at 9am Pacific (17:00 UTC), and can be triggered manually

**Required GitHub Secrets** (repo Settings → Secrets → Actions):

| Secret | What it's for |
|--------|--------------|
| `GUESTY_CLIENT_ID` | Guesty API authentication |
| `GUESTY_CLIENT_SECRET` | Guesty API authentication |
| `NTFY_TOPIC` | ntfy.sh push notification topic name |

**If the sync starts failing:**
1. Check the GitHub Actions log (repo → Actions tab → click the failed run)
2. Common causes: Guesty API credentials expired, Guesty API changed, network timeout
3. You'll get a push notification via ntfy when it fails

---

## Key Business Info

| Field | Value |
|-------|-------|
| Property address | 1385 Whiskey Creek Beach Rd, Port Angeles, WA 98363 |
| Phone | (844) 769-2322 |
| Email | whiskeycreekbeachnw@gmail.com |
| Booking platform | reservenow.com |
| Live site | www.whiskeycreekbeachnw.com |

---

## Things That Are Intentionally Left Undone

- **`policies.html`** still has an inline nav (not using the shared partial). It works fine;
  it just means nav changes need to be made there separately too. Migrate it when convenient.
- **Newsletter section** — visible on all pages as a decorative visual band only.
  No email form is wired up. If you want to add a newsletter, wire `.newsletter-left`
  and `.newsletter-right` to Mailchimp or similar.

---

## If Something Breaks

| Symptom | Likely cause | Where to look |
|---------|-------------|---------------|
| Site is down | Render outage or deploy failure | render.com dashboard |
| Version didn't update after push | Deploy failed or still running | Render deploy logs |
| Properties missing from accommodations page | Sync failed or `property-map.txt` out of sync | GitHub Actions log, check `listings.json` |
| Contact form not delivering | Formspree issue | formspree.io dashboard |
| No sync notifications | `NTFY_TOPIC` secret wrong, or ntfy topic changed | GitHub Secrets, ntfy app subscription |
| Nav/footer not showing | `nav-loader.js` or `footer-loader.js` failed to fetch partial | Browser console errors |

---

*Document created: 2026-03-27 — update as the stack changes.*
