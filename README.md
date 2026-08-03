# Cortex: Research Workspace

Cortex is a research workspace for planning, running, and writing up a
research project end to end — literature search, methodology tracking,
hypotheses, statistical analysis, manuscript drafting, and journal
submission tracking, all in one place. It's general-purpose: pick one of
12 research types and get a methodology checklist matched to it, whether
that's a lab experiment, a clinical trial, a field study, a computational
project, or a literature review.

Available two ways:
- **A native desktop app for macOS** - no install of Python or Node
  required, just [download and open it](#macos-app-no-setup-required).
- **A web app** (Flask backend + React frontend) that you run yourself on
  any OS (macOS, Windows, or Linux) - see [Running the web
  app](#running-the-web-app-macos-windows-linux) below. This is also how
  you'd run it if you're developing on the code.

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
- **Data & Analysis** - import a CSV/TSV dataset and run statistical tests
  (t-tests, ANOVA, non-parametric equivalents, correlation, regression,
  chi-square) or charts (bar, line, scatter, histogram, box plot) on the
  columns you choose - nothing is decided automatically.
- **Manuscript** - draft each section of a manuscript (abstract, intro,
  methods, results, discussion, references) with autosave.
- **Journals** - track target journals and submission status, and look up
  curated formatting/structure guidelines for common journals.

## Optional AI features

AI features are opt-in, triggered by an explicit button click. Choose a
provider:

- **Local (Ollama)** - free, fully private, runs on your own machine.
  Install [Ollama](https://ollama.com) separately and pull a model
  (default: `qwen2.5:7b-instruct`, CPU-friendly).
- **Your own API key** for a hosted provider - OpenAI, Anthropic, Google
  Gemini, Mistral, or Groq - added in the AI Settings panel (sparkle icon,
  bottom-right of the app).
- **A custom OpenAI-compatible endpoint** - point Cortex at any other
  OpenAI-compatible server (OpenRouter, Together AI, a self-hosted
  vLLM/LM Studio, etc.) via a base URL you supply.

Used for: literature synthesis and gap analysis, manuscript feedback,
hypothesis feedback, statistical results interpretation, paper
summarization, and follow-up chat on any of the above.

## macOS app (no setup required)

For most Mac users, this is the easiest way to use Cortex - no Python,
Node, or terminal required.

1. **[Download the latest `.dmg`](https://github.com/rajalakshmi-sriram/cortex/releases/latest)**
   from the Releases page (look for `Cortex-<version>-arm64.dmg`, for
   Apple Silicon Macs - M1/M2/M3/M4).
2. Open the downloaded `.dmg` and drag **Cortex** into your **Applications**
   folder.
3. Open **Cortex** from Applications (or Spotlight). The **first time**,
   macOS will say it's from an "unidentified developer" - expected for an
   app distributed outside the Mac App Store. To open it anyway:
   - Right-click (or Control-click) the Cortex app icon → **Open** → click
     **Open** again in the dialog, **or**
   - Go to **System Settings → Privacy & Security**, scroll to the message
     about Cortex being blocked, and click **Open Anyway**.

   Only needed once - after the first launch it opens normally.

   > **Says "Cortex is damaged and can't be opened" instead?** This is a
   > stricter form of the same warning, not actual corruption - it shows up
   > because Cortex isn't signed with a paid Apple Developer certificate.
   > Open Terminal and run:
   > ```bash
   > xattr -cr /Applications/Cortex.app
   > ```
   > then open Cortex again.

Project data is saved locally on your own Mac
(`~/Library/Application Support/Cortex`), not uploaded anywhere.

*Windows and Linux users: there isn't a packaged desktop app for those
platforms yet - use the web app below instead, which works identically.*

To build the desktop app from source instead of downloading it, see
[DESKTOP_APP_BUILD.md](DESKTOP_APP_BUILD.md).

## Running the web app (macOS, Windows, Linux)

For running Cortex from source - needed on Windows/Linux, or for
development. Requires [Python 3.9+](https://www.python.org/downloads/) and
[Node.js](https://nodejs.org/).

**1. Clone (or download) the repo and open a terminal in that folder** -
the one containing `run.py` and `requirements.txt`.

**2. Start the backend** (Flask, serves on port 5050):

macOS / Linux:
```bash
python3 -m venv venv-run
venv-run/bin/pip install -r requirements.txt
venv-run/bin/python3 run.py
```

Windows (PowerShell):
```powershell
py -m venv venv-run
venv-run\Scripts\pip install -r requirements.txt
venv-run\Scripts\python run.py
```

> **"Address already in use" on port 5050:** a previous backend run is
> still active. Find and stop it:
> - macOS/Linux: `lsof -nP -iTCP:5050 -sTCP:LISTEN`, then `kill <PID>`.
> - Windows: `netstat -ano | findstr :5050`, then `taskkill /PID <PID> /F`.

Leave that terminal running - the backend needs to stay up.

**3. In a *second* terminal**, start the frontend (React + Vite, proxies
`/api` requests to the backend):
```bash
cd web
npm install
npm run dev
```

**4. Open the `http://localhost:...` URL printed in that terminal.**

To stop everything, press `Ctrl+C` in both terminals.

## Project structure

```
app/                     Flask backend: routes, project storage,
                         literature search, statistics/chart engines, AI
                         assistant, citation formatting
config/                  App configuration (research types, methodology
                         step sequences, data directories)
web/                     React frontend (Vite)
desktop-tauri/           Tauri desktop app wrapper (macOS/Windows)
run.py                   Development entry point for the backend
run_desktop.py           Production entry point used by the packaged
                         desktop app
cortex_backend.spec      PyInstaller spec for bundling the backend
DESKTOP_APP_BUILD.md     How to build the desktop app from source
LEGAL.md                 AI-generated content, data sharing, and storage
                         disclosures
```

Saved project data lives in `data/` during development, or in a normal
per-user app-data folder when running as the packaged desktop app
(`~/Library/Application Support/Cortex` on macOS) - never inside the app
bundle itself.

## Data sources

Literature search draws on free, public sources: Europe PMC, CrossRef,
arXiv, ERIC, Semantic Scholar, and OpenAlex. Optional keys for
paid/institutional databases (Elsevier/Scopus, Web of Science, IEEE
Xplore, Springer Nature, CORE) can be added in Literature Sources settings
(database icon) - no paid subscription is required to use the app.

## License & legal

MIT licensed - see [LICENSE](LICENSE). See [LEGAL.md](LEGAL.md) for AI-
generated content, third-party data sharing, and data storage details.

This app's code was written with substantial assistance from
[Claude Code](https://claude.com/claude-code), Anthropic's AI coding tool.
