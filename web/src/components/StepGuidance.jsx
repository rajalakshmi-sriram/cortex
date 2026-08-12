import { useState } from 'react';
import './StepGuidance.css';

/**
 * "How do I actually do this?" for one methodology step.
 *
 * Collapsed by default and driven by a preference the user controls, so the
 * checklist stays terse for someone who has run studies before and opens up
 * for someone who hasn't.
 */
export function StepGuidance({ guidance, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);

  if (!guidance) return null;

  return (
    <div className="step-guide">
      <button
        type="button"
        className="step-guide__toggle"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
      >
        <span className="step-guide__chevron" aria-hidden="true">{open ? '▾' : '▸'}</span>
        {open ? 'Hide guidance' : 'How do I do this?'}
      </button>

      {open && (
        <div className="step-guide__body">
          <p className="step-guide__what">{guidance.what}</p>

          {guidance.how?.length > 0 && (
            <>
              <h4 className="step-guide__heading">How to approach it</h4>
              <ul className="step-guide__list">
                {guidance.how.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </>
          )}

          {guidance.mistakes?.length > 0 && (
            <>
              <h4 className="step-guide__heading step-guide__heading--warn">Common mistakes</h4>
              <ul className="step-guide__list step-guide__list--warn">
                {guidance.mistakes.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </>
          )}

          {guidance.done_when && (
            <p className="step-guide__done">
              <strong>You're done when:</strong> {guidance.done_when}
            </p>
          )}

          {guidance.beginner_note && (
            <p className="step-guide__note">
              <span className="step-guide__note-label">If this is your first project</span>
              {guidance.beginner_note}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
