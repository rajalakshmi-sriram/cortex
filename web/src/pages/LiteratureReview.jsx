import { useState, useEffect } from 'react';
import { useProject } from './Workspace';
import { api } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { MicButton } from '../components/MicButton';
import { AiChatPanel } from '../components/AiChatPanel';
import { PageInstructions } from '../components/PageInstructions';
import './LiteratureReview.css';

export function LiteratureReview() {
  const { project } = useProject();
  const [idea, setIdea] = useState('');
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [selected, setSelected] = useState(new Set());
  const [saveStatus, setSaveStatus] = useState('');
  const [aiAvailable, setAiAvailable] = useState(false);
  const [useAI, setUseAI] = useState(false);
  const [summarizingIndex, setSummarizingIndex] = useState(null);

  useEffect(() => {
    api.aiStatus().then((d) => setAiAvailable(d.available)).catch(() => setAiAvailable(false));
  }, []);

  async function search() {
    if (idea.trim().length < 10) {
      setError('Idea must be at least 10 characters.');
      return;
    }
    setSearching(true);
    setError('');
    setResult(null);
    setSelected(new Set());
    try {
      const data = useAI && aiAvailable ? await api.validateIdeaWithAI(idea) : await api.validateIdea(idea);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setSearching(false);
    }
  }

  const papers = result ? (result.related_papers || result.similar_papers || []) : [];

  function toggleSelect(index) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  }

  function selectAll() {
    setSelected(new Set(papers.map((_, i) => i)));
  }
  function selectNone() {
    setSelected(new Set());
  }

  async function saveSelected() {
    if (selected.size === 0) return;
    setSaveStatus(`Saving ${selected.size}…`);
    try {
      await Promise.all(
        [...selected].map((i) => {
          const p = papers[i];
          return api.addPaper(project.id, {
            title: p.title,
            authors: Array.isArray(p.authors) ? p.authors.join(', ') : p.authors,
            year: p.year,
            source: p.source,
            doi: p.doi,
            url: p.url,
            match_score: p.similarity_score,
            tfidf_score: p.tfidf_score,
            keyword_overlap: p.keyword_overlap,
            matched_idea: idea,
            abstract: p.abstract || '',
            annotations: '',
          });
        })
      );
      setSaveStatus(`Saved ${selected.size} paper(s) to your library ✓`);
      setSelected(new Set());
    } catch (e) {
      setSaveStatus('');
      setError(e.message);
    }
  }

  return (
    <div>
      <PageInstructions
        accent="rose"
        items={[
          'Describe your research idea or topic and click Search to find real papers and see how novel your idea is against what\'s already published.',
          'If an AI assistant is set up (sparkle icon, bottom-right), check "Search with AI" to also get a synthesis + gap analysis — click "Discuss with AI" under it to ask follow-ups.',
          'Click "✨ Summarize" next to any result for an AI summary of that specific paper.',
          'Check the papers you want to keep and click "Save Selected to Library" to add them to Paper Library.',
        ]}
      />
      <Card
        title="Search Literature"
        hint="Find real papers for a specific research topic and check how novel it is against what's already published."
        accent="rose"
      >
        <label htmlFor="lit-idea">Your research idea or topic</label>
        <div style={{ display: 'flex', gap: 8 }}>
          <textarea
            id="lit-idea"
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            placeholder="e.g. Investigate the role of astrocytes in memory consolidation using optogenetics"
            style={{ flex: 1, minHeight: 60 }}
          />
          <MicButton label="research idea" onTranscript={(t) => setIdea((prev) => (prev ? prev + ' ' + t : t))} />
        </div>

        <div className="lit-search__controls">
          <Button accent="rose" onClick={search} disabled={searching}>
            {searching ? 'Searching…' : 'Search'}
          </Button>
          {aiAvailable && (
            <label className="lit-search__ai-toggle">
              <input type="checkbox" checked={useAI} onChange={(e) => setUseAI(e.target.checked)} />
              Search with AI (adds a synthesis + gap analysis from the local model)
            </label>
          )}
        </div>
        {error && <p role="alert" style={{ color: 'var(--accent1-text)' }}>{error}</p>}
      </Card>

      {result && (
        <Card title="Results" accent="sage">
          <p aria-live="polite">
            <strong>{result.status === 'similar' ? 'Similar to existing work' : 'Appears unique'}</strong> &mdash; {result.message}
          </p>
          {result.confidence && <p style={{ color: 'var(--text-muted)', fontSize: 12 }}>{result.confidence}</p>}

          {result.top_match_breakdown && (
            <div>
              <MetricBar label="Overall similarity" value={result.max_similarity_score} />
              <MetricBar label="Topic overlap" value={result.top_match_breakdown.tfidf_score} />
              <MetricBar label="Shared terms" value={result.top_match_breakdown.keyword_overlap} />
            </div>
          )}

          {result.ai_synthesis && (
            <div className="lit-search__ai-synthesis">
              <strong>AI Synthesis</strong>
              <p>{result.ai_synthesis}</p>
              <div style={{ marginTop: 10 }}>
                <AiChatPanel
                  key={idea}
                  contextType="literature_synthesis"
                  context={{ idea, papers }}
                  kickoffMessage="Please summarize the current literature on this topic and identify gaps."
                  seedAssistantMessage={result.ai_synthesis}
                  triggerLabel="Discuss with AI"
                  accent="rose"
                />
              </div>
            </div>
          )}

          {papers.length > 0 && (
            <>
              <div className="lit-search__select-row">
                <button className="chip" onClick={selectAll}>Select all</button>
                <button className="chip" onClick={selectNone}>Select none</button>
                <Button accent="sage" onClick={saveSelected} disabled={selected.size === 0}>
                  Save {selected.size > 0 ? `${selected.size} ` : ''}Selected to Library
                </Button>
                {saveStatus && <span role="status">{saveStatus}</span>}
              </div>

              <ul className="lit-search__papers">
                {papers.map((p, i) => (
                  <li key={i} className="lit-search__paper">
                    <label className="lit-search__paper-check">
                      <input
                        type="checkbox"
                        checked={selected.has(i)}
                        onChange={() => toggleSelect(i)}
                        aria-label={`Select "${p.title}" to save`}
                      />
                    </label>
                    <div className="lit-search__paper-body">
                      <div className="lit-search__paper-title">{p.title}</div>
                      <div className="lit-search__paper-meta">
                        {Array.isArray(p.authors) ? p.authors.join(', ') : p.authors} &middot; {p.year}
                        {' '}<span className="source-tag">{p.source}</span>
                        {p.doi && (
                          <>
                            {' '}
                            <a href={`https://doi.org/${p.doi}`} target="_blank" rel="noreferrer">DOI</a>
                          </>
                        )}
                      </div>
                      <div className="lit-search__paper-score">
                        Match: {Math.round((p.similarity_score || 0) * 100)}%
                        {' '}
                        <button
                          type="button"
                          className="chip"
                          style={{ marginLeft: 8 }}
                          onClick={() => setSummarizingIndex(summarizingIndex === i ? null : i)}
                          disabled={!p.abstract}
                          title={p.abstract ? '' : 'No abstract available for this paper'}
                        >
                          ✨ Summarize
                        </button>
                      </div>
                      {summarizingIndex === i && (
                        <div style={{ marginTop: 10 }}>
                          <AiChatPanel
                            key={i}
                            contextType="paper_summary"
                            context={{ paper: { title: p.title, authors: Array.isArray(p.authors) ? p.authors.join(', ') : p.authors, year: p.year, abstract: p.abstract } }}
                            kickoffMessage="Please summarize this paper for me."
                            triggerLabel="Summarize with AI"
                            accent="rose"
                          />
                        </div>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </>
          )}
        </Card>
      )}
    </div>
  );
}

function MetricBar({ label, value }) {
  const pct = Math.round((value || 0) * 100);
  return (
    <div className="metric-bar-row">
      <span>{label}</span>
      <div className="progress-bar" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100} aria-label={label}>
        <div className="progress-bar__fill" style={{ width: `${pct}%` }} />
      </div>
      <span className="value">{pct}%</span>
    </div>
  );
}
