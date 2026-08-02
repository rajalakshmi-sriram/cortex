import { useEffect, useState } from 'react';
import { useProject } from './Workspace';
import { api } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { MicButton } from '../components/MicButton';
import { AiChatPanel } from '../components/AiChatPanel';
import { PageInstructions } from '../components/PageInstructions';
import './PaperLibrary.css';

const STYLES = [
  ['apa', 'APA'],
  ['mla', 'MLA'],
  ['chicago', 'Chicago'],
  ['vancouver', 'Vancouver'],
];

export function PaperLibrary() {
  const { project } = useProject();
  const [papers, setPapers] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [annotation, setAnnotation] = useState('');
  const [saveStatus, setSaveStatus] = useState('');
  const [style, setStyle] = useState('apa');
  const [citations, setCitations] = useState({});
  const [copyStatus, setCopyStatus] = useState('');

  useEffect(() => {
    refresh();
  }, [project.id]);

  useEffect(() => {
    if (papers.length === 0) return;
    api.getCitations(project.id, style).then((d) => {
      const map = {};
      d.citations.forEach((c) => { map[c.id] = c.citation; });
      setCitations(map);
    }).catch(() => {});
  }, [style, papers, project.id]);

  async function refresh() {
    const data = await api.listPapers(project.id);
    const sorted = (data.papers || []).sort((a, b) => (b.match_score || 0) - (a.match_score || 0));
    setPapers(sorted);
  }

  const selected = papers.find((p) => p.id === selectedId);

  function select(p) {
    setSelectedId(p.id);
    setAnnotation(p.annotations || '');
    setSaveStatus('');
  }

  async function saveAnnotation() {
    setSaveStatus('Saving…');
    await api.updatePaper(project.id, selectedId, { annotations: annotation });
    setSaveStatus('Saved ✓');
    refresh();
  }

  async function removePaper(id) {
    await api.deletePaper(project.id, id);
    if (id === selectedId) setSelectedId(null);
    refresh();
  }

  async function copyCitation(id) {
    const text = citations[id];
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopyStatus('Copied ✓');
      setTimeout(() => setCopyStatus(''), 2000);
    } catch {
      setCopyStatus('Could not copy — select and copy manually');
    }
  }

  return (
    <div>
      <PageInstructions
        accent="sand"
        items={[
          'Papers you save from Literature Review show up here, sorted by match score. Pick a citation style and copy or download citations for any of them.',
          'Click a paper to open its details, add your own annotations, or open the source.',
          'Once a paper is selected, use "Summarize with AI" under Paper Details to get an AI summary grounded in its abstract.',
        ]}
      />
      <Card
        title="Paper Library"
        hint="Papers saved from Literature Review, sorted by match score. Select one to add annotations or open the source."
        accent="sand"
      >
        <div className="paper-library__style-row">
          <label htmlFor="citation-style" style={{ margin: 0 }}>Citation style</label>
          <select id="citation-style" value={style} onChange={(e) => setStyle(e.target.value)} style={{ width: 160 }}>
            {STYLES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
          <a className="btn btn--secondary" style={{ '--btn-accent-tint': 'var(--accent4-tint)', '--btn-accent-text': 'var(--accent4-text)' }}
            href={api.bibtexUrl(project.id)} download>
            Download .bib
          </a>
          {copyStatus && <span role="status">{copyStatus}</span>}
        </div>

        {papers.length === 0 && <p>No papers saved yet — find some in Literature Review.</p>}

        <ul className="paper-library__list">
          {papers.map((p) => (
            <li key={p.id}>
              <div className={`paper-library__row ${p.id === selectedId ? 'paper-library__row--selected' : ''}`}>
                <button className="paper-library__select" onClick={() => select(p)}>
                  <span className="paper-library__title">
                    {p.match_score ? <strong>[{Math.round(p.match_score * 100)}%]</strong> : null} {p.title}
                  </span>
                  <span className="lit-search__paper-meta">
                    {p.authors} &middot; {p.year} <span className="source-tag">{p.source}</span>
                  </span>
                </button>
                <div className="paper-library__citation">
                  <code>{citations[p.id] || '…'}</code>
                  <Button variant="ghost" accent="sand" onClick={() => copyCitation(p.id)}>Copy</Button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </Card>

      {selected && (
        <Card title="Paper Details & Annotations" accent="sand">
          <p><strong>{selected.title}</strong></p>
          <p className="lit-search__paper-meta">{selected.authors} &middot; {selected.year} &middot; {selected.source}</p>

          <div style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
            {(selected.url || selected.doi) && (
              <a className="btn btn--primary" style={{ '--btn-accent-solid': 'var(--accent4-btn)' }}
                href={selected.url || `https://doi.org/${selected.doi}`} target="_blank" rel="noreferrer">
                Open Paper ↗
              </a>
            )}
            <Button variant="ghost" accent="rose" onClick={() => removePaper(selected.id)}>Remove from Library</Button>
          </div>

          <label htmlFor="annotation">Your annotations</label>
          <div style={{ display: 'flex', gap: 8 }}>
            <textarea id="annotation" value={annotation} onChange={(e) => setAnnotation(e.target.value)} style={{ flex: 1 }} />
            <MicButton label="annotation" onTranscript={(t) => setAnnotation((prev) => (prev ? prev + ' ' + t : t))} />
          </div>
          <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 10 }}>
            <Button accent="sand" onClick={saveAnnotation}>Save Annotation</Button>
            {saveStatus && <span role="status">{saveStatus}</span>}
          </div>
        </Card>
      )}

      {selected && (
        <Card title="Summarize with AI" hint="Get a quick summary grounded only in this paper's title, authors, and abstract." accent="sand">
          <AiChatPanel
            key={selected.id}
            contextType="paper_summary"
            context={{ paper: { title: selected.title, authors: selected.authors, year: selected.year, abstract: selected.abstract } }}
            kickoffMessage="Please summarize this paper for me."
            triggerLabel="Summarize with AI"
            accent="sand"
            disabled={!selected.abstract}
            disabledReason="No abstract was available for this paper, so it can't be summarized."
          />
        </Card>
      )}
    </div>
  );
}
