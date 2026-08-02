# Cortex: Research Workspace

Cortex is a research workspace for planning, running, and writing up a
research project end to end — literature search, methodology tracking,
hypotheses, statistical analysis, manuscript drafting, and journal
submission tracking, all in one place.

**It's a general-purpose research tool, not a neuroscience-specific one.**
Every project picks one of 12 research types (see the table below) and gets
a methodology checklist matched to that type — the same structure applies
whether you're running a biochemistry assay, a chemistry synthesis study, a
clinical trial, an ecology field study, a computational/theoretical
project, or anything else. Literature search pulls from general-purpose
sources (Europe PMC, CrossRef, arXiv, ERIC, Semantic Scholar, OpenAlex),
not a neuroscience-only database.

Available as a web app (Flask backend + React frontend) and as a native
desktop app for macOS (built with Tauri) - see
[DESKTOP_APP_BUILD.md](DESKTOP_APP_BUILD.md) for building the desktop app.

## Research types

Each type gets its own methodology checklist and recommended reporting
guidelines (e.g. CONSORT, STROBE, PRISMA) - defined in
[`config/config.py`](config/config.py).

| Type | Goal | Methodology |
|---|---|---|
| **Theoretical** | Develop or improve a formal theory | Build/refine a conceptual framework, test for logical consistency - no new data collection |
| **Experimental** | Establish causal relationships | Manipulate variables under controlled conditions (covers fundamental/basic-science as well as applied studies) |
| **Quasi-Experimental** | Approximate causal inference without randomization | Compare naturally occurring groups, statistically control for confounds |
| **Observational** | Identify relationships between variables | Measure variables as they naturally occur, without manipulation |
| **Descriptive** | Document a novel phenomenon or population | Systematic observation/measurement and characterization, no relationship-testing |
| **Exploratory** | Deeply understand a single case | Case study: gather evidence, compare against known generalizations |
| **Pilot** | Test feasibility ahead of a full study | Small-cohort version of an experimental design |
| **Translational** | Bridge a lab finding to practice | Preclinical testing through early applied/human testing |
| **Computational** | Build/validate a model or simulation | Implement a model or algorithm, validate against benchmarks, run simulations |
| **Literature Review** | Narratively synthesize existing research | Search, screen, extract, synthesize, identify gaps |
| **Meta-Analytic** | Quantitatively pool results across studies | Systematic search, effect-size extraction, statistical pooling, heterogeneity testing |
| **Clinical** | Evaluate an intervention in human participants | Protocol design, ethics approval, recruitment, safety monitoring, outcome analysis |

## What it does

- **Project Search** - narrow a broad topic into a specific research focus,
  aims, and questions, backed by a real literature search.
- **Literature Review** - search real papers across multiple free sources,
  see similarity/novelty scoring against your idea, and save results to a
  library.
- **Paper Library** - saved papers with annotations and one-click citation
  formatting (APA, MLA, Chicago, Vancouver) or BibTeX export.
- **Methodology** - a checklist of the standard steps for your project's
  research type, plus relevant reporting guidelines and recommended tools
  per step.
- **Hypotheses** - track candidate hypotheses and their status.
- **Tasks** - lightweight task/milestone tracking.
- **Data & Analysis** - import a dataset (CSV/TSV) and run a real statistical
  test on the columns you choose (descriptive statistics, independent/
  paired/one-sample t-tests, one-way ANOVA, Mann-Whitney U, Wilcoxon
  signed-rank, Kruskal-Wallis, Pearson/Spearman correlation, a correlation
  matrix, chi-square, and simple/multiple linear regression), plus bar,
  line, scatter, histogram, and box-plot charts. Nothing is decided
  automatically - you pick the test/chart type and the columns.
- **Manuscript** - draft each section of a manuscript (abstract, intro,
  methods, results, discussion, references) with autosave.
- **Journals** - track target journals and submission status, and look up
  curated formatting/structure guidelines for common journals.

## Optional AI features

AI features are entirely opt-in - nothing runs automatically, and every AI
action is triggered by an explicit button click. You choose the provider:

- **Local (Ollama)** - free, fully private, runs on your own machine. No
  API key, no data leaves your computer. Install
  [Ollama](https://ollama.com) separately and pull a model (default:
  `qwen2.5:7b-instruct`, CPU-friendly).
- **Your own OpenAI or Anthropic API key** - if you'd rather use a hosted
  model, add your own key in the AI Settings panel (sparkle icon,
  bottom-right of the app).

Where AI shows up, grounded only in your own real data (never inventing
facts beyond what you gave it):
- Literature synthesis + gap analysis during a search
- Manuscript feedback aimed at publication quality
- Hypothesis specificity/testability feedback
- Statistical results interpretation, related to your hypotheses
- Paper summarization
- Follow-up chat on any of the above, to ask clarifying questions

## Getting started (development)

Backend (Flask, port 5050):
```bash
python3.11 -m venv venv-run
venv-run/bin/pip install -r requirements.txt
venv-run/bin/python3 run.py
```

Frontend (React + Vite, port 5173, proxies `/api` to the backend):
```bash
cd web
npm install
npm run dev
```

Then open `http://localhost:5173`.

## Building the desktop app

See [DESKTOP_APP_BUILD.md](DESKTOP_APP_BUILD.md) for the full build guide
(macOS is fully built and tested; Windows build config is included but
needs to be built on a Windows machine or CI, since neither PyInstaller nor
the Tauri toolchain cross-compile).

## Project structure

```
app/            Flask backend: routes, project storage, literature search,
                statistics/chart engines, AI assistant, citation formatting
config/         App configuration (research types, methodology step
                sequences, data directories)
web/            React frontend (Vite)
desktop-tauri/  Tauri desktop app wrapper (macOS/Windows)
run.py          Development entry point for the backend
run_desktop.py  Production entry point used by the packaged desktop app
cortex_backend.spec   PyInstaller spec for bundling the backend
```

Saved project data lives in `data/` during development, or in a normal
per-user app-data folder when running as the packaged desktop app
(`~/Library/Application Support/Cortex` on macOS) - never inside the app
bundle itself.

## Data sources

Literature search draws on free, public sources: Europe PMC, CrossRef,
arXiv, ERIC, and Semantic Scholar, plus OpenAlex. Optional API keys
(Elsevier/Scopus, Web of Science) can be added via `.env` if you have them,
but nothing requires a paid subscription to use.

## License & legal

MIT licensed - see [LICENSE](LICENSE). See [LEGAL.md](LEGAL.md) for the
full disclosure on AI-generated content, third-party data sharing (what
leaves your machine if you use a hosted AI provider vs. local Ollama), and
data storage.

This app's code was written with substantial assistance from
[Claude Code](https://claude.com/claude-code), Anthropic's AI coding tool.
