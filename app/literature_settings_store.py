"""
Persisted literature-database API key settings for Cortex.

Mirrors app/ai_settings_store.py: lets a user add their own institutional/
personal API key for a paid literature database (Elsevier/Scopus,
Web of Science) or raise their Semantic Scholar rate limit, from the app
itself rather than only via a .env file. Settings are stored in a plain
JSON file under the app's data directory and are used only for that user's
own searches on their own machine - never sent anywhere except the
database provider itself, and never shared with any other user of the app.
"""

import json
from pathlib import Path
from typing import Dict


class LiteratureSettingsStore:
    """Reads/writes data/literature_settings.json, falling back to Config env defaults"""

    def __init__(self, config):
        self.path: Path = Path(config.DATA_DIR) / 'literature_settings.json'
        self._env_defaults = {
            'elsevier_api_key': getattr(config, 'ELSEVIER_API_KEY', '') or '',
            'wos_api_key': getattr(config, 'WOS_API_KEY', '') or '',
            'semantic_scholar_api_key': getattr(config, 'SEMANTIC_SCHOLAR_API_KEY', '') or '',
        }

    def load(self) -> Dict:
        if self.path.exists():
            try:
                with open(self.path) as f:
                    data = json.load(f)
                return {
                    'elsevier_api_key': data.get('elsevier_api_key', ''),
                    'wos_api_key': data.get('wos_api_key', ''),
                    'semantic_scholar_api_key': data.get('semantic_scholar_api_key', ''),
                }
            except (json.JSONDecodeError, OSError):
                pass
        return dict(self._env_defaults)

    def save(self, elsevier_api_key=None, wos_api_key=None, semantic_scholar_api_key=None) -> Dict:
        current = self.load()
        new_settings = {
            'elsevier_api_key': elsevier_api_key if elsevier_api_key is not None else current.get('elsevier_api_key', ''),
            'wos_api_key': wos_api_key if wos_api_key is not None else current.get('wos_api_key', ''),
            'semantic_scholar_api_key': semantic_scholar_api_key if semantic_scholar_api_key is not None else current.get('semantic_scholar_api_key', ''),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        from app.project_store import atomic_write_text
        atomic_write_text(self.path, json.dumps(new_settings, indent=2))
        return new_settings

    def public(self) -> Dict:
        """Settings safe to send to the frontend - never the raw keys"""
        settings = self.load()
        return {
            'has_elsevier_key': bool(settings.get('elsevier_api_key')),
            'has_wos_key': bool(settings.get('wos_api_key')),
            'has_semantic_scholar_key': bool(settings.get('semantic_scholar_api_key')),
        }
