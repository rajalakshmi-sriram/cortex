import { useState, useRef, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import './LiteratureSettings.css';

const SOURCES = [
  {
    key: 'elsevier_api_key',
    hasKeyField: 'has_elsevier_key',
    label: 'Elsevier (Scopus / ScienceDirect)',
    blurb: 'If your institution or account has an Elsevier API key, add it here to also search Scopus/ScienceDirect. Register free at dev.elsevier.com.',
    placeholder: 'Elsevier API key',
  },
  {
    key: 'wos_api_key',
    hasKeyField: 'has_wos_key',
    label: 'Web of Science',
    blurb: 'Requires institutional Clarivate access. Add your key to also search Web of Science.',
    placeholder: 'Web of Science API key',
  },
  {
    key: 'semantic_scholar_api_key',
    hasKeyField: 'has_semantic_scholar_key',
    label: 'Semantic Scholar (optional)',
    blurb: 'Semantic Scholar is already searched for everyone - this just raises your personal rate limit if you have a key. Free at semanticscholar.org/product/api.',
    placeholder: 'Semantic Scholar API key',
  },
  {
    key: 'ieee_api_key',
    hasKeyField: 'has_ieee_key',
    label: 'IEEE Xplore',
    blurb: 'Add your key to also search IEEE Xplore (engineering/CS). Register free at developer.ieee.org.',
    placeholder: 'IEEE Xplore API key',
  },
  {
    key: 'springer_api_key',
    hasKeyField: 'has_springer_key',
    label: 'Springer Nature',
    blurb: 'Add your key to also search Springer Nature. Register free at dev.springernature.com.',
    placeholder: 'Springer Nature API key',
  },
  {
    key: 'core_api_key',
    hasKeyField: 'has_core_key',
    label: 'CORE (open access aggregator)',
    blurb: 'Add your key to also search CORE, a large open-access paper aggregator. Register free at core.ac.uk/services/api.',
    placeholder: 'CORE API key',
  },
];

export function LiteratureSettings() {
  const [open, setOpen] = useState(false);
  const [settings, setSettings] = useState(null);
  const [values, setValues] = useState({});
  const [saveState, setSaveState] = useState('');
  const containerRef = useRef(null);

  const refresh = useCallback(async () => {
    try {
      const data = await api.getLiteratureSettings();
      setSettings(data.settings);
    } catch {
      /* optional feature - fail silently if the backend can't be reached yet */
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

  async function save(e) {
    e.preventDefault();
    setSaveState('Saving…');
    try {
      // Only send fields the user actually typed into this time - omitted
      // fields keep whatever was saved before, so switching one key doesn't
      // clobber another.
      const body = {};
      for (const source of SOURCES) {
        if (values[source.key] !== undefined) body[source.key] = values[source.key].trim();
      }
      await api.updateLiteratureSettings(body);
      setValues({});
      setSaveState('Saved ✓');
      await refresh();
    } catch (err) {
      setSaveState('');
      alert(err.message);
    }
  }

  async function clearKey(sourceKey) {
    await api.updateLiteratureSettings({ [sourceKey]: '' });
    await refresh();
  }

  return (
    <div className="lit-settings" ref={containerRef}>
      {open && (
        <div className="lit-settings__panel">
          <div className="lit-settings__section-label">Literature Sources</div>
          <p className="lit-settings__intro">
            Europe PMC, CrossRef, arXiv, ERIC, Semantic Scholar, and OpenAlex are always searched for free.
            If you have your own subscription or API key for a paid database, add it below to also search that
            one. It's used only for your own searches on your own machine - never shared with anyone else using
            this app.
          </p>

          <form onSubmit={save}>
            {SOURCES.map((source) => {
              const hasKey = settings?.[source.hasKeyField];
              return (
                <div key={source.key} className="lit-settings__source">
                  <label htmlFor={`lit-${source.key}`} className="lit-settings__field-label">
                    {source.label} {hasKey && <span className="lit-settings__saved-tag">saved</span>}
                  </label>
                  <p className="lit-settings__blurb">{source.blurb}</p>
                  <div className="lit-settings__input-row">
                    <input
                      id={`lit-${source.key}`}
                      type="password"
                      value={values[source.key] ?? ''}
                      onChange={(e) => setValues({ ...values, [source.key]: e.target.value })}
                      placeholder={hasKey ? '••••••••••••' : source.placeholder}
                      autoComplete="off"
                    />
                    {hasKey && (
                      <button type="button" className="lit-settings__clear" onClick={() => clearKey(source.key)}>
                        Remove
                      </button>
                    )}
                  </div>
                </div>
              );
            })}

            <div className="lit-settings__actions">
              <button type="submit" className="lit-settings__save">Save</button>
              {saveState && <span role="status" className="lit-settings__save-status">{saveState}</span>}
            </div>
          </form>
        </div>
      )}
      <button
        className="lit-settings__trigger"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="true"
        aria-expanded={open}
        aria-label="Literature source settings"
      >
        <DatabaseIcon />
      </button>
    </div>
  );
}

function DatabaseIcon() {
  return (
    <svg width="19" height="19" viewBox="0 0 24 24" fill="none">
      <ellipse cx="12" cy="6" rx="8" ry="3" stroke="currentColor" strokeWidth="1.6" />
      <path d="M4 6v6c0 1.66 3.58 3 8 3s8-1.34 8-3V6" stroke="currentColor" strokeWidth="1.6" />
      <path d="M4 12v6c0 1.66 3.58 3 8 3s8-1.34 8-3v-6" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  );
}
