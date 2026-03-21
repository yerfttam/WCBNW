#!/usr/bin/env python3
"""
sync-guesty.py

Fetches listing data from the Guesty Open API and writes NEW/data/listings.json.
Categories come from NEW/property-map.txt (owner-defined, not Guesty's propertyType).

Usage:
    python3 scripts/sync-guesty.py

Requires GUESTY_CLIENT_ID and GUESTY_CLIENT_SECRET in .env or environment.

See SYNC-PLAN.md for full documentation.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import HTTPError

# ── Config ────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
PROPERTY_MAP = REPO_ROOT / "NEW" / "property-map.txt"
OUTPUT_FILE  = REPO_ROOT / "NEW" / "data" / "listings.json"
ENV_FILE     = REPO_ROOT / ".env"

GUESTY_TOKEN_URL   = "https://open-api.guesty.com/oauth2/token"
GUESTY_LISTINGS_URL = "https://open-api.guesty.com/v1/listings"
GUESTY_BOOKING_HOST = "whiskeycreekbeachnw.guestybookings.com"

MAX_PHOTOS = 8  # max photos to store per listing

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_env():
    """Load .env file into os.environ if it exists."""
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())


def get_token(client_id, client_secret):
    """Obtain a Guesty OAuth2 Bearer token."""
    body = urlencode({
        "grant_type": "client_credentials",
        "scope": "open-api",
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()
    req = Request(GUESTY_TOKEN_URL, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urlopen(req) as resp:
        return json.load(resp)["access_token"]


def guesty_get(path, token, params=None):
    """Make an authenticated GET request to the Guesty API."""
    url = path
    if params:
        url += "?" + urlencode(params)
    req = Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    with urlopen(req) as resp:
        return json.load(resp)


def parse_property_map(path):
    """
    Parse property-map.txt into a dict:
        { guesty_id: { "name": str, "category": str, "booking_url": str } }

    Also returns ordered list of category names.
    """
    listings_by_id = {}
    category_order = []
    current_category = None

    for line in path.read_text().splitlines():
        line = line.strip()

        # Category header: # BEACH FRONT CABINS (5) or # A-FRAMES (9)  [...]
        cat_match = re.match(r"^#\s+([A-Z][A-Z\s\-]+?)\s*\(\d+\)", line)
        if cat_match:
            raw = cat_match.group(1).strip()
            # Title-case words, but keep known acronyms uppercase
            KEEP_UPPER = {"RV"}
            current_category = " ".join(
                w if w in KEEP_UPPER else w.capitalize()
                for w in raw.replace("-", " ").split()
            )
            # Restore hyphens for A-Frames
            current_category = current_category.replace("A Frames", "A-Frames")
            if current_category not in category_order:
                category_order.append(current_category)
            continue

        # Skip comments and blank lines
        if not line or line.startswith("#"):
            continue

        # Data line: Name | ID | URL
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 3:
            name, gid, url = parts[0], parts[1], parts[2]
            if len(gid) == 24 and current_category:
                listings_by_id[gid] = {
                    "name": name,
                    "category": current_category,
                    "booking_url": url,
                }

    return listings_by_id, category_order


def fetch_all_listings(token):
    """Fetch all listings from Guesty, return as dict keyed by _id."""
    data = guesty_get(GUESTY_LISTINGS_URL, token, {"limit": 100})
    results = data.get("results", [])
    print(f"  Guesty returned {len(results)} total listings")

    by_id = {}
    for l in results:
        gid = l.get("_id")
        if gid:
            by_id[gid] = l
    return by_id


def build_listing(map_entry, guesty_data):
    """Combine property-map entry with Guesty API data into a clean dict."""
    gid = guesty_data["_id"]
    pd  = guesty_data.get("publicDescription") or {}
    prices = guesty_data.get("prices") or {}

    photos = [
        {"original": p["original"], "thumbnail": p.get("thumbnail", p["original"])}
        for p in (guesty_data.get("pictures") or [])
        if p.get("original")
    ][:MAX_PHOTOS]

    return {
        "id":          gid,
        "name":        map_entry["name"],
        "title":       guesty_data.get("title", ""),
        "summary":     pd.get("summary", ""),
        "description": pd.get("space", ""),
        "price": {
            "base":     prices.get("basePrice"),
            "cleaning": prices.get("cleaningFee"),
            "currency": prices.get("currency", "USD"),
        },
        "accommodates": guesty_data.get("accommodates"),
        "bedrooms":     guesty_data.get("bedrooms"),
        "bathrooms":    guesty_data.get("bathrooms"),
        "amenities":    guesty_data.get("amenities") or [],
        "photos":       photos,
        "bookingUrl":   map_entry["booking_url"],
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("── Guesty Sync ──────────────────────────────")

    # 1. Load credentials
    load_env()
    client_id     = os.environ.get("GUESTY_CLIENT_ID")
    client_secret = os.environ.get("GUESTY_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("ERROR: GUESTY_CLIENT_ID and GUESTY_CLIENT_SECRET must be set")
        sys.exit(1)

    # 2. Authenticate
    print("  Authenticating with Guesty...")
    token = get_token(client_id, client_secret)
    print("  ✓ Token obtained")

    # 3. Parse property map (categories + IDs)
    print(f"  Parsing {PROPERTY_MAP.name}...")
    listings_by_id, category_order = parse_property_map(PROPERTY_MAP)
    print(f"  ✓ {len(listings_by_id)} properties across {len(category_order)} categories")

    # 4. Fetch all Guesty listings
    print("  Fetching listings from Guesty API...")
    guesty_listings = fetch_all_listings(token)

    # 5. Build output grouped by category
    categories = []
    total = 0
    missing = []

    for cat_name in category_order:
        cat_listings = []
        for gid, map_entry in listings_by_id.items():
            if map_entry["category"] != cat_name:
                continue
            guesty_data = guesty_listings.get(gid)
            if not guesty_data:
                missing.append(f"{map_entry['name']} ({gid})")
                continue
            cat_listings.append(build_listing(map_entry, guesty_data))
            total += 1

        slug = cat_name.lower().replace(" ", "-")
        categories.append({"name": cat_name, "slug": slug, "listings": cat_listings})

    if missing:
        print(f"  ⚠ {len(missing)} properties in map not found in Guesty API:")
        for m in missing:
            print(f"    - {m}")

    # 6. Write output
    output = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "account":   GUESTY_BOOKING_HOST.split(".")[0],
        "total":     total,
        "categories": categories,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False))

    print(f"  ✓ Wrote {total} listings to {OUTPUT_FILE.relative_to(REPO_ROOT)}")
    print("─────────────────────────────────────────────")


if __name__ == "__main__":
    main()
