# Cortex Skill: Literature Analysis & Research Synthesis

## Overview
The Literature Analysis skill provides tools to comprehensively analyze neuroscience literature, identify gaps, synthesize findings, and ensure your research idea is novel and builds on existing work.

## Purpose
- Find relevant papers in neuroscience literature
- Identify research gaps and white spaces
- Synthesize conflicting findings
- Track latest advances in your research area
- Benchmark your idea against the state-of-the-art

## Key Features

### 1. Literature Search
```python
from app.literature_fetcher import LiteratureFetcher

fetcher = LiteratureFetcher(config)

# Search multiple databases simultaneously
papers = fetcher.fetch_relevant_papers(
    query="memory consolidation sleep",
    max_results=50
)
```

**Sources:**
- PubMed (biomedical literature)
- bioRxiv (neuroscience preprints)
- arXiv (computational neuroscience)
- 39+ institutional repositories

### 2. Paper Analysis
```python
from skills.literature_analyzer import PaperAnalyzer

analyzer = PaperAnalyzer()

# Extract key information from papers
analysis = analyzer.analyze_paper(
    paper=paper_object,
    extract_methods=True,
    extract_findings=True,
    extract_limitations=True
)
```

**Extraction:**
- Methodology details
- Key findings and effect sizes
- Study limitations
- Future directions proposed
- Relevant citations

### 3. Gap Identification
```python
gaps = analyzer.identify_research_gaps(
    papers=literature_results,
    research_area="memory consolidation"
)
```

**Identifies:**
- Underexplored populations
- Untested interventions
- Conflicting findings
- Methodological gaps
- Technological limitations

## Neuroscience Literature Sources

### Primary Databases
1. **PubMed** - NCBI's biomedical literature database
   - 35+ million citations
   - Coverage: 1960-present
   - Search: MeSH terms recommended

2. **bioRxiv** - Preprints in neuroscience
   - Latest unpublished findings
   - 2-3 month lag to peer review
   - Search: Category + keyword

3. **arXiv** - Computational and theoretical
   - Math, computer science, physics approaches
   - Rapid dissemination
   - Categories: q-bio.NC (neuroscience)

### Specialty Journals & Repositories
- **Nature Neuroscience** - Top-tier findings
- **Cell Neuron** - Mechanisms and circuits
- **Journal of Neuroscience** - Broad neuroscience
- **NeuroImage** - Neuroimaging methods
- **Brain** - Human neurology and behavior
- **eLife Sciences** - Open access peer review
- **Frontiers Neuroscience** - Broad neuroscience
- **Trends Neurosciences** - Review articles

### Data Repositories
- **OpenNeuro** - Neuroimaging datasets
- **Human Connectome Project** - Brain connectivity
- **Allen Brain Atlas** - Neuroanatomy
- **DANDI Archive** - Neurophysiology data
- **NeuroQuery** - Semantic search tool
- **NeuroSynth** - Meta-analytic maps

## Search Strategies

### Effective PubMed Searches

**Basic search:**
```
memory consolidation sleep
# Returns all papers with any of these terms
```

**Boolean operators:**
```
("memory consolidation" OR "memory consolidation") AND sleep AND (mouse OR rodent)
# Specific combination of terms
```

**MeSH terms:**
```
[MeSH Terms: "Memory, Long-Term"] AND [MeSH Terms: "Sleep"]
# More precise, uses controlled vocabulary
```

**Date filtering:**
```
memory consolidation[ti] 2020:2024[pdat]
# Title contains term, published 2020-2024
```

**Author/Journal:**
```
memory consolidation[ti] AND "Nature Neuroscience"[jour]
# Papers from specific journal
```

### Advanced Search Examples

**Finding specific techniques:**
```
optogenetics AND hippocampus AND memory
# Studies using optogenetics in hippocampus for memory research
```

**Identifying animal models:**
```
memory consolidation AND (transgenic OR "knockout mice" OR "conditional knockout")
# Genetic animal model studies
```

**Human studies in neuroscience:**
```
("memory consolidation" OR "memory consolidation") AND humans AND (fMRI OR imaging)
# Human neuroimaging studies
```

## Literature Analysis Process

### Step 1: Systematic Search
1. Define research question
2. Identify key search terms and variations
3. Search multiple databases
4. Export results to bibliography manager
5. Document search strategy

### Step 2: Screen Results
1. Remove duplicates
2. Screen titles and abstracts
3. Apply inclusion/exclusion criteria
4. Pull full texts for inclusion
5. Track screening decisions

### Step 3: Extraction
For each included paper, extract:
- Bibliographic information
- Study design (mode)
- Sample characteristics
- Methods used
- Key findings
- Effect sizes (if applicable)
- Limitations noted
- Future research suggested

### Step 4: Analysis
- Identify methodological approaches
- Categorize findings (confirmatory vs. conflicting)
- Look for effect size patterns
- Note technology used (e.g., fMRI, electrophysiology)
- Identify underexplored areas

### Step 5: Synthesis
- Narrative summary of findings
- Effect size meta-analysis (if applicable)
- Identification of conflicts
- Emerging consensus areas
- Specific research gaps

## API Reference

### LiteratureFetcher
```python
from app.literature_fetcher import LiteratureFetcher

fetcher = LiteratureFetcher(config)

# Fetch papers
papers = fetcher.fetch_relevant_papers(
    query="memory consolidation",
    max_results=20
)
# Returns: List[Dict] with title, authors, abstract, year, source, DOI
```

### PaperAnalyzer (hypothetical)
```python
from skills.literature_analyzer import PaperAnalyzer

analyzer = PaperAnalyzer()

# Analyze methodology of papers
methods = analyzer.extract_methodologies(papers)
# Returns: Common techniques, animal models, measurement approaches

# Identify gaps
gaps = analyzer.identify_gaps(papers)
# Returns: Populations, interventions, measures not yet studied

# Extract findings
findings = analyzer.extract_findings(papers)
# Returns: Effect sizes, contradictions, consensus areas
```

## Use Cases

### Case 1: Comprehensive Lit Review
Researcher needs thorough background before starting study:

```python
# 1. Search broadly
papers = fetcher.fetch_relevant_papers("memory consolidation", max_results=50)

# 2. Screen to relevant subset
screened = [p for p in papers if p['year'] >= 2018]

# 3. Categorize approaches
empirical = [p for p in screened if 'electrophysiology' in p['methods']]
computational = [p for p in screened if 'model' in p['title'].lower()]
clinical = [p for p in screened if 'human' in p['species']]

# 4. Identify gaps
gaps = analyzer.identify_gaps(papers)
# "Most studies use young animals - aging literature sparse"
# "Optogenetics common, but chemogenetics rare"
```

### Case 2: Confirming Novelty
Validating that your idea is truly novel:

```python
idea = "Astrocyte signaling in memory consolidation"

# Search for similar studies
papers = fetcher.fetch_relevant_papers(idea, max_results=100)

# Check similarity
similarity_scores = analyzer.compute_similarity(idea, papers)

# Identify most similar papers
similar = sorted(similarity_scores, key=lambda x: x['score'], reverse=True)[:5]

# Assess novelty
novelty = analyzer.assess_novelty(idea, papers)
# Returns novelty_score, unique_aspects, closest_competitors
```

### Case 3: Identifying Research Gaps
Finding white-space research opportunities:

```python
# Analyze literature in an area
papers = fetcher.fetch_relevant_papers("neuroplasticity", max_results=200)

# Find gaps
gaps = analyzer.identify_research_gaps(papers)

# Examine each gap
for gap in gaps:
    print(f"Gap: {gap['description']}")
    print(f"Related studies: {gap['related_paper_count']}")
    print(f"Feasibility: {gap['feasibility_assessment']}")
```

## Best Practices

### 1. Comprehensive Searching
- Use multiple databases (PubMed, bioRxiv, specialty journals)
- Try multiple search term combinations
- Don't just use Google Scholar results
- Set date limits appropriately
- Document your search strategy

### 2. Screening Quality
- Use standardized inclusion/exclusion criteria
- Have 2 people screen (when possible) to check agreement
- Extract screening decisions and rationale
- Note when papers are borderline
- Maintain audit trail of decisions

### 3. Data Extraction
- Use standard forms/templates
- Define variables clearly before extraction
- Pilot test extraction form on 3-5 papers
- Check extraction on subset for accuracy
- Document any clarifications

### 4. Analysis Rigor
- Look for methodological quality issues
- Note conflicts in findings
- Don't just count studies (weight by quality)
- Consider publication bias
- Look for effect size patterns

### 5. Synthesis Quality
- Go beyond simple summary
- Integrate findings narratively
- Highlight contradictions
- Propose mechanistic explanations
- Identify specific future research needs

## Common Pitfalls

1. **Incomplete searches**
   - Only looking at PubMed, missing preprints
   - Limited search terms
   - Ignoring older foundational papers

2. **Citation bias**
   - Only reading most-cited papers
   - Missing recent cutting-edge work
   - Overlooking minority opinions

3. **Confirmation bias**
   - Over-weighting agreeing studies
   - Dismissing contradictory findings
   - Not considering alternative explanations

4. **Shallow synthesis**
   - Just listing papers
   - Not critically evaluating methodology
   - Missing nuanced findings in papers

5. **Novelty overestimation**
   - Not finding similar existing work
   - Missing recent preprints
   - Underestimating indirect similarity

## Tools & Resources

### Bibliography Managers
- **Zotero** (free, open-source)
- **Mendeley** (free version available)
- **Notion** (flexible, all-in-one)

### Systematic Review Tools
- **Covidence** (commercial)
- **DistillerSR** (commercial)
- **CADIMA** (free, online)
- **Rayyan** (free from Qatar Computing)

### Semantic Search
- **NeuroQuery** (pubmed, bioRxiv, neurosynth)
- **Scopus** (multidisciplinary)
- **Web of Science** (citation tracking)

### Meta-Analysis
- **Review Manager** (Cochrane tool)
- **Comprehensive Meta-Analysis** (commercial)
- **R metafor package** (open-source)

## Examples

### Example Search Strategy
```
Goal: Find studies on circadian regulation of memory consolidation

Search 1: PubMed
"circadian rhythm*" AND ("memory consolidation" OR "memory formation")
Limits: Last 5 years, English, humans OR animals
Result: 127 papers

Search 2: bioRxiv
"circadian" AND "memory consolidation"
Result: 23 preprints

Search 3: arXiv (computational angle)
"circadian" AND "memory" AND ("model" OR "simulation" OR "network")
Result: 8 papers

Total unique papers: 145
After screening: 45 relevant papers
Final review set: 25 high-quality papers
```

### Example Gap Analysis
```
Analysis of 100 papers on memory consolidation:

Findings:
✓ 89 studies in rodents; 11 in humans
✓ Hippocampus covered extensively; anterior temporal lobe rare
✓ Sleep-dependent consolidation well-studied; wake consolidation understudied
✓ Electrophysiology dominant; optogenetics increasing
✗ Astrocyte-neuron interactions understudied
✗ Aging population largely absent (only 2 papers)
✗ Sex differences minimally examined
✗ Translational/clinical studies rare (3 papers)

Identified Gaps:
1. Astrocyte-neuron signaling → HIGH PRIORITY
2. Aging memory consolidation → MEDIUM PRIORITY
3. Sex-specific differences → MEDIUM PRIORITY
4. Clinical translation → EMERGING
```

## Version
Skill Version: 1.0.0
Last Updated: 2024
Cortex Version: 1.0+
Compatible with: All research modes
