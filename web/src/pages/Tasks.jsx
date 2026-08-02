import { useProject } from './Workspace';
import { CrudList } from '../components/CrudList';
import { PageInstructions } from '../components/PageInstructions';
import { PAGE_TOOLS } from '../data/pageTools';

const FIELDS = [
  { key: 'title', label: 'Task', kind: 'line' },
  { key: 'status', label: 'Status', kind: 'combo', options: ['todo', 'in_progress', 'done'] },
  { key: 'due_date', label: 'Due Date', kind: 'line', placeholder: 'YYYY-MM-DD' },
];

export function Tasks() {
  const { project } = useProject();
  return (
    <div>
      <PageInstructions
        accent="sage"
        items={[
          'Add a task with an optional due date and status, then track it here.',
          'Select any saved task to delete it once it\'s done or no longer needed.',
        ]}
      />
      <CrudList
        projectId={project.id}
        resource="tasks"
        title="Tasks & Milestones"
        hint="Track tasks for this project."
        accent="sage"
        fields={FIELDS}
        renderer={(t) => `${t.title || ''}\n[${t.status || ''}] due ${t.due_date || '—'}`}
        tools={PAGE_TOOLS.tasks}
      />
    </div>
  );
}
