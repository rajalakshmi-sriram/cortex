import { useMemo, useState } from 'react';
import { Card } from './Card';
import { Button } from './Button';

/** Every [@key] marker in the text, in order of appearance. */
export function extractCitationKeys(text) {
  const keys = [];
  const pattern = /\[@([A-Za-z0-9_]+)\]/g;
  let match;
  while ((match = pattern.exec(text || '')) !== null) keys.push(match[1]);
  return keys;
}

/**
 * The reference list, derived live from what's actually cited in the draft.
 *
 * Deriving it rather than storing it means it can never drift out of step with
 * the text - delete a citation and the entry disappears, which is exactly the
 * bookkeeping people otherwise do by hand and get wrong.
 */
export function ReferenceList({ sections, entries, style, onInsertIntoReferences }) {
  const [copied, setCopied] = useState('');

  const { cited, unknown } = useMemo(() => {
    const used = new Set();
    Object.entries(sections || {}).forEach(([name, text]) => {
      // The references section is the output, not a source of citations.
      if (name === 'references') return;
      extractCitationKeys(text).forEach((k) => used.add(k));
    });

    const byKey = new Map(entries.map((e) => [e.key, e]));
    const found = [];
    const missing = [];
    used.forEach((key) => {
      const entry = byKey.get(key);
      if (entry) found.push(entry);
      else missing.push(key);
    });

    found.sort((a, b) => (a.reference || '').toLowerCase().localeCompare((b.reference || '').toLowerCase()));
    return { cited: found, unknown: missing.sort() };
  }, [sections, entries]);

  const plainText = cited.map((e) => e.reference).join('\n\n');

  async function copyAll() {
    try {
      await navigator.clipboard.writeText(plainText);
      setCopied('Copied ✓');
      setTimeout(() => setCopied(''), 2000);
    } catch {
      setCopied('Could not copy — select the list and copy manually');
    }
  }

  return (
    <Card
      title="References"
      hint={`Built automatically from the [@citations] in your draft, in ${style.toUpperCase()} style. Cite a paper and it appears here; remove the citation and it goes away.`}
      accent="blue"
      data-tour="reference-list"
    >
      {cited.length === 0 ? (
        <p className="cite-refs__empty">
          No citations yet. Type <strong>@</strong> anywhere in your draft to cite a paper from your library.
        </p>
      ) : (
        <>
          <p className="cite-refs__count">
            {cited.length} reference{cited.length === 1 ? '' : 's'} cited
          </p>
          <ul className="cite-refs__list">
            {cited.map((e) => (
              <li key={e.id} className="cite-refs__item">
                <span className="cite-refs__key">{e.key}</span>
                <span>{e.reference}</span>
              </li>
            ))}
          </ul>
        </>
      )}

      {unknown.length > 0 && (
        <div className="cite-refs__unknown" role="alert">
          <strong>{unknown.length} citation{unknown.length === 1 ? '' : 's'} not in your library:</strong>{' '}
          {unknown.map((k, i) => (
            <span key={k}>{i > 0 && ', '}<code>[@{k}]</code></span>
          ))}
          <br />
          These stay in your text but can't be turned into references — the paper may have been removed
          from the library, or the key mistyped.
        </div>
      )}

      {cited.length > 0 && (
        <div className="cite-refs__actions">
          <Button variant="secondary" accent="blue" onClick={copyAll}>Copy reference list</Button>
          <Button variant="ghost" accent="blue" onClick={() => onInsertIntoReferences(plainText)}>
            Write into References section
          </Button>
          {copied && <span role="status">{copied}</span>}
        </div>
      )}
    </Card>
  );
}
