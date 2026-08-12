import { useCallback, useEffect, useState } from 'react';

const KEY = 'cortex_guidance_level';
const EVENT = 'cortex-guidance-level-change';

/**
 * Whether to show beginner guidance expanded by default.
 *
 * Defaults to 'guided' - the app is aimed first at people doing their first
 * project, and someone experienced only has to turn it off once. Stored in
 * localStorage and broadcast, so every mounted component agrees without
 * threading a context through the whole tree.
 *
 * 'guided'  - explanations open by default
 * 'concise' - explanations collapsed, still one click away
 */
export function useGuidanceLevel() {
  const [level, setLevelState] = useState(() => localStorage.getItem(KEY) || 'guided');

  useEffect(() => {
    const sync = () => setLevelState(localStorage.getItem(KEY) || 'guided');
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
