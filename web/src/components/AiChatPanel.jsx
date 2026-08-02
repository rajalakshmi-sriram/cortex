import { useState, useEffect, useRef } from 'react';
import { api } from '../api/client';
import { Button } from './Button';
import './AiChatPanel.css';

/**
 * Reusable "AI use" button + grounded follow-up chat thread. Used for every
 * AI feature in the app: manuscript feedback, hypothesis feedback, data
 * interpretation, paper summaries, and follow-ups on the literature
 * synthesis / search-angle suggestions. Nothing here runs automatically -
 * the AI is only ever contacted when the user clicks the trigger button or
 * sends a follow-up message.
 *
 * `context` is a snapshot taken at the moment the user clicks the trigger
 * (or, for `seedAssistantMessage`, at render time) - it grounds the AI's
 * answers in real data already in the app (the actual manuscript text, the
 * actual stats results, etc.), never anything invented.
 */
export function AiChatPanel({
  contextType,
  context,
  kickoffMessage,
  triggerLabel,
  accent = 'blue',
  seedAssistantMessage, // optional: skip the first AI call, start the thread already seeded with this reply
  disabled,
  disabledReason,
}) {
  const [available, setAvailable] = useState(true);
  const [messages, setMessages] = useState(seedAssistantMessage ? [
    { role: 'user', content: kickoffMessage },
    { role: 'assistant', content: seedAssistantMessage },
  ] : []);
  const [started, setStarted] = useState(!!seedAssistantMessage);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const threadEndRef = useRef(null);

  useEffect(() => {
    api.aiStatus().then((d) => setAvailable(d.available)).catch(() => setAvailable(false));
  }, []);

  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, [messages]);

  async function start() {
    setError('');
    setSending(true);
    const firstTurn = [{ role: 'user', content: kickoffMessage }];
    setMessages(firstTurn);
    setStarted(true);
    try {
      const data = await api.aiConverse(contextType, context, firstTurn);
      setMessages([...firstTurn, { role: 'assistant', content: data.reply }]);
    } catch (e) {
      setError(e.message);
      setStarted(false);
      setMessages([]);
    } finally {
      setSending(false);
    }
  }

  async function sendFollowUp(e) {
    e.preventDefault();
    if (!input.trim() || sending) return;
    setError('');
    const nextMessages = [...messages, { role: 'user', content: input.trim() }];
    setMessages(nextMessages);
    setInput('');
    setSending(true);
    try {
      const data = await api.aiConverse(contextType, context, nextMessages);
      setMessages([...nextMessages, { role: 'assistant', content: data.reply }]);
    } catch (e) {
      setError(e.message);
    } finally {
      setSending(false);
    }
  }

  function reset() {
    setMessages([]);
    setStarted(false);
    setError('');
    setInput('');
  }

  if (!available) {
    return (
      <p className="ai-chat-panel__unavailable">
        AI assistant isn't set up yet — configure it via the sparkle icon in the corner to use this feature.
      </p>
    );
  }

  if (!started) {
    return (
      <div>
        <Button accent={accent} onClick={start} disabled={disabled || sending}>
          {sending ? 'Thinking…' : `✨ ${triggerLabel}`}
        </Button>
        {disabled && disabledReason && (
          <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6 }}>{disabledReason}</p>
        )}
        {error && <p role="alert" style={{ color: 'var(--accent1-text)', marginTop: 8 }}>{error}</p>}
      </div>
    );
  }

  return (
    <div className="ai-chat-panel">
      <div className="ai-chat-panel__thread" aria-live="polite">
        {messages.map((m, i) => (
          <div key={i} className={`ai-chat-panel__msg ai-chat-panel__msg--${m.role}`}>
            {m.content}
          </div>
        ))}
        {sending && <div className="ai-chat-panel__msg ai-chat-panel__msg--assistant ai-chat-panel__msg--pending">Thinking&hellip;</div>}
        <div ref={threadEndRef} />
      </div>
      {error && <p role="alert" style={{ color: 'var(--accent1-text)' }}>{error}</p>}
      <form className="ai-chat-panel__form" onSubmit={sendFollowUp}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a follow-up…"
          aria-label="Follow-up message to AI"
        />
        <Button type="submit" accent={accent} disabled={sending || !input.trim()}>Send</Button>
      </form>
      <button type="button" className="ai-chat-panel__reset" onClick={reset}>Start over</button>
    </div>
  );
}
