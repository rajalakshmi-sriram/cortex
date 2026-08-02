import { useState } from 'react';
import { useProject } from './Workspace';
import { api } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { MicButton } from '../components/MicButton';
import { AiChatPanel } from '../components/AiChatPanel';
import { PageInstructions } from '../components/PageInstructions';

export function ProjectSearch() {
  const { project, refresh } = useProject();

  const [broadTopic, setBroadTopic] = useState('');
  const [exploring, setExploring] = useState(false);
  const [error, setError] = useState('');

  const [suggestedAngles, setSuggestedAngles] = useState([]);
  const [synthesis, setSynthesis] = useState(null);
  const [gaps, setGaps] = useState([]);
  const [synthesisPapers, setSynthesisPapers] = useState([]);

  const [specificTopic, setSpecificTopic] = useState(project.specific_topic || '');
  const [specificAims, setSpecificAims] = useState(project.specific_aims || '');
  const [questions, setQuestions] = useState(project.research_questions?.length ? project.research_questions : ['']);
  const [saveStatus, setSaveStatus] = useState('');

  async function explore() {
    if (!broadTopic.trim()) return;
    setExploring(true);
    setError('');
    setSuggestedAngles([]);
    setSynthesis(null);
    try {
      const [terms, aiResult] = await Promise.all([
        api.suggestSearchTerms(broadTopic).catch(() => ({ terms: [] })),
        api.validateIdeaWithAI(broadTopic).catch(() => null),
      ]);
      setSuggestedAngles(terms.terms || []);
      if (aiResult) {
        setSynthesis(aiResult.ai_synthesis || null);
        setSynthesisPapers(aiResult.related_papers || aiResult.similar_papers || []);
        const gapLines = (aiResult.ai_synthesis || '')
          .split('\n')
          .filter((l) => l.trim().startsWith('-') || l.trim().startsWith('•'));
        setGaps(gapLines);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setExploring(false);
    }
  }

  function pickAngle(angle) {
    setSpecificTopic(angle);
  }

  function updateQuestion(i, value) {
    setQuestions((qs) => qs.map((q, idx) => (idx === i ? value : q)));
  }
  function addQuestion() {
    setQuestions((qs) => [...qs, '']);
  }
  function removeQuestion(i) {
    setQuestions((qs) => qs.filter((_, idx) => idx !== i));
  }

  async function saveToProject() {
    setSaveStatus('Saving…');
    try {
      await api.updateProject(project.id, {
        specific_topic: specificTopic,
        specific_aims: specificAims,
        research_questions: questions.filter((q) => q.trim()),
      });
      await refresh();
      setSaveStatus('Saved ✓');
    } catch (e) {
      setSaveStatus('');
      setError(e.message);
    }
  }

  return (
    <div>
      <PageInstructions
        accent="sage"
        items={[
          'Type a broad topic and click Explore Topic — Cortex searches real literature and (if you\'ve set up an AI assistant via the sparkle icon, bottom-right) suggests specific angles and a synthesis of what\'s already published.',
          'Click "Discuss with AI" under the synthesis to ask follow-up questions about it.',
          'Click any suggested angle to drop it into "Specific topic" below, or type your own. Fill in aims and research questions, then Save to Project.',
        ]}
      />
      <Card
        title="Explore a Broad Topic"
        hint="Start broad. Cortex will search real literature and suggest specific angles you can narrow down into a research topic, aims, and questions."
        accent="sage"
      >
        <label htmlFor="broad-topic">Broad topic</label>
        <div style={{ display: 'flex', gap: 8 }}>
          <textarea
            id="broad-topic"
            value={broadTopic}
            onChange={(e) => setBroadTopic(e.target.value)}
            placeholder="e.g. enzyme catalysis"
            style={{ flex: 1, minHeight: 44 }}
          />
          <MicButton label="broad topic" onTranscript={(t) => setBroadTopic((prev) => (prev ? prev + ' ' + t : t))} />
        </div>
        <div style={{ marginTop: 12 }}>
          <Button accent="sage" onClick={explore} disabled={exploring || !broadTopic.trim()}>
            {exploring ? 'Exploring…' : 'Explore Topic'}
          </Button>
        </div>
        {error && <p role="alert" style={{ color: 'var(--accent1-text)' }}>{error}</p>}
      </Card>

      {(suggestedAngles.length > 0 || synthesis) && (
        <Card title="What Cortex Found" accent="blue">
          {synthesis && (
            <>
              <p><strong>Synthesis of current literature:</strong></p>
              <p>{synthesis}</p>
              <div style={{ marginBottom: 14 }}>
                <AiChatPanel
                  key={broadTopic}
                  contextType="literature_synthesis"
                  context={{ idea: broadTopic, papers: synthesisPapers }}
                  kickoffMessage="Please summarize the current literature on this topic and identify gaps."
                  seedAssistantMessage={synthesis}
                  triggerLabel="Discuss with AI"
                  accent="sage"
                />
              </div>
            </>
          )}
          {suggestedAngles.length > 0 && (
            <>
              <p><strong>Specific angles you could narrow into:</strong></p>
              <div className="chip-row">
                {suggestedAngles.map((angle, i) => (
                  <button key={i} className="chip" onClick={() => pickAngle(angle)}>
                    {angle}
                  </button>
                ))}
              </div>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>Click an angle to use it as your specific topic below.</p>
            </>
          )}
        </Card>
      )}

      <Card
        title="Your Specific Research Focus"
        hint="Narrow your broad topic into a specific topic, aims, and research questions. Save it to your project when ready."
        accent="rose"
      >
        <label htmlFor="specific-topic">Specific topic</label>
        <div style={{ display: 'flex', gap: 8 }}>
          <input id="specific-topic" type="text" value={specificTopic} onChange={(e) => setSpecificTopic(e.target.value)} />
          <MicButton label="specific topic" onTranscript={(t) => setSpecificTopic((prev) => (prev ? prev + ' ' + t : t))} />
        </div>

        <label htmlFor="specific-aims">Specific aims</label>
        <div style={{ display: 'flex', gap: 8 }}>
          <textarea id="specific-aims" value={specificAims} onChange={(e) => setSpecificAims(e.target.value)} style={{ flex: 1 }} />
          <MicButton label="specific aims" onTranscript={(t) => setSpecificAims((prev) => (prev ? prev + ' ' + t : t))} />
        </div>

        <fieldset>
          <legend style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', margin: '12px 0 5px' }}>Research questions</legend>
          {questions.map((q, i) => (
            <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 6 }}>
              <input
                type="text"
                value={q}
                onChange={(e) => updateQuestion(i, e.target.value)}
                aria-label={`Research question ${i + 1}`}
                placeholder={`Research question ${i + 1}`}
                style={{ flex: 1 }}
              />
              <MicButton label={`research question ${i + 1}`} onTranscript={(t) => updateQuestion(i, q ? q + ' ' + t : t)} />
              <Button variant="ghost" accent="rose" onClick={() => removeQuestion(i)} aria-label={`Remove research question ${i + 1}`}>
                &times;
              </Button>
            </div>
          ))}
          <Button variant="secondary" accent="rose" onClick={addQuestion}>+ Add Question</Button>
        </fieldset>

        <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
          <Button accent="rose" onClick={saveToProject}>Save to Project</Button>
          {saveStatus && <span role="status">{saveStatus}</span>}
        </div>
      </Card>
    </div>
  );
}
