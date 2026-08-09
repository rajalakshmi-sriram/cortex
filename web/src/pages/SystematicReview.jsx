import { useEffect, useState, useCallback } from 'react';
import { useProject } from './Workspace';
import { api } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { PageInstructions } from '../components/PageInstructions';
import { PrismaDiagram } from '../components/PrismaDiagram';
import './SystematicReview.css';

const STAGE_LABEL = {
  title_abstract: 'Title & abstract',
  full_text: 'Full text',
};

/** Papers waiting for a decision at the given stage. */
function pending(papers, stage) {
  return papers.filter((p) => p.screening.stage === stage && p.screening.decision === 'pending');
}

function decided(papers) {
  return papers.filter((p) => p.screening.decision !== 'pending');
}

function ScreeningCard({ paper, reasons, onDecide, busy }) {
  const [reason, setReason] = useState(reasons[0] || 'Other');
  const [customReason, setCustomReason] = useState('');
  const [showExclude, setShowExclude] = useState(false);

  const stage = paper.screening.stage;
  const finalReason = reason === 'Other' ? (customReason.trim() || 'Other') : reason;

  return (
    <div className="screen-card">
      <div className="screen-card__stage">{STAGE_LABEL[stage]}</div>
      <h3 className="screen-card__title">{paper.title}</h3>
      <p className="screen-card__meta">
        {paper.authors || 'Unknown authors'} · {paper.year || 'n.d.'}
        {paper.source && <> · <span className="source-tag">{paper.source}</span></>}
      </p>

      {paper.abstract ? (
        <p className="screen-card__abstract">{paper.abstract}</p>
      ) : (
        <p className="screen-card__abstract screen-card__abstract--none">
          No abstract available — open the paper to judge it.
        </p>
      )}

      {(paper.url || paper.doi) && (
        <a
          className="screen-card__link"
          href={paper.url || `https://doi.org/${paper.doi}`}
          target="_blank"
          rel="noreferrer"
        >
          Open full paper ↗
        </a>
      )}

      {!showExclude ? (
        <div className="screen-card__actions">
          <Button accent="sage" disabled={busy} onClick={() => onDecide(paper.id, 'include')}>
            {stage === 'title_abstract' ? '✓ Include — get full text' : '✓ Include in review'}
          </Button>
          <Button variant="secondary" accent="rose" disabled={busy} onClick={() => setShowExclude(true)}>
            ✕ Exclude
          </Button>
        </div>
      ) : (
        <div className="screen-card__exclude">
          <label htmlFor={`reason-${paper.id}`}>Reason for exclusion</label>
          <select id={`reason-${paper.id}`} value={reason} onChange={(e) => setReason(e.target.value)}>
            {reasons.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
          {reason === 'Other' && (
            <input
              type="text"
              value={customReason}
              onChange={(e) => setCustomReason(e.target.value)}
              placeholder="Describe the reason…"
              aria-label="Custom exclusion reason"
            />
          )}
          <p className="screen-card__note">
            {stage === 'full_text'
              ? 'PRISMA requires a reason for every full-text exclusion — these are totalled in the diagram.'
              : 'Optional at this stage, but useful for your audit trail.'}
          </p>
          <div className="screen-card__actions">
            <Button accent="rose" disabled={busy} onClick={() => onDecide(paper.id, 'exclude', finalReason)}>
              Confirm exclusion
            </Button>
            <Button variant="ghost" accent="sage" disabled={busy} onClick={() => setShowExclude(false)}>
              Cancel
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export function SystematicReview() {
  const { project } = useProject();
  const [data, setData] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [savedNote, setSavedNote] = useState('');
  const [tab, setTab] = useState('screen');

  const refresh = useCallback(async () => {
    try {
      const d = await api.getScreening(project.id);
      setData(d);
      setError('');
    } catch (e) {
      setError(e.message);
    }
  }, [project.id]);

  useEffect(() => { refresh(); }, [refresh]);

  async function decide(paperId, decision, reason = '') {
    setBusy(true);
    try {
      await api.screenPaper(project.id, paperId, { decision, reason });
      await refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function saveState(patch) {
    try {
      await api.updateScreening(project.id, patch);
      await refresh();
      setSavedNote('Saved ✓');
      setTimeout(() => setSavedNote(''), 2000);
    } catch (e) {
      setError(e.message);
    }
  }

  if (error && !data) return <p role="alert">{error}</p>;
  if (!data) return <p role="status">Loading screening…</p>;

  const papers = data.papers || [];
  const taQueue = pending(papers, 'title_abstract');
  const ftQueue = pending(papers, 'full_text');
  const done = decided(papers);
  const current = taQueue[0] || ftQueue[0] || null;

  return (
    <div>
      <PageInstructions
        accent="sage"
        items={[
          'Systematic review mode screens every paper in your library in two passes — title/abstract first, then full text — and records a reason for each exclusion.',
          'Decisions build the PRISMA flow diagram below automatically. Download it as an SVG for your manuscript.',
          'Papers get here from Literature Review or by importing a .bib/.ris file in Paper Library. Screen them here rather than deleting them, so the numbers stay auditable.',
        ]}
      />

      <div className="review__tabs" role="tablist">
        {[['screen', `Screening${taQueue.length + ftQueue.length > 0 ? ` (${taQueue.length + ftQueue.length})` : ''}`],
          ['prisma', 'PRISMA diagram'],
          ['protocol', 'Protocol & counts'],
          ['decided', `Decided (${done.length})`]].map(([key, label]) => (
          <button
            key={key}
            role="tab"
            aria-selected={tab === key}
            className={`review__tab ${tab === key ? 'review__tab--active' : ''}`}
            onClick={() => setTab(key)}
          >
            {label}
          </button>
        ))}
      </div>

      {error && <p role="alert" className="review__error">{error}</p>}

      {tab === 'screen' && (
        <Card
          title="Screening Queue"
          hint="One paper at a time, in two passes. Including at title/abstract promotes the paper to full-text review rather than finishing it."
          accent="sage"
          data-tour="screening-queue"
        >
          <div className="review__progress">
            <span><strong>{taQueue.length}</strong> awaiting title/abstract</span>
            <span><strong>{ftQueue.length}</strong> awaiting full text</span>
            <span><strong>{data.prisma.studies_included}</strong> included so far</span>
          </div>

          {papers.length === 0 ? (
            <p>
              No papers in this project yet. Add some from Literature Review, or import a
              reference-manager export in Paper Library.
            </p>
          ) : current ? (
            <ScreeningCard
              key={current.id}
              paper={current}
              reasons={data.exclusion_reasons}
              onDecide={decide}
              busy={busy}
            />
          ) : (
            <p className="review__done">
              ✓ Every paper has been screened. {data.prisma.studies_included} stud
              {data.prisma.studies_included === 1 ? 'y is' : 'ies are'} included — see the PRISMA tab
              for the flow diagram.
            </p>
          )}
        </Card>
      )}

      {tab === 'prisma' && (
        <Card
          title="PRISMA 2020 Flow Diagram"
          hint="Generated from your screening decisions. Numbers the library can't know (duplicates removed, reports not retrieved) come from the Protocol & counts tab."
          accent="sage"
          data-tour="prisma-diagram"
        >
          <PrismaDiagram prisma={data.prisma} />
        </Card>
      )}

      {tab === 'protocol' && (
        <>
          <Card title="Review Protocol" hint="Your review question and the criteria you're screening against — shown alongside each paper decision." accent="sage">
            <label htmlFor="review-question">Review question</label>
            <textarea
              id="review-question"
              defaultValue={data.screening.review_question}
              onBlur={(e) => saveState({ review_question: e.target.value })}
              placeholder="e.g. Does caffeine improve reaction time in healthy adults?"
              style={{ minHeight: 60 }}
            />
            <label htmlFor="inclusion">Inclusion criteria</label>
            <textarea
              id="inclusion"
              defaultValue={data.screening.inclusion_criteria}
              onBlur={(e) => saveState({ inclusion_criteria: e.target.value })}
              placeholder="Population, intervention, comparator, outcomes, study designs to include…"
              style={{ minHeight: 80 }}
            />
            <label htmlFor="exclusion">Exclusion criteria</label>
            <textarea
              id="exclusion"
              defaultValue={data.screening.exclusion_criteria}
              onBlur={(e) => saveState({ exclusion_criteria: e.target.value })}
              placeholder="What disqualifies a study from your review…"
              style={{ minHeight: 80 }}
            />
            {savedNote && <span role="status">{savedNote}</span>}
          </Card>

          <Card
            title="Counts Cortex Can't Know"
            hint="PRISMA boxes that don't come from your library — duplicates your reference manager removed before import, records dropped by automation, reports you couldn't obtain."
            accent="sand"
          >
            <div className="review__counts">
              {data.manual_count_fields.map((field) => (
                <div key={field.key}>
                  <label htmlFor={`count-${field.key}`}>{field.label}</label>
                  <input
                    id={`count-${field.key}`}
                    type="number"
                    min="0"
                    defaultValue={data.screening.counts?.[field.key] ?? 0}
                    onBlur={(e) => saveState({ counts: { [field.key]: Number(e.target.value) || 0 } })}
                  />
                </div>
              ))}
            </div>
          </Card>
        </>
      )}

      {tab === 'decided' && (
        <Card title="Decisions So Far" hint="Every screened paper and why. Reset one to send it back to the start of screening." accent="sage">
          {done.length === 0 ? (
            <p>Nothing screened yet.</p>
          ) : (
            <ul className="review__decided">
              {done.map((p) => (
                <li key={p.id} className={`review__decided-item review__decided-item--${p.screening.decision}`}>
                  <div>
                    <span className={`review__badge review__badge--${p.screening.decision}`}>
                      {p.screening.decision === 'include' ? 'Included' : 'Excluded'}
                    </span>
                    <span className="review__decided-stage">{STAGE_LABEL[p.screening.stage]}</span>
                  </div>
                  <div className="review__decided-title">{p.title}</div>
                  <div className="review__decided-meta">
                    {p.authors} · {p.year}
                    {p.screening.reason && <> — <em>{p.screening.reason}</em></>}
                  </div>
                  <Button variant="ghost" accent="sage" onClick={() => decide(p.id, 'reset')} disabled={busy}>
                    Re-screen
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </Card>
      )}
    </div>
  );
}
