import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import { Card } from './Card';
import { Button } from './Button';
import { ToolChips } from './ToolChips';

/**
 * A reusable "add form + list + delete" card bound to a project sub-resource
 * (hypotheses, tasks, journals, ...). Mirrors the desktop app's CrudListTab.
 */
export function CrudList({ projectId, resource, title, hint, accent, fields, renderer, tools, extraForSelected }) {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(() => Object.fromEntries(fields.map((f) => [f.key, f.kind === 'combo' ? f.options[0] : ''])));
  const [selectedId, setSelectedId] = useState(null);
  const [error, setError] = useState('');

  const refresh = useCallback(async () => {
    if (!projectId) return;
    try {
      const data = await api.listCollection(projectId, resource);
      setItems(data[resource] || []);
    } catch (e) {
      setError(e.message);
    }
  }, [projectId, resource]);

  useEffect(() => { refresh(); }, [refresh]);

  async function addItem(e) {
    e.preventDefault();
    try {
      await api.addToCollection(projectId, resource, form);
      setForm(Object.fromEntries(fields.map((f) => [f.key, f.kind === 'combo' ? f.options[0] : ''])));
      refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  async function deleteSelected() {
    if (!selectedId) return;
    await api.deleteFromCollection(projectId, resource, selectedId);
    setSelectedId(null);
    refresh();
  }

  const selectedItem = items.find((item) => item.id === selectedId);

  return (
    <div>
      <Card title={title} hint={hint} accent={accent}>
        <form onSubmit={addItem}>
          {fields.map((f) => (
            <div key={f.key}>
              <label htmlFor={`${resource}-${f.key}`}>{f.label}</label>
              {f.kind === 'combo' ? (
                <select
                  id={`${resource}-${f.key}`}
                  value={form[f.key]}
                  onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
                >
                  {f.options.map((opt) => <option key={opt} value={opt}>{opt}</option>)}
                </select>
              ) : f.kind === 'multiline' ? (
                <textarea
                  id={`${resource}-${f.key}`}
                  value={form[f.key]}
                  onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
                  placeholder={f.placeholder}
                />
              ) : (
                <input
                  id={`${resource}-${f.key}`}
                  type="text"
                  value={form[f.key]}
                  onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
                  placeholder={f.placeholder}
                />
              )}
            </div>
          ))}
          <div style={{ marginTop: 14 }}>
            <Button type="submit" accent={accent}>Add</Button>
          </div>
          {error && <p role="alert" style={{ color: 'var(--accent1-text)' }}>{error}</p>}
        </form>

        {tools && (
          <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid var(--border)' }}>
            <label style={{ margin: 0 }}>Recommended Tools</label>
            <ToolChips tools={tools} />
          </div>
        )}
      </Card>

      <Card title="Saved Entries" accent={accent}>
        {items.length === 0 && <p style={{ color: 'var(--text-muted)' }}>Nothing here yet.</p>}
        <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 8 }}>
          {items.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => setSelectedId(item.id === selectedId ? null : item.id)}
                style={{
                  width: '100%', textAlign: 'left', cursor: 'pointer',
                  background: item.id === selectedId ? 'var(--accent1-tint)' : 'var(--surface-alt)',
                  border: `1px solid ${item.id === selectedId ? 'var(--accent1-text)' : 'var(--border)'}`,
                  borderRadius: 10, padding: '10px 12px', whiteSpace: 'pre-line', fontSize: 13,
                }}
              >
                {renderer(item)}
              </button>
            </li>
          ))}
        </ul>
        {selectedId && (
          <div style={{ marginTop: 12 }}>
            <Button variant="ghost" accent="rose" onClick={deleteSelected}>Delete Selected</Button>
          </div>
        )}
      </Card>

      {selectedItem && extraForSelected && (
        <Card title="AI Feedback" accent={accent}>
          {extraForSelected(selectedItem)}
        </Card>
      )}
    </div>
  );
}
