import { useGuidanceLevel } from '../hooks/useGuidanceLevel';
import './GuidanceToggle.css';

/**
 * Switches beginner explanations between open-by-default and collapsed.
 *
 * Cortex is aimed first at people doing their first project, so this starts
 * on. Someone who already knows the material turns it off once and it stays
 * off everywhere.
 */
export function GuidanceToggle() {
  const { level, setLevel } = useGuidanceLevel();

  return (
    <div className="guidance-toggle" role="group" aria-label="Level of explanation">
      <span className="guidance-toggle__label">Explanations</span>
      {[['guided', 'Guided'], ['concise', 'Concise']].map(([value, label]) => (
        <button
          key={value}
          type="button"
          className={`guidance-toggle__btn ${level === value ? 'guidance-toggle__btn--active' : ''}`}
          aria-pressed={level === value}
          onClick={() => setLevel(value)}
          title={value === 'guided'
            ? 'Show step-by-step guidance opened by default'
            : 'Collapse guidance — still one click away on each step'}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
