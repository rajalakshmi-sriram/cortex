# Cortex: Research Workspace

Cortex is a research workspace for planning, running, and writing up a
research project end to end — literature search, methodology tracking,
hypotheses, statistical analysis, manuscript drafting, and journal
submission tracking, all in one place.

**It's a general-purpose research tool, not a neuroscience-specific one.**
Every project picks a research type (theoretical, experimental, exploratory,
pilot, literature review, or clinical) and gets a methodology checklist
matched to that type — the same structure applies whether you're running a
biochemistry assay, a chemistry synthesis study, a clinical trial, an
ecology field study, a computational/theoretical project, or anything else.
Literature search pulls from general-purpose sources (Europe PMC, CrossRef,
arXiv, ERIC, Semantic Scholar, OpenAlex), not a neuroscience-only database.

Available as a web app (Flask backend + React frontend) and as a native
desktop app for macOS (built with Tauri) - see
[DESKTOP_APP_BUILD.md](DESKTOP_APP_BUILD.md) for building the desktop app.

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
- **Data & Analysis** - import a dataset (CSV/TSV), run real statistical
  tests (t-tests, ANOVA, correlation, regression, non-parametric tests,
  etc.) and generate charts, entirely under your control (you pick the test
  and the columns - nothing is decided automatically).
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

## License

Personal research tool - no license file included; treat as all rights
reserved unless you add one.
