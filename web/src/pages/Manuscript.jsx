import { useState, useEffect } from 'react';
import { useProject } from './Workspace';
import { api } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { MicButton } from '../components/MicButton';
import { ToolChips } from '../components/ToolChips';
import { AiChatPanel } from '../components/AiChatPanel';
import { PageInstructions } from '../components/PageInstructions';
import { PAGE_TOOLS } from '../data/pageTools';

const SECTIONS = ['abstract', 'introduction', 'methods', 'results', 'discussion', 'references'];

export function Manuscript() {
  const { project } = useProject();
  const [sections, setSections] = useState(Object.fromEntries(SECTIONS.map((s) => [s, ''])));
  const [saveStatus, setSaveStatus] = useState('');

  useEffect(() => {
    api.getManuscript(project.id).then((d) => setSections((prev) => ({ ...prev, ...d.manuscript })));
  }, [project.id]);

  async function save() {
    setSaveStatus('Saving…');
    await api.updateManuscript(project.id, sections);
    setSaveStatus('Saved ✓');
  }

  const hasContent = Object.values(sections).some((v) => v && v.trim());

  return (
    <div>
      <PageInstructions
        accent="blue"
        items={[
          'Write each section of your manuscript below (use the mic button to dictate) and click Save Manuscript.',
          'Once you\'ve written some of your draft, click "Get AI Feedback on My Draft" in the AI Feedback section for reviewer-style feedback aimed at top-journal quality — then ask follow-up questions in the chat that appears.',
        ]}
      />
      <Card title="Manuscript Draft" hint="Draft each section of your manuscript. Saved to this project." accent="blue">
        {SECTIONS.map((section) => (
          <div key={section}>
            <label htmlFor={`section-${section}`} style={{ textTransform: 'capitalize' }}>{section}</label>
            <div style={{ display: 'flex', gap: 8 }}>
              <textarea
                id={`section-${section}`}
                value={sections[section] || ''}
                onChange={(e) => setSections({ ...sections, [section]: e.target.value })}
                placeholder={`Write your ${section}...`}
                style={{ flex: 1, minHeight: 90 }}
              />
              <MicButton label={section} onTranscript={(t) => setSections((prev) => ({ ...prev, [section]: prev[section] ? prev[section] + ' ' + t : t }))} />
            </div>
          </div>
        ))}

        <div style={{ marginTop: 14, display: 'flex', alignItems: 'center', gap: 12 }}>
          <Button accent="blue" onClick={save}>Save Manuscript</Button>
          {saveStatus && <span role="status">{saveStatus}</span>}
        </div>

        <div style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
          <label style={{ margin: 0 }}>Recommended Tools</label>
          <ToolChips tools={PAGE_TOOLS.manuscript} />
        </div>
      </Card>

      <Card
        title="AI Feedback"
        hint="Get constructive, journal-reviewer-style feedback on your draft, grounded only in what you've written — then ask follow-up questions."
        accent="blue"
      >
        <AiChatPanel
          contextType="manuscript_feedback"
          context={{ sections }}
          kickoffMessage="Please review my manuscript draft and give me constructive feedback to help it reach the quality bar of a good/top journal."
          triggerLabel="Get AI Feedback on My Draft"
          accent="blue"
          disabled={!hasContent}
          disabledReason="Write (and ideally save) some of your draft first."
        />
      </Card>
    </div>
  );
}
