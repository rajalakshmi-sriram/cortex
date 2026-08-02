"""
Persisted literature-database API key settings for Cortex.

Mirrors app/ai_settings_store.py: lets a user add their own institutional/
personal API key for a paid literature database (Elsevier/Scopus,
Web of Science, IEEE Xplore, Springer Nature, CORE) or raise their
Semantic Scholar rate limit, from the app itself rather than only via a
.env file. Settings are stored in a plain JSON file under the app's data
directory and are used only for that user's own searches on their own
machine - never sent anywhere except the database provider itself, and
never shared with any other user of the app.
"""

import json
from pathlib import Path
from typing import Dict

KEY_FIELDS = (
    'elsevier_api_key',
    'wos_api_key',
    'semantic_scholar_api_key',
    'ieee_api_key',
    'springer_api_key',
    'core_api_key',
)


class LiteratureSettingsStore:
    """Reads/writes data/literature_settings.json, falling back to Config env defaults"""

    def __init__(self, config):
        self.path: Path = Path(config.DATA_DIR) / 'literature_settings.json'
        self._env_defaults = {
            'elsevier_api_key': getattr(config, 'ELSEVIER_API_KEY', '') or '',
            'wos_api_key': getattr(config, 'WOS_API_KEY', '') or '',
            'semantic_scholar_api_key': getattr(config, 'SEMANTIC_SCHOLAR_API_KEY', '') or '',
            'ieee_api_key': getattr(config, 'IEEE_API_KEY', '') or '',
            'springer_api_key': getattr(config, 'SPRINGER_API_KEY', '') or '',
            'core_api_key': getattr(config, 'CORE_API_KEY', '') or '',
        }

    def load(self) -> Dict:
        if self.path.exists():
            try:
                with open(self.path) as f:
                    data = json.load(f)
                return {field: data.get(field, '') for field in KEY_FIELDS}
            except (json.JSONDecodeError, OSError):
                pass
        return dict(self._env_defaults)

    def save(self, **kwargs) -> Dict:
        current = self.load()
        new_settings = {
            field: kwargs[field] if kwargs.get(field) is not None else current.get(field, '')
            for field in KEY_FIELDS
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        from app.project_store import atomic_write_text
        atomic_write_text(self.path, json.dumps(new_settings, indent=2))
        return new_settings

    def public(self) -> Dict:
        """Settings safe to send to the frontend - never the raw keys"""
        settings = self.load()
        return {f'has_{field.replace("_api_key", "")}_key': bool(settings.get(field)) for field in KEY_FIELDS}
