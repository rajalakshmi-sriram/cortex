import { NavLink } from 'react-router-dom';
import './Sidebar.css';

const ACCENT_VAR = { rose: '1', sage: '2', blue: '3', sand: '4' };

export function Sidebar({ brand, tagline, items, footer, backTo, backLabel }) {
  return (
    <nav className="sidebar" aria-label={brand ? `${brand} navigation` : 'Main navigation'}>
      <div className="sidebar__brand">
        <span className="sidebar__logo" aria-hidden="true">
          <svg width="26" height="26" viewBox="0 0 24 24">
            <circle cx="12" cy="5" r="2.2" fill="var(--accent1)" />
            <circle cx="5" cy="13" r="2.2" fill="var(--accent2)" />
            <circle cx="19" cy="13" r="2.2" fill="var(--accent3)" />
            <circle cx="12" cy="20" r="2.2" fill="var(--accent4)" />
            <path d="M12 7.2 5 13M12 7.2 19 13M5 13 12 20M19 13 12 20M5 13H19"
              stroke="var(--border)" strokeWidth="1.3" fill="none" />
          </svg>
        </span>
        <div>
          <div className="sidebar__brand-name font-serif">{brand}</div>
          {tagline && <div className="sidebar__tagline">{tagline}</div>}
        </div>
      </div>

      {backTo && (
        <NavLink to={backTo} className="sidebar__back">
          <span aria-hidden="true">&larr;</span> {backLabel}
        </NavLink>
      )}

      <ul className="sidebar__list">
        {items.map((item) => {
          const accentNum = ACCENT_VAR[item.accent] || '1';
          return (
            <li key={item.to}>
              <NavLink
                to={item.to}
                end={item.end}
                className={({ isActive }) => `sidebar__item ${isActive ? 'sidebar__item--active' : ''}`}
                style={{ '--item-accent': `var(--accent${accentNum}-text)`, '--item-accent-tint': `var(--accent${accentNum}-tint)` }}
              >
                <span className="sidebar__icon" aria-hidden="true">{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            </li>
          );
        })}
      </ul>

      {footer && <div className="sidebar__footer">{footer}</div>}
    </nav>
  );
}
