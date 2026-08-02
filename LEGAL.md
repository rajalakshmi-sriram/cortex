# Legal notices

## Built with Claude Code

This application's code was written with substantial assistance from
[Claude Code](https://claude.com/claude-code), Anthropic's AI coding tool.
Development, features, and this documentation were AI-assisted under human
direction and review.

## License

Cortex is licensed under the [MIT License](LICENSE). In short: you can use,
modify, and redistribute it, provided the copyright notice is kept, and it
comes with **no warranty of any kind** - see the license text for the full
terms, including the liability limitation.

## No warranty on research outputs

Cortex helps you organize a research project, but it does not replace your
own judgment or your field's standards of rigor. Specifically:

- **Statistical results** are computed with standard, real methods (scipy),
  but you are responsible for choosing the right test for your data and
  interpreting the output correctly.
- **AI-generated content** (literature synthesis, manuscript feedback,
  hypothesis feedback, data interpretation, paper summaries) may be
  incomplete, wrong, or misleading. It is grounded in data you provide, but
  language models can still make mistakes. Verify anything AI-generated
  before relying on it in a manuscript, decision, or submission.
- **Citations and literature search results** are pulled from third-party
  sources (see below) and are not guaranteed to be complete or error-free -
  always verify citations against the original source before publishing.

## Third-party data sharing - read this before entering sensitive data

**Literature search** queries your research topic against free, public
APIs: Europe PMC, CrossRef, arXiv, ERIC, Semantic Scholar, and OpenAlex
(plus Elsevier/Web of Science if you supply your own API key for them).
Each is subject to its own terms of service.

**AI features are opt-in, and where that data goes depends on which
provider you choose** in AI Settings (the sparkle icon):
- **Local (Ollama)** - runs entirely on your own machine. Nothing you type
  is sent anywhere.
- **Your own OpenAI or Anthropic API key** - if you choose this option,
  whatever you send to that AI feature (manuscript text, hypotheses,
  statistical results, research ideas) is transmitted to that provider's
  servers and subject to their terms of service and privacy policy, not
  Cortex's.

**If your research involves human subjects, patient data, or other
regulated/sensitive data (e.g. anything covered by HIPAA or your
institution's IRB protocol): do not enter that data into a hosted AI
provider (OpenAI/Anthropic) unless you have confirmed that doing so
complies with your protocol and any required data agreements (e.g. a BAA).
Use the Local (Ollama) option to keep everything on your own machine
instead.** This is your responsibility as the user - Cortex has no way to
know what data you enter or what regulations apply to it.

## Data storage

Project data is stored locally: in `data/` during development, or in your
OS's per-user application data folder when running the packaged desktop app
(`~/Library/Application Support/Cortex` on macOS). Nothing is uploaded to
any Cortex-operated server, because there isn't one - Cortex has no backend
of its own beyond what runs on your machine.

## Trademark note

"Cortex" is used here only as this project's working name. It is not
affiliated with, endorsed by, or connected to any other product or company
using a similar name.
