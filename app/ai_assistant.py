"""
AI Assistant for Cortex
Optional, explicitly opt-in AI features. The user picks the provider from
Cortex's own AI Settings panel:

  - "local"            - a local Ollama server (default: qwen2.5:7b-instruct,
                          CPU-friendly, fully private, no API key, no data
                          leaves the machine)
  - "openai"            - the user's own OpenAI API key
  - "anthropic"         - the user's own Anthropic API key
  - "gemini"            - the user's own Google Gemini API key
  - "mistral"           - the user's own Mistral API key
  - "groq"              - the user's own Groq API key
  - "openai_compatible" - any other OpenAI-compatible endpoint the user
                          points at (OpenRouter, Together AI, a self-hosted
                          vLLM/LM Studio server, etc.) via a custom base URL

Nothing here runs automatically; every AI feature is triggered by an explicit
user action ("Search with AI" button, etc.) and is grounded in real data
already fetched by Cortex's own (non-AI) pipelines rather than left to
free-form generation.

If the configured provider isn't reachable (Ollama not running) or isn't
configured (no API key saved), these functions raise AIUnavailableError so
callers can show a clear message rather than a generic 500.
"""

from typing import Dict, List
import requests
from app.logger import logger
from app.ai_settings_store import AISettingsStore, DEFAULT_MODELS

# Providers that speak the OpenAI chat-completions request/response shape -
# only the base URL (and, for Gemini, the completions path) differs.
# Anthropic has its own distinct API shape, handled separately below.
OPENAI_COMPATIBLE_PROVIDERS = {'local', 'openai', 'gemini', 'mistral', 'groq', 'openai_compatible'}

# Most OpenAI-compatible providers expose chat completions at
# "<base_url>/v1/chat/completions". Gemini's compatibility layer is the one
# exception - its own version prefix is already part of the documented base
# path, so the standard "/v1/..." suffix doesn't apply to it.
CHAT_COMPLETIONS_PATH = {
    'gemini': '/chat/completions',
}
DEFAULT_CHAT_COMPLETIONS_PATH = '/v1/chat/completions'


class AIUnavailableError(Exception):
    """Raised when the configured AI provider can't be reached or isn't set up"""
    pass


class AIAssistant:
    """Thin client that dispatches to whichever AI provider the user has configured"""

    def __init__(self, config):
        self.settings_store = AISettingsStore(config)
        self.timeout = getattr(config, 'AI_TIMEOUT', 120)

    def is_available(self) -> Dict:
        """Check whether the currently configured provider is reachable/ready"""
        settings = self.settings_store.load()
        provider = settings['provider']

        if provider == 'local':
            try:
                response = requests.get(f"{settings['base_url']}/api/tags", timeout=3)
                response.raise_for_status()
                models = [m['name'] for m in response.json().get('models', [])]
                model_ready = settings['model'] in models
                return {
                    'available': model_ready,
                    'provider': provider,
                    'server_reachable': True,
                    'model': settings['model'],
                    'model_pulled': model_ready,
                    'installed_models': models,
                }
            except Exception:
                return {
                    'available': False,
                    'provider': provider,
                    'server_reachable': False,
                    'model': settings['model'],
                    'model_pulled': False,
                    'installed_models': [],
                }

        if provider == 'openai_compatible':
            # A custom endpoint might not require auth at all (e.g. a local
            # LM Studio/vLLM server) - the one thing it truly needs is a
            # base URL to talk to.
            has_base_url = bool(settings.get('base_url'))
            return {
                'available': has_base_url,
                'provider': provider,
                'server_reachable': None,
                'model': settings['model'],
                'model_pulled': has_base_url,
                'installed_models': [],
            }

        # Hosted providers (openai/anthropic/gemini/mistral/groq): "available"
        # just means a key is saved. We don't ping the provider on every
        # status check to avoid burning quota.
        has_key = bool(settings.get('api_key'))
        return {
            'available': has_key,
            'provider': provider,
            'server_reachable': None,
            'model': settings['model'],
            'model_pulled': has_key,
            'installed_models': [],
        }

    def _chat(self, messages: List[Dict], max_tokens: int = 500, temperature: float = 0.3) -> str:
        settings = self.settings_store.load()
        provider = settings['provider']

        if provider == 'local' or provider == 'openai_compatible':
            return self._chat_openai_compatible(settings, messages, max_tokens, temperature, api_key=settings.get('api_key') or None)
        elif provider in OPENAI_COMPATIBLE_PROVIDERS:
            if not settings.get('api_key'):
                raise AIUnavailableError(
                    f"No {provider} API key is saved. Add one in AI Settings, or switch to Local (Ollama)."
                )
            return self._chat_openai_compatible(settings, messages, max_tokens, temperature, api_key=settings['api_key'])
        elif provider == 'anthropic':
            if not settings.get('api_key'):
                raise AIUnavailableError(
                    "No Anthropic API key is saved. Add one in AI Settings, or switch to Local (Ollama)."
                )
            return self._chat_anthropic(settings, messages, max_tokens, temperature)
        else:
            raise AIUnavailableError(f"Unknown AI provider '{provider}'.")

    def _chat_openai_compatible(self, settings, messages, max_tokens, temperature, api_key) -> str:
        headers = {'Authorization': f'Bearer {api_key}'} if api_key else {}
        path = CHAT_COMPLETIONS_PATH.get(settings['provider'], DEFAULT_CHAT_COMPLETIONS_PATH)
        try:
            response = requests.post(
                f"{settings['base_url']}{path}",
                json={
                    'model': settings['model'],
                    'messages': messages,
                    'max_tokens': max_tokens,
                    'temperature': temperature,
                },
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
        except requests.exceptions.RequestException as e:
            logger.error(f"AI backend unreachable ({settings['provider']}): {str(e)}")
            if settings['provider'] == 'local':
                raise AIUnavailableError(
                    f"Could not reach the local AI model at {settings['base_url']}. "
                    f"Make sure Ollama is running (`ollama serve`) and the model is pulled "
                    f"(`ollama pull {settings['model']}`), or switch to an API key in AI Settings."
                ) from e
            raise AIUnavailableError(
                f"Could not reach {settings['provider']} ({str(e)}). Check your API key/base URL in AI Settings."
            ) from e
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Unexpected AI response shape: {str(e)}")
            raise AIUnavailableError("The AI model returned an unexpected response.") from e

    def _chat_anthropic(self, settings, messages, max_tokens, temperature) -> str:
        system = '\n'.join(m['content'] for m in messages if m['role'] == 'system') or None
        user_messages = [m for m in messages if m['role'] != 'system']
        try:
            payload = {
                'model': settings['model'],
                'max_tokens': max_tokens,
                'temperature': temperature,
                'messages': user_messages,
            }
            if system:
                payload['system'] = system
            response = requests.post(
                f"{settings['base_url']}/v1/messages",
                json=payload,
                headers={
                    'x-api-key': settings['api_key'],
                    'anthropic-version': '2023-06-01',
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return ''.join(block.get('text', '') for block in data.get('content', [])).strip()
        except requests.exceptions.RequestException as e:
            logger.error(f"AI backend unreachable (anthropic): {str(e)}")
            raise AIUnavailableError(
                f"Could not reach Anthropic ({str(e)}). Check your API key in AI Settings."
            ) from e
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Unexpected AI response shape: {str(e)}")
            raise AIUnavailableError("The AI model returned an unexpected response.") from e

    def synthesize_literature(self, idea: str, papers: List[Dict]) -> Dict:
        """
        Summarize the real, already-fetched papers into a short synthesis and
        gap analysis. Explicitly grounded: the model is only given the titles/
        abstracts Cortex already fetched from real sources, and instructed not
        to invent citations or claims beyond them.

        Args:
            idea (str): The user's research idea/topic
            papers (List[Dict]): Real papers already fetched (title, authors, year, abstract)

        Returns:
            Dict: {'synthesis': str, 'papers_used': int}
        """
        if not papers:
            return {'synthesis': 'No papers were available to synthesize.', 'papers_used': 0}

        sources_block = "\n\n".join(
            f"[{i + 1}] {p.get('title', 'Untitled')} ({p.get('year', 'n.d.')}) - "
            f"{(p.get('abstract') or '')[:600]}"
            for i, p in enumerate(papers[:10])
        )

        messages = [
            {
                'role': 'system',
                'content': (
                    "You are a research assistant helping a researcher understand existing literature. "
                    "You must ONLY use the numbered sources provided - never invent papers, authors, or "
                    "findings that are not in the provided sources. When you reference a claim, cite it "
                    "with its bracket number like [1]. Be concise and factual."
                ),
            },
            {
                'role': 'user',
                'content': (
                    f"Research topic: \"{idea}\"\n\n"
                    f"Here are {min(len(papers), 10)} real papers found on this topic:\n\n{sources_block}\n\n"
                    "Write a short synthesis (3-5 sentences) of what these sources say about this topic, "
                    "noting where they agree or disagree, followed by 1-3 bullet points identifying "
                    "apparent gaps or open questions this topic's existing literature does not yet answer. "
                    "Cite sources by bracket number."
                ),
            },
        ]

        synthesis = self._chat(messages, max_tokens=500)
        return {'synthesis': synthesis, 'papers_used': min(len(papers), 10)}

    def suggest_search_terms(self, broad_topic: str) -> List[str]:
        """
        Given a broad topic, suggest more specific search angles/terms a
        researcher could explore - used in the Project Search workflow to
        help narrow a broad topic toward a specific research question.

        Args:
            broad_topic (str): A broad research area/topic

        Returns:
            List[str]: 4-8 suggested more specific search angles
        """
        messages = [
            {
                'role': 'system',
                'content': (
                    "You help researchers narrow a broad topic into specific, searchable angles. "
                    "Respond with ONLY a numbered list, one short phrase per line, no other text."
                ),
            },
            {
                'role': 'user',
                'content': (
                    f"Broad topic: \"{broad_topic}\"\n\n"
                    "List 5-8 specific, searchable sub-topics or angles within this broad topic that "
                    "could each become a focused research question."
                ),
            },
        ]

        raw = self._chat(messages, max_tokens=300)
        lines = [line.strip() for line in raw.split('\n') if line.strip()]
        cleaned = []
        for line in lines:
            # strip leading "1.", "1)", "-", etc.
            stripped = line.lstrip('0123456789.-) \t')
            if stripped:
                cleaned.append(stripped)
        return cleaned

    # ------------------------------------------------------------------
    # Generic grounded conversation - powers every "chat with AI" follow-up
    # thread in the app (manuscript feedback, hypothesis feedback, data
    # interpretation, paper summaries, and follow-ups on the literature
    # synthesis / search-angle suggestions above). One system prompt is
    # rebuilt fresh from context_type + context on every call - the backend
    # never trusts or stores an arbitrary system prompt from the frontend,
    # only the specific, already-fetched data each context type expects.
    # ------------------------------------------------------------------

    def _build_context_prompt(self, context_type: str, context: Dict) -> str:
        if context_type == 'manuscript_feedback':
            sections = context.get('sections') or {}
            written = {k: v for k, v in sections.items() if v and v.strip()}
            sources_block = "\n\n".join(f"[{name.upper()}]\n{text.strip()}" for name, text in written.items())
            return (
                "You are an experienced peer reviewer and journal editor giving constructive, specific "
                "feedback on a manuscript draft, aimed at helping it reach the quality bar of a good/top-tier "
                "journal in its field. Only comment on what is actually written below - never invent claims, "
                "data, or sections that aren't present, and never fabricate citations. Be direct and specific "
                "(reference section names), and note both genuine strengths and concrete things to improve: "
                "clarity, structure, rigor of the argument, strength of evidence, and anything a reviewer at a "
                "selective journal would flag as missing or weak.\n\n"
                f"Manuscript draft:\n\n{sources_block or '(no content written yet)'}"
            )

        if context_type == 'hypothesis_feedback':
            project = context.get('project') or {}
            project_line = (
                f"Project research type: {project.get('research_type_name', '')}. "
                f"Research area: {project.get('research_area', '')}.\n\n"
                if project else ''
            )
            return (
                "You evaluate research hypotheses for specificity, testability, and falsifiability. "
                f"{project_line}"
                "Assess ONLY the hypothesis given below - don't invent extra context about the study. State "
                "plainly whether it is specific and testable enough for this kind of project, and if not, "
                "explain exactly why (e.g. missing variables, no clear direction of effect, not falsifiable, "
                "too vague a population/condition) and suggest a concretely sharper rewrite.\n\n"
                f"Hypothesis: \"{context.get('hypothesis', '')}\""
            )

        if context_type == 'data_interpretation':
            analyses = context.get('analyses') or []
            analyses_block = "\n\n".join(
                f"- Test: {a.get('test')}\n  Columns/params used: {a.get('params')}\n"
                f"  Result: {(a.get('result') or {}).get('interpretation', a.get('result'))}"
                for a in analyses
            )
            hyp = context.get('hypotheses')
            hyp_block = f"\n\nThis project's hypothesis/hypotheses (for context, not to be treated as ground truth):\n{hyp}" if hyp else ''
            return (
                "You help a researcher interpret statistical results they already computed themselves in this "
                "app - you are NOT running any new analysis, only interpreting results already given to you. "
                "Only reference the specific tests/results listed below - never invent numbers or claim a test "
                f"was run that isn't listed.\n\nDataset: {context.get('dataset_name', '')}\n\n"
                f"Results already computed:\n{analyses_block or '(no analyses run yet)'}"
                f"{hyp_block}\n\n"
                "Explain in plain language what these results mean, whether they support, contradict, or are "
                "inconclusive relative to the hypothesis (if one is given), and flag any caveats a careful "
                "reader should keep in mind (sample size, assumptions of the test, multiple-comparisons risk, "
                "correlation vs. causation, etc.)."
            )

        if context_type == 'paper_summary':
            p = context.get('paper') or {}
            return (
                "Summarize the following real paper for a researcher deciding whether to read it in full. Use "
                "ONLY the information given below - never invent findings, methods, or claims not present in "
                f"the abstract.\n\nTitle: {p.get('title', '')}\nAuthors: {p.get('authors', '')}\n"
                f"Year: {p.get('year', '')}\nAbstract: {p.get('abstract') or '(no abstract available)'}\n\n"
                "Give a short summary (3-5 sentences) of what the paper does and finds, then 1-2 bullet points "
                "on why it might be relevant to this researcher or what to watch for (limitations, scope, "
                "how directly it applies)."
            )

        if context_type == 'literature_synthesis':
            idea = context.get('idea', '')
            papers = context.get('papers') or []
            sources_block = "\n\n".join(
                f"[{i + 1}] {p.get('title', 'Untitled')} ({p.get('year', 'n.d.')})"
                for i, p in enumerate(papers[:10])
            )
            return (
                "You are continuing a conversation about a literature synthesis you already gave for a "
                f"research topic. Stay grounded ONLY in the sources below - never invent papers or findings.\n\n"
                f"Research topic: \"{idea}\"\n\nSources referenced:\n{sources_block or '(none)'}"
            )

        if context_type == 'search_terms':
            return (
                "You are continuing a conversation about specific research angles you already suggested for "
                f"a broad topic. Stay focused on helping narrow this topic further.\n\n"
                f"Broad topic: \"{context.get('broad_topic', '')}\""
            )

        raise ValueError(f"Unknown AI context type: {context_type}")

    def continue_conversation(self, context_type: str, context: Dict, messages: List[Dict]) -> str:
        """
        Run one more turn of a grounded conversation. `messages` is the full
        visible thread so far (starting with a user turn), rebuilt against a
        fresh system prompt each call so the model always stays grounded in
        the same real data it started with.
        """
        if not messages:
            raise ValueError("messages must include at least one turn")
        system_prompt = self._build_context_prompt(context_type, context)
        full_messages = [{'role': 'system', 'content': system_prompt}] + messages
        return self._chat(full_messages, max_tokens=600)
