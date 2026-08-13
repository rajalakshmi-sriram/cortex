import { useCallback, useEffect, useState } from 'react';

const KEY = 'cortex_guidance_level';
const EVENT = 'cortex-guidance-level-change';

/**
 * Whether to show step guidance expanded by default.
 *
 * Defaults to 'concise': the checklist is the primary thing on the page, and
 * eleven expanded explainers bury it. Guidance stays one click away per step,
 * and switching to 'guided' opens it everywhere.
 *
 * Stored in localStorage and broadcast, so every mounted component agrees
 * without threading a context through the whole tree.
 *
 * 'concise' - explanations collapsed, one click away (default)
 * 'guided'  - explanations open by default
 */
export function useGuidanceLevel() {
  const [level, setLevelState] = useState(() => localStorage.getItem(KEY) || 'concise');

  useEffect(() => {
    const sync = () => setLevelState(localStorage.getItem(KEY) || 'concise');
    window.addEventListener(EVENT, sync);
    // 'storage' only fires in *other* tabs, which is exactly what we want on
    // top of the same-tab custom event above.
    window.addEventListener('storage', sync);
    return () => {
      window.removeEventListener(EVENT, sync);
      window.removeEventListener('storage', sync);
    };
  }, []);

  const setLevel = useCallback((next) => {
    localStorage.setItem(KEY, next);
    setLevelState(next);
    window.dispatchEvent(new Event(EVENT));
  }, []);

  return { level, setLevel, guided: level === 'guided' };
}
