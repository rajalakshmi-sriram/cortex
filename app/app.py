"""
Main Cortex Application
Flask-based REST API for a general-purpose research workspace platform
"""

import re
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import datetime

from config.config import get_config
from app.logger import logger
from app.idea_validator import IdeaValidator
from app.methodology_engine import MethodologyEngine
from app.project_store import ProjectStore
from app.data_import import parse_csv_text, parse_rows, parse_excel_bytes, table_to_dataframe
from app.stats_engine import run_analysis, recommend_test, TEST_CATALOG
from app.chart_engine import generate_chart, CHART_TYPES
from app.journal_guidelines import lookup_guidelines, list_known_journals
from app.ai_assistant import AIAssistant, AIUnavailableError
from app.citation_formatter import (
    format_citation, papers_to_bibtex, papers_to_ris, CITATION_STYLES,
    assign_citation_keys, in_text_citation,
)
from app.citation_parser import parse_references, dedupe_against, CitationParseError
from app.research_guide import get_basics, get_glossary, glossary_categories, GLOSSARY
from app.screening import (
    compute_prisma, screening_summary, paper_screening, apply_decision, reset_decision,
    COMMON_EXCLUSION_REASONS, MANUAL_COUNT_FIELDS,
)
from app.google_docs_store import GoogleDocsStore, build_authorize_url, exchange_code_for_tokens, get_valid_access_token, fetch_document_text


def _paper_summary(p):
    return {
        'title': p['title'],
        'authors': p['authors'],
        'year': p['year'],
        'source': p['source'],
        'doi': p.get('doi', ''),
        'url': p.get('url', ''),
        'similarity_score': p.get('similarity_score', 0),
        'tfidf_score': p.get('tfidf_score', 0),
        'keyword_overlap': p.get('keyword_overlap', 0),
        'abstract': p.get('abstract', ''),
    }


def _error(message, status=500):
    return jsonify({'status': 'error', 'message': message}), status


def create_app():
    """
    Create and configure Flask application

    Returns:
        Flask: Configured Flask app instance
    """
    app = Flask(__name__)
    config = get_config()
    app.config.from_object(config)

    CORS(app)

    idea_validator = IdeaValidator(config)
    methodology_engine = MethodologyEngine(config)
    project_store = ProjectStore(config)
    ai_assistant = AIAssistant(config)
    google_docs_store = GoogleDocsStore(config)

    # ========== Health Check ==========
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'Cortex',
            'timestamp': datetime.now().isoformat()
        }), 200

    @app.route('/api/v1', methods=['GET'])
    def api_root():
        return jsonify({
            'service': 'Cortex',
            'version': '2.0.0',
            'description': 'General-purpose AI-assisted research workspace',
            'endpoints': {
                'research_types': '/api/v1/research-types',
                'ideas': '/api/v1/ideas/validate',
                'methodology': '/api/v1/methodology/select',
                'projects': '/api/v1/projects',
            }
        }), 200

    # ========== Idea Validation (literature novelty check) ==========

    @app.route('/api/v1/ideas/validate', methods=['POST'])
    def validate_idea():
        try:
            data = request.get_json()
            if not data or 'idea' not in data:
                return _error('Missing required field: idea', 400)

            idea = data.get('idea', '').strip()
            result = idea_validator.validate_idea(idea)

            if 'related_papers' in result:
                result['related_papers'] = [_paper_summary(p) for p in result['related_papers']]
            if 'similar_papers' in result:
                result['similar_papers'] = [_paper_summary(p) for p in result['similar_papers']]

            return jsonify(result), 200

        except Exception as e:
            logger.error(f"Error in idea validation: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    # ========== AI Assistant (optional, explicitly opt-in) ==========
    # Provider is user-selectable: a local Ollama model (private, no API key), or
    # the user's own OpenAI/Anthropic API key. See app/ai_settings_store.py.

    @app.route('/api/v1/ai/status', methods=['GET'])
    def ai_status():
        return jsonify({'status': 'success', **ai_assistant.is_available()}), 200

    @app.route('/api/v1/settings/ai', methods=['GET'])
    def get_ai_settings():
        return jsonify({'status': 'success', 'settings': ai_assistant.settings_store.public()}), 200

    @app.route('/api/v1/settings/ai', methods=['POST'])
    def update_ai_settings():
        data = request.get_json(silent=True) or {}
        provider = data.get('provider')
        if not provider:
            return _error('provider is required', 400)
        try:
            ai_assistant.settings_store.save(
                provider=provider,
                model=data.get('model'),
                base_url=data.get('base_url'),
                api_key=data.get('api_key'),  # None = keep existing key
            )
        except ValueError as e:
            return _error(str(e), 400)
        return jsonify({'status': 'success', 'settings': ai_assistant.settings_store.public()}), 200

    # ========== Literature source settings (optional, your own API keys) ==========
    # If you have a subscription/API key for a paid database (Elsevier/Scopus,
    # Web of Science) or want to raise your Semantic Scholar rate limit, add it
    # here. Used only for your own searches on your own machine - never sent
    # anywhere except that database's own API, and never shared with anyone
    # else using this app. See app/literature_settings_store.py.

    @app.route('/api/v1/settings/literature', methods=['GET'])
    def get_literature_settings():
        return jsonify({'status': 'success', 'settings': idea_validator.literature_fetcher.settings_store.public()}), 200

    @app.route('/api/v1/settings/literature', methods=['POST'])
    def update_literature_settings():
        data = request.get_json(silent=True) or {}
        idea_validator.literature_fetcher.settings_store.save(
            elsevier_api_key=data.get('elsevier_api_key'),
            wos_api_key=data.get('wos_api_key'),
            semantic_scholar_api_key=data.get('semantic_scholar_api_key'),
            ieee_api_key=data.get('ieee_api_key'),
            springer_api_key=data.get('springer_api_key'),
            core_api_key=data.get('core_api_key'),
        )
        return jsonify({'status': 'success', 'settings': idea_validator.literature_fetcher.settings_store.public()}), 200

    # ========== Google Docs (optional, for AI Feedback on a linked Google Doc) ==========
    # Read-only OAuth connection to your own Google account, using your own
    # Google Cloud OAuth client credentials (added below, not baked into
    # Cortex - see DESKTOP_APP_BUILD.md for setup steps). Used only to fetch
    # the text of a Google Doc you've linked in Manuscript, so AI Feedback
    # can read it - never sent anywhere except Google's own API and your
    # chosen AI provider. See app/google_docs_store.py.

    @app.route('/api/v1/settings/google', methods=['GET'])
    def get_google_settings():
        return jsonify({'status': 'success', 'settings': google_docs_store.public()}), 200

    @app.route('/api/v1/settings/google', methods=['POST'])
    def update_google_settings():
        data = request.get_json(silent=True) or {}
        client_id = data.get('client_id', '').strip()
        client_secret = data.get('client_secret', '').strip()
        if not client_id or not client_secret:
            return _error('client_id and client_secret are both required', 400)
        google_docs_store.save_credentials(client_id, client_secret)
        return jsonify({'status': 'success', 'settings': google_docs_store.public()}), 200

    @app.route('/api/v1/settings/google/disconnect', methods=['POST'])
    def disconnect_google():
        google_docs_store.disconnect()
        return jsonify({'status': 'success', 'settings': google_docs_store.public()}), 200

    @app.route('/api/v1/settings/google/oauth/authorize-url', methods=['GET'])
    def google_authorize_url():
        settings = google_docs_store.load()
        if not settings.get('client_id'):
            return _error('Add your Google OAuth client ID and secret first', 400)
        redirect_uri = request.host_url.rstrip('/') + '/api/v1/settings/google/oauth/callback'
        return jsonify({'status': 'success', 'url': build_authorize_url(settings['client_id'], redirect_uri)}), 200

    @app.route('/api/v1/settings/google/oauth/callback', methods=['GET'])
    def google_oauth_callback():
        code = request.args.get('code')
        error = request.args.get('error')
        if error:
            return f"<html><body><p>Google sign-in was cancelled or failed: {error}. You can close this tab.</p></body></html>", 400

        settings = google_docs_store.load()
        redirect_uri = request.host_url.rstrip('/') + '/api/v1/settings/google/oauth/callback'
        try:
            tokens = exchange_code_for_tokens(settings['client_id'], settings['client_secret'], code, redirect_uri)
            google_docs_store.save_tokens(tokens['access_token'], tokens.get('refresh_token'), tokens.get('expires_in', 3600))
        except Exception as e:
            logger.error(f"Google OAuth callback error: {str(e)}")
            return f"<html><body><p>Something went wrong connecting your Google account: {str(e)}. You can close this tab and try again.</p></body></html>", 500

        return "<html><body><p>Google account connected. You can close this tab and return to Cortex.</p></body></html>", 200

    @app.route('/api/v1/google/docs/<doc_id>/content', methods=['GET'])
    def google_doc_content(doc_id):
        try:
            access_token = get_valid_access_token(google_docs_store)
            text = fetch_document_text(doc_id, access_token)
            return jsonify({'status': 'success', 'text': text}), 200
        except ValueError as e:
            return _error(str(e), 400)
        except Exception as e:
            logger.error(f"Error fetching Google Doc content: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/ai/converse', methods=['POST'])
    def ai_converse():
        """
        Generic grounded chat turn, shared by every "AI use" button in the
        app (manuscript feedback, hypothesis feedback, data interpretation,
        paper summaries, and follow-ups on the literature synthesis / search
        angle suggestions). The frontend sends the whole visible thread so
        far as `messages` (starting with a user turn) plus `context_type` +
        `context` - the real data that grounds the system prompt, rebuilt
        fresh on every call rather than trusted/stored from the client.
        """
        data = request.get_json(silent=True) or {}
        context_type = data.get('context_type')
        context = data.get('context') or {}
        messages = data.get('messages') or []
        if not context_type:
            return _error('context_type is required', 400)
        if not messages:
            return _error('messages is required (at least one user turn)', 400)
        try:
            reply = ai_assistant.continue_conversation(context_type, context, messages)
            return jsonify({'status': 'success', 'reply': reply}), 200
        except AIUnavailableError as e:
            return _error(str(e), 503)
        except ValueError as e:
            return _error(str(e), 400)
        except Exception as e:
            logger.error(f"Error in AI conversation: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/ideas/validate-with-ai', methods=['POST'])
    def validate_idea_with_ai():
        """
        Same free/manual literature search as /ideas/validate, plus an
        AI-generated synthesis and gap analysis grounded ONLY in the papers
        that search actually returned. Only called when the user explicitly
        clicks "Search with AI" instead of the regular search button.
        """
        try:
            data = request.get_json()
            if not data or 'idea' not in data:
                return _error('Missing required field: idea', 400)

            idea = data.get('idea', '').strip()
            result = idea_validator.validate_idea(idea)

            raw_papers = result.get('related_papers') or result.get('similar_papers') or []
            raw_paper_dicts = [
                {'title': p.get('title', ''), 'year': p.get('year', ''), 'abstract': p.get('paper', {}).get('abstract', '')}
                for p in raw_papers
            ]

            try:
                ai_result = ai_assistant.synthesize_literature(idea, raw_paper_dicts)
                result['ai_synthesis'] = ai_result['synthesis']
                result['ai_papers_used'] = ai_result['papers_used']
            except AIUnavailableError as e:
                result['ai_synthesis'] = None
                result['ai_error'] = str(e)

            if 'related_papers' in result:
                result['related_papers'] = [_paper_summary(p) for p in result['related_papers']]
            if 'similar_papers' in result:
                result['similar_papers'] = [_paper_summary(p) for p in result['similar_papers']]

            return jsonify(result), 200

        except Exception as e:
            logger.error(f"Error in AI-assisted idea validation: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/ai/suggest-search-terms', methods=['POST'])
    def ai_suggest_search_terms():
        try:
            data = request.get_json() or {}
            topic = (data.get('topic') or '').strip()
            if not topic:
                return _error('Missing required field: topic', 400)

            terms = ai_assistant.suggest_search_terms(topic)
            return jsonify({'status': 'success', 'terms': terms}), 200
        except AIUnavailableError as e:
            return _error(str(e), 503)
        except Exception as e:
            logger.error(f"Error suggesting search terms: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    # ========== Research Types ==========

    @app.route('/api/v1/research-types', methods=['GET'])
    def get_research_types():
        try:
            types = methodology_engine.get_research_types()
            return jsonify({
                'status': 'success',
                'types': types,
                'modes': types,  # backward-compatible alias
                'total_types': len(types),
                'timestamp': datetime.now().isoformat()
            }), 200
        except Exception as e:
            logger.error(f"Error retrieving research types: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/methodology/select', methods=['POST'])
    def select_methodology():
        try:
            data = request.get_json()
            if not data:
                return _error('Request body required', 400)

            idea = data.get('idea', '').strip()
            research_type = (data.get('type') or data.get('mode') or '').strip()

            if not idea or not research_type:
                return _error('Missing required fields: idea, type', 400)

            result = methodology_engine.select_research_type(research_type, idea)
            return jsonify(result), 200

        except Exception as e:
            logger.error(f"Error in methodology selection: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/methodology/<research_type>/step/<int:step_number>', methods=['GET'])
    def get_step_details(research_type, step_number):
        try:
            result = methodology_engine.get_step_details(research_type, step_number)
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Error retrieving step details: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    # ========== Projects ==========

    @app.route('/api/v1/projects', methods=['GET'])
    def list_projects():
        try:
            return jsonify({'status': 'success', 'projects': project_store.list_projects()}), 200
        except Exception as e:
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/projects', methods=['POST'])
    def create_project():
        try:
            data = request.get_json() or {}
            if not data.get('title'):
                return _error('Missing required field: title', 400)
            if not data.get('research_type'):
                return _error('Missing required field: research_type', 400)

            project = project_store.create_project(data)
            return jsonify({'status': 'success', 'project': project}), 201
        except ValueError as e:
            return _error(str(e), 400)
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/projects/sample', methods=['POST'])
    def create_sample_project():
        try:
            project = project_store.create_sample_project()
            return jsonify({'status': 'success', 'project': project}), 201
        except Exception as e:
            logger.error(f"Error creating sample project: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/projects/<project_id>', methods=['GET'])
    def get_project(project_id):
        project = project_store.get_project(project_id)
        if not project:
            return _error('Project not found', 404)
        return jsonify({'status': 'success', 'project': project}), 200

    @app.route('/api/v1/projects/<project_id>', methods=['PUT'])
    def update_project(project_id):
        try:
            data = request.get_json() or {}
            project = project_store.update_project(project_id, data)
            if not project:
                return _error('Project not found', 404)
            return jsonify({'status': 'success', 'project': project}), 200
        except Exception as e:
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/projects/<project_id>', methods=['DELETE'])
    def delete_project(project_id):
        deleted = project_store.delete_project(project_id)
        if not deleted:
            return _error('Project not found', 404)
        return jsonify({'status': 'success'}), 200

    # ========== Whole-project export/import (backup, sharing with a co-author) ==========

    @app.route('/api/v1/projects/<project_id>/export', methods=['GET'])
    def export_project(project_id):
        try:
            project = project_store.get_project(project_id)
            if not project:
                return _error('Project not found', 404)

            zip_bytes = project_store.export_project(project_id)
            filename = re.sub(r'[^A-Za-z0-9_-]+', '_', project.get('title', 'cortex-project')) + '.cortexproject.zip'

            return Response(
                zip_bytes,
                mimetype='application/zip',
                headers={'Content-Disposition': f'attachment; filename="{filename}"'}
            )
        except Exception as e:
            logger.error(f"Error exporting project: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/projects/import', methods=['POST'])
    def import_project():
        try:
            if 'file' not in request.files:
                return _error('No file provided', 400)

            zip_bytes = request.files['file'].read()
            project = project_store.import_project(zip_bytes)
            return jsonify({'status': 'success', 'project': project}), 201
        except ValueError as e:
            return _error(str(e), 400)
        except Exception as e:
            logger.error(f"Error importing project: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    # ========== Generic sub-resource collections (tasks, papers, notes, hypotheses, journals) ==========

    def _collection_routes(name):
        @app.route(f'/api/v1/projects/<project_id>/{name}', methods=['GET'], endpoint=f'list_{name}')
        def _list(project_id):
            try:
                items = project_store.collection(project_id, name).list()
                return jsonify({'status': 'success', name: items}), 200
            except Exception as e:
                return _error(f'Internal server error: {str(e)}')

        @app.route(f'/api/v1/projects/<project_id>/{name}', methods=['POST'], endpoint=f'add_{name}')
        def _add(project_id):
            try:
                data = request.get_json() or {}
                item = project_store.collection(project_id, name).add(data)
                return jsonify({'status': 'success', 'item': item}), 201
            except Exception as e:
                return _error(f'Internal server error: {str(e)}')

        @app.route(f'/api/v1/projects/<project_id>/{name}/<item_id>', methods=['PUT'], endpoint=f'update_{name}')
        def _update(project_id, item_id):
            try:
                data = request.get_json() or {}
                item = project_store.collection(project_id, name).update(item_id, data)
                if not item:
                    return _error('Item not found', 404)
                return jsonify({'status': 'success', 'item': item}), 200
            except Exception as e:
                return _error(f'Internal server error: {str(e)}')

        @app.route(f'/api/v1/projects/<project_id>/{name}/<item_id>', methods=['DELETE'], endpoint=f'delete_{name}')
        def _delete(project_id, item_id):
            try:
                deleted = project_store.collection(project_id, name).delete(item_id)
                if not deleted:
                    return _error('Item not found', 404)
                return jsonify({'status': 'success'}), 200
            except Exception as e:
                return _error(f'Internal server error: {str(e)}')

    for resource_name in ['tasks', 'papers', 'notes', 'hypotheses', 'journals', 'datasets', 'analyses', 'charts']:
        _collection_routes(resource_name)

    # ========== Citations (Paper Library export) ==========

    @app.route('/api/v1/projects/<project_id>/papers/citations', methods=['GET'])
    def paper_citations(project_id):
        try:
            style = request.args.get('style', 'apa')
            if style not in CITATION_STYLES:
                return _error(f"Unknown citation style: {style}. Choose from {CITATION_STYLES}", 400)

            papers = project_store.collection(project_id, 'papers').list()
            citations = [{'id': p['id'], 'citation': format_citation(p, style)} for p in papers]
            return jsonify({'status': 'success', 'style': style, 'citations': citations}), 200
        except Exception as e:
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/projects/<project_id>/papers/cite-index', methods=['GET'])
    def paper_cite_index(project_id):
        """
        Everything the manuscript editor needs to cite from the Paper Library:
        a stable short key per paper, the in-text form, and the full reference
        entry - all in one request, since the @-picker needs them together.
        """
        try:
            style = request.args.get('style', 'apa')
            if style not in CITATION_STYLES:
                return _error(f"Unknown citation style: {style}. Choose from {CITATION_STYLES}", 400)

            papers = project_store.collection(project_id, 'papers').list()
            keys = assign_citation_keys(papers)

            entries = [
                {
                    'id': p['id'],
                    'key': keys[p['id']],
                    'title': p.get('title', ''),
                    'authors': p.get('authors', ''),
                    'year': p.get('year', ''),
                    'source': p.get('source', ''),
                    'in_text': in_text_citation(p, style),
                    'reference': format_citation(p, style),
                }
                for p in papers
            ]
            # Reference lists are alphabetical by author in every style Cortex
            # supports, so sort once here rather than in the client.
            entries.sort(key=lambda e: (e['reference'] or '').lower())
            return jsonify({'status': 'success', 'style': style, 'entries': entries}), 200
        except Exception as e:
            logger.error(f"Error building cite index: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/projects/<project_id>/papers/bibtex', methods=['GET'])
    def paper_bibtex(project_id):
        try:
            papers = project_store.collection(project_id, 'papers').list()
            bib_content = papers_to_bibtex(papers)
            project = project_store.get_project(project_id)
            filename = re.sub(r'[^A-Za-z0-9_-]+', '_', (project or {}).get('title', 'cortex-library')) + '.bib'

            return Response(
                bib_content,
                mimetype='application/x-bibtex',
                headers={'Content-Disposition': f'attachment; filename="{filename}"'}
            )
        except Exception as e:
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/projects/<project_id>/papers/ris', methods=['GET'])
    def paper_ris(project_id):
        try:
            papers = project_store.collection(project_id, 'papers').list()
            ris_content = papers_to_ris(papers)
            project = project_store.get_project(project_id)
            filename = re.sub(r'[^A-Za-z0-9_-]+', '_', (project or {}).get('title', 'cortex-library')) + '.ris'

            return Response(
                ris_content,
                mimetype='application/x-research-info-systems',
                headers={'Content-Disposition': f'attachment; filename="{filename}"'}
            )
        except Exception as e:
            return _error(f'Internal server error: {str(e)}')

    # ========== Research guide (beginner help) ==========

    @app.route('/api/v1/guide/basics', methods=['GET'])
    def guide_basics():
        return jsonify({'status': 'success', 'sections': get_basics()}), 200

    @app.route('/api/v1/guide/glossary', methods=['GET'])
    def guide_glossary():
        query = request.args.get('q', '')
        return jsonify({
            'status': 'success',
            'terms': get_glossary(query),
            'categories': glossary_categories(),
            'total': len(GLOSSARY),
        }), 200

    # ========== Systematic review: screening + PRISMA ==========

    @app.route('/api/v1/projects/<project_id>/screening', methods=['GET'])
    def get_screening(project_id):
        try:
            if not project_store.get_project(project_id):
                return _error('Project not found', 404)

            papers = project_store.collection(project_id, 'papers').list()
            state = project_store.get_screening(project_id)
            return jsonify({
                'status': 'success',
                'screening': state,
                'summary': screening_summary(papers),
                'prisma': compute_prisma(papers, state),
                'exclusion_reasons': COMMON_EXCLUSION_REASONS,
                'manual_count_fields': [{'key': k, 'label': l} for k, l in MANUAL_COUNT_FIELDS],
                'papers': [
                    {
                        'id': p['id'],
                        'title': p.get('title', ''),
                        'authors': p.get('authors', ''),
                        'year': p.get('year', ''),
                        'source': p.get('source', ''),
                        'abstract': p.get('abstract', ''),
                        'doi': p.get('doi', ''),
                        'url': p.get('url', ''),
                        'screening': paper_screening(p),
                    }
                    for p in papers
                ],
            }), 200
        except Exception as e:
            logger.error(f"Error loading screening state: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/projects/<project_id>/screening', methods=['PUT'])
    def update_screening(project_id):
        try:
            if not project_store.get_project(project_id):
                return _error('Project not found', 404)
            state = project_store.update_screening(project_id, request.get_json() or {})
            papers = project_store.collection(project_id, 'papers').list()
            return jsonify({
                'status': 'success',
                'screening': state,
                'prisma': compute_prisma(papers, state),
            }), 200
        except Exception as e:
            logger.error(f"Error updating screening state: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/projects/<project_id>/screening/<paper_id>', methods=['PUT'])
    def screen_paper(project_id, paper_id):
        try:
            collection = project_store.collection(project_id, 'papers')
            paper = collection.get(paper_id)
            if not paper:
                return _error('Paper not found', 404)

            data = request.get_json() or {}
            decision = data.get('decision', '')

            if decision == 'reset':
                screening = reset_decision(paper)
            else:
                try:
                    screening = apply_decision(
                        paper, decision, reason=data.get('reason', ''), notes=data.get('notes', '')
                    )
                except ValueError as e:
                    return _error(str(e), 400)

            collection.update(paper_id, {'screening': screening})

            papers = collection.list()
            state = project_store.get_screening(project_id)
            return jsonify({
                'status': 'success',
                'screening': screening,
                'summary': screening_summary(papers),
                'prisma': compute_prisma(papers, state),
            }), 200
        except Exception as e:
            logger.error(f"Error screening paper: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    # ========== Reference-manager import (.bib / .ris -> Paper Library) ==========

    @app.route('/api/v1/projects/<project_id>/papers/import', methods=['POST'])
    def import_references(project_id):
        """
        Import a BibTeX or RIS export from Zotero/Mendeley/EndNote into the
        Paper Library. Papers already in the library (matched by DOI or
        title) are reported back as skipped rather than duplicated.
        """
        try:
            if not project_store.get_project(project_id):
                return _error('Project not found', 404)

            if 'file' in request.files:
                upload = request.files['file']
                filename = upload.filename or ''
                try:
                    text = upload.read().decode('utf-8')
                except UnicodeDecodeError:
                    # EndNote and older managers still emit latin-1.
                    upload.seek(0)
                    text = upload.read().decode('latin-1', errors='replace')
            else:
                data = request.get_json(silent=True) or {}
                text = data.get('text', '')
                filename = data.get('filename', '')

            if not text.strip():
                return _error('No file content provided', 400)

            papers, fmt = parse_references(text, filename)
            collection = project_store.collection(project_id, 'papers')
            new_papers, duplicates = dedupe_against(papers, collection.list())

            added = []
            for paper in new_papers:
                added.append(collection.add({
                    **paper,
                    'import_source': f'{fmt} import',
                    'annotations': '',
                }))

            return jsonify({
                'status': 'success',
                'format': fmt,
                'parsed': len(papers),
                'imported': len(added),
                'skipped': len(duplicates),
                'skipped_titles': [p['title'] for p in duplicates[:20]],
                'papers': added,
            }), 201

        except CitationParseError as e:
            return _error(str(e), 400)
        except Exception as e:
            logger.error(f"Error importing references: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    # ========== Data import (CSV/manual rows -> dataset) ==========

    @app.route('/api/v1/projects/<project_id>/datasets/import', methods=['POST'])
    def import_dataset(project_id):
        try:
            if 'file' in request.files:
                file = request.files['file']
                filename = file.filename or ''
                name = (request.form.get('name') or filename or 'Untitled Dataset').strip() or 'Untitled Dataset'

                if filename.lower().endswith(('.xlsx', '.xls')):
                    table = parse_excel_bytes(file.read())
                else:
                    table = parse_csv_text(file.read().decode('utf-8', errors='replace'))
                source = 'file_upload'
            else:
                data = request.get_json() or {}
                name = data.get('name', 'Untitled Dataset').strip() or 'Untitled Dataset'
                source = data.get('source', 'import')

                if data.get('csv_text'):
                    table = parse_csv_text(data['csv_text'])
                elif data.get('rows'):
                    table = parse_rows(data['rows'])
                else:
                    return _error('Provide either csv_text, rows, or a file', 400)

            dataset = project_store.collection(project_id, 'datasets').add({
                'name': name,
                'source': source,
                **table,
            })
            return jsonify({'status': 'success', 'dataset': dataset}), 201
        except ValueError as e:
            return _error(str(e), 400)
        except Exception as e:
            logger.error(f"Error importing dataset: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    # ========== Statistical analysis (manual test + column selection) ==========

    @app.route('/api/v1/stats/tests', methods=['GET'])
    def list_stat_tests():
        return jsonify({'status': 'success', 'tests': TEST_CATALOG}), 200

    @app.route('/api/v1/projects/<project_id>/datasets/<dataset_id>/analyze', methods=['POST'])
    def analyze_dataset(project_id, dataset_id):
        try:
            dataset = project_store.collection(project_id, 'datasets').get(dataset_id)
            if not dataset:
                return _error('Dataset not found', 404)

            data = request.get_json() or {}
            test = data.get('test')
            if not test:
                return _error('Missing required field: test', 400)

            df = table_to_dataframe(dataset)
            result = run_analysis(df, test, data.get('params', {}))

            saved = project_store.collection(project_id, 'analyses').add({
                'dataset_id': dataset_id,
                'dataset_name': dataset.get('name'),
                'test': test,
                'params': data.get('params', {}),
                'result': result,
            })

            return jsonify({'status': 'success', 'analysis': saved}), 200
        except ValueError as e:
            return _error(str(e), 400)
        except KeyError as e:
            return _error(f'Missing column selection: {str(e)}', 400)
        except Exception as e:
            logger.error(f"Error running analysis: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/projects/<project_id>/datasets/<dataset_id>/recommend-test', methods=['POST'])
    def recommend_stat_test(project_id, dataset_id):
        try:
            dataset = project_store.collection(project_id, 'datasets').get(dataset_id)
            if not dataset:
                return _error('Dataset not found', 404)

            data = request.get_json() or {}
            value_column = data.get('value_column')
            group_column = data.get('group_column')
            if not value_column or not group_column:
                return _error('Missing required fields: value_column, group_column', 400)

            df = table_to_dataframe(dataset)
            result = recommend_test(df, value_column, group_column, data.get('row_range'))
            return jsonify({'status': 'success', 'recommendation': result}), 200
        except ValueError as e:
            return _error(str(e), 400)
        except KeyError as e:
            return _error(f'Missing column selection: {str(e)}', 400)
        except Exception as e:
            logger.error(f"Error recommending test: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    # ========== Charts (manual chart type + column selection) ==========

    @app.route('/api/v1/charts/types', methods=['GET'])
    def list_chart_types():
        return jsonify({'status': 'success', 'chart_types': CHART_TYPES}), 200

    @app.route('/api/v1/projects/<project_id>/datasets/<dataset_id>/chart', methods=['POST'])
    def chart_dataset(project_id, dataset_id):
        try:
            dataset = project_store.collection(project_id, 'datasets').get(dataset_id)
            if not dataset:
                return _error('Dataset not found', 404)

            data = request.get_json() or {}
            chart_type = data.get('chart_type')
            if not chart_type:
                return _error('Missing required field: chart_type', 400)

            df = table_to_dataframe(dataset)
            image_b64 = generate_chart(df, chart_type, data.get('params', {}))

            saved = project_store.collection(project_id, 'charts').add({
                'dataset_id': dataset_id,
                'dataset_name': dataset.get('name'),
                'chart_type': chart_type,
                'params': data.get('params', {}),
                'image_base64': image_b64,
            })

            return jsonify({'status': 'success', 'chart': saved}), 200
        except ValueError as e:
            return _error(str(e), 400)
        except KeyError as e:
            return _error(f'Missing column selection: {str(e)}', 400)
        except Exception as e:
            logger.error(f"Error generating chart: {str(e)}")
            return _error(f'Internal server error: {str(e)}')

    # ========== Journal guidelines (curated reference lookup) ==========

    @app.route('/api/v1/journal-guidelines', methods=['GET'])
    def journal_guidelines():
        name = request.args.get('name', '')
        return jsonify({
            'status': 'success',
            'guidelines': lookup_guidelines(name),
            'known_journals': list_known_journals()
        }), 200

    # ========== Methodology progress (per-project) ==========

    @app.route('/api/v1/projects/<project_id>/methodology', methods=['GET'])
    def get_project_methodology(project_id):
        try:
            return jsonify({'status': 'success', 'methodology': project_store.get_methodology(project_id)}), 200
        except ValueError as e:
            return _error(str(e), 404)
        except Exception as e:
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/projects/<project_id>/methodology/<int:step_index>', methods=['PUT'])
    def set_project_methodology_step(project_id, step_index):
        try:
            data = request.get_json() or {}
            completed = bool(data.get('completed', True))
            methodology = project_store.set_methodology_step(project_id, step_index, completed)
            return jsonify({'status': 'success', 'methodology': methodology}), 200
        except Exception as e:
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/projects/<project_id>/methodology/<int:step_index>/tools', methods=['POST'])
    def add_step_tool(project_id, step_index):
        try:
            data = request.get_json() or {}
            name = (data.get('name') or '').strip()
            if not name:
                return _error('Missing required field: name', 400)
            methodology = project_store.add_step_tool(project_id, step_index, name, (data.get('url') or '').strip())
            return jsonify({'status': 'success', 'methodology': methodology}), 201
        except Exception as e:
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/projects/<project_id>/methodology/<int:step_index>/tools/<tool_id>', methods=['DELETE'])
    def remove_step_tool(project_id, step_index, tool_id):
        try:
            methodology = project_store.remove_step_tool(project_id, step_index, tool_id)
            return jsonify({'status': 'success', 'methodology': methodology}), 200
        except Exception as e:
            return _error(f'Internal server error: {str(e)}')

    # ========== Manuscript ==========

    @app.route('/api/v1/projects/<project_id>/manuscript', methods=['GET'])
    def get_manuscript(project_id):
        try:
            return jsonify({'status': 'success', 'manuscript': project_store.get_manuscript(project_id)}), 200
        except Exception as e:
            return _error(f'Internal server error: {str(e)}')

    @app.route('/api/v1/projects/<project_id>/manuscript', methods=['PUT'])
    def update_manuscript(project_id):
        try:
            data = request.get_json() or {}
            manuscript = project_store.update_manuscript(project_id, data)
            return jsonify({'status': 'success', 'manuscript': manuscript}), 200
        except Exception as e:
            return _error(f'Internal server error: {str(e)}')

    # ========== Error Handlers ==========

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'Endpoint not found',
            'path': request.path
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

    @app.before_request
    def log_request():
        logger.debug(f"{request.method} {request.path}")

    return app


if __name__ == '__main__':
    app = create_app()
    logger.info("Starting Cortex application")
    app.run(
        host='0.0.0.0',
        port=5050,
        debug=True
    )
