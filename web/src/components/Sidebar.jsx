import { NavLink } from 'react-router-dom';
import './Sidebar.css';

const ACCENT_VAR = { rose: '1', sage: '2', blue: '3', sand: '4' };

export function Sidebar({ brand, tagline, items, footer, backTo, backLabel }) {
  return (
    <nav className="sidebar" aria-label={brand ? `${brand} navigation` : 'Main navigation'}>
      <div className="sidebar__brand">
        <span className="sidebar__logo" aria-hidden="true">
          <svg width="26" height="26" viewBox="0 0 24 24">
            {/* Golden-ratio spiral: 4 nodes at the golden angle (~137.5deg) apart,
                radius growing by the golden ratio each half-turn, joined by the
                matching logarithmic spiral curve. Each node has a small white
                specular-highlight dot for a polished, glossy feel that still
                works with any of the 4 accent colors across every palette. */}
            <path
              d="M 12.0 8.3 L 12.448 8.281 L 12.901 8.316 L 13.353 8.407 L 13.795 8.552 L 14.222 8.752 L 14.627 9.004 L 15.004 9.307 L 15.346 9.658 L 15.647 10.051 L 15.902 10.483 L 16.105 10.948 L 16.254 11.44 L 16.344 11.953 L 16.372 12.479 L 16.336 13.012 L 16.236 13.542 L 16.071 14.064 L 15.842 14.567 L 15.55 15.046 L 15.199 15.492 L 14.792 15.898 L 14.334 16.256 L 13.83 16.561 L 13.287 16.806 L 12.711 16.987 L 12.11 17.099 L 11.493 17.138 L 10.868 17.103 L 10.243 16.992 L 9.629 16.805 L 9.035 16.542 L 8.469 16.206 L 7.941 15.8 L 7.459 15.328 L 7.033 14.794 L 6.669 14.207 L 6.374 13.572 L 6.154 12.898 L 6.015 12.194 L 5.961 11.47 L 5.994 10.735 L 6.117 10.001 L 6.329 9.278 L 6.63 8.576 L 7.017 7.908 L 7.487 7.283 L 8.036 6.712 L 8.656 6.204 L 9.342 5.769 L 10.083 5.415 L 10.871 5.149 L 11.696 4.977 L 12.545 4.904 L 13.408 4.933 L 14.272 5.068 L 15.124 5.307 L 15.951 5.652 L 16.741 6.098 L 17.48 6.642 L 18.158 7.279"
              fill="none" stroke="var(--border)" strokeWidth="0.9" strokeLinecap="round" opacity="0.6"
            />
            <circle cx="12" cy="8.3" r="2.15" fill="var(--accent1)" />
            <circle cx="11.31" cy="7.48" r="0.86" fill="#ffffff" opacity="0.55" />
            <circle cx="15.199" cy="15.492" r="1.85" fill="var(--accent2)" />
            <circle cx="14.61" cy="14.79" r="0.74" fill="#ffffff" opacity="0.55" />
            <circle cx="5.961" cy="11.47" r="1.55" fill="var(--accent3)" />
            <circle cx="5.46" cy="10.88" r="0.62" fill="#ffffff" opacity="0.55" />
            <circle cx="18.158" cy="7.279" r="1.25" fill="var(--accent4)" />
            <circle cx="17.76" cy="6.8" r="0.5" fill="#ffffff" opacity="0.55" />
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
