import './Card.css';

const ACCENT_VAR = { rose: '1', sage: '2', blue: '3', sand: '4' };

/**
 * A card with a flat, offset "sticker" shadow in the section's accent color
 * instead of a blurred drop shadow - keeps the hand-designed, paper-like
 * feel rather than a glossy dashboard panel look.
 */
export function Card({ title, hint, accent = 'sand', children, id, ...rest }) {
  const accentNum = ACCENT_VAR[accent] || '4';
  return (
    <section className="card-shadow" style={{ '--card-accent': `var(--accent${accentNum}-tint)` }} aria-labelledby={id} {...rest}>
      <div className="card">
        {title && <h2 className="card-title" id={id}>{title}</h2>}
        {hint && <p className="card-hint">{hint}</p>}
        {children}
      </div>
    </section>
  );
}
