import { useGuidanceLevel } from '../hooks/useGuidanceLevel';
import './GuidanceToggle.css';

/**
 * Switches step explanations between collapsed and open-by-default.
 *
 * Starts collapsed so the checklist stays readable; flipping to Guided opens
 * every step's explainer and the choice persists across pages and sessions.
 */
export function GuidanceToggle() {
  const { level, setLevel } = useGuidanceLevel();

  return (
    <div className="guidance-toggle" role="group" aria-label="Level of explanation">
      <span className="guidance-toggle__label">Explanations</span>
      {[['concise', 'Concise'], ['guided', 'Guided']].map(([value, label]) => (
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
