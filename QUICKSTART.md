# Cortex Quick Start Guide

Get up and running with Cortex in 5 minutes!

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## Installation

### 1. Navigate to Project Directory
```bash
cd /Users/rajalakshmisriram/cortex
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
# On Windows: venv\Scripts\activate
```

You should see `(venv)` at the start of your terminal prompt.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

This will install all required packages (Flask, requests, scikit-learn, etc.)

## Running the Application

### Start the Server
```bash
python run.py
```

You should see output like:
```
2024-01-15 10:30:45,123 - cortex - INFO - Starting Cortex application
2024-01-15 10:30:45,124 - cortex - INFO - Environment: development
2024-01-15 10:30:45,125 - cortex - INFO - SemanticAnalyzer initialized
2024-01-15 10:30:45,126 - cortex - INFO - LiteratureFetcher initialized with 39 sources
 * Running on http://0.0.0.0:5000/
 * Press CTRL+C to quit
```

The application is now running on `http://localhost:5000`

## Testing the API

### Option 1: Using the Test Client (Recommended)

In a new terminal (with venv activated):
```bash
python test_client.py
```

This will run comprehensive tests and show you all features in action.

### Option 2: Using curl

In a new terminal, test individual endpoints:

**1. Health Check**
```bash
curl http://localhost:5000/health
```

**2. Validate an Idea**
```bash
curl -X POST http://localhost:5000/api/v1/ideas/validate \
  -H "Content-Type: application/json" \
  -d '{"idea": "Study the role of astrocytes in memory consolidation using optogenetics"}'
```

**3. Get Research Modes**
```bash
curl http://localhost:5000/api/v1/research-modes
```

**4. Select a Methodology**
```bash
curl -X POST http://localhost:5000/api/v1/methodology/select \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "Study memory consolidation in aging mice",
    "mode": "experimental"
  }'
```

### Option 3: Using Python Requests

Create a file `test.py`:

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# Validate an idea
response = requests.post(
    f"{BASE_URL}/api/v1/ideas/validate",
    json={"idea": "Investigate neuroplasticity in aging brains"}
)

result = response.json()
print(json.dumps(result, indent=2))
```

Run it:
```bash
python test.py
```

## Example Workflow

### Step 1: Check Health
```bash
curl http://localhost:5000/health
```
**Expected Response**: `{"status": "healthy", ...}`

### Step 2: Validate Your Research Idea
```bash
curl -X POST http://localhost:5000/api/v1/ideas/validate \
  -H "Content-Type: application/json" \
  -d '{"idea": "Investigate dopamine effects on decision-making in the prefrontal cortex"}'
```

**Expected Response**:
- If unique: `{"status": "unique", "message": "Congratulations!", ...}`
- If similar: `{"status": "similar", "message": "Your idea is similar to...", ...}`

### Step 3: Browse Research Modes
```bash
curl http://localhost:5000/api/v1/research-modes
```

**Expected Response**: List of 10 research modes with descriptions

### Step 4: Select a Methodology
Based on your idea and research situation, select appropriate mode:

```bash
curl -X POST http://localhost:5000/api/v1/methodology/select \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "Investigate dopamine effects on decision-making",
    "mode": "experimental"
  }'
```

**Expected Response**:
- Mode name and description
- 25 sequential steps
- Timeline estimate: "6-24 months"
- Key considerations
- Resource requirements
- Common pitfalls to avoid

### Step 5: Get Step Details
For the first step of your selected methodology:

```bash
curl http://localhost:5000/api/v1/methodology/experimental/step/1
```

**Expected Response**:
- Step description: "Identify a research problem"
- Required resources
- Best practices
- Common issues

## Understanding the Output

### Idea Validation Response
```json
{
  "status": "unique",           // unique, similar, or invalid
  "message": "Congratulations!",
  "valid": true,
  "max_similarity_score": 0.45,  // 0-1, how similar to existing research
  "related_papers": [            // Top 5 papers
    {
      "title": "Paper title",
      "authors": ["Author1", "Author2"],
      "year": 2023,
      "source": "Nature Neuroscience",
      "similarity_score": 0.45
    }
  ]
}
```

### Methodology Selection Response
```json
{
  "status": "success",
  "mode": "experimental",
  "mode_name": "Experimental Mode",
  "description": "Establish causal relationships...",
  "steps": [
    "Identify a research problem",
    "Review existing literature",
    "Define the research question",
    ...
  ],
  "total_steps": 25,
  "guidance": {
    "overview": "...",
    "timeline_estimate": "6-24 months",
    "key_considerations": [...],
    "resources_needed": [...],
    "common_pitfalls": [...]
  }
}
```

## Common Issues & Solutions

### Issue: "Connection refused"
**Solution**: Make sure the application is running:
```bash
python run.py
```

### Issue: "ModuleNotFoundError"
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: "Permission denied" (on Mac/Linux)
**Solution**: Make script executable:
```bash
chmod +x run.py
python run.py
```

### Issue: Port 5000 already in use
**Solution**: Use a different port:
```bash
PORT=5001 python run.py
```

Then test with: `curl http://localhost:5001/health`

## Understanding the 10 Research Modes

| Mode | Use Case | Timeline |
|------|----------|----------|
| **Experimental** | Test hypotheses with random assignment | 6-24 months |
| **Quasi-Experimental** | Compare naturally-occurring groups | 6-18 months |
| **Observational** | Identify associations | 3-12 months |
| **Descriptive** | Document novel phenomena | 6-18 months |
| **Basic Research** | Discover mechanisms | 2-5 years |
| **Translational** | Bridge lab to clinic | 3-5 years |
| **Clinical** | Test in humans | 2-7 years |
| **Empirical** | Generate new data | 1-3 years |
| **Computational** | Build mathematical models | 1-3 years |
| **Meta-Analytic** | Synthesize existing research | 1-2 years |

## Next Steps

### 1. Read the Full README
```bash
cat README.md
```

### 2. Explore the Skills
The `skills/` directory contains detailed guidance:
- `SKILL_idea_generator.md` - Generate and refine ideas
- `SKILL_research_modes.md` - Deep dive into each mode
- `SKILL_literature_analysis.md` - Conduct literature reviews

### 3. Try Real Examples
```python
# Example ideas to validate
ideas = [
    "Role of astrocytes in memory consolidation",
    "Circadian effects on neuroplasticity",
    "Dopamine in decision-making",
    "Sleep-dependent learning mechanisms",
]

# For each idea:
# 1. Validate uniqueness
# 2. Review recommended papers
# 3. Select appropriate mode
# 4. Follow step-by-step guidance
```

### 4. Check the Data
Validation history is stored in:
```bash
cat data/validation_history.jsonl
cat data/methodology_history.jsonl
```

## API Endpoints Reference

### Health & Information
- `GET /health` - Health check
- `GET /api/v1` - API information

### Idea Management
- `POST /api/v1/ideas/validate` - Validate research idea

### Research Modes
- `GET /api/v1/research-modes` - Get all research modes

### Methodology
- `POST /api/v1/methodology/select` - Select methodology
- `GET /api/v1/methodology/{mode}/step/{step}` - Get step details

## Features Overview

✅ **Idea Validation**
- Check uniqueness against 30+ literature sources
- Get similarity scores
- Receive related paper recommendations

✅ **Research Mode Guidance**
- Choose from 10 distinct research methodologies
- Get mode-specific step-by-step guidance
- Understand timeline, resources, and common pitfalls

✅ **Literature Integration**
- Search PubMed, bioRxiv, arXiv simultaneously
- Get paper metadata and abstracts
- Identify related work in your area

✅ **Comprehensive Guidance**
- Best practices for each methodology
- Common issues to avoid
- Resource requirements
- Realistic timeline estimates

## Tips for Success

1. **Start with a clear idea** - More specific ideas yield better validation
2. **Review recommended papers** - Understand the state-of-the-art
3. **Choose appropriate mode** - Consider your resources and timeline
4. **Follow the steps** - Don't skip steps, they build on each other
5. **Plan early** - Better to plan thoroughly upfront

## Performance Expectations

- **Idea validation**: 2-5 seconds (includes literature search)
- **Research modes retrieval**: <1 second
- **Methodology selection**: 1-2 seconds
- **Step details**: <1 second

## Getting Help

### View Logs
```bash
tail -f logs/cortex.log
```

### Check Configuration
```bash
cat config/config.py
```

### Review Documentation
- Main README: `README.md`
- Skill modules: `skills/SKILL_*.md`
- API reference: `README.md` → API Reference section

## Deactivate Virtual Environment

When done, deactivate the virtual environment:
```bash
deactivate
```

---

**You're all set! Start by validating your research idea and exploring the 10 research methodologies.**

Need more help? Check the full README.md or explore the skills directory for detailed guidance.
