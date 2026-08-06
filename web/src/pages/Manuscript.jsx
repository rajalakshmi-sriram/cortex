import { useState, useEffect, useCallback } from 'react';
import { useProject } from './Workspace';
import { api } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { MicButton } from '../components/MicButton';
import { ToolChips } from '../components/ToolChips';
import { AiChatPanel } from '../components/AiChatPanel';
import { PageInstructions } from '../components/PageInstructions';
import { PAGE_TOOLS } from '../data/pageTools';
import './Manuscript.css';

const SECTIONS = ['abstract', 'introduction', 'methods', 'results', 'discussion', 'references'];

function PaperReferencePanel({ projectId }) {
  const [papers, setPapers] = useState([]);
  const [query, setQuery] = useState('');
  const [selectedId, setSelectedId] = useState(null);

  useEffect(() => {
    api.listPapers(projectId).then((d) => setPapers(d.papers || [])).catch(() => {});
  }, [projectId]);

  const filtered = papers.filter((p) => {
    const q = query.trim().toLowerCase();
    if (!q) return true;
    return (p.title || '').toLowerCase().includes(q) || (p.authors || '').toLowerCase().includes(q);
  });

  const selected = papers.find((p) => p.id === selectedId);

  return (
    <div className="manuscript-refpanel">
      <div className="manuscript-refpanel__header">
        <strong>Paper Reference</strong>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Filter your library…"
          aria-label="Filter papers"
        />
      </div>
      {filtered.length === 0 && (
        <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>
          {papers.length === 0 ? 'No papers saved yet — find some in Literature Review.' : 'No matches.'}
        </p>
      )}
      <ul className="manuscript-refpanel__list">
        {filtered.map((p) => (
          <li key={p.id}>
            <button
              className={`manuscript-refpanel__item ${p.id === selectedId ? 'manuscript-refpanel__item--selected' : ''}`}
              onClick={() => setSelectedId(selectedId === p.id ? null : p.id)}
            >
              <span className="manuscript-refpanel__title">{p.title}</span>
              <span className="manuscript-refpanel__meta">{p.authors} &middot; {p.year}</span>
            </button>
          </li>
        ))}
      </ul>

      {selected && (
        <div className="manuscript-refpanel__detail">
          <div className="manuscript-refpanel__detail-title">{selected.title}</div>
          <div className="manuscript-refpanel__meta">
            {selected.authors} &middot; {selected.year} {selected.source && <>&middot; {selected.source}</>}
          </div>
          {(selected.url || selected.doi) && (
            <a
              href={selected.url || `https://doi.org/${selected.doi}`}
              target="_blank"
              rel="noreferrer"
              className="manuscript-refpanel__link"
            >
              Open paper ↗
            </a>
          )}
          <div className="manuscript-refpanel__section-label">Abstract</div>
          <p className="manuscript-refpanel__abstract">{selected.abstract || 'No abstract available for this paper.'}</p>
          {selected.annotations && (
            <>
              <div className="manuscript-refpanel__section-label">Your annotations</div>
              <p className="manuscript-refpanel__abstract">{selected.annotations}</p>
            </>
          )}
        </div>
      )}
    </div>
  );
}

function extractGoogleDocId(input) {
  const match = input.match(/\/document\/d\/([a-zA-Z0-9_-]+)/);
  return match ? match[1] : input.trim();
}

function GoogleDocEditor({ projectId, docId, onUnlink }) {
  const [iframeError, setIframeError] = useState(false);
  const editUrl = `https://docs.google.com/document/d/${docId}/edit`;

  return (
    <Card title="Google Doc" hint="Editing live in Google Docs - changes save to your Google account, not to Cortex." accent="blue">
      <div style={{ marginBottom: 10, display: 'flex', gap: 10, alignItems: 'center' }}>
        <a href={editUrl} target="_blank" rel="noreferrer" className="btn btn--secondary">Open in Google Docs ↗</a>
        <Button variant="ghost" accent="rose" onClick={onUnlink}>Unlink Doc</Button>
      </div>
      {iframeError && (
        <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>
          If the embedded view below looks blank, your browser or Google's sharing settings may be
          blocking the embed - use "Open in Google Docs" above instead. Make sure the doc is shared
          as "Anyone with the link can edit" (or you're signed into the right Google account).
        </p>
      )}
      <iframe
        title="Google Doc"
        src={`${editUrl}?embedded=true`}
        style={{ width: '100%', height: 700, border: '1px solid var(--border)', borderRadius: 10 }}
        onError={() => setIframeError(true)}
      />
    </Card>
  );
}

function LinkGoogleDocForm({ onLink }) {
  const [docInput, setDocInput] = useState('');
  return (
    <Card title="Link a Google Doc" hint="Paste the share link (or just the document ID) of a Google Doc you own or can edit." accent="blue">
      <form onSubmit={(e) => { e.preventDefault(); if (docInput.trim()) onLink(extractGoogleDocId(docInput)); }}>
        <label htmlFor="google-doc-url">Google Doc link</label>
        <input
          id="google-doc-url"
          type="text"
          value={docInput}
          onChange={(e) => setDocInput(e.target.value)}
          placeholder="https://docs.google.com/document/d/…/edit"
        />
        <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: '6px 0 0' }}>
          Create a doc at <a href="https://docs.google.com" target="_blank" rel="noreferrer">docs.google.com</a> first,
          then set its sharing to "Anyone with the link can edit" (or make sure you're signed into the
          right Google account in this browser) before linking it here.
        </p>
        <div style={{ marginTop: 12 }}>
          <Button type="submit" accent="blue">Link Doc</Button>
        </div>
      </form>
    </Card>
  );
}

function GoogleAccountPanel({ onStatusChange }) {
  const [settings, setSettings] = useState(null);
  const [clientId, setClientId] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState('');

  const refresh = useCallback(() => {
    api.getGoogleSettings().then((d) => {
      setSettings(d.settings);
      onStatusChange?.(d.settings.connected);
    }).catch(() => {});
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { refresh(); }, [refresh]);

  async function saveCredentials(e) {
    e.preventDefault();
    setError('');
    if (!clientId.trim() || !clientSecret.trim()) return;
    try {
      await api.saveGoogleCredentials(clientId.trim(), clientSecret.trim());
      setClientId('');
      setClientSecret('');
      refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  async function connect() {
    setError('');
    try {
      const data = await api.getGoogleAuthorizeUrl();
      window.open(data.url, '_blank', 'width=520,height=680');
      setConnecting(true);
      const interval = setInterval(async () => {
        try {
          const d = await api.getGoogleSettings();
          if (d.settings.connected) {
            clearInterval(interval);
            setConnecting(false);
            setSettings(d.settings);
            onStatusChange?.(true);
          }
        } catch {
          /* keep polling */
        }
      }, 2000);
      setTimeout(() => { clearInterval(interval); setConnecting(false); }, 120000);
    } catch (e) {
      setError(e.message);
      setConnecting(false);
    }
  }

  async function disconnect() {
    await api.disconnectGoogle();
    refresh();
  }

  if (!settings) return null;

  return (
    <Card title="Google Account" hint="Connect a Google account (read-only) so AI Feedback can read your linked doc's live content." accent="blue">
      {!settings.has_client_credentials ? (
        <form onSubmit={saveCredentials}>
          <p style={{ fontSize: 12.5, color: 'var(--text-muted)', margin: '0 0 10px' }}>
            Requires your own Google Cloud OAuth client (one-time setup, free) - create one at{' '}
            <a href="https://console.cloud.google.com/apis/credentials" target="_blank" rel="noreferrer">
              console.cloud.google.com/apis/credentials
            </a>{' '}
            (Application type: "Desktop app"), enable the "Google Docs API" for that project, then paste
            the Client ID and Client Secret below. See DESKTOP_APP_BUILD.md for full steps.
          </p>
          <label htmlFor="google-client-id">Client ID</label>
          <input id="google-client-id" type="text" value={clientId} onChange={(e) => setClientId(e.target.value)} placeholder="…apps.googleusercontent.com" />
          <label htmlFor="google-client-secret">Client Secret</label>
          <input id="google-client-secret" type="password" value={clientSecret} onChange={(e) => setClientSecret(e.target.value)} />
          <div style={{ marginTop: 10 }}>
            <Button type="submit" accent="blue">Save Credentials</Button>
          </div>
        </form>
      ) : !settings.connected ? (
        <Button accent="blue" onClick={connect} disabled={connecting}>
          {connecting ? 'Waiting for Google sign-in…' : 'Connect Google Account'}
        </Button>
      ) : (
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span>✓ Google account connected</span>
          <Button variant="ghost" accent="rose" onClick={disconnect}>Disconnect</Button>
        </div>
      )}
      {error && <p role="alert" style={{ color: 'var(--accent1-text)', marginTop: 8 }}>{error}</p>}
    </Card>
  );
}

function GoogleDocAiFeedback({ docId, connected }) {
  const [docText, setDocText] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function loadDoc() {
    setLoading(true);
    setError('');
    try {
      const data = await api.getGoogleDocContent(docId);
      setDocText(data.text);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  if (!connected) {
    return (
      <Card title="AI Feedback" accent="blue">
        <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>
          Connect your Google account above to get AI feedback grounded in this doc's live content.
        </p>
      </Card>
    );
  }

  return (
    <Card
      title="AI Feedback"
      hint="Get constructive, journal-reviewer-style feedback grounded in the current content of your linked Google Doc."
      accent="blue"
    >
      <Button variant={docText === null ? 'primary' : 'ghost'} accent="blue" onClick={loadDoc} disabled={loading} style={{ marginBottom: docText !== null ? 12 : 0 }}>
        {loading ? 'Reading document…' : docText === null ? '✨ Load Document for AI Feedback' : 'Refresh Document Content'}
      </Button>
      {error && <p role="alert" style={{ color: 'var(--accent1-text)', marginTop: 8 }}>{error}</p>}
      {docText !== null && (
        <AiChatPanel
          key={docText.length}
          contextType="manuscript_feedback"
          context={{ sections: { full_document: docText } }}
          kickoffMessage="Please review my manuscript draft and give me constructive feedback to help it reach the quality bar of a good/top journal."
          triggerLabel="Get AI Feedback on My Draft"
          accent="blue"
          disabled={!docText.trim()}
          disabledReason="The linked document appears to be empty."
        />
      )}
    </Card>
  );
}

export function Manuscript() {
  const { project } = useProject();
  const [sections, setSections] = useState(Object.fromEntries(SECTIONS.map((s) => [s, ''])));
  const [saveStatus, setSaveStatus] = useState('');
  const [showReferences, setShowReferences] = useState(false);
  const [editorMode, setEditorMode] = useState('cortex');
  const [googleDocId, setGoogleDocId] = useState('');
  const [googleConnected, setGoogleConnected] = useState(false);

  useEffect(() => {
    api.getManuscript(project.id).then((d) => {
      setSections((prev) => ({ ...prev, ...d.manuscript }));
      if (d.manuscript?.google_doc_url) {
        setGoogleDocId(d.manuscript.google_doc_url);
        setEditorMode('google');
      } else {
        setGoogleDocId('');
        setEditorMode('cortex');
      }
    });
  }, [project.id]);

  async function save() {
    setSaveStatus('Saving…');
    await api.updateManuscript(project.id, sections);
    setSaveStatus('Saved ✓');
  }

  async function linkGoogleDoc(docId) {
    await api.updateManuscript(project.id, { google_doc_url: docId });
    setGoogleDocId(docId);
  }

  async function unlinkGoogleDoc() {
    await api.updateManuscript(project.id, { google_doc_url: '' });
    setGoogleDocId('');
  }

  const hasContent = Object.values(sections).some((v) => v && v.trim());

  return (
    <div>
      <PageInstructions
        accent="blue"
        items={[
          'Write each section of your manuscript below (use the mic button to dictate) and click Save Manuscript.',
          'Once you\'ve written some of your draft, click "Get AI Feedback on My Draft" in the AI Feedback section for reviewer-style feedback aimed at top-journal quality — then ask follow-up questions in the chat that appears.',
        ]}
      />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, flexWrap: 'wrap', gap: 10 }}>
        <div style={{ display: 'flex', gap: 6 }}>
          <Button
            variant={editorMode === 'cortex' ? 'primary' : 'secondary'}
            accent="blue"
            onClick={() => setEditorMode('cortex')}
          >
            Cortex Editor
          </Button>
          <Button
            variant={editorMode === 'google' ? 'primary' : 'secondary'}
            accent="blue"
            onClick={() => setEditorMode('google')}
          >
            Google Docs
          </Button>
        </div>
        <Button variant="secondary" accent="blue" onClick={() => setShowReferences((v) => !v)}>
          {showReferences ? 'Hide' : 'Show'} Paper Reference Panel
        </Button>
      </div>

      <div className={showReferences ? 'manuscript-split' : undefined}>
        {editorMode === 'cortex' ? (
          <Card title="Manuscript Draft" hint="Draft each section of your manuscript. Saved to this project." accent="blue">
            {SECTIONS.map((section) => (
              <div key={section}>
                <label htmlFor={`section-${section}`} style={{ textTransform: 'capitalize' }}>{section}</label>
                <div style={{ display: 'flex', gap: 8 }}>
                  <textarea
                    id={`section-${section}`}
                    value={sections[section] || ''}
                    onChange={(e) => setSections({ ...sections, [section]: e.target.value })}
                    placeholder={`Write your ${section}...`}
                    style={{ flex: 1, minHeight: 90 }}
                  />
                  <MicButton label={section} onTranscript={(t) => setSections((prev) => ({ ...prev, [section]: prev[section] ? prev[section] + ' ' + t : t }))} />
                </div>
              </div>
            ))}

            <div style={{ marginTop: 14, display: 'flex', alignItems: 'center', gap: 12 }}>
              <Button accent="blue" onClick={save}>Save Manuscript</Button>
              {saveStatus && <span role="status">{saveStatus}</span>}
            </div>

            <div style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
              <label style={{ margin: 0 }}>Recommended Tools</label>
              <ToolChips tools={PAGE_TOOLS.manuscript} />
            </div>
          </Card>
        ) : googleDocId ? (
          <GoogleDocEditor projectId={project.id} docId={googleDocId} onUnlink={unlinkGoogleDoc} />
        ) : (
          <LinkGoogleDocForm onLink={linkGoogleDoc} />
        )}

        {showReferences && <PaperReferencePanel projectId={project.id} />}
      </div>

      {editorMode === 'cortex' ? (
        <Card
          title="AI Feedback"
          hint="Get constructive, journal-reviewer-style feedback on your draft, grounded only in what you've written — then ask follow-up questions."
          accent="blue"
        >
          <AiChatPanel
            contextType="manuscript_feedback"
            context={{ sections }}
            kickoffMessage="Please review my manuscript draft and give me constructive feedback to help it reach the quality bar of a good/top journal."
            triggerLabel="Get AI Feedback on My Draft"
            accent="blue"
            disabled={!hasContent}
            disabledReason="Write (and ideally save) some of your draft first."
          />
        </Card>
      ) : (
        <>
          <GoogleAccountPanel onStatusChange={setGoogleConnected} />
          {googleDocId && <GoogleDocAiFeedback docId={googleDocId} connected={googleConnected} />}
        </>
      )}
    </div>
  );
}
