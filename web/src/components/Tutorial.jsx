import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { api } from '../api/client';
import './Tutorial.css';

const SEEN_KEY = 'cortex_tutorial_seen';

/**
 * A real guided tour: creates an actual sample project via the same API
 * "Try a Sample Project" uses, then navigates the real router through it,
 * spotlighting real UI elements with real (sample) data - not a mockup.
 * The rest of the page is click-blocked while touring, so nothing gets
 * triggered for real (no accidental external searches, AI calls, etc.)
 * except the one safe, local-only dataset selection needed to reveal the
 * stats wizard on the Data & Analysis step.
 */

const selectSampleDataset = () => {
  if (!document.querySelector('[data-tour="stats-wizard"]')) {
    document.querySelector('[data-tour="datasets-list"] li button')?.click();
  }
};

const STEPS = [
  {
    navTo: '',
    selector: '[data-tour="overview-details"]',
    title: 'Your project at a glance',
    body: "This is Overview - a snapshot of the project's details. The tabs on the left are where you actually do things.",
  },
  {
    navTo: '',
    selector: '[data-tour="overview-methodology"]',
    title: 'Methodology progress, at a glance',
    body: 'A quick read on how far along the checklist you are, without leaving Overview.',
  },
  {
    navTo: '',
    selector: '[data-tour="overview-backup"]',
    title: 'Back up or share this project',
    body: 'Export everything in this project - details, papers, datasets, manuscript, progress - as one .zip file. Hand it to a co-author, or use it as a backup.',
  },
  {
    navTo: 'literature-review',
    selector: '[data-tour="lit-search"]',
    title: 'Search real literature',
    body: 'Describe a research idea here and Cortex searches real, free sources (Europe PMC, CrossRef, arXiv, and more) for related papers, with a novelty score against your idea. Check "Search with AI" (if set up) for a synthesis + gap analysis too.',
  },
  {
    navTo: 'paper-library',
    selector: '[data-tour="paper-library-list"]',
    title: 'Your saved papers',
    body: "Papers you save from Literature Review land here. This sample project already has one - click it to see full details, add annotations, or open the source.",
  },
  {
    navTo: 'paper-library',
    selector: '[data-tour="citation-export"]',
    title: 'Citations, formatted for you',
    body: 'Pick a style (APA, MLA, Chicago, Vancouver) to copy any citation, or download your whole library as BibTeX (LaTeX) or RIS (EndNote/Zotero/Mendeley).',
  },
  {
    navTo: 'methodology',
    selector: '[data-tour="methodology-checklist"]',
    title: 'Methodology checklist',
    body: 'Every project gets a checklist matched to its research type, with recommended tools per step. This sample already has the first two checked off.',
  },
  {
    navTo: 'hypotheses',
    selector: '[data-tour="hypotheses-list"]',
    title: 'Track your hypotheses',
    body: 'A lightweight place to track candidate hypotheses and their status as your thinking evolves - with AI feedback available on how testable each one is.',
  },
  {
    navTo: 'tasks',
    selector: '[data-tour="tasks-list"]',
    title: 'Tasks & milestones',
    body: "Simple task tracking for this project - nothing fancy, just a checklist of what's next.",
  },
  {
    navTo: 'data-analysis',
    selector: '[data-tour="import-data"]',
    title: 'Bring in your data',
    body: 'Paste CSV/tab-separated data, or upload a file directly - CSV, TSV, or Excel (.xlsx) all work.',
  },
  {
    navTo: 'data-analysis',
    selector: '[data-tour="stats-wizard"]',
    title: 'Not sure which test to run?',
    body: '"Which Test Should I Use?" checks normality and sample size on your data, then recommends - and can run - the right statistical test, like a stats calculator\'s guided mode.',
    ensureVisible: selectSampleDataset,
  },
  {
    navTo: 'data-analysis',
    selector: '[data-tour="chart-generator"]',
    title: 'Or pick everything yourself',
    body: 'Prefer full control? Pick any test and columns directly under "Run a Statistical Test", or generate a bar/line/scatter/histogram/box/pie chart here.',
    ensureVisible: selectSampleDataset,
  },
  {
    navTo: 'manuscript',
    selector: '[data-tour="manuscript-editor"]',
    title: 'Draft your manuscript',
    body: 'Write each section here (abstract, intro, methods, results, discussion, references). This sample project already has a starter abstract.',
  },
  {
    navTo: 'manuscript',
    selector: '[data-tour="manuscript-modes"]',
    title: 'Or write in Google Docs',
    body: 'Switch to Google Docs mode to link and edit a real Google Doc instead, live - and toggle the Paper Reference Panel to see your saved papers side-by-side while you write, in either mode.',
  },
  {
    navTo: 'journals',
    selector: '[data-tour="journals-list"]',
    title: 'Track submissions',
    body: 'Track target journals, submission status, and an optional deadline for each.',
  },
  {
    navTo: 'journals',
    selector: '[data-tour="journals-deadlines"]',
    title: 'Deadline reminders',
    body: "Anything due within 30 days (or overdue) surfaces here automatically - this sample journal's deadline is 20 days out.",
  },
  {
    navTo: 'journals',
    selector: '.ai-settings__trigger',
    title: 'Optional AI features',
    body: 'This sparkle icon is available on every page - set up a free local model (Ollama) or add your own API key (OpenAI, Anthropic, Gemini, Mistral, Groq). Every AI feature stays off until you click a button that uses it.',
  },
  {
    navTo: 'journals',
    selector: '.lit-settings__trigger',
    title: 'Your own literature database keys',
    body: 'Add a personal/institutional API key for a paid database (Elsevier/Scopus, Web of Science, IEEE Xplore, Springer Nature, CORE), or raise your Semantic Scholar rate limit - optional, nothing requires it.',
  },
  {
    navTo: 'journals',
    selector: '.palette-picker__trigger',
    title: 'Make it yours',
    body: 'Pick a color palette and light/dark/auto appearance - purely cosmetic, applies everywhere in the app.',
  },
  {
    navTo: 'ROOT',
    selector: '[data-tour="import-project"]',
    title: 'Bring a project back in',
    body: 'Got a project exported elsewhere (by you, or a co-author)? Import it here - it always creates a new project, so it can never overwrite anything.',
  },
];

const FADE_MS = 220;

export function Tutorial() {
  const [phase, setPhase] = useState('closed'); // closed | intro | creating | touring | outro
  const [stepIndex, setStepIndex] = useState(0);
  const [projectId, setProjectId] = useState(null);
  const [rect, setRect] = useState(null);
  const [visible, setVisible] = useState(false);
  const [error, setError] = useState('');
  const pollRef = useRef(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!localStorage.getItem(SEEN_KEY)) setPhase('intro');
  }, []);

  useEffect(() => {
    if (phase === 'closed') return undefined;
    function onKey(e) { if (e.key === 'Escape') close(); }
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }); // eslint-disable-line react-hooks/exhaustive-deps

  const measure = useCallback((el) => {
    const r = el.getBoundingClientRect();
    setRect({ top: r.top, left: r.left, width: r.width, height: r.height });
  }, []);

  // Drives navigation + waits for (and measures) each step's real target
  // element. Same-page step changes never hide the overlay - rect just
  // updates and CSS transitions glide it to the new spot. Cross-page steps
  // fade out first (so nothing floats over the wrong page mid-navigation),
  // measure the new element while still invisible, then fade back in.
  useEffect(() => {
    clearInterval(pollRef.current);
    if (phase !== 'touring' || !projectId) return undefined;

    const step = STEPS[stepIndex];
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
      } else if (attempts > 50) {
        clearInterval(pollRef.current);
      }
    }, 100);
    return () => clearInterval(pollRef.current);
  }, [phase, stepIndex, projectId, location.pathname]); // eslint-disable-line react-hooks/exhaustive-deps

  // Keep the spotlight aligned on scroll/resize (glides via the same CSS
  // transition, since visibility doesn't change here).
  useEffect(() => {
    if (phase !== 'touring') return undefined;
    function reflow() {
      const step = STEPS[stepIndex];
      const el = step && document.querySelector(step.selector);
      if (el) measure(el);
    }
    window.addEventListener('resize', reflow);
    window.addEventListener('scroll', reflow, true);
    return () => {
      window.removeEventListener('resize', reflow);
      window.removeEventListener('scroll', reflow, true);
    };
  }, [phase, stepIndex, measure]);

  function close() {
    localStorage.setItem(SEEN_KEY, '1');
    clearInterval(pollRef.current);
    setPhase('closed');
    setVisible(false);
    setRect(null);
  }

  function openIntro() {
    setError('');
    setPhase('intro');
  }

  async function beginTour() {
    setPhase('creating');
    setError('');
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

  function next() {
    if (stepIndex < STEPS.length - 1) setStepIndex((i) => i + 1);
    else setPhase('outro');
  }

  function back() {
    setStepIndex((i) => Math.max(0, i - 1));
  }

  const isLast = stepIndex === STEPS.length - 1;

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
        <div className="tutorial__overlay" role="dialog" aria-modal="true" aria-label="Cortex guided tour">
          <div className="tutorial__modal tutorial__modal--center">
            <button className="tutorial__close" onClick={close} aria-label="Close">&times;</button>
            <h2 className="tutorial__heading">Take a guided tour</h2>
            <p className="tutorial__body">
              This creates a real sample project (papers, a hypothesis, a dataset, a manuscript
              draft, a journal entry - all pre-filled) and walks you through each part of Cortex
              using it, for real. It's yours afterward to explore or delete.
            </p>
            {error && <p role="alert" className="tutorial__error">{error}</p>}
            <div className="tutorial__actions tutorial__actions--center">
              <button className="tutorial__skip" onClick={close}>No thanks</button>
              <button className="tutorial__btn tutorial__btn--primary" onClick={beginTour}>Start Tour</button>
            </div>
          </div>
        </div>
      )}

      {phase === 'creating' && (
        <div className="tutorial__overlay" role="dialog" aria-modal="true" aria-label="Setting up tour">
          <div className="tutorial__modal tutorial__modal--center">
            <p className="tutorial__body" style={{ margin: 0 }}>Setting up your sample project&hellip;</p>
          </div>
        </div>
      )}

      {phase === 'touring' && (
        <>
          <div className="tour__blocker" onClick={(e) => e.preventDefault()} />
          <div
            className="tour__spotlight"
            style={{
              opacity: visible && rect ? 1 : 0,
              top: (rect?.top ?? 0) - 8,
              left: (rect?.left ?? 0) - 8,
              width: (rect?.width ?? 0) + 16,
              height: (rect?.height ?? 0) + 16,
            }}
          />
          <div
            className="tour__tooltip"
            style={{
              opacity: visible && rect ? 1 : 0,
              pointerEvents: visible && rect ? 'auto' : 'none',
              ...(rect ? tooltipStyle(rect) : { top: '50%', left: '50%' }),
            }}
          >
            <div className="tour__step-count">Step {stepIndex + 1} of {STEPS.length}</div>
            <h3 className="tour__title">{STEPS[stepIndex].title}</h3>
            <p className="tour__body">{STEPS[stepIndex].body}</p>
            <div className="tutorial__actions">
              <button className="tutorial__skip" onClick={close}>End tour</button>
              <div className="tutorial__nav">
                {stepIndex > 0 && <button className="tutorial__btn tutorial__btn--secondary" onClick={back} disabled={!visible}>Back</button>}
                <button className="tutorial__btn tutorial__btn--primary" onClick={next} disabled={!visible}>{isLast ? 'Finish' : 'Next'}</button>
              </div>
            </div>
          </div>
        </>
      )}

      {phase === 'outro' && (
        <div className="tutorial__overlay" role="dialog" aria-modal="true" aria-label="Tour complete">
          <div className="tutorial__modal tutorial__modal--center">
            <button className="tutorial__close" onClick={close} aria-label="Close">&times;</button>
            <h2 className="tutorial__heading">That's the tour</h2>
            <p className="tutorial__body">
              This sample project is yours now - keep exploring it, or delete it anytime from the
              "All Projects" screen. You can replay this tour later with the <strong>?</strong> button.
            </p>
            <div className="tutorial__actions tutorial__actions--center">
              <button className="tutorial__btn tutorial__btn--primary" onClick={close}>Done</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function tooltipStyle(rect) {
  const spaceBelow = window.innerHeight - (rect.top + rect.height);
  const placeBelow = spaceBelow > 220 || rect.top < 220;
  return placeBelow
    ? { top: Math.min(rect.top + rect.height + 20, window.innerHeight - 260), left: clampLeft(rect.left) }
    : { top: Math.max(rect.top - 240, 16), left: clampLeft(rect.left) };
}

function clampLeft(left) {
  const width = 340;
  return Math.min(Math.max(left, 16), window.innerWidth - width - 16);
}
