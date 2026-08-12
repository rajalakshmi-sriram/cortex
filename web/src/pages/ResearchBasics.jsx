import { useEffect, useState, useMemo } from 'react';
import { api } from '../api/client';
import { Card } from '../components/Card';
import { PageInstructions } from '../components/PageInstructions';
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

function Glossary({ terms, categories }) {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('All');

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return terms.filter((t) => {
      if (category !== 'All' && t.category !== category) return false;
      if (!q) return true;
      return t.term.toLowerCase().includes(q) || t.definition.toLowerCase().includes(q);
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
          'This is a short primer on how research works, written for a first project — how to pick a question you can finish, how to read papers without drowning, and how not to fool yourself with your own data.',
          'The Glossary tab defines the jargon in plain language. Search it whenever a paper or a page in Cortex uses a word you don\'t know.',
          <>Step-by-step guidance for <em>your</em> project lives on the <strong>Methodology</strong> page — every step there has a "How do I do this?" explainer.</>,
        ]}
      />

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
