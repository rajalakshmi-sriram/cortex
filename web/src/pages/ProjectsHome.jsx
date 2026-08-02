import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { PageInstructions } from '../components/PageInstructions';
import { LegalNotice } from '../components/LegalNotice';
import './ProjectsHome.css';

const RESEARCH_TYPES = [
  ['theoretical', 'Theoretical Research'],
  ['experimental', 'Experimental Research'],
  ['exploratory', 'Exploratory Research'],
  ['pilot', 'Pilot Research'],
  ['literature_review', 'Literature Review'],
  ['clinical', 'Clinical Research'],
];

export function ProjectsHome() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ title: '', research_area: '', research_type: 'experimental' });
  const [creating, setCreating] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    refresh();
  }, []);

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
              {RESEARCH_TYPES.map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>

            <Button type="submit" accent="rose" disabled={creating}>
              {creating ? 'Creating…' : 'Create Project'}
            </Button>
          </form>
        </Card>

        <Card title="Your Projects" accent="blue">
          {loading && <p role="status">Loading projects&hellip;</p>}
          {error && <p role="alert" className="projects-home__error">{error}</p>}
          {!loading && projects.length === 0 && <p>No projects yet &mdash; create your first one above.</p>}

          <ul className="projects-home__list">
            {projects.map((p) => (
              <li key={p.id}>
                <button className="projects-home__project" onClick={() => navigate(`/projects/${p.id}`)}>
                  <span className="projects-home__project-title">{p.title}</span>
                  <span className="projects-home__project-meta">
                    {RESEARCH_TYPES.find(([v]) => v === p.research_type)?.[1] || p.research_type}
                    {p.research_area ? ` · ${p.research_area}` : ''}
                  </span>
                </button>
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
