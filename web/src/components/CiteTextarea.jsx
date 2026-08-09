import { useEffect, useRef, useState, useCallback } from 'react';
import { getCaretCoordinates, getMentionQuery } from '../utils/caret';
import './CiteTextarea.css';

const MAX_RESULTS = 8;

/**
 * A textarea that can cite.
 *
 * Type "@" to open a picker over your Paper Library; choosing a paper inserts
 * a marker like [@Smith2020]. Markers are plain text, so the draft stays
 * readable and portable - nothing here depends on a rich-text model.
 */
export function CiteTextarea({ value, onChange, entries = [], id, placeholder, style, ...rest }) {
  const textareaRef = useRef(null);
  const listRef = useRef(null);
  const [mention, setMention] = useState(null);   // { query, start }
  const [position, setPosition] = useState(null); // { top, left, height }
  const [activeIndex, setActiveIndex] = useState(0);

  const matches = mention
    ? entries
        .filter((e) => {
          const q = mention.query.trim().toLowerCase();
          if (!q) return true;
          return (
            e.key.toLowerCase().includes(q)
            || (e.title || '').toLowerCase().includes(q)
            || (e.authors || '').toLowerCase().includes(q)
            || String(e.year || '').includes(q)
          );
        })
        .slice(0, MAX_RESULTS)
    : [];

  const close = useCallback(() => {
    setMention(null);
    setPosition(null);
    setActiveIndex(0);
  }, []);

  function syncMention(el) {
    const found = getMentionQuery(el.value, el.selectionStart);
    if (!found) {
      close();
      return;
    }
    setMention(found);
    setPosition(getCaretCoordinates(el, el.selectionStart));
    setActiveIndex(0);
  }

  function handleChange(e) {
    onChange(e.target.value);
    syncMention(e.target);
  }

  function insert(entry) {
    const el = textareaRef.current;
    if (!el || !mention) return;

    const marker = `[@${entry.key}]`;
    const next = value.slice(0, mention.start) + marker + value.slice(el.selectionStart);
    onChange(next);
    close();

    // Put the caret after the inserted marker once React has re-rendered.
    const caret = mention.start + marker.length;
    requestAnimationFrame(() => {
      el.focus();
      el.setSelectionRange(caret, caret);
    });
  }

  function handleKeyDown(e) {
    if (!mention || matches.length === 0) {
      // Escape closes the picker even when nothing matched.
      if (e.key === 'Escape' && mention) close();
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((i) => (i + 1) % matches.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((i) => (i - 1 + matches.length) % matches.length);
    } else if (e.key === 'Enter' || e.key === 'Tab') {
      e.preventDefault();
      insert(matches[activeIndex]);
    } else if (e.key === 'Escape') {
      e.preventDefault();
      close();
    }
  }

  // Keep the highlighted row scrolled into view during keyboard navigation.
  useEffect(() => {
    listRef.current?.querySelector('[data-active="true"]')?.scrollIntoView({ block: 'nearest' });
  }, [activeIndex]);

  // The picker is positioned in viewport coordinates, so it has to close if
  // the page moves under it.
  useEffect(() => {
    if (!mention) return undefined;
    const onScrollOrResize = () => close();
    window.addEventListener('scroll', onScrollOrResize, true);
    window.addEventListener('resize', onScrollOrResize);
    return () => {
      window.removeEventListener('scroll', onScrollOrResize, true);
      window.removeEventListener('resize', onScrollOrResize);
    };
  }, [mention, close]);

  const open = mention && matches.length > 0 && position;

  return (
    <>
      <textarea
        {...rest}
        id={id}
        ref={textareaRef}
        value={value}
        placeholder={placeholder}
        style={style}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        onClick={(e) => syncMention(e.target)}
        onBlur={() => setTimeout(close, 150)}
        role="combobox"
        aria-expanded={!!open}
        aria-controls={open ? `${id}-cite-picker` : undefined}
        aria-autocomplete="list"
      />

      {open && (
        <div
          className="cite-picker"
          id={`${id}-cite-picker`}
          role="listbox"
          ref={listRef}
          style={{
            top: Math.min(position.top + position.height + 4, window.innerHeight - 260),
            left: Math.min(position.left, window.innerWidth - 380),
          }}
          onMouseDown={(e) => e.preventDefault()} // don't blur the textarea
        >
          <div className="cite-picker__hint">
            ↑↓ to choose · Enter to insert · Esc to dismiss
          </div>
          {matches.map((entry, i) => (
            <button
              key={entry.id}
              type="button"
              role="option"
              aria-selected={i === activeIndex}
              data-active={i === activeIndex}
              className={`cite-picker__item ${i === activeIndex ? 'cite-picker__item--active' : ''}`}
              onMouseEnter={() => setActiveIndex(i)}
              onClick={() => insert(entry)}
            >
              <span className="cite-picker__key">{entry.key}</span>
              <span className="cite-picker__title">{entry.title}</span>
              <span className="cite-picker__meta">{entry.authors} · {entry.year}</span>
            </button>
          ))}
        </div>
      )}

      {mention && matches.length === 0 && position && (
        <div
          className="cite-picker cite-picker--empty"
          style={{
            top: Math.min(position.top + position.height + 4, window.innerHeight - 90),
            left: Math.min(position.left, window.innerWidth - 380),
          }}
        >
          {entries.length === 0
            ? 'No papers in your library yet — save some from Literature Review, or import a .bib file.'
            : `No paper matches "${mention.query}".`}
        </div>
      )}
    </>
  );
}
