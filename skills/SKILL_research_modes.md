# Cortex Skill: Research Mode Selection & Methodology Guidance

## Overview
The Research Modes skill helps researchers select appropriate research methodologies and provides step-by-step guidance through complex research designs. It covers 10 distinct research modes ranging from exploratory to clinical investigations.

## Purpose
- Select appropriate research methodology for your idea
- Understand the 10 research modes (modes of inquiry, translational pipeline, data workflows)
- Get detailed step-by-step guidance
- Access mode-specific best practices and common pitfalls

## The 10 Research Modes

### 1. Experimental Mode
**Goal:** Establish causal relationships by manipulating independent variables

**When to use:**
- Testing specific hypotheses
- Examining cause-effect relationships
- Controlled laboratory settings
- Need for internal validity

**Key characteristics:**
- Random assignment to conditions
- Manipulation of independent variable
- Control of confounding variables
- Statistical analysis of effects

**Timeline:** 6-24 months
**Complexity:** High
**Sample size:** Depends on effect size and power

### 2. Quasi-Experimental Mode
**Goal:** Compare naturally occurring groups when random assignment is impossible

**When to use:**
- Clinical populations (TBI, stroke)
- Unethical/impossible to randomize
- Longitudinal comparisons
- Natural disasters/interventions

**Key characteristics:**
- Pre-existing groups
- Statistical control of confounders
- No manipulation by researcher
- Careful matching/adjustment

**Timeline:** 6-18 months
**Complexity:** Medium-High
**Important:** Cannot claim causality as strongly as experimental

### 3. Observational / Correlational Mode
**Goal:** Identify relationships without intervention

**When to use:**
- Identifying associations
- Preliminary hypothesis generation
- Feasibility assessment
- Long-term tracking studies

**Key characteristics:**
- Natural measurement of variables
- No intervention
- Correlational analysis
- Multiple regression for prediction

**Timeline:** 3-12 months
**Complexity:** Medium
**Limitation:** Correlation ≠ Causation

### 4. Descriptive / Exploratory Mode
**Goal:** Describe unknown phenomena and generate future hypotheses

**When to use:**
- Novel phenomena just discovered
- Rare conditions or populations
- Detailed documentation needed
- Pattern identification

**Key characteristics:**
- Qualitative and quantitative description
- Case studies and detailed observation
- Pattern identification
- Hypothesis generation

**Timeline:** 6-18 months
**Complexity:** Medium
**Output:** Detailed descriptions and classifications

### 5. Basic (Fundamental) Neuro-Research
**Goal:** Discover fundamental biological mechanisms

**When to use:**
- Understanding normal brain function
- Mechanism discovery
- Animal models and in vitro systems
- Pure science without application focus

**Key characteristics:**
- Mechanistic hypothesis testing
- Reductionist approach
- Multiple model systems
- Theoretical framework building

**Timeline:** 2-5 years
**Complexity:** Very High
**Impact:** Foundational for future translational work

### 6. Translational Neuro-Research
**Goal:** Convert basic discoveries into therapeutic applications

**When to use:**
- Moving from lab to clinic
- Drug/device development
- Disease model testing
- Intervention validation

**Key characteristics:**
- Target validation from basic research
- Intervention design
- Disease model testing
- Safety and efficacy assessment

**Timeline:** 3-5 years
**Complexity:** Very High
**Resources:** Interdisciplinary team needed

### 7. Clinical Neuro-Research
**Goal:** Evaluate treatments, diagnostics, or outcomes in humans

**When to use:**
- Testing in human subjects
- Regulatory approval needed
- Patient safety paramount
- Clinical decision-making

**Key characteristics:**
- Prospective registration
- Ethics approval
- Informed consent
- Adverse event monitoring
- Phase I-IV trial structure

**Timeline:** 2-7 years
**Complexity:** Very High
**Regulation:** FDA, EMA, regulatory approval required

### 8. Empirical (Wet-Lab / Direct Measurement) Mode
**Goal:** Generate new primary biological data

**When to use:**
- Need raw, primary biological data
- Method development
- Data for computational models
- Instrument/technique validation

**Key characteristics:**
- Direct physical measurement
- Microscopy, electrophysiology, imaging
- Quality control essential
- Reproducible protocols

**Timeline:** 1-3 years
**Complexity:** Medium-High
**Key skill:** Instrument mastery and troubleshooting

### 9. Computational / In Silico Mode
**Goal:** Build mathematical models or simulations

**When to use:**
- System-level understanding
- Prediction from theory
- Large-scale simulations
- Data-driven model building

**Key characteristics:**
- Mathematical/algorithmic models
- Computational simulation
- Data validation
- Parameter exploration

**Timeline:** 1-3 years
**Complexity:** Medium-High
**Key skill:** Programming and mathematics

### 10. Secondary / Meta-Analytic Mode
**Goal:** Synthesize existing research to produce stronger evidence

**When to use:**
- Multiple independent studies exist
- Conflicting findings need resolution
- Strong evidence synthesis needed
- Systematic knowledge review

**Key characteristics:**
- Systematic search strategy
- Quality assessment
- Effect size calculation
- Meta-analysis or narrative synthesis

**Timeline:** 1-2 years
**Complexity:** Medium
**Output:** Stronger evidence, gap identification

## Mode Selection Framework

### Decision Tree
```
1. Do you need to establish causality?
   YES → Do you have random assignment capability?
         YES → Experimental Mode
         NO → Quasi-Experimental Mode
   NO → Continue to 2

2. Do you want to identify associations?
   YES → Observational Mode
   NO → Continue to 3

3. Is the phenomenon well-understood?
   YES → Skip Descriptive Mode
   NO → Descriptive Mode (first!)

4. What pipeline stage?
   - Basic science → Basic Neuro-Research
   - Bridge to application → Translational
   - Human testing → Clinical

5. What data approach?
   - New primary data → Empirical Mode
   - Mathematical modeling → Computational
   - Synthesizing existing → Meta-Analytic
```

## Step-by-Step Guidance

Each mode provides 15-25 sequential steps with details on:

### For Each Step:
- **Action:** What to do
- **Resources:** Tools and expertise needed
- **Best Practices:** Proven approaches
- **Common Pitfalls:** What to avoid
- **Timeline:** Realistic duration
- **Success Criteria:** How to know you're done

### Example: Experimental Mode Steps
1. Identify a research problem
2. Review existing literature
3. Define the research question
4. Construct hypotheses
5. Identify independent, dependent, control variables
6. Design the experiment
... (through to publication)

## API Reference

### MethodologyEngine Class

```python
from app.methodology_engine import MethodologyEngine

engine = MethodologyEngine(config)
```

#### Methods:

**`get_research_modes()`**
```python
modes = engine.get_research_modes()
# Returns: Dict of all 10 research modes with descriptions
```

**`select_research_mode(mode_key, idea)`**
```python
result = engine.select_research_mode('experimental', 'Study memory formation')
# Returns: Mode details, steps, guidance, timeline estimate
```

**`get_step_details(mode_key, step_number)`**
```python
step = engine.get_step_details('experimental', 5)
# Returns: Step description, resources, best practices, common issues
```

## Mode Comparison Matrix

| Mode | Causality | Feasibility | Timeline | Cost | Publication Impact |
|------|-----------|------------|----------|------|-------------------|
| Experimental | Very High | Medium | 6-24 mo | Medium | Very High |
| Quasi-Experimental | Medium | High | 6-18 mo | Low-Med | High |
| Observational | Low | Very High | 3-12 mo | Low | Medium |
| Descriptive | None | High | 6-18 mo | Medium | Medium |
| Basic Research | N/A | Low | 2-5 yr | High | Very High |
| Translational | Medium | Low | 3-5 yr | Very High | High |
| Clinical | Very High | Low | 2-7 yr | Very High | Very High |
| Empirical | N/A | Medium | 1-3 yr | High | Medium-High |
| Computational | N/A | High | 1-3 yr | Low-Med | High |
| Meta-Analytic | Medium | Very High | 1-2 yr | Low | High |

## Use Cases

### Case 1: Testing Brain-Computer Interface
```
Idea: "BCI improves motor recovery after stroke"

Mode Selection Process:
1. Need causality? YES
2. Random assignment possible? YES → Experimental Mode
3. Population: Stroke patients (quasi-random)
4. Actually: Quasi-Experimental (can't randomly give stroke)

Guidance: 23 steps from problem identification through publication
Timeline: 18-24 months
Key steps: Ethics approval, participant recruitment, device testing, outcome measures
```

### Case 2: Understanding Neural Circuit Function
```
Idea: "Map connectivity of prefrontal-amygdala circuits"

Mode Selection:
1. Need causality? Not initially
2. Phenomenon well-understood? No → Start with Descriptive
3. Use empirical methods → Empirical (Direct Measurement)
4. Later: Experimental for manipulation studies

Best Approach: 
- Phase 1: Descriptive mapping
- Phase 2: Empirical electrophysiology
- Phase 3: Experimental optogenetic manipulation
```

### Case 3: Meta-Analysis of Neuroimaging
```
Idea: "Synthesize findings on amygdala in anxiety"

Mode: Meta-Analytic
1. Search 20+ neuroimaging studies
2. Extract effect sizes
3. Calculate meta-analytic effect
4. Assess publication bias
5. Identify heterogeneity sources

Timeline: 12-18 months
Output: Systematic review + meta-analysis publication
```

## Common Questions

**Q: How do I know which mode is right?**
A: Start with the decision tree above. Consider:
- Do you need to prove causality?
- What resources do you have?
- What timeline is realistic?
- Is the phenomenon well-understood?

**Q: Can I combine modes?**
A: Absolutely! Many studies use mixed approaches:
- Descriptive → Experimental (pilot findings first)
- Basic → Translational → Clinical (traditional pipeline)
- Empirical + Computational (data validates models)

**Q: What if my idea doesn't fit cleanly?**
A: Describe key aspects of your study, and we can recommend the closest fit, then discuss hybrid approaches

## Best Practices

1. **Select mode BEFORE designing study**
   - Prevents wasted time and resources
   - Guides power calculations
   - Informs recruitment strategy

2. **Consider combination approaches**
   - Descriptive studies generate hypotheses
   - Experimental studies test hypotheses
   - Meta-analyses synthesize findings

3. **Match feasibility to resources**
   - Realistic timeline critical
   - Don't underestimate regulatory requirements
   - Plan team composition early

4. **Follow step-by-step guidance**
   - Don't skip steps (especially early planning)
   - Each step builds on previous
   - Late changes become expensive

## Additional Resources

- [Research Mode Step Tracker](./SKILL_step_tracker.md)
- [Statistical Methods by Mode](./SKILL_statistics.md)
- [Ethics & Compliance Guide](./SKILL_ethics.md)
- [Regulatory Pathways](./SKILL_regulatory.md)

## Troubleshooting

**My idea seems to need multiple modes**
- This is common and good! Plan sequential studies:
  1. Descriptive/exploratory first
  2. Then experimental/observational
  3. Follow with translational/clinical

**Timeline seems too long**
- Review for parallel workstreams
- Consider pilot data reduction phases
- Consult domain experts for realistic estimates

**Not sure between two modes**
- Review the mode comparison matrix
- Check case examples
- Consult with methodologists

## Version
Skill Version: 1.0.0
Last Updated: 2024
Cortex Version: 1.0+
Compatible Modes: All 10 modes
