import { useState } from 'react';
import './PageInstructions.css';

const ACCENT_VAR = { rose: '1', sage: '2', blue: '3', sand: '4' };

/**
 * A short "how to use this page" callout shown at the top of every page.
 * Collapsible so it doesn't permanently eat space once a user knows the
 * page, but starts open since first-time use is the point of it.
 */
export function PageInstructions({ items, accent = 'sand' }) {
  const [open, setOpen] = useState(true);
  const accentNum = ACCENT_VAR[accent] || '4';

  return (
    <div className="page-instructions" style={{ '--pi-accent': `var(--accent${accentNum}-tint)`, '--pi-accent-text': `var(--accent${accentNum}-text)` }}>
      <button
        type="button"
        className="page-instructions__toggle"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
      >
        <span aria-hidden="true">💡</span>
        <span className="page-instructions__title">How to use this page</span>
        <span className="page-instructions__chevron" aria-hidden="true">{open ? '−' : '+'}</span>
      </button>
      {open && (
        <ul className="page-instructions__list">
          {items.map((item, i) => <li key={i}>{item}</li>)}
        </ul>
      )}
    </div>
  );
}
