import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { PALETTES, PALETTE_KEYS, isDaytimeNow } from './palettes';

const PALETTE_STORAGE_KEY = 'cortex-palette';
const MODE_OVERRIDE_STORAGE_KEY = 'cortex-mode-override';
const ThemeContext = createContext(null);

const toKebabCase = (key) => key.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase();

function applyThemeVars(paletteKey, mode) {
  const palette = PALETTES[paletteKey] || PALETTES.terracotta;
  const vars = palette[mode];
  const root = document.documentElement;
  Object.entries(vars).forEach(([key, value]) => {
    root.style.setProperty(`--${toKebabCase(key)}`, value);
  });
  root.setAttribute('data-mode', mode);
  root.setAttribute('data-palette', paletteKey);
}

export function ThemeProvider({ children }) {
  const [paletteKey, setPaletteKeyState] = useState(
    () => localStorage.getItem(PALETTE_STORAGE_KEY) || 'terracotta'
  );
  // 'auto' (default) follows time of day; 'light'/'dark' pin it regardless of time.
  const [modeOverride, setModeOverrideState] = useState(
    () => localStorage.getItem(MODE_OVERRIDE_STORAGE_KEY) || 'auto'
  );
  const [autoMode, setAutoMode] = useState(() => (isDaytimeNow() ? 'light' : 'dark'));

  // Time-based auto light/dark - only drives the resolved mode when
  // modeOverride is 'auto'. Re-checked every 5 minutes so a long-open tab
  // crosses the day/night boundary live without needing a refresh.
  useEffect(() => {
    const tick = () => setAutoMode(isDaytimeNow() ? 'light' : 'dark');
    tick();
    const interval = setInterval(tick, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const mode = modeOverride === 'auto' ? autoMode : modeOverride;

  useEffect(() => {
    applyThemeVars(paletteKey, mode);
  }, [paletteKey, mode]);

  const setPaletteKey = useCallback((key) => {
    if (!PALETTES[key]) return;
    localStorage.setItem(PALETTE_STORAGE_KEY, key);
    setPaletteKeyState(key);
  }, []);

  const setModeOverride = useCallback((value) => {
    if (!['auto', 'light', 'dark'].includes(value)) return;
    localStorage.setItem(MODE_OVERRIDE_STORAGE_KEY, value);
    setModeOverrideState(value);
  }, []);

  return (
    <ThemeContext.Provider
      value={{
        paletteKey, setPaletteKey,
        mode, modeOverride, setModeOverride,
        palettes: PALETTES, paletteKeys: PALETTE_KEYS,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
}
