"""
Configuration module for Cortex app
Handles all environment and application settings
"""

import os
import sys
import platform
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent


def _user_data_dir() -> Path:
    """
    Where project data lives when Cortex runs as a packaged desktop app.
    The app bundle itself (Contents/Resources on macOS, install dir on
    Windows) is read-only / gets replaced on update, so saved projects must
    live in a normal per-user data directory instead - the same pattern
    every desktop app uses.
    """
    if platform.system() == 'Darwin':
        return Path.home() / 'Library' / 'Application Support' / 'Cortex'
    if platform.system() == 'Windows':
        return Path(os.getenv('APPDATA', Path.home())) / 'Cortex'
    return Path.home() / '.cortex'


# PyInstaller sets sys.frozen=True on the bundled backend. In that case (the
# packaged desktop app) use a writable per-user directory; in normal
# development, keep using the project's own data/ folder as before.
if getattr(sys, 'frozen', False):
    DATA_DIR = _user_data_dir()
else:
    DATA_DIR = BASE_DIR / 'data'

PROJECTS_DIR = DATA_DIR / 'projects'
LOGS_DIR = DATA_DIR / 'logs' if getattr(sys, 'frozen', False) else BASE_DIR / 'logs'
SKILLS_DIR = BASE_DIR / 'skills'

# Create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
SKILLS_DIR.mkdir(parents=True, exist_ok=True)


class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False

    # Paths
    BASE_DIR = BASE_DIR
    DATA_DIR = DATA_DIR
    PROJECTS_DIR = PROJECTS_DIR
    LOGS_DIR = LOGS_DIR

    # Flask settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

    # App settings
    MAX_IDEA_LENGTH = 500
    MIN_IDEA_LENGTH = 10

    # API settings
    API_TIMEOUT = 30
    API_RATE_LIMIT = 100  # requests per minute

    # Research types supported across all research disciplines (not limited to
    # any single field). Each maps to a fixed step sequence in RESEARCH_TYPE_STEPS.
    RESEARCH_TYPES = {
        'theoretical': {
            'name': 'Theoretical Research',
            'description': 'Develop or improve scientific theories',
            'icon': 'lightbulb'
        },
        'experimental': {
            'name': 'Experimental Research',
            'description': 'Establish causal relationships by manipulating variables under controlled conditions',
            'icon': 'flask'
        },
        'exploratory': {
            'name': 'Exploratory Research',
            'description': 'Investigate a single case in depth and compare it against known generalizations',
            'icon': 'compass'
        },
        'pilot': {
            'name': 'Pilot Research',
            'description': 'Run a small-cohort feasibility study ahead of a full-scale study',
            'icon': 'flask'
        },
        'literature_review': {
            'name': 'Literature Review',
            'description': 'Search, screen, and synthesize existing published research',
            'icon': 'book'
        },
        'clinical': {
            'name': 'Clinical Research',
            'description': 'Evaluate interventions, treatments, or outcomes in human participants',
            'icon': 'flask'
        },
    }

    # Step sequences for each research type. These describe what should be done
    # for that project type in general, with or without AI assistance.
    RESEARCH_TYPE_STEPS = {
        'theoretical': [
            'Identify gap or inconsistency in an existing theory',
            'Write research problem',
            'Do literature review on that theory',
            "Build a framework or concept map on the theory's premises or other information",
            'Construct hypotheses',
            'Test logical consistency of the modified theory',
            'Draft review specific to journals of interest',
            'Record rejections or acceptances of journals',
        ],
        'experimental': [
            'Identify broad research question',
            'Do literature review',
            'Construct hypothesis',
            'Standardize the experimental design',
            'Recruit participants',
            'Conduct experiment',
            'Collect data',
            'Analyze data using statistical tests',
            'Interpret data with interpretations of statistical output',
            'Draft review specific to journals of interest',
            'Record rejections or acceptances of journals',
        ],
        'exploratory': [
            'Choose 1 case',
            'Gather documents on that case',
            'Conduct interviews on that case',
            'Organize evidence on that case',
            'Analyze evidence on the case',
            'Compare analysis of this case to other well-known generalizations of similar cases',
            'Draft review specific to journals of interest',
            'Record rejections or acceptances of journals',
        ],
        'pilot': [
            'Identify broad research question',
            'Do literature review',
            'Construct hypothesis',
            'Standardize the experimental design for small cohort',
            'Recruit participants',
            'Conduct experiment',
            'Collect data',
            'Analyze data using statistical tests',
            'Interpret data with interpretations of statistical output',
            'Draft review specific to journals of interest',
            'Record rejections or acceptances of journals',
        ],
        'literature_review': [
            'Identify broad research question',
            'Search databases and screen all papers',
            'Exclude weak studies',
            'Extract information from the papers',
            'Synthesize findings from the papers',
            'Identify limitations and gaps',
            'Draft review specific to journals of interest',
            'Record rejections or acceptances of journals',
        ],
        'clinical': [
            'Identify broad research question',
            'Do literature review',
            'Construct hypothesis',
            'Design protocol',
            'Get ethics approval',
            'Recruit participants',
            'Give and track interventions',
            'Monitor safety',
            'Collect data',
            'Analyze data using statistical tests',
            'Interpret data with interpretations of statistical output',
            'Draft review specific to journals of interest',
            'Record rejections or acceptances of journals',
        ],
    }

    # Manuscript sections drafted per project
    MANUSCRIPT_SECTIONS = [
        'abstract', 'introduction', 'methods', 'results', 'discussion', 'references'
    ]

    # Journal submission statuses
    SUBMISSION_STATUSES = ['target', 'submitted', 'under_review', 'revisions_requested', 'accepted', 'rejected']

    # Project lifecycle statuses
    PROJECT_STATUSES = ['active', 'on_hold', 'completed', 'archived']

    # API Keys from environment
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # Optional literature database keys. Europe PMC, CrossRef, arXiv, ERIC,
    # and Semantic Scholar are free/public and always active. Scopus and
    # ScienceDirect (Elsevier) and Web of Science (Clarivate) require a
    # registered API key and are only queried if the corresponding key is set.
    ELSEVIER_API_KEY = os.getenv('ELSEVIER_API_KEY')  # covers Scopus + ScienceDirect
    WOS_API_KEY = os.getenv('WOS_API_KEY')  # Web of Science Starter/Expanded API
    SEMANTIC_SCHOLAR_API_KEY = os.getenv('SEMANTIC_SCHOLAR_API_KEY')  # raises anonymous rate limits

    # Local AI assistant (optional, explicitly opt-in per feature - never automatic).
    # Defaults target a local Ollama server running qwen2.5:7b-instruct, which runs
    # fine on CPU (no GPU required). Override via .env to point at a different
    # OpenAI-compatible server/model.
    AI_BASE_URL = os.getenv('AI_BASE_URL', 'http://localhost:11434')
    AI_MODEL = os.getenv('AI_MODEL', 'qwen2.5:7b-instruct')
    AI_TIMEOUT = int(os.getenv('AI_TIMEOUT', '120'))


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True


def get_config():
    """Get config based on environment"""
    env = os.getenv('FLASK_ENV', 'development')

    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()
