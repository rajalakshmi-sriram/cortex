import { useState, useRef, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import './AiSettings.css';

const PROVIDERS = [
  {
    value: 'local',
    label: 'Local (Ollama)',
    blurb: 'Free and fully private - runs on your own machine. Install Ollama separately from ollama.com, then pull a model (e.g. "ollama pull qwen2.5:7b-instruct").',
    needsKey: false,
    modelPlaceholder: 'qwen2.5:7b-instruct',
  },
  {
    value: 'openai',
    label: 'OpenAI (your API key)',
    blurb: 'Uses your own OpenAI account and billing. Get a key at platform.openai.com.',
    needsKey: true,
    modelPlaceholder: 'gpt-4o-mini',
  },
  {
    value: 'anthropic',
    label: 'Anthropic Claude (your API key)',
    blurb: 'Uses your own Anthropic account and billing. Get a key at console.anthropic.com.',
    needsKey: true,
    modelPlaceholder: 'claude-3-5-haiku-20241022',
  },
  {
    value: 'gemini',
    label: 'Google Gemini (your API key)',
    blurb: 'Uses your own Google account and billing. Get a key at aistudio.google.com.',
    needsKey: true,
    modelPlaceholder: 'gemini-2.0-flash',
  },
  {
    value: 'mistral',
    label: 'Mistral (your API key)',
    blurb: 'Uses your own Mistral account and billing. Get a key at console.mistral.ai.',
    needsKey: true,
    modelPlaceholder: 'mistral-small-latest',
  },
  {
    value: 'groq',
    label: 'Groq (your API key)',
    blurb: 'Fast hosted inference for open-weight models. Get a key at console.groq.com.',
    needsKey: true,
    modelPlaceholder: 'llama-3.3-70b-versatile',
  },
  {
    value: 'openai_compatible',
    label: 'Custom (OpenAI-compatible endpoint)',
    blurb: 'Point this at any other OpenAI-compatible server - OpenRouter, Together AI, a self-hosted vLLM/LM Studio, etc. Model name and base URL are required; API key only if your endpoint needs one.',
    needsKey: true,
    keyOptional: true,
    needsBaseUrl: true,
    modelPlaceholder: 'e.g. meta-llama/llama-3.3-70b',
  },
];

export function AiSettings() {
  const [open, setOpen] = useState(false);
  const [settings, setSettings] = useState(null);
  const [provider, setProvider] = useState('local');
  const [model, setModel] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [baseUrl, setBaseUrl] = useState('');
  const [status, setStatus] = useState(null);
  const [saveState, setSaveState] = useState('');
  const containerRef = useRef(null);

  const refresh = useCallback(async () => {
    try {
      const data = await api.getAiSettings();
      setSettings(data.settings);
      setProvider(data.settings.provider);
      setModel(data.settings.model);
      setBaseUrl(data.settings.base_url || '');
      const statusData = await api.aiStatus();
      setStatus(statusData);
    } catch {
      /* AI settings are optional - fail silently if the backend can't be reached yet */
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  useEffect(() => {
    function onClickOutside(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) setOpen(false);
    }
    function onKey(e) {
      if (e.key === 'Escape') setOpen(false);
    }
    document.addEventListener('mousedown', onClickOutside);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onClickOutside);
      document.removeEventListener('keydown', onKey);
    };
  }, []);

  const activeProvider = PROVIDERS.find((p) => p.value === provider) || PROVIDERS[0];

  async function save(e) {
    e.preventDefault();
    setSaveState('Saving…');
    try {
      await api.updateAiSettings({
        provider,
        model: model.trim() || undefined,
        base_url: activeProvider.needsBaseUrl ? baseUrl.trim() : undefined,
        api_key: activeProvider.needsKey && apiKey.trim() ? apiKey.trim() : undefined,
      });
      setApiKey('');
      setSaveState('Saved ✓');
      await refresh();
    } catch (err) {
      setSaveState('');
      alert(err.message);
    }
  }

  const dotColor = status?.available ? 'var(--accent2-text)' : 'var(--text-muted)';

  return (
    <div className="ai-settings" ref={containerRef}>
      {open && (
        <div className="ai-settings__panel">
          <div className="ai-settings__section-label">AI Assistant</div>
          <p className="ai-settings__intro">
            AI features are optional and only run when you click a "Search with AI" button.
            Choose a free local model, or bring your own API key.
          </p>

          <form onSubmit={save}>
            <label htmlFor="ai-provider" className="ai-settings__field-label">Provider</label>
            <select id="ai-provider" value={provider} onChange={(e) => { setProvider(e.target.value); setModel(''); setBaseUrl(''); }}>
              {PROVIDERS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
            </select>
            <p className="ai-settings__blurb">{activeProvider.blurb}</p>

            <label htmlFor="ai-model" className="ai-settings__field-label">Model</label>
            <input
              id="ai-model"
              type="text"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              placeholder={activeProvider.modelPlaceholder}
            />

            {activeProvider.needsBaseUrl && (
              <>
                <label htmlFor="ai-base-url" className="ai-settings__field-label">Base URL</label>
                <input
                  id="ai-base-url"
                  type="text"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  placeholder="e.g. https://openrouter.ai/api"
                />
              </>
            )}

            {activeProvider.needsKey && (
              <>
                <label htmlFor="ai-key" className="ai-settings__field-label">
                  API Key {activeProvider.keyOptional && '(optional)'} {settings?.provider === provider && settings?.has_api_key && '(already saved)'}
                </label>
                <input
                  id="ai-key"
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder={settings?.provider === provider && settings?.has_api_key ? '••••••••••••' : 'sk-...'}
                  autoComplete="off"
                />
              </>
            )}

            <div className="ai-settings__actions">
              <button type="submit" className="ai-settings__save">Save</button>
              {saveState && <span role="status" className="ai-settings__save-status">{saveState}</span>}
            </div>
          </form>

          <div className="ai-settings__status">
            <span className="ai-settings__dot" style={{ background: dotColor }} aria-hidden="true" />
            {status?.available
              ? <>Ready ({status.provider === 'local' ? `Ollama, ${status.model}` : `${status.provider}, ${status.model}`})</>
              : status?.provider === 'local'
                ? <>Ollama not detected at localhost:11434 &mdash; install it separately, or switch to an API key above.</>
                : <>No API key saved yet for {status?.provider || 'this provider'}.</>}
          </div>
        </div>
      )}
      <button
        className="ai-settings__trigger"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="true"
        aria-expanded={open}
        aria-label="AI Assistant settings"
      >
        <SparkleIcon />
      </button>
    </div>
  );
}

function SparkleIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <path d="M12 3v5M12 16v5M3 12h5M16 12h5M6 6l3 3M15 15l3 3M18 6l-3 3M9 15l-3 3"
        stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <circle cx="12" cy="12" r="2.4" fill="currentColor" />
    </svg>
  );
}
