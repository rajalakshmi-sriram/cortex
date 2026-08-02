import './Button.css';

const ACCENT_VAR = { rose: '1', sage: '2', blue: '3', sand: '4' };

export function Button({ accent = 'rose', variant = 'primary', children, icon, ...props }) {
  const accentNum = ACCENT_VAR[accent] || '1';
  const style = {
    '--btn-accent-tint': `var(--accent${accentNum}-tint)`,
    // Solid fills need extra-darkened accent so white button text stays readable (WCAG AA).
    '--btn-accent-solid': `var(--accent${accentNum}-btn)`,
    // Borders/text on top of the tint background need the same darkened treatment.
    '--btn-accent-text': `var(--accent${accentNum}-text)`,
  };

  return (
    <button className={`btn btn--${variant}`} style={style} {...props}>
      {icon && <span className="btn__icon" aria-hidden="true">{icon}</span>}
      {children}
    </button>
  );
}
