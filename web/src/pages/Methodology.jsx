import { useState, useEffect, useCallback } from 'react';
import { useProject } from './Workspace';
import { api } from '../api/client';
import { Card } from '../components/Card';
import { ToolChips } from '../components/ToolChips';
import { PageInstructions } from '../components/PageInstructions';

export function Methodology() {
  const { project } = useProject();
  const [methodology, setMethodology] = useState(null);
  const [error, setError] = useState('');

  const refresh = useCallback(async () => {
    try {
      const data = await api.getMethodology(project.id);
      setMethodology(data.methodology);
    } catch (e) {
      setError(e.message);
    }
  }, [project.id]);

  useEffect(() => { refresh(); }, [refresh]);

  async function toggleStep(index, completed) {
    const data = await api.setMethodologyStep(project.id, index, completed);
    setMethodology(data.methodology);
  }

  async function addTool(index, name, url) {
    const data = await api.addMethodologyTool(project.id, index, name, url);
    setMethodology(data.methodology);
  }

  async function removeTool(index, toolId) {
    const data = await api.removeMethodologyTool(project.id, index, toolId);
    setMethodology(data.methodology);
  }

  if (error) return <p role="alert">{error}</p>;
  if (!methodology) return <p role="status">Loading methodology&hellip;</p>;

  return (
    <div>
      <PageInstructions
        accent="sage"
        items={[
          'This checklist is generated from your project\'s research type and doesn\'t change automatically — check off each step as you actually complete it.',
          'Each step has recommended tools; click "+ Add Tool" under any step to attach your own.',
          'If reporting guidelines exist for your research type, they appear above the checklist regardless of which step you\'re on.',
        ]}
      />
      {methodology.methodology_guidelines?.length > 0 && (
        <Card
          title="Methodology & Reporting Guidelines"
          hint={`Reporting standards and regulatory guidance for ${methodology.research_type_name}, independent of which step you're on.`}
          accent="blue"
        >
          <ToolChips tools={methodology.methodology_guidelines} />
        </Card>
      )}

      <Card
        title="Methodology Checklist"
        hint="The standard steps for this project's research type. Check off each step as you complete it."
        accent="sage"
        data-tour="methodology-checklist"
      >
        <p style={{ color: 'var(--text-muted)' }}>
          {methodology.research_type_name} &mdash; {methodology.completed_count} / {methodology.total_steps} steps completed
        </p>
        <div className="progress-bar" role="progressbar"
          aria-valuenow={methodology.completed_count} aria-valuemin={0} aria-valuemax={methodology.total_steps}
          aria-label="Methodology progress">
          <div className="progress-bar__fill" style={{ width: `${(methodology.completed_count / methodology.total_steps) * 100}%` }} />
        </div>

        <ol style={{ listStyle: 'none', margin: '16px 0 0', padding: 0, display: 'flex', flexDirection: 'column', gap: 14 }}>
          {methodology.steps.map((step) => (
            <li key={step.index} style={{ borderTop: step.index > 0 ? '1px solid var(--border)' : 'none', paddingTop: step.index > 0 ? 14 : 0 }}>
              <label style={{ display: 'flex', alignItems: 'flex-start', gap: 10, margin: 0, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={step.completed}
                  onChange={(e) => toggleStep(step.index, e.target.checked)}
                  style={{ marginTop: 3 }}
                />
                <span style={{ fontWeight: step.completed ? 400 : 600, color: step.completed ? 'var(--text-muted)' : 'var(--text)', textDecoration: step.completed ? 'line-through' : 'none' }}>
                  {step.index + 1}. {step.text}
                </span>
              </label>
              <div style={{ marginLeft: 28, marginTop: 6 }}>
                <ToolChips
                  tools={step.recommended_tools}
                  customTools={step.custom_tools}
                  onRemove={(toolId) => removeTool(step.index, toolId)}
                  onAdd={(name, url) => addTool(step.index, name, url)}
                />
              </div>
            </li>
          ))}
        </ol>
      </Card>
    </div>
  );
}
