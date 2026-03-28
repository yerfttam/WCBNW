import os
import re
import json
import base64
import traceback
import requests
from datetime import datetime, timezone, date as date_type
from flask import Flask, request, jsonify
import anthropic

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    return response

# Environment variables (set these in Render dashboard)
ADMIN_PASSWORD      = os.environ.get('ADMIN_PASSWORD', 'changeme')
ANTHROPIC_API_KEY   = os.environ.get('ANTHROPIC_API_KEY')
GITHUB_TOKEN        = os.environ.get('GITHUB_TOKEN')
REPO                = 'yerfttam/WCBNW'
STAGING_BRANCH      = 'staging'
GUESTY_CLIENT_ID    = os.environ.get('GUESTY_CLIENT_ID', '0oatpyo652QA9S4Av5d7')
GUESTY_CLIENT_SECRET = os.environ.get('GUESTY_CLIENT_SECRET')
GUESTY_TOKEN_URL    = 'https://open-api.guesty.com/oauth2/token'

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# In-memory conversation history (resets on server restart — that's fine)
conversation: list = []


# ── GitHub helpers ─────────────────────────────────────────────────────────────

def gh_headers():
    return {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github+json'}

def read_file(path: str) -> dict | None:
    url = f'https://api.github.com/repos/{REPO}/contents/{path}'
    r = requests.get(url, headers=gh_headers(), params={'ref': STAGING_BRANCH})
    if r.status_code == 200:
        data = r.json()
        return {
            'content': base64.b64decode(data['content']).decode('utf-8'),
            'sha': data['sha']
        }
    print(f"read_file failed: {path} → {r.status_code} {r.text[:300]}")
    return None

def edit_file(path: str, old_string: str, new_string: str, commit_message: str) -> str:
    """Read file from GitHub, replace old_string with new_string, commit back."""
    current = read_file(path)
    if not current:
        return f"Could not read {path} from GitHub — check that the file path is correct."
    if old_string not in current['content']:
        return (
            f"Could not find that exact text in {path}. "
            "Please read the file first and copy the text you want to change exactly as it appears."
        )
    new_content = current['content'].replace(old_string, new_string, 1)
    url = f'https://api.github.com/repos/{REPO}/contents/{path}'
    payload = {
        'message': commit_message,
        'content': base64.b64encode(new_content.encode('utf-8')).decode('utf-8'),
        'sha': current['sha'],
        'branch': STAGING_BRANCH,
    }
    r = requests.put(url, headers=gh_headers(), json=payload)
    if r.status_code in (200, 201):
        return 'Edit saved successfully.'
    print(f"edit_file write failed: {path} → {r.status_code} {r.text[:300]}")
    return f'GitHub rejected the save ({r.status_code}) — please try again.'

def merge_to_main() -> bool:
    url = f'https://api.github.com/repos/{REPO}/merges'
    payload = {
        'base': 'main',
        'head': STAGING_BRANCH,
        'commit_message': 'chore: deploy to production via admin chat',
    }
    r = requests.post(url, headers=gh_headers(), json=payload)
    # 201 = merged, 204 = already up-to-date
    return r.status_code in (201, 204)


# ── Claude tool definitions ────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "read_file",
        "description": (
            "Read the current content of a file in the website repository. "
            "Always call this before editing so you can find the exact text to change."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to repo root, e.g. 'NEW/policies.html'",
                }
            },
            "required": ["path"],
        },
    },
    {
        "name": "edit_file",
        "description": (
            "Make a targeted text replacement in a file and commit it to the staging branch. "
            "You must read the file first. The old_string must match exactly what is in the file — "
            "copy it character-for-character from the read_file result."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to repo root",
                },
                "old_string": {
                    "type": "string",
                    "description": (
                        "The exact text currently in the file that you want to replace. "
                        "Copy it exactly from the read_file result — include enough surrounding "
                        "context (e.g. a full sentence or line) to be unique in the file."
                    ),
                },
                "new_string": {
                    "type": "string",
                    "description": "The new text to put in its place.",
                },
                "commit_message": {
                    "type": "string",
                    "description": "Short description of the change, e.g. 'update damage deposit to $200'",
                },
            },
            "required": ["path", "old_string", "new_string", "commit_message"],
        },
    },
    {
        "name": "deploy_to_production",
        "description": (
            "Merge the staging branch into main, pushing all staged changes live to the public website. "
            "Only do this when the owner explicitly says she's happy and wants to go live."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "confirm": {
                    "type": "boolean",
                    "description": "Must be true to confirm the deployment.",
                }
            },
            "required": ["confirm"],
        },
    },
]

SYSTEM_PROMPT = """You are a friendly, helpful website assistant for Whiskey Creek Beach NW — a beautiful beach vacation rental property in Port Angeles, WA (www.whiskeycreekbeachnw.com).

You help the property owner make content updates to the website through a simple chat. You can read and edit website files directly and push changes live.

## Site Pages
- NEW/index.html — Home page
- NEW/about.html — About Us
- NEW/accommodations.html — Property listings
- NEW/contact.html — Contact page
- NEW/policies.html — Booking, cancellation & pet policies
- NEW/other-properties.html — Other properties
- NEW/partials/nav.html — Navigation bar (shows on every page)
- NEW/partials/footer.html — Footer with version number (shows on every page)

## How to Make a Change
1. Call read_file on the relevant page to see the current text
2. Call edit_file with the exact old text and your replacement — make only the specific change requested
3. Call read_file on NEW/partials/footer.html, then edit_file to bump the patch version (e.g. v2.2.1 → v2.2.2)
4. Tell the owner what you changed and that it's ready to preview at https://wcbnw-stage.onrender.com
5. Ask if she'd like to push it live — if yes, use deploy_to_production

## Rules
- Only make content edits: text, descriptions, policies, contact info, hours
- Never change HTML structure, CSS styles, JavaScript, or navigation layout
- Always bump the version number in NEW/partials/footer.html after every change
- The version is in a <span class="site-version"> tag — bump the last number only
- Keep your replies short and friendly — she's on her phone
- Speak plainly, no technical jargon
- If you're unsure what she wants, ask a quick clarifying question before making changes
- After deploying to production, remind her the live site updates in about 2 minutes"""


# ── Tool execution ─────────────────────────────────────────────────────────────

def execute_tool(name: str, inputs: dict) -> str:
    # Log tool calls (truncate long values for readability)
    short = {k: (v[:80] + '…' if isinstance(v, str) and len(v) > 80 else v)
             for k, v in inputs.items()}
    print(f"TOOL {name}: {short}")

    if name == 'read_file':
        result = read_file(inputs['path'])
        if result:
            print(f"  → read ok ({len(result['content'])} chars)")
            return result['content']
        return f"Could not read file: {inputs['path']}"

    if name == 'edit_file':
        result = edit_file(
            inputs['path'],
            inputs['old_string'],
            inputs['new_string'],
            inputs['commit_message'],
        )
        print(f"  → {result}")
        return result

    if name == 'deploy_to_production':
        if not inputs.get('confirm'):
            return 'Deployment cancelled.'
        success = merge_to_main()
        result = (
            'Deployed to production! The live site will update in about 2 minutes.'
            if success else
            'Deployment failed — please try again or contact the developer.'
        )
        print(f"  → {result}")
        return result

    return f'Unknown tool: {name}'


# ── Conversation trimming ──────────────────────────────────────────────────────

def trim_conversation(messages: list) -> list:
    """Keep only user text turns and assistant text-only turns.

    Strips tool_use / tool_result blocks (which can contain entire HTML files)
    so the conversation history stays small and doesn't cause OOM.
    """
    trimmed = []
    for msg in messages:
        if msg['role'] == 'user' and isinstance(msg['content'], str):
            trimmed.append(msg)
        elif msg['role'] == 'assistant' and isinstance(msg['content'], list):
            text_blocks = [
                b for b in msg['content']
                if isinstance(b, dict) and b.get('type') == 'text'
            ]
            if text_blocks:
                trimmed.append({'role': 'assistant', 'content': text_blocks})
    return trimmed


# ── Serialization helpers ──────────────────────────────────────────────────────

def serialize_block(block) -> dict:
    """Convert an Anthropic content block to a plain dict."""
    if hasattr(block, 'type'):
        if block.type == 'text':
            return {'type': 'text', 'text': block.text}
        if block.type == 'tool_use':
            return {'type': 'tool_use', 'id': block.id, 'name': block.name, 'input': block.input}
    return block if isinstance(block, dict) else {}

def serialize_content(content) -> list | str:
    if isinstance(content, list):
        return [serialize_block(b) for b in content]
    return content


# ── Chat endpoint ──────────────────────────────────────────────────────────────

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return '', 200

    global conversation
    data = request.json or {}

    if data.get('password') != ADMIN_PASSWORD:
        return jsonify({'error': 'Invalid password'}), 401

    user_message = (data.get('message') or '').strip()
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    conversation.append({'role': 'user', 'content': user_message})
    print(f"USER: {user_message[:120]}")

    try:
        # Agentic loop — keep going until Claude stops using tools
        while True:
            response = client.messages.create(
                model='claude-sonnet-4-5',
                max_tokens=8096,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=conversation,
            )

            block_types = [getattr(b, 'type', '?') for b in response.content]
            print(f"CLAUDE stop={response.stop_reason} blocks={block_types}")

            # Add assistant turn to history
            assistant_content = serialize_content(response.content)
            conversation.append({'role': 'assistant', 'content': assistant_content})

            if response.stop_reason != 'tool_use':
                break

            # Execute tool calls and collect results
            tool_results = []
            for block in response.content:
                if hasattr(block, 'type') and block.type == 'tool_use':
                    result_text = execute_tool(block.name, block.input)
                    tool_results.append({
                        'type': 'tool_result',
                        'tool_use_id': block.id,
                        'content': result_text,
                    })

            if tool_results:
                conversation.append({'role': 'user', 'content': tool_results})

        # Extract final text reply
        reply = ' '.join(
            b.text for b in response.content
            if hasattr(b, 'type') and b.type == 'text'
        ).strip()

        if not reply:
            reply = "Done! Let me know if there's anything else you'd like to change."

        print(f"REPLY ({len(reply)} chars): {reply[:120]}")

        # Trim history to text-only to keep memory low
        conversation[:] = trim_conversation(conversation)

        return jsonify({'response': reply})

    except Exception:
        print(f"EXCEPTION:\n{traceback.format_exc()}")
        return jsonify({'error': 'Something went wrong on my end — please try again.'}), 500


@app.route('/reset', methods=['POST', 'OPTIONS'])
def reset():
    if request.method == 'OPTIONS':
        return '', 200
    global conversation
    data = request.json or {}
    if data.get('password') != ADMIN_PASSWORD:
        return jsonify({'error': 'Invalid password'}), 401
    conversation = []
    return jsonify({'status': 'ok'})


# ── Guesty guest lookup ────────────────────────────────────────────────────────

def get_guesty_token():
    """Fetch a fresh Guesty OAuth2 bearer token."""
    r = requests.post(GUESTY_TOKEN_URL, data={
        'grant_type': 'client_credentials',
        'scope': 'open-api',
        'client_id': GUESTY_CLIENT_ID,
        'client_secret': GUESTY_CLIENT_SECRET,
    })
    if r.status_code == 200:
        return r.json().get('access_token')
    print(f"Guesty token error: {r.status_code} {r.text[:200]}")
    return None


@app.route('/guest-lookup', methods=['POST', 'OPTIONS'])
def guest_lookup():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.json or {}
    last_name   = (data.get('last_name') or '').strip()
    phone_last4 = (data.get('phone_last4') or '').strip()

    if not last_name or not phone_last4:
        return jsonify({'error': 'Please provide your last name and last 4 digits of your phone number.'}), 400
    if len(phone_last4) != 4 or not phone_last4.isdigit():
        return jsonify({'error': 'Phone digits must be exactly 4 numbers.'}), 400

    token = get_guesty_token()
    if not token:
        return jsonify({'error': 'Service temporarily unavailable. Please call (844) 769-2322.'}), 503

    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}

    # Fetch confirmed/active reservations with a future checkout
    now_str = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    params = {
        'filters': json.dumps([
            {'field': 'checkOut', 'operator': '$gt', 'value': now_str},
            {'field': 'status', 'operator': '$in', 'value': ['confirmed', 'checked_in']},
        ]),
        'fields': '_id guest checkIn checkOut listing status',
        'limit': 200,
    }
    r = requests.get('https://open-api.guesty.com/v1/reservations', headers=headers, params=params)
    if r.status_code != 200:
        print(f"Guesty reservations error: {r.status_code} {r.text[:300]}")
        return jsonify({'error': 'Service temporarily unavailable. Please call (844) 769-2322.'}), 503

    reservations = r.json().get('results', [])
    print(f"GUEST LOOKUP: searching {len(reservations)} reservations for '{last_name}' / ***{phone_last4}")

    # Match on last name (case-insensitive) + phone last 4
    match = None
    for res in reservations:
        guest = res.get('guest', {})
        res_last  = (guest.get('lastName') or '').strip().lower()
        res_phone = re.sub(r'\D', '', guest.get('phone') or '')
        if res_last == last_name.lower() and res_phone.endswith(phone_last4):
            match = res
            break

    if not match:
        return jsonify({
            'found': False,
            'message': "We couldn't find a reservation matching that information. Double-check the last name and phone number you used when booking, or call us at (844) 769-2322.",
        })

    res_id       = match['_id']
    listing      = match.get('listing') or {}
    listing_name = listing.get('nickname') or listing.get('title') or 'your property'
    check_in     = match.get('checkIn', '')
    check_out    = match.get('checkOut', '')

    # Fetch lock codes
    codes_r = requests.get(
        f'https://open-api.guesty.com/v1/reservations/{res_id}/locks-and-codes',
        headers=headers,
    )

    if codes_r.status_code != 200:
        # Property has no lock integration (tent sites, A-frames)
        return jsonify({'found': True, 'has_code': False, 'listing': listing_name, 'check_in': check_in})

    locks = codes_r.json()
    if isinstance(locks, dict):
        locks = locks.get('locks', [])

    guest_code  = None
    backup_code = None

    # Only show backup code on/after check-in day
    try:
        check_in_date      = datetime.fromisoformat(check_in.replace('Z', '+00:00')).date()
        is_checkin_or_after = date_type.today() >= check_in_date
    except Exception:
        is_checkin_or_after = False

    for lock in locks:
        for entry in lock.get('accessCodes', []):
            purpose = entry.get('purpose', '')
            code    = entry.get('code') or entry.get('pin')
            if purpose == 'GUEST' and code and not guest_code:
                guest_code = code
            elif purpose == 'GUEST_BACKUP' and code and is_checkin_or_after and not backup_code:
                backup_code = code

    if not guest_code:
        return jsonify({'found': True, 'has_code': False, 'listing': listing_name, 'check_in': check_in})

    print(f"GUEST LOOKUP: code found for '{listing_name}'")
    return jsonify({
        'found':       True,
        'has_code':    True,
        'listing':     listing_name,
        'check_in':    check_in,
        'check_out':   check_out,
        'guest_code':  guest_code,
        'backup_code': backup_code,
    })


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
