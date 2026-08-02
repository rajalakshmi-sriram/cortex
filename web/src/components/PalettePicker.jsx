import { useState, useRef, useEffect } from 'react';
import { useTheme } from '../theme/ThemeContext';
import './PalettePicker.css';

const MODE_OPTIONS = [
  { value: 'auto', label: 'Auto' },
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
];

export function PalettePicker() {
  const { paletteKey, setPaletteKey, palettes, paletteKeys, mode, modeOverride, setModeOverride } = useTheme();
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    function onClickOutside(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) setOpen(false);
    }
    function onKey(e) {
      if (e.key === 'Escape') setOpen(false);
    }
    document.addEventListener('mousedown', onClickOutside);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onClickOutside);
      document.removeEventListener('keydown', onKey);
    };
  }, []);

  return (
    <div className="palette-picker" ref={containerRef}>
      {open && (
        <div className="palette-picker__panel">
          <div className="palette-picker__section-label" id="mode-label">Appearance</div>
          <div className="palette-picker__mode-toggle" role="radiogroup" aria-labelledby="mode-label">
            {MODE_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                role="radio"
                aria-checked={modeOverride === opt.value}
                className={`palette-picker__mode-btn ${modeOverride === opt.value ? 'palette-picker__mode-btn--selected' : ''}`}
                onClick={() => setModeOverride(opt.value)}
              >
                {opt.label}
              </button>
            ))}
          </div>
          <div className="palette-picker__mode-note">
            {modeOverride === 'auto'
              ? <>Currently <strong>{mode}</strong> mode &middot; follows time of day</>
              : <>Pinned to <strong>{mode}</strong> mode</>}
          </div>

          <div className="palette-picker__section-label" id="palette-label">Palette</div>
          <div role="radiogroup" aria-labelledby="palette-label">
            {paletteKeys.map((key) => (
              <button
                key={key}
                role="radio"
                aria-checked={key === paletteKey}
                className={`palette-picker__option ${key === paletteKey ? 'palette-picker__option--selected' : ''}`}
                onClick={() => setPaletteKey(key)}
              >
                <span className="palette-picker__swatch" style={{ background: palettes[key].swatch }} aria-hidden="true" />
                {palettes[key].label}
                {key === paletteKey && <span aria-hidden="true">&#10003;</span>}
              </button>
            ))}
          </div>
        </div>
      )}
      <button
        className="palette-picker__trigger"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="true"
        aria-expanded={open}
        aria-label="Choose appearance and color palette"
      >
        <span className="palette-picker__swatch" style={{ background: palettes[paletteKey].swatch }} aria-hidden="true" />
      </button>
    </div>
  );
}
