# Cortex: Brain Research Methodology Platform

A comprehensive Python application for developing, validating, and guiding neuroscience research ideas through rigorous methodologies.

## Overview

**Cortex** is an intelligent research assistant that:

1. **Validates Research Ideas** - Checks uniqueness against 30+ neuroscience literature sources
2. **Recommends Related Research** - Identifies and summarizes top 5 related papers
3. **Guides Research Design** - Provides step-by-step methodology for 10 distinct research modes
4. **Supports Research Planning** - Offers mode-specific best practices and common pitfalls

### The 10 Research Modes

| Mode | Purpose | Use Case |
|------|---------|----------|
| **Experimental** | Establish causal relationships | Hypothesis-driven lab studies |
| **Quasi-Experimental** | Compare naturally occurring groups | Clinical populations, unethical-to-randomize |
| **Observational** | Identify relationships | Correlational studies, surveys |
| **Descriptive** | Document novel phenomena | Rare conditions, new discoveries |
| **Basic Research** | Discover fundamental mechanisms | Understanding normal brain function |
| **Translational** | Bridge basic to clinical | Drug/device development |
| **Clinical** | Evaluate in humans | Clinical trials, patient outcomes |
| **Empirical** | Generate primary data | Wet-lab measurement |
| **Computational** | Build mathematical models | Simulations, algorithms |
| **Meta-Analytic** | Synthesize existing research | Systematic reviews |

## Project Structure

```
cortex/
├── app/                          # Main application modules
│   ├── app.py                   # Flask REST API
│   ├── idea_validator.py        # Idea validation engine
│   ├── literature_fetcher.py    # Research paper aggregator
│   ├── nlp_engine.py            # Semantic analysis
│   ├── methodology_engine.py    # Research methodology guidance
│   └── logger.py                # Logging configuration
├── config/
│   └── config.py                # Application configuration
├── skills/                       # Specialized skill modules
│   ├── SKILL_idea_generator.md          # Idea generation and refinement
│   ├── SKILL_research_modes.md          # Research mode selection
│   └── SKILL_literature_analysis.md     # Literature analysis
├── data/                         # Data storage
│   ├── validation_history.jsonl # Idea validation history
│   └── methodology_history.jsonl # Methodology selections
├── logs/                         # Application logs
├── tests/                        # Unit tests
├── requirements.txt              # Python dependencies
├── run.py                        # Application entry point
└── README.md                     # This file
```

## Installation

### Prerequisites
- Python 3.8+
- pip or conda
- Virtual environment (recommended)

### Setup

1. **Clone or navigate to project**
```bash
cd /Users/rajalakshmisriram/cortex
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variables** (optional)
```bash
# Create .env file in project root
export FLASK_ENV=development
export PORT=5000
export ANTHROPIC_API_KEY=your_key_here  # For future Claude integration
export OPENAI_API_KEY=your_key_here     # For embedding models
```

## Quick Start

### Run the Application

```bash
# From project root
python run.py
```

The application will start on `http://localhost:5000`

### API Endpoints

#### 1. Health Check
```bash
curl http://localhost:5000/health
```

#### 2. Validate a Research Idea
```bash
curl -X POST http://localhost:5000/api/v1/ideas/validate \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "Investigate the role of astrocytes in memory consolidation using optogenetics"
  }'
```

**Response (Unique Idea):**
```json
{
  "status": "unique",
  "message": "Congratulations! Your idea appears to be unique...",
  "valid": true,
  "related_papers": [
    {
      "title": "Astrocytes regulate sleep homeostasis...",
      "authors": ["Author1", "Author2"],
      "year": 2023,
      "source": "Nature Neuroscience",
      "similarity_score": 0.68
    }
  ],
  "max_similarity_score": 0.68,
  "next_action": "Proceed to methodology selection"
}
```

**Response (Similar/Duplicate Idea):**
```json
{
  "status": "similar",
  "message": "Your idea is similar to existing research...",
  "valid": false,
  "similar_papers": [
    {
      "title": "Memory consolidation requires astrocyte signaling",
      "authors": ["Author3", "Author4"],
      "year": 2022,
      "source": "Cell Neuron",
      "similarity_score": 0.82
    }
  ],
  "max_similarity_score": 0.82,
  "next_action": "Please refine your idea and try again"
}
```

#### 3. Get Available Research Modes
```bash
curl http://localhost:5000/api/v1/research-modes
```

#### 4. Select Research Methodology
```bash
curl -X POST http://localhost:5000/api/v1/methodology/select \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "Investigate astrocytes in memory consolidation",
    "mode": "experimental"
  }'
```

**Response:**
```json
{
  "status": "success",
  "valid": true,
  "mode": "experimental",
  "mode_name": "Experimental Mode",
  "description": "Establish causal relationship by manipulating independent variables",
  "steps": [
    "Identify a research problem",
    "Review existing literature",
    "Define the research question",
    ...
  ],
  "total_steps": 25,
  "guidance": {
    "overview": "Establish a causal relationship...",
    "key_considerations": [...],
    "timeline_estimate": "6-24 months",
    "resources_needed": [...],
    "common_pitfalls": [...]
  }
}
```

#### 5. Get Step Details
```bash
curl http://localhost:5000/api/v1/methodology/experimental/step/3
```

## Usage Examples

### Example 1: Validate and Get Guidance

```python
import requests
import json

BASE_URL = "http://localhost:5000/api/v1"

# Step 1: Validate idea
idea = "Study neuroplasticity in aging brain using fMRI"

response = requests.post(
    f"{BASE_URL}/ideas/validate",
    json={"idea": idea}
)

result = response.json()

if result['valid']:
    print(f"✓ Idea is {result['status']}")
    print(f"Similarity score: {result['max_similarity_score']:.2%}")
    
    if result['status'] == 'unique':
        # Step 2: Select research mode
        mode_response = requests.post(
            f"{BASE_URL}/methodology/select",
            json={
                "idea": idea,
                "mode": "experimental"
            }
        )
        
        methodology = mode_response.json()
        print(f"\nSelected: {methodology['mode_name']}")
        print(f"Total steps: {methodology['total_steps']}")
        print(f"Timeline: {methodology['guidance']['timeline_estimate']}")
        
        # Step 3: Get first step details
        step_response = requests.get(
            f"{BASE_URL}/methodology/experimental/step/1"
        )
        
        step = step_response.json()
        print(f"\nFirst step: {step['step']}")
else:
    print(f"✗ Idea validation failed: {result['message']}")
```

### Example 2: Research Mode Exploration

```python
# Get all research modes
modes_response = requests.get(f"{BASE_URL}/research-modes")
modes = modes_response.json()['modes']

print("Available Research Modes:")
for mode_key, mode_info in modes.items():
    print(f"  {mode_info['name']}")
    print(f"    {mode_info['description']}\n")
```

### Example 3: Literature-Aware Idea Validation

```python
# Batch validate multiple ideas
ideas = [
    "Dopamine role in decision-making",
    "Serotonin and anxiety in aging mice",
    "Circadian rhythm effects on cognition"
]

for idea in ideas:
    response = requests.post(
        f"{BASE_URL}/ideas/validate",
        json={"idea": idea}
    )
    result = response.json()
    
    print(f"Idea: {idea}")
    print(f"Status: {result['status']}")
    print(f"Match: {result['max_similarity_score']:.1%}\n")
```

## Key Features

### 1. Idea Validation Engine
- **Semantic Similarity Matching**: Uses NLP to compare ideas against 30+ literature sources
- **Multi-Source Aggregation**: Fetches papers from PubMed, bioRxiv, arXiv
- **Duplicate Detection**: Identifies similar existing research
- **Paper Recommendations**: Suggests top 5 related papers

### 2. Research Methodology Guidance
- **10 Distinct Modes**: Covers experimental, translational, clinical, and computational approaches
- **Step-by-Step Guidance**: 15-25 sequential steps per mode
- **Mode-Specific Resources**: Best practices and common pitfalls
- **Timeline Estimates**: Realistic duration for each mode

### 3. Literature Integration
- **PubMed API**: Access to 35+ million biomedical articles
- **bioRxiv Integration**: Latest preprints in neuroscience
- **arXiv Support**: Computational and theoretical neuroscience
- **Smart Deduplication**: Removes duplicate papers from multiple sources

### 4. Intelligent Search
- **Keyword-Based Matching**: Identifies relevant papers
- **Semantic Analysis**: Understands concept relationships
- **Source Diversity**: Aggregates across multiple databases
- **Quality Filtering**: Prioritizes peer-reviewed sources

## Architecture

### Components

#### 1. **IdeaValidator**
Validates research ideas for uniqueness and relevance
- Validates input format and length
- Fetches relevant papers from literature
- Calculates semantic similarity
- Determines uniqueness status
- Saves validation history

#### 2. **LiteratureFetcher**
Aggregates research papers from multiple sources
- PubMed search and retrieval
- bioRxiv preprint integration
- arXiv computational research
- Paper deduplication
- Metadata extraction

#### 3. **SemanticAnalyzer** (NLP Engine)
Performs semantic analysis on text
- Keyword extraction
- Embedding generation
- Cosine similarity calculation
- Neuroscience-aware weighting

#### 4. **MethodologyEngine**
Provides research methodology guidance
- Offers 10 distinct research modes
- Generates step-by-step guidance
- Provides mode-specific recommendations
- Tracks methodology selections

#### 5. **Flask REST API**
Exposes all functionality via HTTP endpoints
- RESTful API design
- JSON request/response
- CORS support
- Error handling
- Request logging

## Configuration

Edit `config/config.py` to customize:

```python
# Idea validation
MAX_IDEA_LENGTH = 500        # Max characters
MIN_IDEA_LENGTH = 10         # Min characters

# Literature sources
NEUROSCIENCE_SOURCES = [...]  # List of 39 sources

# Research modes
RESEARCH_MODES = {...}        # 10 modes with descriptions
METHODOLOGY_STEPS = {...}     # Step lists for each mode

# API settings
API_TIMEOUT = 30              # Request timeout (seconds)
API_RATE_LIMIT = 100          # Requests per minute
```

## Data Flow

```
User Input (Idea)
    ↓
[Idea Validator]
    ├→ Input validation
    ├→ Literature fetching
    └→ Similarity calculation
        ↓
    Unique? 
        ├→ YES: Recommend related papers
        └→ NO: Suggest refinement
            ↓
[Methodology Engine]
    ├→ Get available modes
    ├→ Select research mode
    └→ Generate step-by-step guidance
        ↓
[User Guidance]
    ├→ Mode overview
    ├→ Timeline estimate
    ├→ Step details
    └→ Best practices & pitfalls
```

## Neuroscience Literature Sources

### Primary Journals
- Nature Neuroscience
- Cell Neuron
- Journal of Neuroscience
- NeuroImage
- Brain
- Nature Reviews Neuroscience

### Databases & Repositories
- PubMed (NCBI)
- bioRxiv
- arXiv (q-bio)
- OpenNeuro
- Human Connectome Project
- Allen Brain Atlas
- DANDI Archive
- NeuroSynth
- NeuroQuery

### Organizations & Institutes
- Society for Neuroscience
- Federation of European Neuroscience Societies
- IBRO (International Brain Research Organization)
- NIH Neuroscience Institute
- Allen Institute
- Human Brain Project
- European BRAIN Initiative

## API Reference

### POST /api/v1/ideas/validate
Validates research idea for uniqueness
- **Request**: `{"idea": "string"}`
- **Response**: Validation result with status, papers, similarity score
- **Status codes**: 200 (success), 400 (bad request), 500 (error)

### GET /api/v1/research-modes
Retrieves all available research modes
- **Response**: List of 10 modes with descriptions
- **Status codes**: 200 (success), 500 (error)

### POST /api/v1/methodology/select
Selects research methodology for an idea
- **Request**: `{"idea": "string", "mode": "string"}`
- **Response**: Mode details, steps, guidance
- **Status codes**: 200 (success), 400 (bad request), 500 (error)

### GET /api/v1/methodology/{mode}/step/{step_number}
Gets detailed guidance for a specific step
- **Parameters**: `mode` (string), `step_number` (integer)
- **Response**: Step details, resources, best practices, common issues
- **Status codes**: 200 (success), 500 (error)

## Skills

Specialized skill modules provide in-depth guidance:

### 1. Idea Generator (SKILL_idea_generator.md)
- Generate novel research ideas
- Refine and clarify ideas
- Analyze idea novelty
- Assess feasibility
- Identify research gaps

### 2. Research Modes (SKILL_research_modes.md)
- Compare 10 research modes
- Select appropriate methodology
- Get mode-specific guidance
- Understand timeline & resources
- Avoid common pitfalls

### 3. Literature Analysis (SKILL_literature_analysis.md)
- Conduct comprehensive literature searches
- Analyze papers systematically
- Identify research gaps
- Synthesize findings
- Assess novelty

## Dependencies

```
Flask==2.3.0                 # Web framework
requests==2.31.0            # HTTP client for API calls
scikit-learn==1.3.0         # Machine learning (similarity)
numpy==1.24.0               # Numerical computing
pandas==2.0.0               # Data processing
beautifulsoup4==4.12.0      # Web scraping
python-dotenv==1.0.0        # Environment variables
anthropic==0.7.0            # Claude AI (future)
openai==1.3.0               # OpenAI (embeddings)
```

## Logging

Logs are written to `/Users/rajalakshmisriram/cortex/logs/cortex.log`

Log levels:
- **DEBUG**: Detailed development information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for issues

View logs:
```bash
tail -f logs/cortex.log          # Live tail
tail -100 logs/cortex.log        # Last 100 lines
grep ERROR logs/cortex.log       # Search for errors
```

## Development

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_idea_validator.py

# Run with coverage
python -m pytest --cov=app tests/
```

### Adding New Features

1. **New Research Mode**:
   - Add mode to `RESEARCH_MODES` in config
   - Add methodology steps to `METHODOLOGY_STEPS`
   - Add guidance to `_generate_mode_guidance()`

2. **New Literature Source**:
   - Add URL to `NEUROSCIENCE_SOURCES`
   - Implement fetcher method in `LiteratureFetcher`
   - Test with sample queries

3. **New Skill**:
   - Create `SKILL_<name>.md` in skills directory
   - Document API and usage
   - Link from main README

## Future Enhancements

### Near-term
- [ ] Claude AI integration for intelligent analysis
- [ ] Machine learning models for idea novelty scoring
- [ ] Interactive research design assistant
- [ ] Automated literature synthesis

### Medium-term
- [ ] Web UI dashboard
- [ ] User accounts and project management
- [ ] Collaborative research planning
- [ ] Budget and timeline estimation

### Long-term
- [ ] AI-powered research assistant
- [ ] Grant writing assistance
- [ ] Regulatory pathway guidance
- [ ] Real-time literature monitoring

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is proprietary. All rights reserved.

## Support

For issues, questions, or suggestions:
- Create an issue in the repository
- Contact: raja@cortex-research.ai
- Documentation: See skills directory

## Citation

If you use Cortex in your research, please cite:

```
Sriram, R. L. (2024). Cortex: A Brain Research Methodology Platform. 
Version 1.0.0. https://github.com/your-repo/cortex
```

## Acknowledgments

Built with:
- Flask for robust web framework
- scikit-learn for machine learning
- PubMed, bioRxiv, arXiv for literature access
- Anthropic's Claude for AI capabilities

## Version History

### v1.0.0 (2024)
- Initial release
- 10 research modes
- Literature validation
- Methodology guidance
- 3 core skills

---

**Cortex: Advancing Neuroscience Research Through Intelligent Methodology Guidance**
