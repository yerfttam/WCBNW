# "If I Get Hit by a Beer Truck"
## Technical Handoff — Whiskey Creek Beach NW (WCBNW)

> This document is for the person who inherits technical ownership of this website.
> It covers everything you need to understand, maintain, and update the site.

---

## What Is This?

A marketing and booking website for a beach vacation rental property in Port Angeles, WA.
The live site is at **[www.whiskeycreekbeachnw.com](https://www.whiskeycreekbeachnw.com)**.

**The site is intentionally simple** — pure HTML, CSS, and JavaScript. No build tools, no
frameworks, no Node.js, no database. If you can describe what you want, Claude Code can
update it.

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

## Credentials — 1Password

All usernames, passwords, and secret keys for this project are stored in the
**WCBNW shared vault in 1Password**. If you've been given access to the project,
you should have been invited to this vault. If you don't have access, contact
one of the other vault members.

The following accounts are stored there:

---

### GitHub
- **URL:** github.com
- **What it's for:** Stores all the website code. You need this to be added as a
  collaborator and to access the repository settings (including GitHub Secrets).
- **1Password entry:** `GitHub — WCBNW`

---

### Claude Code (Anthropic)
- **URL:** claude.ai
- **What it's for:** Signing in to the Claude Code desktop app to make website changes.
- **Note:** Set up your own account at claude.ai — this is not a shared login.
  A paid plan (Claude Pro) is recommended for regular use.

---

### Render
- **URL:** render.com
- **What it's for:** The hosting platform. Log in here to see deploy history and
  troubleshoot if the site goes down.
- **1Password entry:** `Render — WCBNW`

---

### Guesty
- **URL:** app.guesty.com
- **What it's for:** Property management system — the source of truth for listings,
  pricing, and availability. Changes made here flow to the website via the daily sync.
- **1Password entry:** `Guesty — Whiskey Creek Beach NW`

---

### Guesty API Credentials
- **What it's for:** The daily sync job uses these to authenticate with Guesty's API.
  They are also stored as GitHub Secrets (`GUESTY_CLIENT_ID` and `GUESTY_CLIENT_SECRET`).
  If those secrets ever need to be rotated, get the values from here.
- **1Password entry:** `Guesty API — Client ID & Secret` (stored as a secure note)

---

### Formspree
- **URL:** formspree.io
- **What it's for:** Handles the contact form on the website. Submissions get emailed
  to the Whiskey Creek Beach NW Gmail account.
- **1Password entry:** `Formspree — WCBNW`

---

### ntfy Topic
- **What it's for:** The private topic name used for push notifications when the
  Guesty sync runs. Also stored as a GitHub Secret (`NTFY_TOPIC`). Treat it like a
  password — don't share it publicly.
- **1Password entry:** `ntfy — WCBNW sync topic` (stored as a secure note)

---

## Getting Set Up

### Step 1 — Get added as a GitHub collaborator

GitHub is where all the website code lives. You need access before you can make changes.

1. Create a free account at github.com if you don't have one
2. Log in using the **`GitHub — WCBNW`** credentials from the 1Password vault
3. Go to the WCBNW repo → Settings → Collaborators → Add people
4. Add your new GitHub username

---

### Step 2 — Install Claude Code

Download the Claude Code desktop app: https://claude.ai/download

Set up your own account at claude.ai — a paid plan (Claude Pro) is recommended.

---

### Step 3 — Get the code onto your computer

The website's files live on GitHub at **https://github.com/yerfttam/WCBNW**.
You need a local copy on your computer to work with them. Claude Code handles this for you.

1. Open Claude Code
2. When it asks you to open a project, create a new folder on your computer
   (e.g. a folder called `WCBNW` in your Documents)
3. Open that folder in Claude Code, then type:

> *"Clone the GitHub repository at https://github.com/yerfttam/WCBNW into this folder"*

Claude Code will download everything automatically.

---

### Step 4 — You're in

Once the files are downloaded, Claude Code reads `CLAUDE.md` automatically — a file
that tells it everything about the project. You don't need to do anything special to
load it.

---

## Making Changes

All changes are made by having a conversation with Claude Code. You don't edit files
manually — just describe what you want and Claude handles the rest, including
versioning, committing, and publishing to the live site.

### Simple changes

> *"Fix the typo on the about page — 'accomodations' should be 'accommodations'"*

> *"Update the check-in time to 4pm on the policies page"*

> *"Change the phone number on the contact page to (555) 123-4567"*

Claude will find the right file, make the change, and publish it. The site is
usually live within 2 minutes.

### Adding a new image

Drop the image file into the `NEW/images/` or `NEW/photos/` folder on your computer,
then tell Claude:

> *"I've added a new photo called sunset.jpg to photos/outdoor — add it to the about page"*

### Bigger changes

> *"Add a new FAQ page with the same look and feel as the other pages"*

> *"The Jasper Inn is no longer available — remove it from the accommodations page"*

For anything significant, ask Claude to explain what it's going to do before it does
it, so you can review the plan first.

### How do I know it went live?

Every page footer shows a version number (e.g. `v2.1.0`). Claude bumps this
automatically with every change. Reload the live site and confirm the number updated —
if it did, the change is live.

**Clicking the version number** opens the changelog page, which shows a full history
of every change ever made to the site — what changed, when, and which version it was.
It's a quick way to confirm your latest change was recorded and deployed.

---

## Understanding the System

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

### File Structure

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
    property-map.txt     ← Manually-maintained list of properties + Guesty IDs + booking URLs
  scripts/
    sync-guesty.py       ← Python script that pulls data from Guesty API
  .github/workflows/
    sync-guesty.yml      ← GitHub Actions job that runs sync-guesty.py every day
  render.yaml            ← Render hosting config (one line: publish NEW/)
  CLAUDE.md              ← AI assistant instructions (also useful reference for developers)
  HANDOFF.md             ← This file
```

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
`partials/nav.html`. Each page loads it automatically at runtime.
Same pattern for the footer via `partials/footer.html`.

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

The accommodations page dynamically renders property cards from `NEW/data/listings.json`.
That file is generated every day by the Guesty sync job and committed back to the repo
if anything changed.

**The property catalog is controlled by `NEW/property-map.txt`** — the manually-maintained
list of which properties exist, their categories, Guesty IDs, and booking URLs. If a
property is added or removed from Guesty, update this file accordingly.

### Hosting

**Host:** [Render](https://render.com) — static site, free tier

How it works:
1. A change is pushed to the `main` branch on GitHub
2. Render detects it and automatically redeploys within ~1-2 minutes
3. No build step — Render just serves the `NEW/` directory as static files

**Render dashboard:** render.com — log in to see deploy history and logs.

### Staging environment

There are two Render sites:

| Environment | URL | Branch |
|-------------|-----|--------|
| Production | https://www.whiskeycreekbeachnw.com | `main` |
| Staging | https://wcbnw-staging.onrender.com | `staging` |

**Always make changes on the `staging` branch first.** Once you've verified the change looks correct at the staging URL, merge to `main` to push it live. This protects the live site from broken changes.

**The workflow in plain English:**
1. Tell Claude Code what you want to change — it works on the `staging` branch
2. Wait ~2 minutes for staging to deploy
3. Check https://wcbnw-staging.onrender.com — does it look right?
4. Say "looks good, merge to main" — Claude handles the merge and push
5. Production updates within ~2 minutes

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
- **Client Secret:** Stored as GitHub secret `GUESTY_CLIENT_SECRET` — value in 1Password under `Guesty API — Client ID & Secret`
- **Booking base URL:** `https://whiskeycreekbeachnw.guestybookings.com`

**The sync flow:**
1. GitHub Actions runs `scripts/sync-guesty.py` every day at 9am Pacific
2. The script authenticates with Guesty's OAuth2 API, fetches all listings
3. It combines Guesty data with categories from `property-map.txt`
4. Writes the result to `NEW/data/listings.json`
5. If the file changed, commits and pushes it — which triggers a Render redeploy

**To run manually:** Go to GitHub → Actions → "Sync Guesty Listings" → "Run workflow"

**To add/remove a property:** Edit `NEW/property-map.txt` — follow the existing format
(category header, then `Name | GuestyID | BookingURL` lines)

---

### 3. ntfy.sh (Sync Notifications)
- **URL:** [ntfy.sh](https://ntfy.sh) — free, no account needed
- **What it does:** Sends push notifications to the website developer's phone after each Guesty sync

**Why this matters:**

The Guesty sync is not optional background housekeeping — it's how the website stays
accurate. Property prices change frequently in Guesty, and when they do, the only way
those changes show up on the website is via the daily sync. If the sync job silently
fails and nobody notices, the website can show outdated pricing for days, which creates
guest confusion and potential booking problems.

ntfy was set up specifically so that doesn't happen. Every morning after the sync runs,
the website developer gets a push notification — green checkmark if it worked, high-priority
alert if it didn't. A failure alert means: go to GitHub Actions, find out why it failed,
and fix it before guests see stale data.

- **Success:** ✅ "Listings synced successfully at [time]"
- **Failure:** 🚨 High-priority alert — check GitHub Actions immediately

**Setup on a new phone:**
1. Install the ntfy app (iOS or Android)
2. Get the topic name from 1Password: `ntfy — WCBNW sync topic`
3. Subscribe to that topic in the ntfy app

> **Treat the topic name like a password** — anyone who knows it can send notifications
> to that phone. Don't hardcode it anywhere; keep it in 1Password and GitHub Secrets only.

---

### 4. Formspree (Contact Form)
- **URL:** [formspree.io](https://formspree.io)
- **Account:** `Formspree — WCBNW` in 1Password
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

| Secret | What it's for | Where to get the value |
|--------|--------------|----------------------|
| `GUESTY_CLIENT_ID` | Guesty API authentication | 1Password: `Guesty API — Client ID & Secret` |
| `GUESTY_CLIENT_SECRET` | Guesty API authentication | 1Password: `Guesty API — Client ID & Secret` |
| `NTFY_TOPIC` | ntfy.sh push notification topic name | 1Password: `ntfy — WCBNW sync topic` |

**If the sync starts failing:**
1. You'll get a high-priority push notification via ntfy
2. Go to GitHub → Actions tab → click the failed run to see what went wrong
3. Common causes: Guesty API credentials expired, Guesty API changed, network timeout

---

## Things That Are Intentionally Left Undone

- All pages now use the shared nav partial — including `policies.html`, migrated in v2.2.1.
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
| No sync notifications | `NTFY_TOPIC` secret wrong, or ntfy topic changed | 1Password, GitHub Secrets, ntfy app subscription |
| Nav/footer not showing | Loader script failed to fetch partial | Browser console errors |

When in doubt, open Claude Code and describe what you're seeing — it can read the
codebase and usually diagnose the problem.

---

*Document created: 2026-03-27 — update as the stack changes.*
