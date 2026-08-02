// Each palette defines its own light and dark variant. Every screen pulls
// four distinct accent colors (not one repeated brand color everywhere) so
// each section of the app keeps its own visual identity regardless of which
// palette or light/dark mode is active.
//
// Each accent has three forms, all WCAG AA-verified (>=4.5:1 for text):
//   accentN       - the vibrant base color. Safe for icons/borders/large
//                    decorative fills, NOT guaranteed safe as small text.
//   accentNTint   - a very light/dark background wash for badges and chips.
//   accentNText   - accentN darkened (light mode only) so it's safe to use
//                    AS TEXT on bg/surface/surfaceAlt/its own tint. In dark
//                    mode this equals accentN, which already passes as-is.
//   accentNBtn    - accentN darkened so white text on top of it (solid
//                    button fills) clears 4.5:1 in both light and dark mode.

export const PALETTES = {
  terracotta: {
    label: 'Terracotta',
    swatch: '#c97b66',
    light: {
      bg: '#faf6ef', surface: '#fffdf8', surfaceAlt: '#f3ede0', border: '#e6dcc8',
      text: '#3d372e', textMuted: '#786f62',
      accent1: '#c97b66', accent1Tint: '#f3ddd0', accent1Text: '#8d5647', accent1Btn: '#a56554',
      accent2: '#7c9a72', accent2Tint: '#e2ebda', accent2Text: '#576c50', accent2Btn: '#637b5b',
      accent3: '#6f93b3', accent3Tint: '#dce8f0', accent3Text: '#506a81', accent3Btn: '#5b7993',
      accent4: '#b8923f', accent4Tint: '#f1e6c9', accent4Text: '#7d632b', accent4Btn: '#907231',
    },
    dark: {
      bg: '#211d17', surface: '#2a251d', surfaceAlt: '#1a1712', border: '#3d362a',
      text: '#f1ece1', textMuted: '#b3a793',
      accent1: '#e0987f', accent1Tint: '#4a3229', accent1Text: '#e0987f', accent1Btn: '#9d6a59',
      accent2: '#9bb890', accent2Tint: '#324034', accent2Text: '#9bb890', accent2Btn: '#66795f',
      accent3: '#8fb2d1', accent3Tint: '#293b49', accent3Text: '#8fb2d1', accent3Btn: '#61798e',
      accent4: '#d4ac5c', accent4Tint: '#453a24', accent4Text: '#d4ac5c', accent4Btn: '#8c723d',
    },
  },
  ocean: {
    label: 'Ocean',
    swatch: '#3d7ea6',
    light: {
      bg: '#f3f7f9', surface: '#ffffff', surfaceAlt: '#e7eef2', border: '#d6e2e8',
      text: '#1f2e35', textMuted: '#5e737d',
      accent1: '#3d7ea6', accent1Tint: '#d7e7ef', accent1Text: '#336a8b', accent1Btn: '#3c7ba3',
      accent2: '#2f9e8f', accent2Tint: '#d3ede9', accent2Text: '#227267', accent2Btn: '#278275',
      accent3: '#6a6cad', accent3Tint: '#e0e0f0', accent3Text: '#5d5f98', accent3Btn: '#6a6cad',
      accent4: '#c98a3f', accent4Tint: '#f3e3cb', accent4Text: '#895e2b', accent4Btn: '#9d6c31',
    },
    dark: {
      bg: '#101a20', surface: '#16222a', surfaceAlt: '#0b1317', border: '#243642',
      text: '#e6eef2', textMuted: '#8fa6b0',
      accent1: '#6fb3dc', accent1Tint: '#1c3644', accent1Text: '#6fb3dc', accent1Btn: '#4b7a96',
      accent2: '#5cc4b3', accent2Tint: '#173b35', accent2Text: '#5cc4b3', accent2Btn: '#3d8176',
      accent3: '#9d9fda', accent3Tint: '#2c2d4c', accent3Text: '#9d9fda', accent3Btn: '#71729d',
      accent4: '#e0ac5f', accent4Tint: '#453421', accent4Text: '#e0ac5f', accent4Btn: '#8f6e3d',
    },
  },
  botanical: {
    label: 'Botanical',
    swatch: '#5f8759',
    light: {
      bg: '#f5f6f0', surface: '#ffffff', surfaceAlt: '#e9ece0', border: '#dbe0cf',
      text: '#293425', textMuted: '#66735f',
      accent1: '#5f8759', accent1Tint: '#dde8d8', accent1Text: '#4c6c47', accent1Btn: '#597f54',
      accent2: '#a06b3d', accent2Tint: '#ecdcc9', accent2Text: '#835832', accent2Btn: '#a06b3d',
      accent3: '#4f8f88', accent3Tint: '#d7e9e6', accent3Text: '#3c6d67', accent3Btn: '#467e78',
      accent4: '#9c7bb0', accent4Tint: '#e9dcef', accent4Text: '#70597f', accent4Btn: '#866a97',
    },
    dark: {
      bg: '#171c14', surface: '#1f251b', surfaceAlt: '#12150f', border: '#2f3728',
      text: '#e9ecdf', textMuted: '#a3af95',
      accent1: '#8fbb87', accent1Tint: '#2a3924', accent1Text: '#8fbb87', accent1Btn: '#5e7b59',
      accent2: '#cf9c6c', accent2Tint: '#412e1b', accent2Text: '#cf9c6c', accent2Btn: '#916d4c',
      accent3: '#7fbcb4', accent3Tint: '#1f3a36', accent3Text: '#7fbcb4', accent3Btn: '#547c77',
      accent4: '#c3a4d3', accent4Tint: '#392c40', accent4Text: '#c3a4d3', accent4Btn: '#816c8b',
    },
  },
  dusk: {
    label: 'Dusk',
    swatch: '#8a6fae',
    light: {
      bg: '#f7f5f9', surface: '#ffffff', surfaceAlt: '#ece7f1', border: '#ddd5e6',
      text: '#2c2536', textMuted: '#75697f',
      accent1: '#8a6fae', accent1Tint: '#e7dfef', accent1Text: '#715b8f', accent1Btn: '#846ba7',
      accent2: '#c76b8a', accent2Tint: '#f4dde3', accent2Text: '#934f66', accent2Btn: '#ab5c77',
      accent3: '#4f8fa8', accent3Tint: '#d8e9ee', accent3Text: '#3c6d80', accent3Btn: '#447b90',
      accent4: '#b3903f', accent4Tint: '#f0e3c7', accent4Text: '#7a622b', accent4Btn: '#8f7332',
    },
    dark: {
      bg: '#19151f', surface: '#221d29', surfaceAlt: '#120f16', border: '#332c3d',
      text: '#ede8f1', textMuted: '#ab9fb5',
      accent1: '#b79bd6', accent1Tint: '#3a2e49', accent1Text: '#b79bd6', accent1Btn: '#806c96',
      accent2: '#e296ae', accent2Tint: '#452a33', accent2Text: '#e296ae', accent2Btn: '#9a6676',
      accent3: '#7fb8cf', accent3Tint: '#213c45', accent3Text: '#7fb8cf', accent3Btn: '#547989',
      accent4: '#d9b567', accent4Tint: '#453824', accent4Text: '#d9b567', accent4Btn: '#877040',
    },
  },
};

export const PALETTE_KEYS = Object.keys(PALETTES);

/** 7am-7pm counts as "day". Re-evaluated periodically by ThemeContext. */
export function isDaytimeNow() {
  const hour = new Date().getHours();
  return hour >= 7 && hour < 19;
}
