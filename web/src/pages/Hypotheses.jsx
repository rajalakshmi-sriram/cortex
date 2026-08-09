import { useProject } from './ProjectContext';
import { CrudList } from '../components/CrudList';
import { AiChatPanel } from '../components/AiChatPanel';
import { PageInstructions } from '../components/PageInstructions';
import { PAGE_TOOLS } from '../data/pageTools';

const FIELDS = [
  { key: 'text', label: 'Hypothesis', kind: 'multiline' },
  { key: 'status', label: 'Status', kind: 'combo', options: ['proposed', 'supported', 'rejected', 'inconclusive'] },
];

export function Hypotheses() {
  const { project } = useProject();
  return (
    <div>
      <PageInstructions
        accent="rose"
        items={[
          'Write a candidate hypothesis, set its status, and click Add to track it.',
          'Select any saved hypothesis below, then click "Check This Hypothesis with AI" in the AI Feedback section to see if it\'s specific and testable enough — and ask follow-up questions in the chat that appears.',
        ]}
      />
      <CrudList
        projectId={project.id}
        resource="hypotheses"
        title="Hypotheses"
        hint="Track candidate hypotheses for this project."
        accent="rose"
        tourId="hypotheses-list"
        fields={FIELDS}
        renderer={(h) => `${h.text || ''}\n[${h.status || ''}]`}
        tools={PAGE_TOOLS.hypotheses}
        extraForSelected={(h) => (
          <AiChatPanel
            key={h.id}
            contextType="hypothesis_feedback"
            context={{
              hypothesis: h.text,
              project: { research_type_name: project.research_type, research_area: project.research_area },
            }}
            kickoffMessage="Is this hypothesis specific and testable enough? If not, how should I sharpen it?"
            triggerLabel="Check This Hypothesis with AI"
            accent="rose"
          />
        )}
      />
    </div>
  );
}
