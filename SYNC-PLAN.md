# Guesty → Website Sync Plan

This document describes the architecture for keeping a static HTML website
in sync with Guesty property listings. Written for WCBNW; reusable for other sites.

**Status:** In progress

---

## Architecture Overview

```
property-map.txt            ← SOURCE OF TRUTH for categories (owner-defined)
        +
Guesty Open API             ← SOURCE OF TRUTH for descriptions, prices, photos
        │
        ▼
scripts/sync-guesty.py      ← sync script (run on a schedule)
        │
        ▼
NEW/data/listings.json      ← generated file, committed to repo
        │
        ▼
NEW/js/listings-loader.js   ← renders property cards in the browser
        │
        ▼
accommodations.html         ← loads loader.js, cards rendered dynamically
```

### Why this approach (static site, no backend)
- No server or API costs
- Guesty credentials stay in GitHub Secrets (never in browser)
- Render auto-deploys when listings.json changes
- Works for any static hosting provider

---

## Key Design Decision: Categories

Guesty's `propertyType` field (Cabin, Hut, Tent, etc.) does NOT match the
categories the owner uses on the website. The owner's categories are:

- Beach Front Cabins
- Cottages
- A-Frames
- Tent Sites
- RV Sites
- Other Properties

These are defined in `NEW/property-map.txt`, which maps each property to its
category by Guesty ID. The sync script reads this file to assign categories —
**do not try to derive categories from Guesty's propertyType**.

When a new property is added to Guesty:
1. Add it to `property-map.txt` in the correct category
2. The next sync will pick it up automatically

---

## Files

| File | Purpose |
|------|---------|
| `NEW/property-map.txt` | Owner-defined categories + Guesty IDs |
| `scripts/sync-guesty.py` | Fetches Guesty data, writes listings.json |
| `NEW/data/listings.json` | Generated. All listing data for the frontend |
| `NEW/js/listings-loader.js` | Renders property cards from listings.json |
| `.env` | Local credentials (gitignored) |
| `.github/workflows/sync-guesty.yml` | Scheduled GitHub Action |

---

## Data Pulled from Guesty Per Listing

| Field | Guesty source |
|-------|--------------|
| Title | `title` |
| Short description | `publicDescription.summary` |
| Long description | `publicDescription.space` |
| Base price (nightly) | `prices.basePrice` |
| Cleaning fee | `prices.cleaningFee` |
| Currency | `prices.currency` |
| Guests | `accommodates` |
| Bedrooms | `bedrooms` |
| Bathrooms | `bathrooms` |
| Photos | `pictures[].original` + `pictures[].thumbnail` |
| Amenities | `amenities[]` |
| Booking URL | `https://[account].guestybookings.com/en/properties/[_id]` |

---

## listings.json Structure

```json
{
  "generated": "2026-03-21T00:00:00Z",
  "account": "whiskeycreekbeachnw",
  "categories": [
    {
      "name": "Beach Front Cabins",
      "slug": "beach-front-cabins",
      "listings": [
        {
          "id": "678ff9a9af15e70011ba3785",
          "title": "Codfish Cottage Cabin on the Strait of Juan de Fuca",
          "summary": "Quaint and Rustic Beachfront Cabin",
          "description": "Full description text...",
          "price": { "base": 261, "cleaning": 25, "currency": "USD" },
          "accommodates": 4,
          "bedrooms": 1,
          "bathrooms": 1,
          "amenities": ["Waterfront", "Pets allowed", ...],
          "photos": [
            { "original": "https://...", "thumbnail": "https://..." }
          ],
          "bookingUrl": "https://whiskeycreekbeachnw.guestybookings.com/en/properties/678ff9a9af15e70011ba3785"
        }
      ]
    }
  ]
}
```

---

## Sync Script (`scripts/sync-guesty.py`)

Steps:
1. Load `.env` for credentials (or read from environment variables)
2. Authenticate with Guesty → get Bearer token
3. Parse `NEW/property-map.txt` → build `{id: category}` lookup
4. Fetch all listings from `/v1/listings?limit=100`
5. Filter to `active=true` + `isListed=true`, skip `z-`/`zt-` internal names
6. For each listing in the property map, enrich with Guesty data
7. Group by category, write `NEW/data/listings.json`

Run locally:
```bash
python3 scripts/sync-guesty.py
```

---

## GitHub Actions Workflow

File: `.github/workflows/sync-guesty.yml`

- Runs on a schedule (e.g. nightly at 3am UTC)
- Also triggerable manually
- Reads `GUESTY_CLIENT_ID` and `GUESTY_CLIENT_SECRET` from GitHub Secrets
- If listings.json changed, commits and pushes → triggers Render redeploy

GitHub Secrets to add:
- `GUESTY_CLIENT_ID`
- `GUESTY_CLIENT_SECRET`

---

## Frontend Renderer (`NEW/js/listings-loader.js`)

- Fetches `data/listings.json` at page load
- Renders category tabs + property cards
- Each card: photo carousel (or single hero), title, summary, price, guest/bed/bath counts, Book Now button
- Pure vanilla JS, no framework

---

## Reusing for Another Site

To set this up for a new Guesty account:
1. Copy `scripts/sync-guesty.py` and `.github/workflows/sync-guesty.yml`
2. Create a new `property-map.txt` for the new account (see `GUESTY-API-HOWTO.md`)
3. Set the `GUESTY_BOOKING_HOST` variable in the sync script to the new account's booking subdomain
4. Add new `GUESTY_CLIENT_ID` / `GUESTY_CLIENT_SECRET` to GitHub Secrets
5. Run `sync-guesty.py` once locally to verify

---

## TODO

- [x] Create property-map.txt with all 32 properties and categories
- [x] Verify Guesty API credentials work
- [x] Confirm API returns descriptions, prices, photos
- [x] Write sync script (scripts/sync-guesty.py)
- [x] Test sync script locally → 32/32 listings, correct categories
- [x] Set up GitHub Actions workflow (.github/workflows/sync-guesty.yml)
- [x] Write listings-loader.js frontend renderer
- [x] Update accommodations.html to use loader (hardcoded cards removed)
- [ ] Add GUESTY_CLIENT_ID / SECRET to GitHub Secrets
- [x] Commit listings.json + all new files → push to trigger Render deploy
- [x] Write other-properties-loader.js → other-properties.html now pulls from Guesty
- [ ] Verify live on Render
- [ ] Test end-to-end: GitHub Action runs sync → Render redeploys
