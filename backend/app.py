import os
import base64
import requests
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
ADMIN_PASSWORD   = os.environ.get('ADMIN_PASSWORD', 'changeme')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
GITHUB_TOKEN     = os.environ.get('GITHUB_TOKEN')
REPO             = 'yerfttam/WCBNW'
STAGING_BRANCH   = 'staging'

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# In-memory conversation history (resets on server restart — that's fine)
conversation: list = []


# ── GitHub helpers ────────────────────────────────────────────────────────────

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
    return None

def write_file(path: str, content: str, message: str) -> bool:
    current = read_file(path)
    if not current:
        return False
    url = f'https://api.github.com/repos/{REPO}/contents/{path}'
    payload = {
        'message': message,
        'content': base64.b64encode(content.encode('utf-8')).decode('utf-8'),
        'sha': current['sha'],
        'branch': STAGING_BRANCH
    }
    r = requests.put(url, headers=gh_headers(), json=payload)
    return r.status_code in (200, 201)

def merge_to_main() -> bool:
    url = f'https://api.github.com/repos/{REPO}/merges'
    payload = {
        'base': 'main',
        'head': STAGING_BRANCH,
        'commit_message': 'chore: deploy to production via admin chat'
    }
    r = requests.post(url, headers=gh_headers(), json=payload)
    # 201 = merged, 204 = already up-to-date
    return r.status_code in (201, 204)


# ── Claude tool definitions ───────────────────────────────────────────────────

TOOLS = [
    {
        "name": "read_file",
        "description": "Read the current content of any file in the website repository. Use this before making edits so you have the exact current content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to repo root, e.g. 'NEW/about.html' or 'NEW/partials/footer.html'"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "update_file",
        "description": "Write new content to a file and commit it to the staging branch. Always read the file first so you can make a targeted edit.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to repo root"
                },
                "content": {
                    "type": "string",
                    "description": "The complete new file content"
                },
                "commit_message": {
                    "type": "string",
                    "description": "Short description of what changed, e.g. 'update check-in time to 3pm on policies page'"
                }
            },
            "required": ["path", "content", "commit_message"]
        }
    },
    {
        "name": "deploy_to_production",
        "description": "Merge the staging branch into main, pushing all staged changes live to the public website. Only do this when the owner explicitly says they're happy and want to go live.",
        "input_schema": {
            "type": "object",
            "properties": {
                "confirm": {
                    "type": "boolean",
                    "description": "Must be true to confirm the deployment"
                }
            },
            "required": ["confirm"]
        }
    }
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
1. Read the relevant file first so you know exactly what's there
2. Make only the specific change requested — touch nothing else
3. Also read NEW/partials/footer.html and bump the patch version number (e.g. v2.2.1 → v2.2.2)
4. Commit both files with clear commit messages starting with the new version number
5. Tell the owner what you changed and that it's ready to preview at https://wcbnw-staging.onrender.com
6. Ask if she'd like to push it live — if yes, use deploy_to_production

## Rules
- Only make content edits: text, descriptions, policies, contact info, hours
- Never change HTML structure, CSS styles, JavaScript, or navigation layout
- Always bump the version number in NEW/partials/footer.html
- The version is in a <span class="site-version"> tag — bump the last number only
- Keep your replies short and friendly — she's on her phone
- Speak plainly, no technical jargon
- If you're unsure what she wants, ask a quick clarifying question before making changes
- After deploying to production, remind her the live site updates in about 2 minutes"""


# ── Tool execution ────────────────────────────────────────────────────────────

def execute_tool(name: str, inputs: dict) -> str:
    if name == 'read_file':
        result = read_file(inputs['path'])
        if result:
            return result['content']
        return f"Could not read file: {inputs['path']}"

    if name == 'update_file':
        success = write_file(inputs['path'], inputs['content'], inputs['commit_message'])
        return 'File updated and committed successfully.' if success else 'Failed to update file — please try again.'

    if name == 'deploy_to_production':
        if not inputs.get('confirm'):
            return 'Deployment cancelled.'
        success = merge_to_main()
        return 'Deployed to production successfully! The live site will update in about 2 minutes.' if success else 'Deployment failed — please try again or contact the developer.'

    return f'Unknown tool: {name}'


# ── Serialization helpers ─────────────────────────────────────────────────────

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


# ── Chat endpoint ─────────────────────────────────────────────────────────────

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

    try:
        # Agentic loop — keep going until Claude stops using tools
        while True:
            response = client.messages.create(
                model='claude-sonnet-4-5',
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=conversation
            )

            # Add assistant turn to history (serialized)
            assistant_content = serialize_content(response.content)
            conversation.append({'role': 'assistant', 'content': assistant_content})

            if response.stop_reason != 'tool_use':
                break

            # Execute any tool calls and add results
            tool_results = []
            for block in response.content:
                if hasattr(block, 'type') and block.type == 'tool_use':
                    result_text = execute_tool(block.name, block.input)
                    tool_results.append({
                        'type': 'tool_result',
                        'tool_use_id': block.id,
                        'content': result_text
                    })

            if tool_results:
                conversation.append({'role': 'user', 'content': tool_results})

        # Extract the final text reply
        reply = ' '.join(
            b.text for b in response.content if hasattr(b, 'type') and b.type == 'text'
        ).strip()

        return jsonify({'response': reply})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/reset', methods=['POST', 'OPTIONS'])
def reset():
    global conversation
    data = request.json or {}
    if data.get('password') != ADMIN_PASSWORD:
        return jsonify({'error': 'Invalid password'}), 401
    conversation = []
    return jsonify({'status': 'ok'})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
