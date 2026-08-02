import { useState } from 'react';
import { Button } from './Button';

/**
 * A wrapping row of external tool chips. `tools` are reference suggestions
 * (not removable); `customTools` are user-attached and removable via onRemove.
 * Pass onAdd to show a small inline "+ Add Tool" form.
 */
export function ToolChips({ tools = [], customTools = [], onRemove, onAdd }) {
  const [adding, setAdding] = useState(false);
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');

  function submitAdd(e) {
    e.preventDefault();
    if (!name.trim()) return;
    onAdd(name.trim(), url.trim());
    setName('');
    setUrl('');
    setAdding(false);
  }

  return (
    <div>
      <div className="chip-row">
        {tools.map((tool, i) => (
          <a
            key={`rec-${i}`}
            className="chip"
            href={tool.url || undefined}
            target="_blank"
            rel="noreferrer"
            title={tool.description}
            onClick={(e) => { if (!tool.url) e.preventDefault(); }}
          >
            {tool.name}
          </a>
        ))}
        {customTools.map((tool) => (
          <span key={tool.id} className="chip chip--custom" style={{ paddingRight: 4 }}>
            <a href={tool.url || undefined} target="_blank" rel="noreferrer" style={{ color: 'inherit', textDecoration: 'none' }}>
              {tool.name}
            </a>
            {onRemove && (
              <button
                type="button"
                onClick={() => onRemove(tool.id)}
                aria-label={`Remove ${tool.name}`}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', fontWeight: 700, padding: '0 2px' }}
              >
                &times;
              </button>
            )}
          </span>
        ))}
        {onAdd && !adding && (
          <button type="button" className="chip" onClick={() => setAdding(true)}>+ Add Tool</button>
        )}
      </div>
      {adding && (
        <form onSubmit={submitAdd} style={{ display: 'flex', gap: 6, marginTop: 8, alignItems: 'center' }}>
          <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Tool name" style={{ maxWidth: 160 }} />
          <input type="text" value={url} onChange={(e) => setUrl(e.target.value)} placeholder="URL (optional)" style={{ maxWidth: 220 }} />
          <Button type="submit" variant="secondary" accent="sand">Add</Button>
          <Button type="button" variant="ghost" accent="sand" onClick={() => setAdding(false)}>Cancel</Button>
        </form>
      )}
    </div>
  );
}
