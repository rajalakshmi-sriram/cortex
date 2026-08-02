"""
Persisted AI provider settings for Cortex's optional AI features.

Lets a user choose between a local model (Ollama, no API key, fully private)
or their own API key for a hosted provider (OpenAI or Anthropic), from the
app itself rather than only via environment variables. Settings are stored
in a plain JSON file under the app's data directory; the API key is never
echoed back to the frontend once saved.
"""

import json
from pathlib import Path
from typing import Dict, Optional

PROVIDERS = ('local', 'openai', 'anthropic')

DEFAULT_MODELS = {
    'local': 'qwen2.5:7b-instruct',
    'openai': 'gpt-4o-mini',
    'anthropic': 'claude-3-5-haiku-20241022',
}

DEFAULT_BASE_URLS = {
    'local': 'http://localhost:11434',
    'openai': 'https://api.openai.com',
    'anthropic': 'https://api.anthropic.com',
}


class AISettingsStore:
    """Reads/writes data/ai_settings.json, falling back to Config env defaults"""

    def __init__(self, config):
        self.path: Path = Path(config.DATA_DIR) / 'ai_settings.json'
        self._env_defaults = {
            'provider': 'local',
            'model': getattr(config, 'AI_MODEL', DEFAULT_MODELS['local']),
            'base_url': getattr(config, 'AI_BASE_URL', DEFAULT_BASE_URLS['local']),
            'api_key': getattr(config, 'OPENAI_API_KEY', None) or getattr(config, 'ANTHROPIC_API_KEY', None) or '',
        }

    def load(self) -> Dict:
        if self.path.exists():
            try:
                with open(self.path) as f:
                    data = json.load(f)
                if data.get('provider') in PROVIDERS:
                    return {
                        'provider': data.get('provider', 'local'),
                        'model': data.get('model') or DEFAULT_MODELS[data.get('provider', 'local')],
                        'base_url': data.get('base_url') or DEFAULT_BASE_URLS[data.get('provider', 'local')],
                        'api_key': data.get('api_key', ''),
                    }
            except (json.JSONDecodeError, OSError):
                pass
        return dict(self._env_defaults)

    def save(self, provider: str, model: Optional[str] = None, base_url: Optional[str] = None,
              api_key: Optional[str] = None) -> Dict:
        if provider not in PROVIDERS:
            raise ValueError(f"Unknown provider '{provider}'. Must be one of {PROVIDERS}.")

        current = self.load()
        new_settings = {
            'provider': provider,
            'model': (model or '').strip() or DEFAULT_MODELS[provider],
            'base_url': (base_url or '').strip() or DEFAULT_BASE_URLS[provider],
            # keep the previously saved key if the caller didn't pass a new one
            # (e.g. switching model without retyping the key)
            'api_key': api_key if api_key is not None else current.get('api_key', ''),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        from app.project_store import atomic_write_text
        atomic_write_text(self.path, json.dumps(new_settings, indent=2))
        return new_settings

    def public(self) -> Dict:
        """Settings safe to send to the frontend - never the raw key"""
        settings = self.load()
        return {
            'provider': settings['provider'],
            'model': settings['model'],
            'base_url': settings['base_url'],
            'has_api_key': bool(settings.get('api_key')),
        }
