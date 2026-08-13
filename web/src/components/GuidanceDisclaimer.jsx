import './GuidanceDisclaimer.css';

/**
 * Shown wherever Cortex gives methodological advice.
 *
 * Placed at the top of the guidance rather than buried at the end of it -
 * a caveat only works if it's read before the thing it qualifies.
 */
export function GuidanceDisclaimer({ compact = false }) {
  return (
    <div className={`guide-disclaimer ${compact ? 'guide-disclaimer--compact' : ''}`} role="note">
      <span className="guide-disclaimer__icon" aria-hidden="true">ℹ</span>
      <div>
        <strong>This is a starting point, not a rulebook.</strong>{' '}
        Every project is different, and research practice varies a great deal between fields — what
        counts as a sound design in molecular biology, economics, and machine learning are three
        different things. Treat this as a way to orient yourself and to ask better questions, not as
        a specification to follow literally.
        {!compact && (
          <>
            {' '}
            Requirements set by your institution, ethics board, funder, or target journal are binding
            and override anything here. Where a real standard exists, read it directly — the links on
            each step point to them.
          </>
        )}{' '}
        <em>When this guide and your teacher, advisor, or ethics board disagree, they are right.</em>
      </div>
    </div>
  );
}
