#!/usr/bin/env python3
"""
sync-nspdm.py

Fetches listing data from the NSPDM API and writes NEW/data/listings.json.
Categories come from NEW/property-map.txt (owner-defined).

Usage:
    python3 scripts/sync-nspdm.py

Requires NSPDM_CLIENT_ID and NSPDM_SECRET in .env or environment.
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

REPO_ROOT    = Path(__file__).parent.parent
PROPERTY_MAP = REPO_ROOT / "NEW" / "property-map.txt"
OUTPUT_FILE  = REPO_ROOT / "NEW" / "data" / "listings.json"
ENV_FILE     = REPO_ROOT / ".env"

NSPDM_TOKEN_URL    = "https://tsttjmynhoskerihpdzr.supabase.co/functions/v1/listings/token"
NSPDM_LISTINGS_URL = "https://tsttjmynhoskerihpdzr.supabase.co/functions/v1/listings"
NSPDM_PROPERTY     = "whiskey-creek-beach-nw"

MAX_PHOTOS = 8

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())


def get_token(client_id, client_secret):
    body = urlencode({
        "grant_type":    "client_credentials",
        "client_id":     client_id,
        "client_secret": client_secret,
    }).encode()
    req = Request(NSPDM_TOKEN_URL, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urlopen(req) as resp:
        return json.load(resp)["access_token"]


def fetch_listings(token):
    url = f"{NSPDM_LISTINGS_URL}?property={NSPDM_PROPERTY}"
    req = Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    with urlopen(req) as resp:
        data = json.load(resp)
    results = data.get("results", [])
    print(f"  NSPDM returned {len(results)} listings for {NSPDM_PROPERTY}")
    return {l["id"]: l for l in results if l.get("id")}


def parse_property_map(path):
    listings_by_id = {}
    category_order = []
    current_category = None

    for line in path.read_text().splitlines():
        line = line.strip()

        cat_match = re.match(r"^#\s+([A-Z][A-Z\s\-]+?)\s*\(\d+\)", line)
        if cat_match:
            raw = cat_match.group(1).strip()
            KEEP_UPPER = {"RV"}
            current_category = " ".join(
                w if w in KEEP_UPPER else w.capitalize()
                for w in raw.replace("-", " ").split()
            )
            current_category = current_category.replace("A Frames", "A-Frames")
            if current_category not in category_order:
                category_order.append(current_category)
            continue

        if not line or line.startswith("#"):
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 2:
            name, pid = parts[0], parts[1]
            if pid and current_category:
                listings_by_id[pid] = {
                    "name":     name,
                    "category": current_category,
                }

    return listings_by_id, category_order


def build_listing(name, api_data):
    photos = [
        {"original": p["original"], "thumbnail": p.get("thumbnail", p["original"])}
        for p in (api_data.get("photos") or [])
        if p.get("original")
    ][:MAX_PHOTOS]

    return {
        "id":           api_data["id"],
        "name":         name,
        "title":        api_data.get("title", ""),
        "summary":      api_data.get("summary", ""),
        "description":  api_data.get("description", ""),
        "price": {
            "base":     api_data.get("basePrice"),
            "cleaning": api_data.get("cleaningFee"),
            "currency": "USD",
        },
        "accommodates": api_data.get("accommodates"),
        "bedrooms":     api_data.get("bedrooms"),
        "bathrooms":    api_data.get("bathrooms"),
        "amenities":    api_data.get("amenities") or [],
        "photos":       photos,
        "bookingUrl":   api_data.get("bookingUrl", ""),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("── NSPDM Sync ───────────────────────────────")

    load_env()
    client_id     = os.environ.get("NSPDM_CLIENT_ID")
    client_secret = os.environ.get("NSPDM_SECRET")
    if not client_id or not client_secret:
        print("ERROR: NSPDM_CLIENT_ID and NSPDM_SECRET must be set")
        sys.exit(1)

    print("  Authenticating with NSPDM...")
    token = get_token(client_id, client_secret)
    print("  ✓ Token obtained")

    print(f"  Parsing {PROPERTY_MAP.name}...")
    listings_by_id, category_order = parse_property_map(PROPERTY_MAP)
    print(f"  ✓ {len(listings_by_id)} properties across {len(category_order)} categories")

    print("  Fetching listings from NSPDM API...")
    api_listings = fetch_listings(token)

    categories = []
    total = 0
    missing = []

    for cat_name in category_order:
        cat_listings = []
        for pid, map_entry in listings_by_id.items():
            if map_entry["category"] != cat_name:
                continue
            api_data = api_listings.get(pid)
            if not api_data:
                missing.append(f"{map_entry['name']} ({pid})")
                continue
            cat_listings.append(build_listing(map_entry["name"], api_data))
            total += 1

        slug = cat_name.lower().replace(" ", "-")
        categories.append({"name": cat_name, "slug": slug, "listings": cat_listings})

    if missing:
        print(f"  ⚠ {len(missing)} properties in map not found in NSPDM API:")
        for m in missing:
            print(f"    - {m}")

    output = {
        "generated":  datetime.now(timezone.utc).isoformat(),
        "account":    NSPDM_PROPERTY,
        "total":      total,
        "categories": categories,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False))

    print(f"  ✓ Wrote {total} listings to {OUTPUT_FILE.relative_to(REPO_ROOT)}")
    print("─────────────────────────────────────────────")


if __name__ == "__main__":
    main()
