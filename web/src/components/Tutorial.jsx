import { useState, useEffect, useRef, useCallback } from 'react';
import './Tutorial.css';

const SEEN_KEY = 'cortex_tutorial_seen';

/**
 * A short, silent product-demo animation: a laptop mockup showing a
 * simulated cursor "using" Cortex (typing, clicking, watching results
 * appear) - one scripted scene per major workflow. Nothing here talks to
 * the real backend; it's a fixed-timeline illustration, not a live app.
 */

function useTypewriter(text, active, speed = 45) {
  const [shown, setShown] = useState('');
  useEffect(() => {
    if (!active) { setShown(''); return undefined; }
    setShown('');
    let i = 0;
    const id = setInterval(() => {
      i += 1;
      setShown(text.slice(0, i));
      if (i >= text.length) clearInterval(id);
    }, speed);
    return () => clearInterval(id);
  }, [text, active, speed]);
  return shown;
}

// Each scene drives its own local timeline via chained setTimeouts, and
// reports cursor position (%) + click pulses up to the shared cursor.
function SceneCreateProject({ active, setCursor, onDone }) {
  const [phase, setPhase] = useState(0);
  const title = useTypewriter('Does Caffeine Improve Reaction Time?', active && phase >= 1);

  useEffect(() => {
    if (!active) { setPhase(0); return undefined; }
    const timers = [];
    timers.push(setTimeout(() => { setCursor(50, 34); }, 200));
    timers.push(setTimeout(() => setPhase(1), 700));
    timers.push(setTimeout(() => setCursor(50, 52), 2200));
    timers.push(setTimeout(() => setPhase(2), 2500));
    timers.push(setTimeout(() => setCursor(28, 76), 3200));
    timers.push(setTimeout(() => setPhase(3), 3600));
    timers.push(setTimeout(() => setCursor(28, 76, true), 3650));
    timers.push(setTimeout(() => setPhase(4), 4100));
    timers.push(setTimeout(() => onDone?.(), 5600));
    return () => timers.forEach(clearTimeout);
  }, [active]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="tut-scene">
      <div className="tut-card">
        <div className="tut-card__title">Start a New Project</div>
        <div className="tut-field">
          <div className="tut-label">Project title</div>
          <div className={`tut-input ${phase === 1 ? 'tut-input--focused' : ''}`}>
            {title}<span className={`tut-caret ${phase === 1 ? 'tut-caret--blink' : 'tut-caret--hidden'}`} />
          </div>
        </div>
        <div className="tut-field">
          <div className="tut-label">Research type</div>
          <div className={`tut-select ${phase >= 2 ? 'tut-select--focused' : ''}`}>Experimental Research ▾</div>
        </div>
        <button className={`tut-btn tut-btn--primary ${phase >= 3 ? 'tut-btn--pressed' : ''}`}>Create Project</button>
        {phase >= 4 && (
          <div className="tut-toast">Methodology checklist created ✓ &mdash; 11 steps</div>
        )}
      </div>
    </div>
  );
}

function SceneLiteratureSearch({ active, setCursor, onDone }) {
  const [phase, setPhase] = useState(0);
  const query = useTypewriter('caffeine and reaction time', active && phase >= 1);
  const results = [
    { title: 'Caffeine and psychomotor performance: a review', match: 91 },
    { title: 'Acute stimulant effects on simple visual reaction time', match: 84 },
    { title: 'Dose-response effects of caffeine on alertness', match: 76 },
  ];

  useEffect(() => {
    if (!active) { setPhase(0); return undefined; }
    const timers = [];
    timers.push(setTimeout(() => setCursor(50, 22), 200));
    timers.push(setTimeout(() => setPhase(1), 600));
    timers.push(setTimeout(() => setCursor(85, 22), 2400));
    timers.push(setTimeout(() => { setPhase(2); setCursor(85, 22, true); }, 2600));
    timers.push(setTimeout(() => setPhase(3), 3200));
    timers.push(setTimeout(() => setPhase(4), 3900));
    timers.push(setTimeout(() => setPhase(5), 4600));
    timers.push(setTimeout(() => setCursor(90, 46), 5000));
    timers.push(setTimeout(() => onDone?.(), 6200));
    return () => timers.forEach(clearTimeout);
  }, [active]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="tut-scene">
      <div className="tut-card">
        <div className="tut-card__title">Literature Review</div>
        <div className="tut-search-row">
          <div className={`tut-input tut-input--grow ${phase === 1 ? 'tut-input--focused' : ''}`}>
            {query}<span className={`tut-caret ${phase === 1 ? 'tut-caret--blink' : 'tut-caret--hidden'}`} />
          </div>
          <button className={`tut-btn tut-btn--primary tut-btn--small ${phase >= 2 ? 'tut-btn--pressed' : ''}`}>Search</button>
        </div>
        <div className="tut-results">
          {results.map((r, i) => phase >= 3 + i && (
            <div className="tut-result-card" key={r.title}>
              <span className="tut-result-match">{r.match}%</span>
              <span className="tut-result-title">{r.title}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function SceneDataAnalysis({ active, setCursor, onDone }) {
  const [phase, setPhase] = useState(0);
  const bars = [42, 68, 90, 55];

  useEffect(() => {
    if (!active) { setPhase(0); return undefined; }
    const timers = [];
    timers.push(setTimeout(() => setCursor(50, 30), 200));
    timers.push(setTimeout(() => { setPhase(1); setCursor(50, 30, true); }, 900));
    timers.push(setTimeout(() => setPhase(2), 1700));
    timers.push(setTimeout(() => setCursor(50, 58), 2600));
    timers.push(setTimeout(() => { setPhase(3); setCursor(50, 58, true); }, 3000));
    timers.push(setTimeout(() => setPhase(4), 3600));
    timers.push(setTimeout(() => onDone?.(), 5400));
    return () => timers.forEach(clearTimeout);
  }, [active]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="tut-scene">
      <div className="tut-card">
        <div className="tut-card__title">Which Test Should I Use?</div>
        <button className={`tut-btn tut-btn--primary ${phase >= 1 ? 'tut-btn--pressed' : ''}`}>Check Assumptions</button>
        {phase >= 2 && (
          <div className="tut-toast tut-toast--wide">
            Recommended: <strong>Independent Samples t-test</strong> &mdash; both groups look normally distributed
          </div>
        )}
        {phase >= 2 && (
          <button className={`tut-btn tut-btn--secondary ${phase >= 3 ? 'tut-btn--pressed' : ''}`} style={{ marginTop: 10 }}>
            Run Independent Samples t-test
          </button>
        )}
        {phase >= 4 && (
          <div className="tut-chart">
            {bars.map((h, i) => <div key={i} className="tut-chart__bar" style={{ '--h': `${h}%` }} />)}
          </div>
        )}
      </div>
    </div>
  );
}

function SceneAiFeedback({ active, setCursor, onDone }) {
  const [phase, setPhase] = useState(0);
  const reply = useTypewriter(
    'Strong opening — the effect size claim in your abstract needs a citation. Consider tightening the second methods paragraph.',
    active && phase >= 3, 18,
  );

  useEffect(() => {
    if (!active) { setPhase(0); return undefined; }
    const timers = [];
    timers.push(setTimeout(() => setCursor(50, 40), 200));
    timers.push(setTimeout(() => { setPhase(1); setCursor(50, 40, true); }, 900));
    timers.push(setTimeout(() => setPhase(2), 1300));
    timers.push(setTimeout(() => setPhase(3), 2400));
    timers.push(setTimeout(() => onDone?.(), 6200));
    return () => timers.forEach(clearTimeout);
  }, [active]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="tut-scene">
      <div className="tut-card">
        <div className="tut-card__title">AI Feedback</div>
        <button className={`tut-btn tut-btn--primary ${phase >= 1 ? 'tut-btn--pressed' : ''}`}>✨ Get AI Feedback on My Draft</button>
        {phase >= 2 && (
          <div className="tut-chat">
            <div className="tut-chat__msg tut-chat__msg--user">Please review my manuscript draft.</div>
            {phase < 3 ? (
              <div className="tut-chat__msg tut-chat__msg--ai tut-chat__msg--thinking">Thinking&hellip;</div>
            ) : (
              <div className="tut-chat__msg tut-chat__msg--ai">{reply}</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

const SCENES = [
  { key: 'create', label: 'Start a project', Component: SceneCreateProject },
  { key: 'search', label: 'Search literature', Component: SceneLiteratureSearch },
  { key: 'analyze', label: 'Analyze your data', Component: SceneDataAnalysis },
  { key: 'ai', label: 'Get AI feedback', Component: SceneAiFeedback },
];

export function Tutorial() {
  const [open, setOpen] = useState(false);
  const [scene, setScene] = useState(0);
  const [cursorPos, setCursorPos] = useState({ x: 50, y: 50 });
  const [clicking, setClicking] = useState(false);
  const clickTimeoutRef = useRef(null);

  useEffect(() => {
    if (!localStorage.getItem(SEEN_KEY)) setOpen(true);
  }, []);

  const setCursor = useCallback((x, y, click = false) => {
    setCursorPos({ x, y });
    if (click) {
      setClicking(true);
      clearTimeout(clickTimeoutRef.current);
      clickTimeoutRef.current = setTimeout(() => setClicking(false), 350);
    }
  }, []);

  useEffect(() => {
    if (!open) return undefined;
    function onKey(e) {
      if (e.key === 'Escape') close();
    }
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }); // eslint-disable-line react-hooks/exhaustive-deps

  function close() {
    localStorage.setItem(SEEN_KEY, '1');
    setOpen(false);
  }

  function openFromStart() {
    setScene(0);
    setCursorPos({ x: 50, y: 50 });
    setOpen(true);
  }

  function goTo(i) {
    setCursorPos({ x: 50, y: 50 });
    setScene(Math.max(0, Math.min(SCENES.length - 1, i)));
  }

  const isLast = scene === SCENES.length - 1;
  const ActiveScene = SCENES[scene].Component;

  return (
    <>
      <button
        className="tutorial__trigger"
        onClick={openFromStart}
        aria-haspopup="dialog"
        aria-label="Open app tutorial"
        title="Tutorial"
      >
        ?
      </button>

      {open && (
        <div className="tutorial__overlay" role="dialog" aria-modal="true" aria-label="Cortex tutorial">
          <div className="tutorial__modal">
            <button className="tutorial__close" onClick={close} aria-label="Close tutorial">&times;</button>
            <h2 className="tutorial__heading">See Cortex in action</h2>
            <p className="tutorial__subheading">{SCENES[scene].label}</p>

            <div className="tut-laptop">
              <div className="tut-laptop__screen">
                {SCENES.map(({ key, Component }, i) => (
                  <div key={key} style={{ display: i === scene ? 'block' : 'none', height: '100%' }}>
                    <Component active={i === scene} setCursor={setCursor} onDone={() => !isLast && goTo(scene + 1)} />
                  </div>
                ))}
                <div
                  className={`tut-cursor ${clicking ? 'tut-cursor--click' : ''}`}
                  style={{ left: `${cursorPos.x}%`, top: `${cursorPos.y}%` }}
                  aria-hidden="true"
                />
              </div>
              <div className="tut-laptop__base" />
            </div>

            <div className="tutorial__dots" role="tablist" aria-label="Scenes">
              {SCENES.map((s, i) => (
                <button
                  key={s.key}
                  role="tab"
                  aria-selected={i === scene}
                  aria-label={s.label}
                  className={`tutorial__dot ${i === scene ? 'tutorial__dot--active' : ''}`}
                  onClick={() => goTo(i)}
                />
              ))}
            </div>

            <div className="tutorial__actions">
              <button className="tutorial__skip" onClick={close}>Skip tour</button>
              <div className="tutorial__nav">
                {scene > 0 && <button className="tutorial__btn tutorial__btn--secondary" onClick={() => goTo(scene - 1)}>Back</button>}
                <button className="tutorial__btn tutorial__btn--primary" onClick={() => (isLast ? close() : goTo(scene + 1))}>
                  {isLast ? 'Done' : 'Next'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
