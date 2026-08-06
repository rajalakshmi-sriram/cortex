import { useEffect, useState } from 'react';
import { useProject } from './Workspace';
import { api } from '../api/client';
import { Card } from '../components/Card';
import { PageInstructions } from '../components/PageInstructions';

export function Overview() {
  const { project } = useProject();
  const [methodology, setMethodology] = useState(null);

  useEffect(() => {
    api.getMethodology(project.id).then((d) => setMethodology(d.methodology)).catch(() => {});
  }, [project.id]);

  return (
    <div>
      <PageInstructions
        accent="rose"
        items={[
          'This is a read-only snapshot of the project: its details, the specific focus you set in Project Search (once you have one), and methodology progress.',
          'To change anything here, use the relevant tab in the sidebar — Project Search for the research focus, Methodology for the checklist.',
        ]}
      />
      <Card title="Project Details" accent="rose" data-tour="overview-details">
        <dl className="overview-grid">
          <div><dt>Research area</dt><dd>{project.research_area || '—'}</dd></div>
          <div><dt>Institution</dt><dd>{project.institution || '—'}</dd></div>
          <div><dt>Status</dt><dd>{project.status}</dd></div>
          <div><dt>Citation style</dt><dd>{project.citation_style}</dd></div>
        </dl>
      </Card>

      {(project.specific_topic || project.specific_aims || (project.research_questions || []).length > 0) && (
        <Card title="Research Focus" hint="Set from the Project Search workflow." accent="sage">
          {project.specific_topic && (
            <p><strong>Specific topic:</strong> {project.specific_topic}</p>
          )}
          {project.specific_aims && (
            <p><strong>Specific aims:</strong> {project.specific_aims}</p>
          )}
          {(project.research_questions || []).length > 0 && (
            <>
              <strong>Research questions:</strong>
              <ul>
                {project.research_questions.map((q, i) => <li key={i}>{q}</li>)}
              </ul>
            </>
          )}
        </Card>
      )}

      {methodology && (
        <Card title="Methodology Progress" accent="blue">
          <p>
            {methodology.research_type_name} &mdash; {methodology.completed_count} / {methodology.total_steps} steps completed
          </p>
          <div className="progress-bar" role="progressbar"
            aria-valuenow={methodology.completed_count} aria-valuemin={0} aria-valuemax={methodology.total_steps}
            aria-label="Methodology progress">
            <div className="progress-bar__fill" style={{ width: `${(methodology.completed_count / methodology.total_steps) * 100}%` }} />
          </div>
        </Card>
      )}

      <Card title="Backup & Sharing" hint="Download everything in this project - details, papers, datasets, manuscript, and progress - as one file." accent="sand">
        <a className="btn btn--secondary" style={{ '--btn-accent-tint': 'var(--accent4-tint)', '--btn-accent-text': 'var(--accent4-text)' }}
          href={api.exportProjectUrl(project.id)} download>
          Export Project (.zip)
        </a>
        <p style={{ marginTop: 10 }}>
          To bring it into another Cortex instance (a co-author's, or after
          reinstalling), use <strong>Import Project</strong> on the "All
          Projects" screen.
        </p>
      </Card>
    </div>
  );
}
