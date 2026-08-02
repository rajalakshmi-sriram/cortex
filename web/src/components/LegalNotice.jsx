import { useState, useEffect, useRef } from 'react';
import './LegalNotice.css';

export function LegalNotice() {
  const [open, setOpen] = useState(false);
  const dialogRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    function onKey(e) {
      if (e.key === 'Escape') setOpen(false);
    }
    document.addEventListener('keydown', onKey);
    dialogRef.current?.focus();
    return () => document.removeEventListener('keydown', onKey);
  }, [open]);

  return (
    <>
      <button type="button" className="legal-notice__trigger" onClick={() => setOpen(true)}>
        Legal &amp; About
      </button>

      {open && (
        <div className="legal-notice__overlay" onClick={() => setOpen(false)}>
          <div
            className="legal-notice__dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="legal-notice-title"
            tabIndex={-1}
            ref={dialogRef}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="legal-notice__header">
              <h2 id="legal-notice-title" className="font-serif">Legal &amp; About</h2>
              <button type="button" className="legal-notice__close" onClick={() => setOpen(false)} aria-label="Close">&times;</button>
            </div>

            <div className="legal-notice__body">
              <p>
                This app's code was written with substantial assistance from{' '}
                <strong>Claude Code</strong>, Anthropic's AI coding tool, under human direction and review.
              </p>

              <h3>License</h3>
              <p>MIT licensed - provided "as is", with no warranty of any kind.</p>

              <h3>AI-generated content isn't guaranteed accurate</h3>
              <p>
                Literature synthesis, manuscript feedback, hypothesis feedback, data interpretation, and
                paper summaries are grounded in your own data, but language models can still make mistakes.
                Verify anything AI-generated before relying on it in a manuscript, decision, or submission.
                The same goes for citations and literature search results pulled from third-party sources -
                always check against the original.
              </p>

              <h3>Where your data goes</h3>
              <p>
                Literature search queries free public APIs (Europe PMC, CrossRef, arXiv, ERIC, Semantic
                Scholar, OpenAlex). If you add your own key for a paid/keyed database (Elsevier/Scopus, Web
                of Science, IEEE Xplore, Springer Nature, or CORE) in Literature Sources settings (database
                icon), it's used only for your own searches on your own machine - never shared with anyone
                else using this app.
              </p>
              <p>
                AI features are opt-in and only run when you click a "Search/Interpret/Get Feedback with AI"
                button - where that data goes depends on your provider choice in AI Settings (sparkle icon):{' '}
                <strong>Local (Ollama)</strong> keeps everything on your machine;{' '}
                <strong>your own API key</strong> for OpenAI, Anthropic, Google Gemini, Mistral, or Groq
                sends that specific request to their servers, under their terms; a{' '}
                <strong>custom OpenAI-compatible endpoint</strong> sends it to whatever server you configure
                - you're responsible for knowing what that endpoint does with it.
              </p>

              <p>
                <strong>If your research involves human subjects, patient data, or other regulated/sensitive
                data</strong> (e.g. HIPAA- or IRB-covered data): don't enter it into any hosted AI provider or
                custom endpoint unless you've confirmed that complies with your protocol. Use Local (Ollama)
                to keep it on your own machine instead. This is your responsibility - Cortex has no way to
                know what data you enter.
              </p>

              <h3>Data storage</h3>
              <p>
                Your project data is stored locally on your own machine - nothing is uploaded to any
                Cortex-operated server, because there isn't one.
              </p>

              <p className="legal-notice__more">See LICENSE and LEGAL.md in the project repository for full terms.</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
