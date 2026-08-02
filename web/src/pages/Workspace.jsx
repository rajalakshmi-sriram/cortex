import { useEffect, useState, createContext, useContext, useCallback } from 'react';
import { Outlet, useParams, useLocation } from 'react-router-dom';
import { api } from '../api/client';
import { Sidebar } from '../components/Sidebar';
import { LegalNotice } from '../components/LegalNotice';
import './Workspace.css';

const ProjectContext = createContext(null);
export function useProject() {
  return useContext(ProjectContext);
}

const NAV_ITEMS = [
  { to: '', end: true, label: 'Overview', accent: 'rose', icon: <HomeIcon /> },
  { to: 'project-search', label: 'Project Search', accent: 'sage', icon: <CompassIcon /> },
  { to: 'literature-review', label: 'Literature Review', accent: 'rose', icon: <BulbIcon /> },
  { to: 'paper-library', label: 'Paper Library', accent: 'sand', icon: <FolderIcon /> },
  { to: 'methodology', label: 'Methodology', accent: 'sage', icon: <CompassIcon /> },
  { to: 'hypotheses', label: 'Hypotheses', accent: 'rose', icon: <QuestionIcon /> },
  { to: 'tasks', label: 'Tasks', accent: 'sage', icon: <ChecklistIcon /> },
  { to: 'data-analysis', label: 'Data & Analysis', accent: 'blue', icon: <BarChartIcon /> },
  { to: 'manuscript', label: 'Manuscript', accent: 'blue', icon: <DocIcon /> },
  { to: 'journals', label: 'Journals', accent: 'sand', icon: <NewspaperIcon /> },
];

export function Workspace() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [error, setError] = useState('');
  const location = useLocation();

  const refresh = useCallback(async () => {
    try {
      const data = await api.getProject(projectId);
      setProject(data.project);
      setError('');
    } catch (e) {
      setError(e.message);
    }
  }, [projectId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const activeItem = NAV_ITEMS.find((item) =>
    item.end ? location.pathname === `/projects/${projectId}` : location.pathname.startsWith(`/projects/${projectId}/${item.to}`)
  ) || NAV_ITEMS[0];

  return (
    <div className="workspace">
      <Sidebar
        brand="Cortex"
        tagline="Research Workspace"
        backTo="/"
        backLabel="All Projects"
        items={NAV_ITEMS.map((item) => ({ ...item, to: `/projects/${projectId}/${item.to}` }))}
        footer={
          <>
            <div>v1.0.0 — Web</div>
            <LegalNotice />
          </>
        }
      />
      <div className="workspace__main">
        <header className="workspace__topbar">
          <div>
            <h1 className="font-serif">{activeItem.label}</h1>
            {project && <p>{project.title}</p>}
          </div>
        </header>
        <main id="main-content" className="workspace__content" tabIndex={-1}>
          {error && <p role="alert">{error}</p>}
          {project ? (
            <ProjectContext.Provider value={{ project, refresh }}>
              <Outlet />
            </ProjectContext.Provider>
          ) : (
            !error && <p role="status">Loading project&hellip;</p>
          )}
        </main>
      </div>
    </div>
  );
}

function HomeIcon() {
  return <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><path d="M4 11 12 4l8 7M6 10v9h12v-9" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" /></svg>;
}
function CompassIcon() {
  return <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="8.5" stroke="currentColor" strokeWidth="1.6" /><path d="M15 9 13 13 9 15 11 11Z" stroke="currentColor" strokeWidth="1.3" /></svg>;
}
function BulbIcon() {
  return <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><path d="M9 18h6M10 21h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" /><path d="M12 3a6.5 6.5 0 0 0-3.6 11.9c.5.35.9.9.9 1.5V17h5.4v-.6c0-.6.4-1.15.9-1.5A6.5 6.5 0 0 0 12 3Z" stroke="currentColor" strokeWidth="1.5" /></svg>;
}
function FolderIcon() {
  return <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><path d="M3 7a1 1 0 0 1 1-1h5l2 2h9a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1Z" stroke="currentColor" strokeWidth="1.5" /></svg>;
}
function QuestionIcon() {
  return <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.5" /><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.7.35-1 .8-1 1.7v.5M12 17h.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" /></svg>;
}
function ChecklistIcon() {
  return <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><path d="M4 6h2M4 12h2M4 18h2M9 6h11M9 12h11M9 18h11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" /></svg>;
}
function BarChartIcon() {
  return <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><path d="M5 20V10M12 20V4M19 20v-7" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" /></svg>;
}
function DocIcon() {
  return <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><path d="M6 3h9l4 4v14H6Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" /><path d="M9 12h7M9 16h7" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" /></svg>;
}
function NewspaperIcon() {
  return <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><path d="M4 5h13v14H6a2 2 0 0 1-2-2Z" stroke="currentColor" strokeWidth="1.5" /><path d="M17 9h3v9a1 1 0 0 1-1 1h-2" stroke="currentColor" strokeWidth="1.5" /></svg>;
}
