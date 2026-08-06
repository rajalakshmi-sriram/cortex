import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { PageInstructions } from '../components/PageInstructions';
import { LegalNotice } from '../components/LegalNotice';
import './ProjectsHome.css';

export function ProjectsHome() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [researchTypes, setResearchTypes] = useState({});
  const [form, setForm] = useState({ title: '', research_area: '', research_type: 'experimental' });
  const [creating, setCreating] = useState(false);
  const [importing, setImporting] = useState(false);
  const [creatingSample, setCreatingSample] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    refresh();
    api.getResearchTypes().then((d) => setResearchTypes(d.types || {})).catch(() => {});
  }, []);

  const researchTypeEntries = Object.entries(researchTypes);

  async function refresh() {
    setLoading(true);
    try {
      const data = await api.listProjects();
      setProjects(data.projects || []);
      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(e) {
    e.preventDefault();
    if (!form.title.trim()) return;
    setCreating(true);
    try {
      const data = await api.createProject(form);
      navigate(`/projects/${data.project.id}`);
    } catch (e) {
      setError(e.message);
    } finally {
      setCreating(false);
    }
  }

  async function handleCreateSample() {
    setCreatingSample(true);
    setError('');
    try {
      const data = await api.createSampleProject();
      navigate(`/projects/${data.project.id}`);
    } catch (e) {
      setError(e.message);
    } finally {
      setCreatingSample(false);
    }
  }

  async function handleImport(e) {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;
    setImporting(true);
    setError('');
    try {
      const data = await api.importProject(file);
      navigate(`/projects/${data.project.id}`);
    } catch (e) {
      setError(`Import failed: ${e.message}`);
    } finally {
      setImporting(false);
    }
  }

  async function handleDelete(project) {
    if (!window.confirm(`Delete "${project.title}"? This permanently removes the project and everything in it (papers, datasets, manuscript, etc.) - it can't be undone unless you've exported a backup.`)) {
      return;
    }
    try {
      await api.deleteProject(project.id);
      refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div className="projects-home">
      <header className="projects-home__header">
        <h1 className="font-serif">Cortex</h1>
        <p>Your research workspace &mdash; every project you're running, in one place.</p>
      </header>

      <main id="main-content" className="projects-home__body">
        <PageInstructions
          accent="rose"
          items={[
            <><strong>New here?</strong> Fill in a title, research area, and research type below, then click Create Project — Cortex builds a matched methodology checklist automatically.</>,
            <><strong>Returning?</strong> Click any project under "Your Projects" to open its workspace.</>,
            <>Each project has its own Literature Review, Data & Analysis, Manuscript, and other tabs. Optional AI features (feedback, interpretation, summaries) are available throughout — set up a free local model or your own API key via the sparkle icon in the bottom-right corner.</>,
          ]}
        />
        <Card title="Start a New Project" hint="Every project gets a methodology checklist matched to its research type." accent="rose">
          <form onSubmit={handleCreate} className="projects-home__form">
            <label htmlFor="new-title">Project title</label>
            <input
              id="new-title"
              type="text"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="e.g. Enzyme Kinetics of Photosynthetic Carbon Fixation"
              required
            />

            <label htmlFor="new-area">Research area</label>
            <input
              id="new-area"
              type="text"
              value={form.research_area}
              onChange={(e) => setForm({ ...form, research_area: e.target.value })}
              placeholder="e.g. Biochemistry, Organic Chemistry, Molecular Biology..."
            />

            <label htmlFor="new-type">Research type</label>
            <select
              id="new-type"
              value={form.research_type}
              onChange={(e) => setForm({ ...form, research_type: e.target.value })}
            >
              {researchTypeEntries.map(([value, info]) => (
                <option key={value} value={value}>{info.name}</option>
              ))}
            </select>
            {researchTypes[form.research_type] && (
              <p className="projects-home__type-description">{researchTypes[form.research_type].description}</p>
            )}

            <Button type="submit" accent="rose" disabled={creating}>
              {creating ? 'Creating…' : 'Create Project'}
            </Button>
          </form>

          <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid var(--border)' }}>
            <p style={{ margin: '0 0 8px', fontSize: 13, color: 'var(--text-muted)' }}>
              New to Cortex? Try a pre-filled example project instead - papers, a hypothesis, a
              dataset, and a manuscript draft already in place, so you can see how everything fits
              together before starting your own.
            </p>
            <Button variant="secondary" accent="rose" onClick={handleCreateSample} disabled={creatingSample}>
              {creatingSample ? 'Creating…' : 'Try a Sample Project'}
            </Button>
          </div>
        </Card>

        <Card title="All Research Types" hint="Every research type gets its own methodology checklist and recommended reporting guidelines." accent="sand">
          <dl className="projects-home__type-list">
            {researchTypeEntries.map(([value, info]) => (
              <div key={value}>
                <dt>{info.name}</dt>
                <dd>{info.description}</dd>
              </div>
            ))}
          </dl>
        </Card>

        <Card title="Your Projects" accent="blue">
          <div className="projects-home__import-row">
            <label className="btn btn--secondary" style={{ '--btn-accent-tint': 'var(--accent3-tint)', '--btn-accent-text': 'var(--accent3-text)' }}>
              {importing ? 'Importing…' : 'Import Project (.zip)'}
              <input
                type="file"
                accept=".zip,application/zip"
                onChange={handleImport}
                disabled={importing}
                style={{ display: 'none' }}
              />
            </label>
            <span className="projects-home__import-hint">
              From a project exported elsewhere (Overview → Export Project)
            </span>
          </div>

          {loading && <p role="status">Loading projects&hellip;</p>}
          {error && <p role="alert" className="projects-home__error">{error}</p>}
          {!loading && projects.length === 0 && <p>No projects yet &mdash; create your first one above.</p>}

          <ul className="projects-home__list">
            {projects.map((p) => (
              <li key={p.id} className="projects-home__row">
                <button className="projects-home__project" onClick={() => navigate(`/projects/${p.id}`)}>
                  <span className="projects-home__project-title">{p.title}</span>
                  <span className="projects-home__project-meta">
                    {researchTypes[p.research_type]?.name || p.research_type}
                    {p.research_area ? ` · ${p.research_area}` : ''}
                  </span>
                </button>
                <Button variant="ghost" accent="rose" onClick={() => handleDelete(p)}>
                  Delete
                </Button>
              </li>
            ))}
          </ul>
        </Card>
      </main>
      <footer className="projects-home__footer">
        <LegalNotice />
      </footer>
    </div>
  );
}
