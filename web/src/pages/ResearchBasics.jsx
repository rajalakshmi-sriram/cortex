import { useEffect, useState, useMemo } from 'react';
import { api } from '../api/client';
import { Card } from '../components/Card';
import { PageInstructions } from '../components/PageInstructions';
import { GuidanceDisclaimer } from '../components/GuidanceDisclaimer';
import './ResearchBasics.css';

function Primer({ sections }) {
  return (
    <>
      {sections.map((section) => (
        <Card key={section.id} title={section.title} accent="sage">
          {section.body.map((para, i) => (
            <p key={i} className="basics__para">{para}</p>
          ))}
        </Card>
      ))}
    </>
  );
}

/**
 * Strip punctuation for matching, so someone typing "preregistration",
 * "p value" or "meta analysis" finds the entries filed as
 * "Pre-registration", "p-value" and "Meta-analysis". Mirrors _search_key()
 * in app/research_guide.py, which does the same for the API.
 */
const searchKey = (text) => (text || '').toLowerCase().replace(/[\s\-/]+/g, '');

function Glossary({ terms, categories }) {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('All');

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const qKey = searchKey(q);
    return terms.filter((t) => {
      if (category !== 'All' && t.category !== category) return false;
      if (!q) return true;
      const haystack = `${t.term} ${t.definition}`;
      return haystack.toLowerCase().includes(q) || searchKey(haystack).includes(qKey);
    });
  }, [terms, query, category]);

  return (
    <Card
      title="Glossary"
      hint="The jargon you'll hit in the first month, in plain language."
      accent="sand"
      data-tour="glossary"
    >
      <div className="basics__filters">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search terms and definitions…"
          aria-label="Search glossary"
          className="basics__search"
        />
        <div className="basics__cats" role="group" aria-label="Filter by category">
          {['All', ...categories].map((c) => (
            <button
              key={c}
              type="button"
              className={`basics__cat ${category === c ? 'basics__cat--active' : ''}`}
              aria-pressed={category === c}
              onClick={() => setCategory(c)}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <p className="basics__count">
        {filtered.length} of {terms.length} terms
      </p>

      {filtered.length === 0 ? (
        <p>No terms match that search.</p>
      ) : (
        <dl className="basics__glossary">
          {filtered.map((t) => (
            <div key={t.term} className="basics__entry">
              <dt>
                {t.term}
                <span className="basics__tag">{t.category}</span>
              </dt>
              <dd>{t.definition}</dd>
            </div>
          ))}
        </dl>
      )}
    </Card>
  );
}

export function ResearchBasics() {
  const [sections, setSections] = useState(null);
  const [glossary, setGlossary] = useState(null);
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState('');
  const [tab, setTab] = useState('primer');

  useEffect(() => {
    Promise.all([api.getGuideBasics(), api.getGlossary()])
      .then(([b, g]) => {
        setSections(b.sections || []);
        setGlossary(g.terms || []);
        setCategories(g.categories || []);
      })
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <p role="alert">{error}</p>;
  if (!sections || !glossary) return <p role="status">Loading guide&hellip;</p>;

  return (
    <div>
      <PageInstructions
        accent="sage"
        items={[
          'A primer on how research works, written for a first project.',
          'The Glossary tab defines the jargon. Search it when a paper uses a term you don\'t know.',
          <>Guidance for <em>your</em> specific project is on the <strong>Methodology</strong> page.</>,
        ]}
      />

      <GuidanceDisclaimer />

      <div className="basics__tabs" role="tablist">
        {[['primer', 'Research Basics'], ['glossary', `Glossary (${glossary.length})`]].map(([key, label]) => (
          <button
            key={key}
            role="tab"
            aria-selected={tab === key}
            className={`basics__tab ${tab === key ? 'basics__tab--active' : ''}`}
            onClick={() => setTab(key)}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'primer'
        ? <Primer sections={sections} />
        : <Glossary terms={glossary} categories={categories} />}
    </div>
  );
}
