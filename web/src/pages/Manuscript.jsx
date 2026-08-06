import { useState, useEffect } from 'react';
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
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    api.listPapers(projectId).then((d) => setPapers(d.papers || [])).catch(() => {});
  }, [projectId]);

  const filtered = papers.filter((p) => {
    const q = query.trim().toLowerCase();
    if (!q) return true;
    return (p.title || '').toLowerCase().includes(q) || (p.authors || '').toLowerCase().includes(q);
  });

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
            <button className="manuscript-refpanel__item" onClick={() => setExpandedId(expandedId === p.id ? null : p.id)}>
              <span className="manuscript-refpanel__title">{p.title}</span>
              <span className="manuscript-refpanel__meta">{p.authors} &middot; {p.year}</span>
              {expandedId === p.id && (
                <span className="manuscript-refpanel__abstract">
                  {p.abstract || 'No abstract available.'}
                  {p.annotations && <><br /><em>Your notes: {p.annotations}</em></>}
                </span>
              )}
            </button>
          </li>
        ))}
      </ul>
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

export function Manuscript() {
  const { project } = useProject();
  const [sections, setSections] = useState(Object.fromEntries(SECTIONS.map((s) => [s, ''])));
  const [saveStatus, setSaveStatus] = useState('');
  const [showReferences, setShowReferences] = useState(false);
  const [editorMode, setEditorMode] = useState('cortex');
  const [googleDocId, setGoogleDocId] = useState('');

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

      {editorMode === 'cortex' && (
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
      )}
    </div>
  );
}
