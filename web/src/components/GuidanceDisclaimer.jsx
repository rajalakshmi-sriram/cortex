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
        <strong>A starting point, not a rulebook.</strong>{' '}
        Every project differs, and practice varies by field — use this to orient yourself and ask
        better questions, not as a spec to follow literally.
        {!compact && (
          <> Requirements from your institution, ethics board, funder or target journal are binding.
            Where a real standard exists, read it directly.
          </>
        )}{' '}
        <em>If this and your advisor disagree, they're right.</em>
      </div>
    </div>
  );
}
