import { useState, useEffect, useRef, useCallback, useLayoutEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../api/client';
import './Tutorial.css';

const SEEN_KEY = 'cortex_tutorial_seen';
const PROGRESS_KEY = 'cortex_tutorial_progress';

/**
 * An interactive guided tour of the real app.
 *
 * It creates an actual sample project (the same one "Try a Sample Project"
 * makes), then walks the real router through it, spotlighting real
 * elements with real data. Steps come in two kinds:
 *
 *  - 'read' steps explain something. The rest of the page is click-blocked
 *    so nothing fires by accident, and you advance with Next.
 *  - 'do' steps ask you to actually perform the action on the real UI. The
 *    blocker lifts, the spotlight pulses, and the tour detects when you've
 *    done it and moves on by itself.
 *
 * Only safe actions are ever asked for or automated - nothing that costs
 * money (AI calls), hits an external service (literature search), or
 * destroys data (delete/export).
 */

const SECTIONS = [
  { key: 'basics', label: 'The basics' },
  { key: 'literature', label: 'Finding literature' },
  { key: 'planning', label: 'Planning the work' },
  { key: 'data', label: 'Analyzing data' },
  { key: 'writing', label: 'Writing it up' },
  { key: 'setup', label: 'Settings & extras' },
];

const selectDatasetIfNeeded = () => {
  if (!document.querySelector('[data-tour="stats-wizard"]')) {
    document.querySelector('[data-tour="datasets-list"] li button')?.click();
  }
};

// CrudList only renders "Delete Selected" once something is selected, which
// makes it a reliable "they picked an item" signal for hypotheses/tasks/journals.
const hasDeleteSelected = (scope) =>
  [...document.querySelectorAll(`${scope} button`)].some((b) => b.textContent.trim() === 'Delete Selected');

const STEPS = [
  // ---------- The basics ----------
  {
    section: 'basics',
    navTo: '',
    selector: '[data-tour="overview-details"]',
    title: 'Your project at a glance',
    body: "This is Overview - a read-only snapshot of the project. The tabs on the left are where you actually do the work.",
  },
  {
    section: 'basics',
    navTo: '',
    selector: '[data-tour="overview-methodology"]',
    title: 'Progress, without digging',
    body: 'How far along the methodology checklist you are, visible without leaving this page.',
  },
  {
    section: 'basics',
    navTo: '',
    selector: '[data-tour="overview-backup"]',
    title: 'Back up or share a project',
    body: 'Export everything - details, papers, datasets, manuscript, progress - as one .zip. Hand it to a co-author, or keep it as a backup.',
    note: "We won't trigger the download during the tour.",
  },

  // ---------- Finding literature ----------
  {
    section: 'literature',
    navTo: 'literature-review',
    selector: '[data-tour="lit-search"]',
    title: 'Search real literature',
    body: 'Describe an idea here and Cortex searches real, free sources (Europe PMC, CrossRef, arXiv and more), scoring each result against your idea.',
    mode: 'do',
    doHint: 'Type a research idea into the box - no need to actually run the search.',
    completeWhen: () => (document.getElementById('lit-idea')?.value || '').trim().length >= 10,
  },
  {
    section: 'literature',
    navTo: 'paper-library',
    selector: '[data-tour="paper-library-list"]',
    title: 'Papers you keep',
    body: 'Anything you save from a search lands here. This sample project already has one.',
    mode: 'do',
    doHint: 'Click the paper to open its details.',
    completeWhen: () => !!document.querySelector('[data-tour="paper-library-list"] .paper-library__row--selected'),
  },
  {
    section: 'literature',
    navTo: 'paper-library',
    selector: '[data-tour="citation-export"]',
    title: 'Citations, already formatted',
    body: 'Every saved paper reformats instantly when you switch style - or export the whole library as BibTeX for LaTeX, or RIS for EndNote, Zotero and Mendeley.',
    mode: 'do',
    doHint: 'Switch the citation style and watch the citation below rewrite itself.',
    capture: () => document.getElementById('citation-style')?.value,
    completeWhen: (initial) => document.getElementById('citation-style')?.value !== initial,
  },

  // ---------- Planning the work ----------
  {
    section: 'planning',
    navTo: 'methodology',
    selector: '[data-tour="methodology-checklist"]',
    title: 'A checklist matched to your research type',
    body: "These steps come from the research type you picked - they don't change on their own. You tick them off as you actually finish them.",
    mode: 'do',
    doHint: 'Tick off step 3 to mark it done.',
    completeWhen: () => {
      const boxes = document.querySelectorAll('[data-tour="methodology-checklist"] input[type="checkbox"]');
      return boxes.length > 2 && boxes[2].checked;
    },
  },
  {
    section: 'planning',
    navTo: 'hypotheses',
    selector: '[data-tour="hypotheses-list"]',
    title: 'Track your hypotheses',
    body: 'Keep candidate hypotheses and their status together. Select one and AI Feedback can tell you how specific and testable it really is.',
    mode: 'do',
    doHint: 'Click the saved hypothesis to select it.',
    completeWhen: () => hasDeleteSelected('[data-tour="hypotheses-list"]'),
  },
  {
    section: 'planning',
    navTo: 'tasks',
    selector: '[data-tour="tasks-list"]',
    title: 'Tasks & milestones',
    body: "Lightweight tracking scoped to this project - just what's next, not a whole project-management system.",
    mode: 'do',
    doHint: 'Click one of the sample tasks to select it.',
    completeWhen: () => hasDeleteSelected('[data-tour="tasks-list"]'),
  },

  // ---------- Analyzing data ----------
  {
    section: 'data',
    navTo: 'data-analysis',
    selector: '[data-tour="import-data"]',
    title: 'Bring in your data',
    body: 'Paste CSV/TSV straight in, or upload a .csv, .tsv or Excel (.xlsx) file. It never leaves your machine.',
    mode: 'do',
    doHint: 'Give a dataset a name in the "Dataset name" box (you don\'t have to import anything).',
    completeWhen: () => (document.getElementById('dataset-name')?.value || '').trim().length >= 3,
  },
  {
    section: 'data',
    navTo: 'data-analysis',
    selector: '[data-tour="stats-wizard"]',
    title: "Not sure which test you need?",
    body: 'Pick your numeric column and grouping column, and Cortex checks normality and sample size before recommending a test - showing its reasoning, not hiding it.',
    mode: 'do',
    doHint: 'Click "Check Assumptions" to see what it recommends.',
    ensureVisible: selectDatasetIfNeeded,
    completeWhen: () => /Recommended:/.test(document.querySelector('[data-tour="stats-wizard"]')?.textContent || ''),
  },
  {
    section: 'data',
    navTo: 'data-analysis',
    selector: '[data-tour="chart-generator"]',
    title: 'Or drive it yourself',
    body: 'Prefer to choose? Pick any test and columns yourself, and build bar, line, scatter, histogram or box plots. Nothing is decided for you.',
    ensureVisible: selectDatasetIfNeeded,
    mode: 'do',
    doHint: 'Pick a different chart type from the dropdown.',
    capture: () => document.getElementById('chart-type')?.value,
    completeWhen: (initial) => document.getElementById('chart-type')?.value !== initial,
  },

  // ---------- Writing it up ----------
  {
    section: 'writing',
    navTo: 'manuscript',
    selector: '[data-tour="manuscript-editor"]',
    title: 'Draft your manuscript',
    body: 'Every section of the paper in one place. This sample already has a starter abstract - nothing saves until you click Save Manuscript.',
    mode: 'do',
    doHint: 'Type something into the Abstract box.',
    capture: () => document.getElementById('section-abstract')?.value,
    completeWhen: (initial) => document.getElementById('section-abstract')?.value !== initial,
  },
  {
    section: 'writing',
    navTo: 'manuscript',
    selector: '[data-tour="manuscript-modes"]',
    title: 'Write here, or in Google Docs',
    body: "Stay in Cortex's editor, or link a real Google Doc and edit it right here. Either way your saved papers can sit open beside you.",
    mode: 'do',
    doHint: 'Click "Show Paper Reference Panel" to open your library alongside the draft.',
    completeWhen: () => !!document.querySelector('.manuscript-refpanel'),
  },
  {
    section: 'writing',
    navTo: 'journals',
    selector: '[data-tour="journals-list"]',
    title: 'Track submissions',
    body: 'Target journals, where each one stands, and a curated lookup of formatting requirements for common journals.',
    mode: 'do',
    doHint: 'Click the saved journal to select it.',
    completeWhen: () => hasDeleteSelected('[data-tour="journals-list"]'),
  },
  {
    section: 'writing',
    navTo: 'journals',
    selector: '[data-tour="journals-deadlines"]',
    title: "Deadlines that don't sneak up",
    body: 'Give a journal a deadline and anything due within 30 days (or already overdue) surfaces here until you mark it submitted.',
  },

  // ---------- Settings & extras ----------
  {
    section: 'setup',
    navTo: 'journals',
    selector: '.ai-settings__trigger',
    title: 'AI is optional, and yours to configure',
    body: 'Every AI feature is opt-in and only runs on an explicit click. Use a free local model (Ollama - nothing leaves your machine), or your own API key for OpenAI, Anthropic, Gemini, Mistral or Groq.',
    placement: 'left',
    mode: 'do',
    doHint: 'Open it and have a look at the providers.',
    completeWhen: () => !!document.querySelector('.ai-settings__panel'),
  },
  {
    section: 'setup',
    navTo: 'journals',
    selector: '.lit-settings__trigger',
    title: 'Your own database keys',
    body: 'Institutional access to Scopus, Web of Science, IEEE, Springer or CORE? Add those keys here and searches will include them. Everything works without them too.',
    placement: 'left',
    mode: 'do',
    doHint: 'Open it to see which databases you can add.',
    completeWhen: () => !!document.querySelector('.lit-settings__panel'),
  },
  {
    section: 'setup',
    navTo: 'journals',
    selector: '.palette-picker__trigger',
    title: 'Make it yours',
    body: 'Several palettes, plus light/dark that can follow the time of day.',
    placement: 'left',
    mode: 'do',
    doHint: 'Open it and actually pick a different palette - the whole app recolors.',
    capture: () => document.documentElement.getAttribute('data-palette'),
    completeWhen: (initial) => document.documentElement.getAttribute('data-palette') !== initial,
  },
  {
    section: 'setup',
    navTo: 'ROOT',
    selector: '[data-tour="import-project"]',
    title: 'Bringing a project back in',
    body: "Someone hands you an exported .zip - import it here. It always creates a new project, so it can't overwrite anything you already have.",
  },
];

const FADE_MS = 220;
// After you complete an interactive step, hold before moving on so you can
// actually see what your action did.
const DONE_PAUSE_MS = 4200;
const TOOLTIP_W = 360;
const GAP = 16;
const MARGIN = 14;

export function Tutorial() {
  const [phase, setPhase] = useState('closed'); // closed | intro | creating | touring | done
  const [stepIndex, setStepIndex] = useState(0);
  const [projectId, setProjectId] = useState(null);
  const [rect, setRect] = useState(null);
  const [radius, setRadius] = useState(12);
  const [visible, setVisible] = useState(false);
  const [placement, setPlacement] = useState('bottom');
  const [tipSize, setTipSize] = useState({ w: TOOLTIP_W, h: 230 });
  const [actionDone, setActionDone] = useState(false);
  const [alreadySatisfied, setAlreadySatisfied] = useState(false);
  const [resumable, setResumable] = useState(null);
  const [error, setError] = useState('');

  const pollRef = useRef(null);
  const watchRef = useRef(null);
  const capturedRef = useRef(null);
  const tipRef = useRef(null);
  const navigate = useNavigate();
  const location = useLocation();

  const step = STEPS[stepIndex];
  const isLast = stepIndex === STEPS.length - 1;
  const isDoStep = step?.mode === 'do';
  const sectionIndex = SECTIONS.findIndex((s) => s.key === step?.section);
  const section = SECTIONS[sectionIndex];

  // ---------- open / restore ----------

  useEffect(() => {
    if (!localStorage.getItem(SEEN_KEY)) setPhase('intro');
  }, []);

  const loadProgress = useCallback(async () => {
    try {
      const raw = localStorage.getItem(PROGRESS_KEY);
      if (!raw) return null;
      const saved = JSON.parse(raw);
      if (!saved?.projectId || typeof saved.stepIndex !== 'number') return null;
      await api.getProject(saved.projectId); // gone? then it isn't resumable
      return saved;
    } catch {
      return null;
    }
  }, []);

  useEffect(() => {
    if (phase !== 'intro') return;
    loadProgress().then(setResumable);
  }, [phase, loadProgress]);

  useEffect(() => {
    if (phase !== 'touring' || !projectId) return;
    localStorage.setItem(PROGRESS_KEY, JSON.stringify({ projectId, stepIndex }));
  }, [phase, projectId, stepIndex]);

  // ---------- measuring ----------

  const measure = useCallback((el) => {
    const r = el.getBoundingClientRect();
    const cs = window.getComputedStyle(el);
    setRadius(parseFloat(cs.borderTopLeftRadius) || 12);
    setRect({ top: r.top, left: r.left, width: r.width, height: r.height });
  }, []);

  useLayoutEffect(() => {
    if (!tipRef.current) return;
    const r = tipRef.current.getBoundingClientRect();
    if (Math.abs(r.height - tipSize.h) > 2 || Math.abs(r.width - tipSize.w) > 2) {
      setTipSize({ w: r.width, h: r.height });
    }
  });

  useEffect(() => {
    if (!rect) return;
    setPlacement(choosePlacement(rect, tipSize, step?.placement));
  }, [rect, tipSize, step]);

  // ---------- step driver: navigate, wait for target, reveal ----------

  useEffect(() => {
    clearInterval(pollRef.current);
    if (phase !== 'touring' || !projectId || !step) return undefined;

    setActionDone(false);
    setAlreadySatisfied(false);
    const targetPath = step.navTo === 'ROOT' ? '/' : `/projects/${projectId}${step.navTo ? '/' + step.navTo : ''}`;

    if (location.pathname !== targetPath) {
      setVisible(false);
      const t = setTimeout(() => navigate(targetPath), FADE_MS);
      return () => clearTimeout(t);
    }

    let attempts = 0;
    pollRef.current = setInterval(() => {
      attempts += 1;
      step.ensureVisible?.();
      const el = document.querySelector(step.selector);
      if (el) {
        clearInterval(pollRef.current);
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(() => {
          measure(el);
          setVisible(true);
        }, 260);
      } else if (attempts > 60) {
        clearInterval(pollRef.current);
        setVisible(true); // fall back to a centered tooltip rather than a dead end
      }
    }, 100);
    return () => clearInterval(pollRef.current);
  }, [phase, stepIndex, projectId, location.pathname]); // eslint-disable-line react-hooks/exhaustive-deps

  // ---------- interactive steps: watch for the user doing the thing ----------

  useEffect(() => {
    clearInterval(watchRef.current);
    if (phase !== 'touring' || !isDoStep || !visible || actionDone) return undefined;

    // Steps that complete on a *change* (a dropdown switched, text edited,
    // palette swapped) need the starting value to compare against.
    capturedRef.current = step.capture ? step.capture() : null;

    const check = () => {
      try {
        return !!step.completeWhen?.(capturedRef.current);
      } catch {
        return false;
      }
    };

    // If the action is already satisfied when we arrive - usually because
    // they're stepping Back through something they already did - don't
    // auto-advance, or the step would be impossible to revisit. Only a
    // fresh false -> true transition counts.
    const satisfiedOnArrival = check();
    setAlreadySatisfied(satisfiedOnArrival);
    if (satisfiedOnArrival) return undefined;

    watchRef.current = setInterval(() => {
      if (check()) {
        clearInterval(watchRef.current);
        setActionDone(true);
      }
    }, 250);
    return () => clearInterval(watchRef.current);
  }, [phase, stepIndex, isDoStep, visible, actionDone]); // eslint-disable-line react-hooks/exhaustive-deps

  // Advance a beat after they've done it, so the "done" tick is visible.
  // Owns its own timer (rather than scheduling from inside the watcher's
  // callback) so React cleans it up properly on any state change.
  useEffect(() => {
    if (phase !== 'touring' || !actionDone) return undefined;
    const t = setTimeout(() => goTo(stepIndex + 1), DONE_PAUSE_MS);
    return () => clearTimeout(t);
  }, [phase, actionDone, stepIndex]); // eslint-disable-line react-hooks/exhaustive-deps

  // ---------- keep aligned ----------

  useEffect(() => {
    if (phase !== 'touring') return undefined;
    function reflow() {
      const el = step && document.querySelector(step.selector);
      if (el) measure(el);
    }
    window.addEventListener('resize', reflow);
    window.addEventListener('scroll', reflow, true);
    return () => {
      window.removeEventListener('resize', reflow);
      window.removeEventListener('scroll', reflow, true);
    };
  }, [phase, stepIndex, measure]); // eslint-disable-line react-hooks/exhaustive-deps

  // ---------- keyboard ----------

  useEffect(() => {
    if (phase === 'closed') return undefined;
    function onKey(e) {
      if (e.key === 'Escape') { exit(); return; }
      if (phase !== 'touring' || !visible) return;
      if (e.key === 'ArrowRight' || e.key === 'Enter') { e.preventDefault(); goTo(stepIndex + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); goTo(stepIndex - 1); }
    }
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (phase === 'touring' && visible) tipRef.current?.focus({ preventScroll: true });
  }, [phase, stepIndex, visible]);

  // ---------- controls ----------

  function stopTimers() {
    clearInterval(pollRef.current);
    clearInterval(watchRef.current);
  }

  function exit() {
    stopTimers();
    localStorage.setItem(SEEN_KEY, '1');
    setPhase('closed');
    setVisible(false);
    setRect(null);
  }

  function finish() {
    stopTimers();
    localStorage.setItem(SEEN_KEY, '1');
    localStorage.removeItem(PROGRESS_KEY);
    setVisible(false);
    setPhase('done');
  }

  function goTo(i) {
    if (i < 0) return;
    if (i >= STEPS.length) { finish(); return; }
    stopTimers();
    setStepIndex(i);
  }

  function openIntro() {
    setError('');
    setPhase('intro');
  }

  async function startTour(resumeFrom) {
    setError('');
    if (resumeFrom) {
      setProjectId(resumeFrom.projectId);
      setStepIndex(resumeFrom.stepIndex);
      setPhase('touring');
      return;
    }
    setPhase('creating');
    try {
      const data = await api.createSampleProject();
      setProjectId(data.project.id);
      setStepIndex(0);
      setPhase('touring');
      navigate(`/projects/${data.project.id}`);
    } catch (e) {
      setError(e.message);
      setPhase('intro');
    }
  }

  const pct = Math.round(((stepIndex + 1) / STEPS.length) * 100);
  const tipPos = rect ? tooltipPosition(rect, tipSize, placement) : null;

  return (
    <>
      <button
        className="tutorial__trigger"
        onClick={openIntro}
        aria-haspopup="dialog"
        aria-label="Open guided tour"
        title="Guided tour"
      >
        ?
      </button>

      {phase === 'intro' && (
        <div className="tutorial__overlay" role="dialog" aria-modal="true" aria-labelledby="tour-intro-title">
          <div className="tutorial__modal">
            <button className="tutorial__close" onClick={exit} aria-label="Close">&times;</button>
            <h2 className="tutorial__heading" id="tour-intro-title">Take the tour</h2>
            <p className="tutorial__body">
              A hands-on walkthrough of Cortex in {STEPS.length} steps. It sets up a real sample
              project for you, and along the way you'll actually do a few things yourself - the
              tour waits for you and moves on when you're done.
            </p>
            <ul className="tutorial__toc">
              {SECTIONS.map((s) => (
                <li key={s.key}>
                  <span className="tutorial__toc-dot" aria-hidden="true" />
                  {s.label}
                </li>
              ))}
            </ul>
            {error && <p role="alert" className="tutorial__error">{error}</p>}
            <div className="tutorial__actions tutorial__actions--end">
              <button className="tutorial__skip" onClick={exit}>Not now</button>
              {resumable && (
                <button className="tutorial__btn tutorial__btn--secondary" onClick={() => startTour(resumable)}>
                  Resume (step {resumable.stepIndex + 1})
                </button>
              )}
              <button className="tutorial__btn tutorial__btn--primary" onClick={() => startTour(null)}>
                {resumable ? 'Start over' : 'Start tour'}
              </button>
            </div>
          </div>
        </div>
      )}

      {phase === 'creating' && (
        <div className="tutorial__overlay" role="dialog" aria-modal="true" aria-label="Preparing tour">
          <div className="tutorial__modal tutorial__modal--slim">
            <div className="tutorial__spinner" aria-hidden="true" />
            <p className="tutorial__body" style={{ margin: 0 }}>Setting up your sample project&hellip;</p>
          </div>
        </div>
      )}

      {phase === 'touring' && (
        <>
          {/* 'read' steps block the page; 'do' steps let you actually use it */}
          {!isDoStep && <div className="tour__blocker" />}

          <div
            className={`tour__spotlight ${isDoStep && !alreadySatisfied ? 'tour__spotlight--active' : ''} ${actionDone || alreadySatisfied ? 'tour__spotlight--done' : ''}`}
            style={{
              opacity: visible && rect ? 1 : 0,
              top: (rect?.top ?? 0) - 6,
              left: (rect?.left ?? 0) - 6,
              width: (rect?.width ?? 0) + 12,
              height: (rect?.height ?? 0) + 12,
              borderRadius: radius + 6,
            }}
          />

          <div
            ref={tipRef}
            tabIndex={-1}
            role="dialog"
            aria-live="polite"
            aria-labelledby="tour-step-title"
            className={`tour__tooltip tour__tooltip--${placement}`}
            style={{
              opacity: visible ? 1 : 0,
              pointerEvents: visible ? 'auto' : 'none',
              ...(tipPos || { top: '50%', left: '50%', transform: 'translate(-50%,-50%)' }),
            }}
          >
            {rect && <span className="tour__arrow" style={arrowStyle(rect, tipPos, placement)} aria-hidden="true" />}

            <div className="tour__progress">
              <div className="tour__progress-bar"><div className="tour__progress-fill" style={{ width: `${pct}%` }} /></div>
              <div className="tour__progress-meta">
                <span className="tour__section">{section?.label}</span>
                <span>{stepIndex + 1} / {STEPS.length}</span>
              </div>
            </div>

            <h3 className="tour__title" id="tour-step-title">{step.title}</h3>
            <p className="tour__body">{step.body}</p>
            {step.note && <p className="tour__note">{step.note}</p>}

            {isDoStep && (
              <div className={`tour__do ${actionDone || alreadySatisfied ? 'tour__do--done' : ''}`}>
                <span className="tour__do-icon" aria-hidden="true">{actionDone || alreadySatisfied ? '✓' : '→'}</span>
                <span>
                  {actionDone
                    ? "Nice - that's it. Have a look at what changed, or hit Continue."
                    : alreadySatisfied
                      ? "Already done - Next when you're ready."
                      : step.doHint}
                </span>
              </div>
            )}

            <div className="tutorial__actions">
              <button className="tutorial__skip" onClick={exit}>End tour</button>
              <div className="tutorial__nav">
                {stepIndex > 0 && (
                  <button className="tutorial__btn tutorial__btn--secondary" onClick={() => goTo(stepIndex - 1)} disabled={!visible}>
                    Back
                  </button>
                )}
                <button className="tutorial__btn tutorial__btn--primary" onClick={() => goTo(stepIndex + 1)} disabled={!visible}>
                  {isLast ? 'Finish' : actionDone ? 'Continue' : isDoStep && !alreadySatisfied ? 'Skip this' : 'Next'}
                </button>
              </div>
            </div>
          </div>
        </>
      )}

      {phase === 'done' && (
        <div className="tutorial__overlay" role="dialog" aria-modal="true" aria-labelledby="tour-done-title">
          <div className="tutorial__modal">
            <button className="tutorial__close" onClick={() => setPhase('closed')} aria-label="Close">&times;</button>
            <h2 className="tutorial__heading" id="tour-done-title">You're set</h2>
            <p className="tutorial__body">Here's what you just covered:</p>
            <ul className="tutorial__toc tutorial__toc--done">
              {SECTIONS.map((s) => (
                <li key={s.key}>
                  <span className="tutorial__toc-check" aria-hidden="true">✓</span>
                  {s.label}
                </li>
              ))}
            </ul>
            <p className="tutorial__body">
              The sample project is yours - keep poking at it, or delete it from the All Projects
              screen. The <strong>?</strong> button replays this tour anytime.
            </p>
            <div className="tutorial__actions tutorial__actions--end">
              <button className="tutorial__skip" onClick={() => { setStepIndex(0); setPhase('touring'); }}>
                Replay
              </button>
              <button className="tutorial__btn tutorial__btn--primary" onClick={() => setPhase('closed')}>
                Start exploring
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// ---------- positioning helpers ----------

function choosePlacement(rect, tip, preferred) {
  const fits = {
    bottom: window.innerHeight - (rect.top + rect.height) >= tip.h + GAP + MARGIN,
    top: rect.top >= tip.h + GAP + MARGIN,
    right: window.innerWidth - (rect.left + rect.width) >= tip.w + GAP + MARGIN,
    left: rect.left >= tip.w + GAP + MARGIN,
  };
  if (preferred && fits[preferred]) return preferred;
  return ['bottom', 'top', 'right', 'left'].find((p) => fits[p]) || 'bottom';
}

function tooltipPosition(rect, tip, placement) {
  const clampX = (x) => Math.min(Math.max(x, MARGIN), window.innerWidth - tip.w - MARGIN);
  const clampY = (y) => Math.min(Math.max(y, MARGIN), window.innerHeight - tip.h - MARGIN);
  const centerX = rect.left + rect.width / 2 - tip.w / 2;
  const centerY = rect.top + rect.height / 2 - tip.h / 2;

  switch (placement) {
    case 'top':
      return { top: clampY(rect.top - tip.h - GAP), left: clampX(centerX) };
    case 'right':
      return { top: clampY(centerY), left: clampX(rect.left + rect.width + GAP) };
    case 'left':
      return { top: clampY(centerY), left: clampX(rect.left - tip.w - GAP) };
    case 'bottom':
    default:
      return { top: clampY(rect.top + rect.height + GAP), left: clampX(centerX) };
  }
}

// Keeps the little arrow pointing at the target even after the tooltip is
// clamped back inside the viewport.
function arrowStyle(rect, pos, placement) {
  if (!pos) return { display: 'none' };
  const targetCX = rect.left + rect.width / 2;
  const targetCY = rect.top + rect.height / 2;
  if (placement === 'top' || placement === 'bottom') {
    return { left: Math.min(Math.max(targetCX - pos.left, 18), TOOLTIP_W - 18) };
  }
  return { top: Math.max(targetCY - pos.top, 18) };
}
