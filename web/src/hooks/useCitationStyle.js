import { useCallback, useState, useEffect } from 'react';
import { api } from '../api/client';

export const CITATION_STYLES = [
  ['apa', 'APA'],
  ['mla', 'MLA'],
  ['chicago', 'Chicago'],
  ['vancouver', 'Vancouver'],
];

/**
 * The project's citation style, shared by every page that formats a citation.
 *
 * Stored on the project itself rather than per-page, so Paper Library, the
 * Manuscript reference panel and the auto-built reference list can't disagree
 * about what style you're writing in - and the choice survives a reload.
 */
export function useCitationStyle(project, refreshProject) {
  const saved = (project?.citation_style || 'apa').toLowerCase();
  const [style, setStyleState] = useState(saved);

  // Follow the project if it changes underneath us (switching projects, or
  // the other page saving a different style).
  useEffect(() => { setStyleState(saved); }, [saved]);

  const setStyle = useCallback(async (next) => {
    setStyleState(next);  // optimistic: the dropdown shouldn't lag the request
    try {
      await api.updateProject(project.id, { citation_style: next });
      await refreshProject?.();
    } catch {
      setStyleState(saved);  // put it back if the save failed
    }
  }, [project?.id, refreshProject, saved]);

  return { style, setStyle };
}
