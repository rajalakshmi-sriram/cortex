import { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { initExternalLinkHandler } from './utils/externalLinks';
import { PalettePicker } from './components/PalettePicker';
import { AiSettings } from './components/AiSettings';
import { LiteratureSettings } from './components/LiteratureSettings';
import { ProjectsHome } from './pages/ProjectsHome';
import { Workspace } from './pages/Workspace';
import { Overview } from './pages/Overview';
import { ProjectSearch } from './pages/ProjectSearch';
import { LiteratureReview } from './pages/LiteratureReview';
import { PaperLibrary } from './pages/PaperLibrary';
import { Methodology } from './pages/Methodology';
import { Hypotheses } from './pages/Hypotheses';
import { Tasks } from './pages/Tasks';
import { DataAnalysis } from './pages/DataAnalysis';
import { Manuscript } from './pages/Manuscript';
import { Journals } from './pages/Journals';

export default function App() {
  useEffect(() => { initExternalLinkHandler(); }, []);

  return (
    <>
      <a href="#main-content" className="skip-link">Skip to main content</a>
      <Routes>
        <Route path="/" element={<ProjectsHome />} />
        <Route path="/projects/:projectId" element={<Workspace />}>
          <Route index element={<Overview />} />
          <Route path="project-search" element={<ProjectSearch />} />
          <Route path="literature-review" element={<LiteratureReview />} />
          <Route path="paper-library" element={<PaperLibrary />} />
          <Route path="methodology" element={<Methodology />} />
          <Route path="hypotheses" element={<Hypotheses />} />
          <Route path="tasks" element={<Tasks />} />
          <Route path="data-analysis" element={<DataAnalysis />} />
          <Route path="manuscript" element={<Manuscript />} />
          <Route path="journals" element={<Journals />} />
        </Route>
      </Routes>
      <PalettePicker />
      <AiSettings />
      <LiteratureSettings />
    </>
  );
}
