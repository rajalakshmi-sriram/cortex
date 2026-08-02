import { useState, useEffect } from 'react';
import { useProject } from './Workspace';
import { CrudList } from '../components/CrudList';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { api } from '../api/client';
import { PageInstructions } from '../components/PageInstructions';
import { PAGE_TOOLS } from '../data/pageTools';

const FIELDS = [
  { key: 'name', label: 'Journal Name', kind: 'line' },
  { key: 'status', label: 'Status', kind: 'combo', options: ['target', 'submitted', 'under_review', 'revisions_requested', 'accepted', 'rejected'] },
  { key: 'notes', label: 'Notes', kind: 'multiline' },
];

function GuidelinesLookup() {
  const [name, setName] = useState('');
  const [guidelines, setGuidelines] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [knownJournals, setKnownJournals] = useState({});

  useEffect(() => {
    api.getJournalGuidelines('').then((d) => setKnownJournals(d.known_journals || {})).catch(() => {});
  }, []);

  async function lookup(e) {
    e.preventDefault();
    if (!name.trim()) return;
    setLoading(true);
    setError('');
    try {
      const data = await api.getJournalGuidelines(name.trim());
      setGuidelines(data.guidelines);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card
      title="Journal Submission Guidelines"
      hint="Look up a curated summary of common formatting/structure requirements. Always confirm current details on the journal's own author guidelines page before submitting."
      accent="sand"
    >
      <form onSubmit={lookup} style={{ display: 'flex', gap: 8 }}>
        <input
          type="text"
          list="known-journals"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Nature, JACS, eLife, BMJ..."
          aria-label="Journal name"
          style={{ flex: 1 }}
        />
        <datalist id="known-journals">
          {Object.values(knownJournals).map((label) => <option key={label} value={label} />)}
        </datalist>
        <Button type="submit" accent="sand" disabled={loading}>{loading ? 'Looking up…' : 'Look Up'}</Button>
      </form>
      {Object.keys(knownJournals).length > 0 && (
        <p style={{ fontSize: 11.5, color: 'var(--text-muted)', marginTop: 6 }}>
          {Object.keys(knownJournals).length} journals curated, spanning general science, chemistry, biology,
          clinical medicine, physics, and CS - start typing for suggestions, or look up any other journal for
          general guidance.
        </p>
      )}
      {error && <p role="alert" style={{ color: 'var(--accent1-text)' }}>{error}</p>}
      {guidelines && (
        <div style={{ marginTop: 14 }}>
          <div style={{ fontWeight: 700, fontSize: 14 }}>{guidelines.name}</div>
          <p style={{ marginTop: 8 }}><strong>Citation style:</strong> {guidelines.citation_style}</p>
          <p><strong>Word limit:</strong> {guidelines.word_limit}</p>
          <p><strong>Structure:</strong> {guidelines.structure}</p>
          <p style={{ color: 'var(--text-muted)' }}>{guidelines.notes}</p>
          {guidelines.homepage && (
            <a href={guidelines.homepage} target="_blank" rel="noreferrer">Official author guidelines &rarr;</a>
          )}
        </div>
      )}
    </Card>
  );
}

export function Journals() {
  const { project } = useProject();
  return (
    <div>
      <PageInstructions
        accent="sand"
        items={[
          'Add target journals with a status (target, submitted, under review, etc.) and notes to track your submission pipeline.',
          'Use "Journal Submission Guidelines" below to look up a curated summary of a journal\'s formatting/structure requirements — always confirm current details on the journal\'s own author guidelines page before submitting.',
        ]}
      />
      <CrudList
        projectId={project.id}
        resource="journals"
        title="Journals & Submissions"
        hint="Track target journals and submission status."
        accent="sand"
        fields={FIELDS}
        renderer={(j) => `${j.name || ''}\n[${j.status || ''}]`}
        tools={PAGE_TOOLS.journals}
      />
      <GuidelinesLookup />
    </div>
  );
}
