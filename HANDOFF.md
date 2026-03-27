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

### GitHub — What It Is and Why It Matters

**GitHub** is a website that stores the website's code in the cloud, similar to how
Dropbox or Google Drive stores documents. Every file that makes up
www.whiskeycreekbeachnw.com lives here.

GitHub does two important things beyond just storing files:
1. **Version history** — every change ever made is recorded, who made it, and when.
   If something breaks, you can see exactly what changed and undo it.
2. **Triggers deploys** — when a change is pushed to GitHub, the hosting service
   (Render) automatically detects it and publishes the updated site within ~2 minutes.

**GitHub repository:** https://github.com/yerfttam/WCBNW

> You'll need to be added as a collaborator to make changes. The previous website
> developer can do this from GitHub → the WCBNW repo → Settings → Collaborators → Add people.

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
manually-maintained list of which properties exist, what category they belong to,
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
- **Client Secret:** Stored as GitHub secret `GUESTY_CLIENT_SECRET` (ask the previous website developer)
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
- **What it does:** Sends push notifications to the owner's phone after each Guesty sync

**Why this matters:**

The Guesty sync is not optional background housekeeping — it's how the website stays
accurate. Property prices change frequently in Guesty, and when they do, the only way
those changes show up on the website is via the daily sync. If the sync job silently
fails and nobody notices, the website can show outdated pricing for days, which creates
guest confusion and potential booking problems.

ntfy was set up specifically so that doesn't happen. Every morning after the sync runs,
the website developer gets a push notification — green checkmark if it worked, high-priority alert
if it didn't. A failure alert means: go to GitHub Actions, find out why it failed, and
fix it before guests see stale data.

- **Success:** ✅ "Listings synced successfully at [time]"
- **Failure:** 🚨 High-priority alert — check GitHub Actions immediately

**Setup (if you need to receive these on a new phone):**
1. Install the ntfy app (iOS or Android)
2. Subscribe to the topic name stored in the GitHub secret `NTFY_TOPIC`
3. Get the topic name from the previous website developer, or find it in GitHub → the WCBNW repo → Settings → Secrets → `NTFY_TOPIC`

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

## Making Changes with Claude Code

This project is maintained using **Claude Code** — an AI assistant that understands
the entire codebase. You describe what you want in plain English, it reads the files,
makes the changes, and publishes the update. No coding experience required.

---

### Step 1 — Install Claude Code

Download the Claude Code desktop app: https://claude.ai/download

Sign in with the Anthropic account credentials from the previous website developer.

---

### Step 2 — Get the code onto your computer

The website's files live on GitHub. You need a copy of them on your computer
before you can work on anything. Claude Code can do this for you — no technical
knowledge needed.

1. Open Claude Code
2. When it asks you to open a project, choose a folder on your computer where you
   want to store the website files (e.g. create a folder called `WCBNW` in your
   Documents folder)
3. Once it's open, type this:

> *"Clone the GitHub repository at https://github.com/yerfttam/WCBNW into this folder"*

Claude Code will download all the files automatically.

> **Note:** You'll need to be added as a GitHub collaborator first, otherwise the
> clone will fail. The previous website developer can add you at:
> GitHub → the WCBNW repo → Settings → Collaborators → Add people.
> You'll need a free GitHub account at github.com.

---

### Step 3 — You're in

Claude Code will read `CLAUDE.md` automatically — this is the file that tells it
everything about the project. You don't need to do anything special to load it.

---

### Step 4 — Make a change (it's just a conversation)

Just type what you want. Some examples:

> *"Update the phone number on the contact page to (555) 123-4567"*

> *"The check-in time changed to 4pm — update the policies page"*

> *"Add a sentence to the About page mentioning that we have kayak rentals available"*

Claude Code will find the right files, make the changes, and show you what it's about
to do before it does it. Review it, approve it, and it will publish the update to the
live site automatically (usually live within 2 minutes).

---

### CLAUDE.md — The Instruction Manual

**Before asking Claude Code to do anything major, tell it to re-read `CLAUDE.md`.**
This file lives in the root of the project and contains everything Claude needs to
know: how the site is structured, all the third-party services, the rules for updating
the version number, and known quirks. It's also a useful reference document for any
human reading it.

---

### How do I know if my change went live?

Every page on the site shows a version number in the footer (e.g. `v2.1.0`). When
Claude Code publishes a change, it bumps that number. Reload the live site
(www.whiskeycreekbeachnw.com) and check the footer — if the number changed, the
update is live.

---

### What if something goes wrong?

- **Check the Render dashboard** (render.com) — it shows whether the latest deploy
  succeeded or failed, with logs if something broke
- **Ask Claude Code** — describe what you're seeing and ask it to diagnose the problem.
  It can read the codebase and usually figure out what went wrong.
- **GitHub Secrets** — some integrations (Guesty, ntfy) use encrypted credentials
  stored in GitHub. Claude Code knows these exist but cannot read them. To update them,
  go to: GitHub → the WCBNW repository → Settings → Secrets and variables → Actions.
  Ask the previous website developer for the actual secret values.

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
