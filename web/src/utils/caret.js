/**
 * Where is the text caret, in pixels?
 *
 * A <textarea> gives you a character offset but no geometry, so the standard
 * trick is to render an invisible <div> with identical text styling, copy the
 * text up to the caret into it, and measure a marker span placed at the end.
 * Same font, same wrapping, so the marker lands where the real caret is.
 *
 * Used to anchor the @-mention picker to the caret instead of parking it in a
 * fixed corner.
 */

// Every property that can affect how text wraps or how wide a glyph is. Miss
// one and the mirror wraps differently from the real textarea, which puts the
// caret estimate off by a line.
const MIRRORED_PROPERTIES = [
  'boxSizing', 'width', 'borderTopWidth', 'borderRightWidth', 'borderBottomWidth', 'borderLeftWidth',
  'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft',
  'fontStyle', 'fontVariant', 'fontWeight', 'fontStretch', 'fontSize', 'fontSizeAdjust',
  'fontFamily', 'lineHeight', 'textAlign', 'textTransform', 'textIndent',
  'letterSpacing', 'wordSpacing', 'tabSize', 'whiteSpace', 'wordBreak', 'overflowWrap',
];

/**
 * @returns {{top: number, left: number, height: number}} caret position in
 * viewport coordinates.
 */
export function getCaretCoordinates(textarea, position) {
  const mirror = document.createElement('div');
  const style = mirror.style;
  const computed = window.getComputedStyle(textarea);

  style.position = 'absolute';
  style.visibility = 'hidden';
  style.whiteSpace = 'pre-wrap';
  style.wordWrap = 'break-word';
  style.top = '0';
  style.left = '-9999px';

  MIRRORED_PROPERTIES.forEach((prop) => {
    style[prop] = computed[prop];
  });
  // The mirror grows with content; the textarea scrolls instead.
  style.overflow = 'hidden';
  style.height = 'auto';

  mirror.textContent = textarea.value.substring(0, position);

  // A zero-width marker at the caret. Using a real character (not just an
  // empty span) so it reliably gets a layout box on the correct line.
  const marker = document.createElement('span');
  marker.textContent = '​';
  mirror.appendChild(marker);

  document.body.appendChild(mirror);
  const markerTop = marker.offsetTop;
  const markerLeft = marker.offsetLeft;
  const lineHeight = parseInt(computed.lineHeight, 10) || parseInt(computed.fontSize, 10) * 1.2;
  document.body.removeChild(mirror);

  const box = textarea.getBoundingClientRect();
  return {
    top: box.top + markerTop - textarea.scrollTop,
    left: box.left + markerLeft - textarea.scrollLeft,
    height: lineHeight,
  };
}

/**
 * If the caret sits just after an "@query" token, return that token plus where
 * it starts - that's what drives the mention picker.
 *
 * Returns null when there's no active trigger, including when the @ is part of
 * an email address (preceded by a word character), which would otherwise pop
 * the picker open every time someone types an address.
 */
export function getMentionQuery(value, caret) {
  const before = value.slice(0, caret);
  const at = before.lastIndexOf('@');
  if (at === -1) return null;

  const preceding = at > 0 ? before[at - 1] : '';
  if (preceding && /[\w@.]/.test(preceding)) return null;

  const query = before.slice(at + 1);
  // A newline (or an already-closed marker) ends the trigger.
  if (/[\n\]]/.test(query)) return null;
  // Don't keep an unmatched picker open across a whole sentence.
  if (query.length > 40) return null;

  return { query, start: at };
}
