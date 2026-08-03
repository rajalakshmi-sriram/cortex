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
- **Your own API key** for a hosted provider - OpenAI, Anthropic, Google
  Gemini, Mistral, or Groq - added in the AI Settings panel (sparkle icon,
  bottom-right of the app).
- **A custom OpenAI-compatible endpoint** - point Cortex at any other
  OpenAI-compatible server (OpenRouter, Together AI, a self-hosted
  vLLM/LM Studio, etc.) via a base URL you supply.

Where AI shows up, grounded only in your own real data (never inventing
facts beyond what you gave it):
- Literature synthesis + gap analysis during a search
- Manuscript feedback aimed at publication quality
- Hypothesis specificity/testability feedback
- Statistical results interpretation, related to your hypotheses
- Paper summarization
- Follow-up chat on any of the above, to ask clarifying questions

## macOS app (no setup required)

For most Mac users, this is the easiest way to use Cortex - no Python,
Node, or terminal required.

1. **[Download the latest `.dmg`](https://github.com/rajalakshmi-sriram/cortex/releases/latest)**
   from the Releases page (look for `Cortex-<version>-arm64.dmg`, for
   Apple Silicon Macs - M1/M2/M3/M4).
2. Open the downloaded `.dmg` and drag **Cortex** into your **Applications**
   folder.
3. Open **Cortex** from Applications (or Spotlight). The **first time**,
   macOS will say it's from an "unidentified developer" and refuse to open
   it normally - this is expected for any app distributed outside the Mac
   App Store without a paid Apple Developer certificate, not a sign
   anything is wrong. To open it anyway:
   - Right-click (or Control-click) the Cortex app icon → **Open** → click
     **Open** again in the dialog that appears, **or**
   - Go to **System Settings → Privacy & Security**, scroll down to the
     message about Cortex being blocked, and click **Open Anyway**.

   You only need to do this once - after the first launch it opens
   normally.

That's it - no other setup. Your project data is saved locally on your own
Mac (`~/Library/Application Support/Cortex`), not uploaded anywhere.

*Windows and Linux users: there isn't a packaged desktop app for those
platforms yet - use the web app below instead, which works identically.*

If you'd rather build the desktop app yourself from source instead of
downloading it, see [DESKTOP_APP_BUILD.md](DESKTOP_APP_BUILD.md).

## Running the web app (macOS, Windows, Linux)

This is for anyone who wants to run Cortex from the source code directly -
useful on Windows/Linux (no desktop app yet), or if you're developing on
the code. You'll need [Python 3.11](https://www.python.org/downloads/) and
[Node.js](https://nodejs.org/) installed first.

**1. Clone (or download) the repo and open a terminal in that folder.**
Every command below assumes you're inside the `cortex` project folder
(i.e. it contains `run.py` and `requirements.txt`) - if a command below
says a file isn't found, `cd` into the right folder first.

**2. Start the backend** (Flask, serves on port 5050):

macOS / Linux:
```bash
python3.11 -m venv venv-run
venv-run/bin/pip install -r requirements.txt
venv-run/bin/python3 run.py
```

Windows (PowerShell):
```powershell
py -3.11 -m venv venv-run
venv-run\Scripts\pip install -r requirements.txt
venv-run\Scripts\python run.py
```

> **Use Python 3.11 specifically** (`python3.11` / `py -3.11`), not
> whichever `python`/`python3` your system defaults to. The pinned
> scientific-library versions in `requirements.txt` (scikit-learn, numpy,
> etc.) don't have prebuilt wheels for Python 3.13+, so installing with a
> newer default Python (common with Homebrew or Anaconda) will fail trying
> to compile them from source. If you don't have 3.11 installed:
> `brew install python@3.11` on macOS, or the installer from
> [python.org](https://www.python.org/downloads/) on Windows.

> **"Address already in use" / port 5050 is in use:** this means a
> previous run of the backend is still running in the background (e.g. from
> a terminal tab you closed without stopping it). Find and stop it, then
> try again:
> - macOS/Linux: `lsof -nP -iTCP:5050 -sTCP:LISTEN` to find the process ID,
>   then `kill <PID>`.
> - Windows: `netstat -ano | findstr :5050` to find the PID, then
>   `taskkill /PID <PID> /F`.

Leave that terminal window running - the backend needs to stay up.

**3. In a *second* terminal window**, start the frontend (React + Vite,
proxies `/api` requests to the backend):
```bash
cd web
npm install
npm run dev
```

**4. Open the `http://localhost:...` URL printed in that terminal, in
your browser.** 

To stop everything, press `Ctrl+C` in both terminal windows.

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
arXiv, ERIC, and Semantic Scholar, plus OpenAlex. Optional keys for
paid/institutional databases (Elsevier/Scopus, Web of Science, IEEE
Xplore, Springer Nature, CORE) can be added in the app itself, in
Literature Sources settings (database icon) - but nothing requires a paid
subscription to use.

## License & legal

MIT licensed - see [LICENSE](LICENSE). See [LEGAL.md](LEGAL.md) for the
full disclosure on AI-generated content, third-party data sharing (what
leaves your machine if you use a hosted AI provider vs. local Ollama), and
data storage.

This app's code was written with substantial assistance from
[Claude Code](https://claude.com/claude-code), Anthropic's AI coding tool.
