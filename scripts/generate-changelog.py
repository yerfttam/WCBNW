#!/usr/bin/env python3
"""
generate-changelog.py

Parses git log and writes NEW/data/changelog.json.
Run locally or via GitHub Actions on every push to main.
"""

import subprocess
import json
import re
from datetime import datetime, timezone
from collections import OrderedDict

# ── Commit patterns ───────────────────────────────────────────────────────────

# New style:  v2.0.9 fix: some description
RE_NEW = re.compile(r'^(v\d+\.\d+\.\d+)\s+(feat|fix|chore|docs|style|refactor|test):\s+(.+)$')

# Old style:  Some description (v1.0.7)
RE_OLD = re.compile(r'^(.+?)\s+\((v\d+\.\d+\.\d+)\)\s*$')

# Skip these — no useful user-facing info
SKIP_PATTERNS = [
    '[skip ci]',
    'sync Guesty',
    'bump version',
    'Update CLAUDE.md version',
    'chore: remove workflow',
]

# ── Parse git log ─────────────────────────────────────────────────────────────

result = subprocess.run(
    ['git', 'log', '--pretty=format:%s|%aI', '--no-merges'],
    capture_output=True, text=True
)

# releases: OrderedDict keyed by version string, preserving insertion order
# We iterate newest-first so the first time we see a version = its latest date
releases = OrderedDict()

for line in result.stdout.strip().split('\n'):
    if '|' not in line:
        continue

    subject, _, iso_date = line.partition('|')
    subject = subject.strip()
    iso_date = iso_date.strip()

    # Skip noise
    if any(pat in subject for pat in SKIP_PATTERNS):
        continue

    # Parse date
    try:
        dt = datetime.fromisoformat(iso_date)
        dt_utc = dt.astimezone(timezone.utc)
        date_str     = dt_utc.strftime('%Y-%m-%d')
        datetime_str = dt_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        display_date = dt_utc.strftime('%B %-d, %Y')        # e.g. March 22, 2026
        display_time = dt_utc.strftime('%-I:%M %p UTC')     # e.g. 6:20 AM UTC
    except Exception:
        date_str = datetime_str = display_date = display_time = ''

    # Try new-style commit message
    m = RE_NEW.match(subject)
    if m:
        version     = m.group(1)
        entry_type  = m.group(2)
        description = m.group(3)
    else:
        # Try old-style commit message
        m2 = RE_OLD.match(subject)
        if m2:
            description = m2.group(1).strip()
            version     = m2.group(2)
            entry_type  = 'fix'   # best guess for old commits
        else:
            # No version found — skip
            continue

    # Skip chore-only noise entries even if they parsed
    if entry_type == 'chore' and version not in releases:
        # Only include chore entries for versions that already have real content
        # (avoids lone "chore: bump version" creating an empty release)
        pass

    if version not in releases:
        releases[version] = {
            'version':      version,
            'date':         date_str,
            'datetime':     datetime_str,
            'display_date': display_date,
            'display_time': display_time,
            'entries':      [],
        }

    releases[version]['entries'].append({
        'type':        entry_type,
        'description': description,
    })

# ── Sort by version descending ────────────────────────────────────────────────

def version_key(v):
    return tuple(int(x) for x in v.lstrip('v').split('.'))

sorted_releases = sorted(
    [r for r in releases.values() if r['entries']],
    key=lambda r: version_key(r['version']),
    reverse=True,
)

# ── Write JSON ────────────────────────────────────────────────────────────────

output = {
    'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'releases':  sorted_releases,
}

out_path = 'NEW/data/changelog.json'
with open(out_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f'Wrote {out_path} — {len(sorted_releases)} releases')
