import { useRef, useState } from 'react';
import { api } from '../api/client';
import { Card } from '../components/Card';
import './ReferenceImport.css';

/**
 * Drop zone for a .bib/.ris export from Zotero, Mendeley, EndNote, etc.
 *
 * Papers already in the library (matched by DOI or title) are skipped rather
 * than duplicated, so re-importing an updated export from the same manager is
 * safe and is in fact the expected way to keep the two in step.
 */
export function ReferenceImport({ projectId, onImported }) {
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  async function handleFile(file) {
    if (!file) return;
    setBusy(true);
    setError('');
    setResult(null);
    try {
      const data = await api.importReferences(projectId, file);
      setResult(data);
      if (data.imported > 0) onImported?.();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  function onDrop(e) {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files?.[0]);
  }

  return (
    <Card
      title="Import from a Reference Manager"
      hint="Export your library as .bib or .ris from Zotero, Mendeley, EndNote or Papers, then drop it here."
      accent="blue"
      data-tour="reference-import"
    >
      <div
        className={`ref-import__zone ${dragging ? 'ref-import__zone--active' : ''} ${busy ? 'ref-import__zone--busy' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => !busy && inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            if (!busy) inputRef.current?.click();
          }
        }}
        role="button"
        tabIndex={0}
        aria-label="Import references: drop a .bib or .ris file here, or press Enter to choose a file"
      >
        <span className="ref-import__icon" aria-hidden="true">⤓</span>
        <span className="ref-import__label">
          {busy ? 'Reading your library…' : 'Drop a .bib or .ris file here'}
        </span>
        <span className="ref-import__sub">
          {busy ? '' : 'or click to choose a file'}
        </span>
        <input
          ref={inputRef}
          type="file"
          accept=".bib,.bibtex,.ris,.nbib,.enw,text/plain"
          style={{ display: 'none' }}
          onChange={(e) => { const f = e.target.files?.[0]; e.target.value = ''; handleFile(f); }}
        />
      </div>

      {error && <p role="alert" className="ref-import__error">{error}</p>}

      {result && (
        <div className="ref-import__result" role="status">
          <p className="ref-import__headline">
            {result.imported > 0
              ? `Imported ${result.imported} paper${result.imported === 1 ? '' : 's'} from your ${result.format.toUpperCase()} file.`
              : 'Nothing new to import — everything in that file is already in your library.'}
          </p>
          {result.skipped > 0 && (
            <details className="ref-import__skipped">
              <summary>
                Skipped {result.skipped} already in your library
              </summary>
              <ul>
                {result.skipped_titles.map((t, i) => <li key={i}>{t}</li>)}
                {result.skipped > result.skipped_titles.length && (
                  <li>…and {result.skipped - result.skipped_titles.length} more</li>
                )}
              </ul>
            </details>
          )}
        </div>
      )}

      <p className="ref-import__how">
        <strong>Finding the export:</strong> Zotero → right-click a collection → Export
        Collection. Mendeley → File → Export. EndNote → File → Export → RIS.
      </p>
    </Card>
  );
}
