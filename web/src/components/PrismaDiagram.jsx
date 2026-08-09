import { useRef } from 'react';
import { Button } from './Button';

/**
 * PRISMA 2020 flow diagram, drawn from live screening counts.
 *
 * Inline SVG rather than a chart library: the layout is fixed by the PRISMA
 * standard, so there's nothing to generalise, and an SVG downloads cleanly for
 * dropping straight into a manuscript.
 *
 * Layout follows Figure 1 of the PRISMA 2020 statement - identification at the
 * top, then screening, eligibility, and inclusion, with exclusions branching
 * to the right at each stage.
 */

const W = 760;
const BOX_W = 300;
const SIDE_W = 300;
const LEFT_X = 40;
const RIGHT_X = 420;

function Box({ x, y, w, h, title, lines, muted, accent }) {
  return (
    <g>
      <rect
        x={x} y={y} width={w} height={h} rx="6"
        fill={muted ? 'var(--surface-alt)' : 'var(--surface)'}
        stroke={accent ? 'var(--accent2-text)' : 'var(--border)'}
        strokeWidth={accent ? 1.8 : 1}
      />
      <text x={x + 12} y={y + 21} className="prisma__box-title">{title}</text>
      {lines.map((line, i) => (
        <text key={i} x={x + 12} y={y + 40 + i * 15} className="prisma__box-line">{line}</text>
      ))}
    </g>
  );
}

function Arrow({ from, to, dashed }) {
  return (
    <line
      x1={from[0]} y1={from[1]} x2={to[0]} y2={to[1]}
      stroke="var(--text-muted)" strokeWidth="1.4"
      strokeDasharray={dashed ? '4 3' : undefined}
      markerEnd="url(#prisma-arrow)"
    />
  );
}

export function PrismaDiagram({ prisma }) {
  const svgRef = useRef(null);

  const p = prisma || {};
  const n = (v) => (v == null ? 0 : v);

  // Row geometry. Heights vary because the exclusion-reasons box grows with
  // however many distinct reasons were recorded.
  const reasons = p.exclusion_reasons || [];
  const rows = [
    { y: 20, h: 74 },    // identification
    { y: 134, h: 60 },   // duplicates removed (right)
    { y: 234, h: 56 },   // records screened
    { y: 330, h: 56 },   // reports sought
    { y: 426, h: 56 },   // reports assessed
    { y: 522 + Math.max(0, (reasons.length - 1) * 15), h: 56 }, // included
  ];
  const height = rows[5].y + rows[5].h + 30;

  const identifiedLines = [`Records from databases (n = ${n(p.identified_databases)})`];
  if (p.identified_registers) identifiedLines.push(`Records from registers (n = ${p.identified_registers})`);
  if (p.identified_other) identifiedLines.push(`Other sources (n = ${p.identified_other})`);

  const removedLines = [`Duplicate records removed (n = ${n(p.duplicates_removed)})`];
  if (p.removed_ineligible_automation) removedLines.push(`Marked ineligible by automation (n = ${p.removed_ineligible_automation})`);
  if (p.removed_other) removedLines.push(`Removed for other reasons (n = ${p.removed_other})`);

  const reasonLines = reasons.length > 0
    ? reasons.map((r) => `${r.reason} (n = ${r.count})`)
    : ['No exclusions recorded yet'];

  function download() {
    const svg = svgRef.current;
    if (!svg) return;
    // Inline the computed colours so the exported file doesn't depend on the
    // app's CSS variables, which won't exist wherever it gets opened.
    const clone = svg.cloneNode(true);
    const computed = window.getComputedStyle(document.documentElement);
    const resolve = (v) => computed.getPropertyValue(v).trim() || '#000';
    clone.querySelectorAll('*').forEach((el) => {
      ['fill', 'stroke'].forEach((prop) => {
        const value = el.getAttribute(prop);
        if (value && value.startsWith('var(')) {
          el.setAttribute(prop, resolve(value.slice(4, -1)));
        }
      });
    });
    const style = document.createElementNS('http://www.w3.org/2000/svg', 'style');
    style.textContent = `
      .prisma__box-title { font: 700 12px system-ui, sans-serif; fill: ${resolve('--text')}; }
      .prisma__box-line  { font: 11px system-ui, sans-serif; fill: ${resolve('--text-muted')}; }
      .prisma__stage     { font: 700 10px system-ui, sans-serif; fill: ${resolve('--accent3-text')}; letter-spacing: 0.08em; }
    `;
    clone.insertBefore(style, clone.firstChild);
    clone.setAttribute('style', `background:${resolve('--surface')}`);

    const blob = new Blob([new XMLSerializer().serializeToString(clone)], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'prisma-flow-diagram.svg';
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div>
      <div className="prisma__scroll">
        <svg
          ref={svgRef}
          viewBox={`0 0 ${W} ${height}`}
          width="100%"
          style={{ maxWidth: W, display: 'block', margin: '0 auto' }}
          role="img"
          aria-label={
            `PRISMA flow diagram: ${n(p.identified_databases)} records identified, `
            + `${n(p.records_screened)} screened, ${n(p.records_excluded)} excluded at title and abstract, `
            + `${n(p.reports_assessed)} full texts assessed, ${n(p.reports_excluded)} excluded, `
            + `${n(p.studies_included)} studies included.`
          }
        >
          <defs>
            <marker id="prisma-arrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
              <path d="M0,0 L0,6 L7,3 z" fill="var(--text-muted)" />
            </marker>
          </defs>

          <text x={LEFT_X} y={12} className="prisma__stage">IDENTIFICATION</text>
          <Box
            x={LEFT_X} y={rows[0].y} w={BOX_W} h={rows[0].h}
            title="Records identified"
            lines={identifiedLines}
          />
          <Box
            x={RIGHT_X} y={rows[1].y - 60} w={SIDE_W} h={rows[1].h}
            title="Records removed before screening"
            lines={removedLines}
            muted
          />
          <Arrow from={[LEFT_X + BOX_W, rows[0].y + 36]} to={[RIGHT_X - 4, rows[0].y + 36]} />

          <text x={LEFT_X} y={rows[2].y - 10} className="prisma__stage">SCREENING</text>
          <Box
            x={LEFT_X} y={rows[2].y} w={BOX_W} h={rows[2].h}
            title="Records screened"
            lines={[`n = ${n(p.records_screened)}`]}
          />
          <Box
            x={RIGHT_X} y={rows[2].y} w={SIDE_W} h={rows[2].h}
            title="Records excluded (title/abstract)"
            lines={[`n = ${n(p.records_excluded)}`]}
            muted
          />
          <Arrow from={[LEFT_X + BOX_W, rows[2].y + 28]} to={[RIGHT_X - 4, rows[2].y + 28]} />
          <Arrow from={[LEFT_X + BOX_W / 2, rows[0].y + rows[0].h]} to={[LEFT_X + BOX_W / 2, rows[2].y - 4]} />

          <Box
            x={LEFT_X} y={rows[3].y} w={BOX_W} h={rows[3].h}
            title="Reports sought for retrieval"
            lines={[`n = ${n(p.reports_sought)}`]}
          />
          <Box
            x={RIGHT_X} y={rows[3].y} w={SIDE_W} h={rows[3].h}
            title="Reports not retrieved"
            lines={[`n = ${n(p.reports_not_retrieved)}`]}
            muted
          />
          <Arrow from={[LEFT_X + BOX_W, rows[3].y + 28]} to={[RIGHT_X - 4, rows[3].y + 28]} />
          <Arrow from={[LEFT_X + BOX_W / 2, rows[2].y + rows[2].h]} to={[LEFT_X + BOX_W / 2, rows[3].y - 4]} />

          <text x={LEFT_X} y={rows[4].y - 10} className="prisma__stage">ELIGIBILITY</text>
          <Box
            x={LEFT_X} y={rows[4].y} w={BOX_W} h={rows[4].h}
            title="Reports assessed for eligibility"
            lines={[`n = ${n(p.reports_assessed)}`]}
          />
          <Box
            x={RIGHT_X} y={rows[4].y} w={SIDE_W} h={Math.max(56, 30 + reasonLines.length * 15)}
            title={`Reports excluded (n = ${n(p.reports_excluded)})`}
            lines={reasonLines}
            muted
          />
          <Arrow from={[LEFT_X + BOX_W, rows[4].y + 28]} to={[RIGHT_X - 4, rows[4].y + 28]} />
          <Arrow from={[LEFT_X + BOX_W / 2, rows[3].y + rows[3].h]} to={[LEFT_X + BOX_W / 2, rows[4].y - 4]} />

          <text x={LEFT_X} y={rows[5].y - 10} className="prisma__stage">INCLUDED</text>
          <Box
            x={LEFT_X} y={rows[5].y} w={BOX_W} h={rows[5].h}
            title="Studies included in review"
            lines={[`n = ${n(p.studies_included)}`]}
            accent
          />
          <Arrow from={[LEFT_X + BOX_W / 2, rows[4].y + rows[4].h]} to={[LEFT_X + BOX_W / 2, rows[5].y - 4]} />
        </svg>
      </div>

      <div className="prisma__actions">
        <Button variant="secondary" accent="sage" onClick={download}>Download diagram (.svg)</Button>
        {(p.pending_title_abstract > 0 || p.pending_full_text > 0) && (
          <span className="prisma__pending">
            {p.pending_title_abstract > 0 && `${p.pending_title_abstract} still to screen`}
            {p.pending_title_abstract > 0 && p.pending_full_text > 0 && ' · '}
            {p.pending_full_text > 0 && `${p.pending_full_text} awaiting full-text decision`}
            {' '}— the diagram updates as you decide.
          </span>
        )}
      </div>
    </div>
  );
}
