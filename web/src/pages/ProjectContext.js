import { createContext, useContext } from 'react';

/**
 * The project the workspace is currently showing, provided by Workspace and
 * read by every page under it.
 *
 * This lives in its own module on purpose. When a context is created in the
 * same file that exports components, React Fast Refresh recreates the context
 * object every time that file is hot-updated - but consumer modules that
 * weren't re-evaluated still hold the *old* context, so useContext falls
 * through to the default value and every page throws
 * "Cannot destructure property 'project' of 'useProject(...)' as it is null"
 * mid-edit. A module with no component exports isn't a refresh boundary, so
 * the context keeps its identity across hot updates.
 */
const ProjectContext = createContext(null);

export function useProject() {
  const value = useContext(ProjectContext);
  if (value === null) {
    throw new Error('useProject() must be used inside a <ProjectProvider> (i.e. within the Workspace route).');
  }
  return value;
}

export const ProjectProvider = ProjectContext.Provider;
