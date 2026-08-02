import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import './MicButton.css';

/** Speech-to-text button - appends the transcribed text via onTranscript. Hidden if the browser doesn't support it. */
export function MicButton({ onTranscript, label = 'field' }) {
  const { supported, listening, toggle } = useSpeechRecognition({ onResult: onTranscript });

  if (!supported) return null;

  return (
    <button
      type="button"
      className={`mic-button ${listening ? 'mic-button--listening' : ''}`}
      onClick={toggle}
      aria-pressed={listening}
      aria-label={listening ? `Stop voice input for ${label}` : `Start voice input for ${label}`}
      title={listening ? 'Listening... click to stop' : 'Click to dictate'}
    >
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="9" y="2" width="6" height="12" rx="3" stroke="currentColor" strokeWidth="1.8" />
        <path d="M5 11a7 7 0 0 0 14 0M12 18v3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
      {listening && <span className="visually-hidden">Listening</span>}
    </button>
  );
}
