# November 30 — NSPDM Cutover Checklist

## Before you start
- Confirm with TOM that the NSPDM booking pages are live and taking reservations
- Confirm the `staging` branch looks correct at https://wcbnw-stage.onrender.com

## Steps

### 1. Merge staging → main (pushes to production)
```
git checkout main
git merge staging
git push
git checkout staging
```

### 2. Update the GitHub Actions workflow
In `.github/workflows/sync-guesty.yml`, change the sync script line from:
```
run: python3 scripts/sync-guesty.py
```
to:
```
run: python3 scripts/sync-nspdm.py
```
Also update the env vars block — replace:
```
GUESTY_CLIENT_ID: ${{ secrets.GUESTY_CLIENT_ID }}
GUESTY_CLIENT_SECRET: ${{ secrets.GUESTY_CLIENT_SECRET }}
```
with:
```
NSPDM_CLIENT_ID: ${{ secrets.NSPDM_CLIENT_ID }}
NSPDM_SECRET: ${{ secrets.NSPDM_SECRET }}
```

### 3. Add GitHub secrets
In the repo settings (Settings → Secrets → Actions), add:
- `NSPDM_CLIENT_ID` = `nspdm_125ddce54453382a64`
- `NSPDM_SECRET` = (the secret Tim sent)

### 4. Trigger a manual sync
In GitHub Actions, run the sync workflow manually to confirm it pulls from NSPDM and updates listings.json cleanly.

### 5. Verify production
- Check https://wcbnw.onrender.com — listings loading correctly
- Click a "Book Now" button — should go to `app.nspdm.com/book/whiskey-creek-beach-nw`
- Check the footer version number to confirm the deploy completed

## Notes
- The new sync script is `scripts/sync-nspdm.py` (already on staging/main after merge)
- The old `scripts/sync-guesty.py` can be deleted after cutover is confirmed stable
- TOM mentioned thumbnails are portrait crops — flag to him if you want landscape thumbnails for faster card loading
- `bookingOpen: false` was set in the feed until Nov 30 — confirm with TOM that it flips to `true` today
