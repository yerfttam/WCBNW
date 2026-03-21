# How to Map Guesty Properties to Booking URLs

This documents how to pull a complete property list from Guesty's Open API —
useful when you need to map all properties to their booking URLs for a website.

---

## 1. Get API Credentials from Guesty

1. Log in to [app.guesty.com](https://app.guesty.com)
2. Navigate to **Integrations → OAuth Applications**
3. Click **New Application**
4. Give it a name (e.g. "Website Integration")
5. Click **Generate new secrets**
6. Enter your Guesty password to confirm
7. **Copy the Client ID and Client Secret immediately** — the secret is only shown once

Store them in a `.env` file at the root of your project:

```
GUESTY_CLIENT_ID=your_client_id_here
GUESTY_CLIENT_SECRET=your_client_secret_here
```

Make sure `.env` is in your `.gitignore`.

---

## 2. Get an Access Token

Tokens are valid for 24 hours. Run this curl command:

```bash
curl -s -X POST "https://open-api.guesty.com/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&scope=open-api&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET"
```

Response will include an `access_token`. Copy it for the next step.

**Rate limit:** Max 5 token requests per Client ID per 24 hours — cache the token.

---

## 3. Fetch All Listings

```bash
curl -s "https://open-api.guesty.com/v1/listings?limit=100" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

To pretty-print and extract the useful fields:

```bash
curl -s "https://open-api.guesty.com/v1/listings?limit=100" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
listings = data.get('results', [])
print(f'Total: {len(listings)}')
for l in sorted(listings, key=lambda x: (x.get('propertyType',''), x.get('nickname',''))):
    print(f\"{l.get('propertyType','?'):12} | listed={l.get('isListed')} active={l.get('active')} | {l['_id']} | {l.get('nickname') or l.get('title','?')}\")
"
```

### Key fields returned per listing

| Field | Description |
|-------|-------------|
| `_id` | 24-character Guesty property ID |
| `nickname` | Short internal name (e.g. "Cabin 01 - CC") |
| `title` | Long public SEO title |
| `propertyType` | Cabin, Hut, Tent, Camper/RV, House, Apartment, etc. |
| `isListed` | Whether it appears on booking channels |
| `active` | Whether the listing is active |

---

## 4. Build the Booking URL

The Guesty booking page URL for any property is:

```
https://YOUR-ACCOUNT.guestybookings.com/en/properties/PROPERTY_ID
```

For WCBNW that's `whiskeycreekbeachnw.guestybookings.com`.
The account subdomain is visible in the browser when you visit the Guesty-hosted booking page.

---

## 5. Notes & Gotchas

- **Internal listings**: Guesty accounts often have internal/management listings
  prefixed with `z-` or `zt-` (e.g. room-level records for multi-unit complexes).
  Filter these out — they won't appear on the public booking page.
- **`isListed=true` + `active=true`** are the two flags that determine if a property
  shows on the public booking widget.
- **Property types don't always match what you'd expect** — A-frames are `Hut`,
  tour buses are `Camper/RV`, off-site houses are `House`.
- **The `fields` query param** (e.g. `?fields=_id,nickname`) appears to silently
  break the response — omit it and filter fields in your script instead.
- **62 vs 32**: The WCBNW account has 62 total listings but only 32 are public.
  The rest are internal room/rate records for channel management.
- **Token expiry**: Tokens last 24 hours. If you get a 401, just re-authenticate.

---

## 6. API Reference

- Auth: `https://open-api.guesty.com/oauth2/token`
- Listings: `https://open-api.guesty.com/v1/listings`
- Full docs: https://open-api-docs.guesty.com/
- Rate limits: 15 req/sec, 120 req/min, 5000 req/hr
