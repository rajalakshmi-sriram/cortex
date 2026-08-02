# Cortex Skill: Idea Generator & Refinement

## Overview
The Idea Generator skill helps researchers brainstorm, formulate, and refine novel neuroscience research ideas. It uses semantic analysis and literature-aware prompting to ensure ideas are scientifically grounded and unique.

## Purpose
- Generate novel research ideas in neuroscience
- Refine existing ideas for clarity and specificity
- Identify gaps in current literature
- Ensure ideas are testable and feasible

## Key Features

### 1. Idea Generation
```python
from skills.idea_generator import IdeaGenerator

generator = IdeaGenerator(config)

# Generate ideas based on research interest
ideas = generator.generate_ideas(
    research_area="memory",
    neuroscience_level="intermediate",
    feasibility="high"
)
```

**Parameters:**
- `research_area` (str): Neuroscience research domain (e.g., "memory", "neural circuits", "neuroplasticity")
- `neuroscience_level` (str): Level of expertise ("beginner", "intermediate", "advanced")
- `feasibility` (str): Resource constraints ("low", "medium", "high")

**Returns:**
- List of novel research ideas
- Rationale for each idea
- Related literature links

### 2. Idea Refinement
```python
refined = generator.refine_idea(
    idea="Investigate dopamine's role in decision-making",
    focus_areas=["methodology", "feasibility", "novelty"]
)
```

**Output:**
- Clarified research question
- Specific hypotheses
- Testable predictions
- Feasibility assessment

### 3. Gap Analysis
```python
gaps = generator.identify_gaps(
    research_idea="Study neuroplasticity in aging",
    research_area="cognitive aging"
)
```

**Identifies:**
- Underexplored aspects
- Conflicting findings in literature
- Methodological gaps
- Population gaps

## Use Cases

### Case 1: Brainstorming Session
A junior researcher wants to develop thesis ideas in memory research:

```python
ideas = generator.generate_ideas(
    research_area="memory consolidation",
    neuroscience_level="intermediate",
    feasibility="high"
)

for idea in ideas:
    print(f"Idea: {idea['title']}")
    print(f"Rationale: {idea['rationale']}")
    print(f"Related Papers: {idea['related_papers']}")
```

### Case 2: Refining a Vague Idea
A researcher has a general idea that needs specificity:

```python
original_idea = "Look at how sleep affects brain"

refined = generator.refine_idea(
    idea=original_idea,
    focus_areas=["hypothesis", "methodology", "feasibility"]
)

print(f"Refined Question: {refined['research_question']}")
print(f"Hypotheses: {refined['hypotheses']}")
print(f"Measurement Approach: {refined['measurement_approach']}")
```

### Case 3: Literature-Informed Idea Development
Developing ideas informed by recent literature:

```python
idea = "Optogenetic stimulation of prefrontal-amygdala circuits in fear extinction"

analysis = generator.analyze_idea(
    idea=idea,
    literature_cutoff="2023"
)

print(f"Novelty Score: {analysis['novelty_score']}")
print(f"Most Similar Papers: {analysis['similar_papers']}")
print(f"Unique Contributions: {analysis['unique_aspects']}")
```

## Technical Details

### Semantic Matching
- Uses embedding-based similarity matching
- Compares ideas against PubMed, bioRxiv, arXiv
- Identifies near-duplicates and similar concepts

### Feasibility Assessment
- Equipment requirements analysis
- Time-to-completion estimation
- Regulatory/ethical considerations
- Budget-conscious recommendations

### Methodology Integration
- Links generated ideas to appropriate research modes
- Suggests suitable experimental designs
- Recommends analysis strategies

## API Reference

### IdeaGenerator Class

#### Methods:

**`generate_ideas(research_area, neuroscience_level, feasibility)`**
- Generates novel research ideas
- Returns: `List[Dict]` with idea, rationale, related papers

**`refine_idea(idea, focus_areas)`**
- Refines and clarifies research ideas
- Returns: `Dict` with refined question, hypotheses, methodology

**`analyze_idea(idea, literature_cutoff)`**
- Analyzes idea novelty and related literature
- Returns: `Dict` with novelty score, similar papers, unique aspects

**`get_gap_analysis(research_area)`**
- Identifies research gaps in given area
- Returns: `List[Dict]` of gap opportunities

**`assess_feasibility(idea, resources)`**
- Assesses practical feasibility of idea
- Returns: `Dict` with feasibility score, constraints, resources needed

## Best Practices

1. **Start Broad, Get Specific**
   - Begin with research area of interest
   - Progressively refine to testable hypothesis
   - Use gap analysis to find white space

2. **Check Literature Frequently**
   - Validate ideas against current research
   - Look for conflicting findings
   - Identify methodological innovations

3. **Consider Feasibility Early**
   - Assess resource availability
   - Plan for timeline realistically
   - Account for ethical/regulatory requirements

4. **Iterate Ideas**
   - Start with rough ideas
   - Refine through multiple iterations
   - Validate each refinement against literature

## Related Skills
- [Research Mode Selection](./SKILL_research_modes.md)
- [Literature Analysis](./SKILL_literature_analysis.md)
- [Hypothesis Formulation](./SKILL_hypothesis.md)

## Examples

### Example 1: Novel Memory Consolidation Study
```python
idea = generator.generate_ideas(
    research_area="memory consolidation",
    neuroscience_level="intermediate",
    feasibility="high"
)[0]

# Outputs:
# {
#   "title": "Role of astrocyte-neuron signaling in sleep-dependent memory consolidation",
#   "rationale": "Recent evidence suggests astrocytes play active roles in synaptic plasticity...",
#   "research_question": "Does targeted activation of astrocytic GPCR pathways enhance memory consolidation during sleep?",
#   "hypotheses": ["H1: Astrocyte activation increases...", "H2: This effect is sleep-stage specific..."],
#   "related_papers": [...]
# }
```

### Example 2: Translational Research Idea
```python
idea = "Develop neuroprotective intervention for Parkinson's disease"

refined = generator.refine_idea(idea)
# Returns specific mechanism, target, and clinical development pathway
```

## Troubleshooting

**Q: Generated ideas are too similar to my earlier ideas**
- A: Specify "novelty_weight=high" to push toward less common research angles

**Q: Ideas seem too broad or unfeasible**
- A: Use "feasibility=high" and specify target research context

**Q: Can't find related literature for refined idea**
- A: May indicate true novelty! Conduct informal literature search to validate

## Version
Skill Version: 1.0.0
Last Updated: 2024
Cortex Version: 1.0+
