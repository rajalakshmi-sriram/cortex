"""
Google Docs integration for Cortex's manuscript "Google Docs" editor mode.

Lets AI Feedback read the live content of a linked Google Doc, via a
standard OAuth 2.0 "Desktop app" flow using your own Google Cloud OAuth
client credentials (added in the app, not baked into Cortex itself - see
README/DESKTOP_APP_BUILD.md for setup steps). Only a read-only Docs scope
is requested. Tokens are stored in a plain JSON file under the app's data
directory, same pattern as app/ai_settings_store.py.
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional

import requests

SCOPE = 'https://www.googleapis.com/auth/documents.readonly'
AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
DOCS_API_URL = 'https://docs.googleapis.com/v1/documents/{doc_id}'


class GoogleDocsStore:
    """Reads/writes data/google_docs_settings.json"""

    def __init__(self, config):
        self.path: Path = Path(config.DATA_DIR) / 'google_docs_settings.json'

    def load(self) -> Dict:
        if self.path.exists():
            try:
                with open(self.path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def _save(self, data: Dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        from app.project_store import atomic_write_text
        atomic_write_text(self.path, json.dumps(data, indent=2))

    def save_credentials(self, client_id: str, client_secret: str) -> Dict:
        current = self.load()
        current['client_id'] = client_id.strip()
        current['client_secret'] = client_secret.strip()
        self._save(current)
        return current

    def save_tokens(self, access_token: str, refresh_token: Optional[str], expires_in: int) -> Dict:
        current = self.load()
        current['access_token'] = access_token
        # Google only returns a refresh_token on the very first consent (or
        # when prompt=consent forces re-consent) - keep the existing one if
        # this response didn't include a new one.
        if refresh_token:
            current['refresh_token'] = refresh_token
        current['token_expires_at'] = time.time() + expires_in - 60  # refresh a little early
        self._save(current)
        return current

    def disconnect(self) -> None:
        current = self.load()
        current.pop('access_token', None)
        current.pop('refresh_token', None)
        current.pop('token_expires_at', None)
        self._save(current)

    def public(self) -> Dict:
        current = self.load()
        return {
            'has_client_credentials': bool(current.get('client_id') and current.get('client_secret')),
            'connected': bool(current.get('refresh_token')),
        }


def build_authorize_url(client_id: str, redirect_uri: str) -> str:
    from urllib.parse import urlencode
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': SCOPE,
        'access_type': 'offline',
        'prompt': 'consent',
    }
    return f"{AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code_for_tokens(client_id: str, client_secret: str, code: str, redirect_uri: str) -> Dict:
    response = requests.post(TOKEN_URL, data={
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    }, timeout=15)
    response.raise_for_status()
    return response.json()


def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> Dict:
    response = requests.post(TOKEN_URL, data={
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
    }, timeout=15)
    response.raise_for_status()
    return response.json()


def get_valid_access_token(store: GoogleDocsStore) -> str:
    """Returns a usable access token, refreshing it first if it's expired or about to be"""
    settings = store.load()
    if not settings.get('refresh_token'):
        raise ValueError('Google account not connected')

    if settings.get('access_token') and time.time() < settings.get('token_expires_at', 0):
        return settings['access_token']

    tokens = refresh_access_token(settings['client_id'], settings['client_secret'], settings['refresh_token'])
    store.save_tokens(tokens['access_token'], tokens.get('refresh_token'), tokens.get('expires_in', 3600))
    return tokens['access_token']


def _extract_text(doc_json: Dict) -> str:
    """Walk a Google Docs API document's body content and reconstruct plain text"""
    lines = []

    def walk_elements(elements):
        text = ''
        for el in elements or []:
            text_run = el.get('textRun')
            if text_run:
                text += text_run.get('content', '')
        return text

    for item in doc_json.get('body', {}).get('content', []):
        paragraph = item.get('paragraph')
        if paragraph:
            lines.append(walk_elements(paragraph.get('elements')))
            continue
        table = item.get('table')
        if table:
            for row in table.get('tableRows', []):
                for cell in row.get('tableCells', []):
                    for cell_item in cell.get('content', []):
                        cell_paragraph = cell_item.get('paragraph')
                        if cell_paragraph:
                            lines.append(walk_elements(cell_paragraph.get('elements')))

    return ''.join(lines).strip()


def fetch_document_text(doc_id: str, access_token: str) -> str:
    response = requests.get(
        DOCS_API_URL.format(doc_id=doc_id),
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=15,
    )
    if response.status_code == 404:
        raise ValueError("Document not found - check the link, and that this Google account has access to it.")
    if response.status_code == 403:
        raise ValueError("This Google account doesn't have permission to read that document.")
    response.raise_for_status()
    return _extract_text(response.json())
