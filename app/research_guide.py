"""
Research guidance for Cortex.

Cortex's methodology checklist says *what* the steps are. This module says
*how* to do each one, concretely enough to act on, for someone running their
first project.

Written to be dense rather than encouraging: every line should either tell
you what to do, name a thing you can look up, or describe a specific failure
mode. Where the field has a named framework that beginners are expected to
know - FINER, PICO/SPIDER/SPICE, the three-pass reading method, the standard
internal-validity threats, probability vs non-probability sampling, IMRaD -
it is named, so the term is searchable and recognisable when it turns up in
a supervisor's feedback.

Content is synthesised from standard methodology teaching (university
library research guides, Cochrane's handbook, reporting-standard
documentation, and the methods literature) and rewritten here in Cortex's
own words. Standards are named in the prose so they can be looked up, but
nothing here links out.

SCOPE, which the UI also states: this is general methodology, the parts that
transfer across disciplines. Field-specific and institutional requirements -
ethics review, lab safety, trial registration, data-protection law - are
binding, vary by where you are, and override anything here.
"""

import re
from typing import Dict, List

# ---------------------------------------------------------------------------
# Step guidance
# ---------------------------------------------------------------------------

STEP_KINDS: Dict[str, Dict] = {
    'question': {
        'label': 'Framing the research question',
        'what': (
            "Converting a topic into a question with a definite answer. A topic has no answer "
            "('caffeine and the brain'); a question does ('does a 200mg caffeine dose reduce mean "
            "simple visual reaction time in healthy adults aged 18-25, relative to placebo?'). The "
            "difference is that the second one names a population, an intervention or exposure, a "
            "comparison, and an outcome."
        ),
        'how': [
            "Use a question framework to force out the missing pieces. PICO (Population, "
            "Intervention, Comparison, Outcome) fits quantitative and clinical questions. SPIDER "
            "(Sample, Phenomenon of Interest, Design, Evaluation, Research type) fits qualitative "
            "and mixed-methods work. SPICE (Setting, Perspective, Intervention, Comparison, "
            "Evaluation) fits evaluating a service or programme. PCC (Population, Concept, Context) "
            "fits broad scoping questions.",
            "Then test the question against FINER: Feasible with your time, access and skills; "
            "Interesting enough to sustain you; Novel relative to what's published; Ethical; "
            "Relevant to someone beyond you.",
            "Write down the units. 'Faster' is not measurable until it is 'mean reaction time in "
            "milliseconds'.",
            "Name the comparison explicitly. A measurement with nothing to compare it against "
            "cannot answer a question about effect.",
            "Expect three or four rewrites. Questions narrow after the literature review, which is "
            "the literature review working correctly.",
        ],
        'mistakes': [
            "Scope too wide to finish - the most common reason a first project stalls.",
            "No comparison group specified, so no result can be interpreted.",
            "An outcome that isn't operationalised: 'better learning' with no named measure.",
            "Forcing PICO onto a qualitative question. PICO assumes an intervention and a "
            "comparison; exploratory and qualitative work often has neither, which is what SPIDER "
            "and PCC exist for.",
        ],
        'done_when': (
            "You can name the population, what varies, what you measure and in what units, and what "
            "you compare against - in one sentence."
        ),
    },

    'literature': {
        'label': 'Reviewing the literature',
        'what': (
            "Establishing what is already known, so your question is actually open, and so your "
            "design can learn from studies that already made the mistakes."
        ),
        'how': [
            "Read in three passes rather than front to back. Pass 1 (5-10 min): title, abstract, "
            "headings, figures, conclusion - decide whether to continue. Pass 2 (~1 hr): figures, "
            "tables and their captions carefully, and the argument, noting references worth "
            "chasing. Pass 3 (several hours, only for papers you'll build on): reconstruct the "
            "work in enough detail to identify what you'd challenge.",
            "Judge each paper on five things: what category of paper it is, what it's responding "
            "to, whether the claims are supported, what it actually contributes, and whether it's "
            "clearly written.",
            "Search several databases, not one. Cortex queries Europe PMC, CrossRef, arXiv, "
            "OpenAlex, Semantic Scholar and CORE together.",
            "Build searches from synonyms joined with OR, then combine concepts with AND. Different "
            "fields name the same thing differently, and one vocabulary will miss half the "
            "literature.",
            "Chase citations both directions: the reference list of a key paper (backwards) and "
            "papers citing it (forwards). This finds work that keyword search misses.",
            "Note in your own words with the citation attached, and mark verbatim text as a quote "
            "at the moment you copy it.",
        ],
        'mistakes': [
            "Reading only supporting work.",
            "Collecting 80 PDFs and reading none past the abstract.",
            "One database, one set of keywords.",
            "Unmarked verbatim text in notes, which becomes accidental plagiarism months later.",
        ],
        'done_when': (
            "You can name the specific papers your work responds to, state what each found, and say "
            "precisely what remains unanswered."
        ),
        'beginner_note': (
            "Paywall routes: the preprint (arXiv, bioRxiv, medRxiv), the author's own page, your "
            "library login, or emailing the author - the last works more often than people expect."
        ),
    },

    'hypothesis': {
        'label': 'Constructing a hypothesis',
        'what': (
            "A specific, falsifiable statement of what you expect and why. Distinct from the "
            "question (which asks) and from the prediction (which is what you'd observe if the "
            "hypothesis held)."
        ),
        'how': [
            "State a direction, not just a difference: 'the caffeine group will have lower mean "
            "reaction time', not 'the groups will differ'.",
            "Give the mechanism in one clause - the reason you expect it. Without that it's a "
            "guess, and you can't say what else the mechanism implies.",
            "Write the null hypothesis explicitly (no difference / no association). That is the "
            "thing your statistics will test against.",
            "Record, before collecting data, which result supports and which contradicts. "
            "Pre-registration (OSF, AsPredicted) timestamps this if you want it on record.",
        ],
        'mistakes': [
            "Unfalsifiable phrasing - if no result could contradict it, it isn't a hypothesis.",
            "HARKing: presenting a hypothesis formed after seeing the data as if it were predicted. "
            "It invalidates the p-values reported against it.",
            "Multiple hypotheses tested without accounting for it - the more tests, the more "
            "spurious 'significant' results.",
        ],
        'done_when': "Someone could design a study specifically to prove you wrong.",
        'beginner_note': (
            "Descriptive and exploratory work legitimately has no hypothesis. What matters is not "
            "presenting exploratory findings as though they had been predicted."
        ),
    },

    'design': {
        'label': 'Designing the study',
        'what': (
            "Deciding what you do, to whom, in what order, and what you measure - fixed in writing "
            "before data collection. Design is what determines whether your result supports a "
            "causal claim or only an associational one."
        ),
        'how': [
            "Classify your variables: independent (what you vary), dependent (what you measure), "
            "controlled (what you hold constant), and confounders (what varies with your "
            "independent variable and could explain the result instead).",
            "Protect internal validity - whether the effect really came from your variable. The "
            "standard threats are named and worth checking one by one: history (something happened "
            "between measurements), maturation (participants changed over time regardless), "
            "instrumentation (your measure or observer drifted), regression to the mean (extreme "
            "scores move toward average on retest), selection (groups differed at baseline), and "
            "attrition (who dropped out wasn't random).",
            "Handle confounders by design where possible - randomisation, matching, or restriction - "
            "and by statistical control only where it isn't.",
            "Recognise the trade-off: tightly controlled conditions raise internal validity and "
            "lower external validity (how far the result generalises). Choose deliberately and say "
            "which you prioritised.",
            "Randomise assignment with an actual random process, not alternation or judgement. "
            "Blind whoever can be blinded - at minimum the person scoring the outcome.",
            "Fix the sample size and the analysis plan before starting, along with rules for "
            "outliers, dropouts and missing data.",
            "Pilot it. Most designs contain one flaw that only appears on contact with reality.",
        ],
        'mistakes': [
            "No control or comparison condition.",
            "Several things varying at once, so no single cause can be isolated.",
            "Choosing the analysis after seeing the data.",
            "Treating statistical control as equivalent to randomisation - it only adjusts for "
            "confounders you measured and thought of.",
        ],
        'done_when': (
            "A stranger could run your study from the written protocol without asking you anything, "
            "and you can name which validity threats your design addresses and which it doesn't."
        ),
        'beginner_note': (
            "Design conventions differ sharply by field, and errors here are the most expensive to "
            "discover later. This is the point at which to get a domain expert to read your "
            "protocol."
        ),
    },

    'ethics': {
        'label': 'Ethics approval and research integrity',
        'what': (
            "Formal authorisation from the body responsible for protecting participants - an IRB or "
            "research ethics committee for humans, IACUC or equivalent for animals. Required before "
            "data collection, not after."
        ),
        'how': [
            "Find the reviewing body and its submission deadlines first. Turnaround is typically "
            "weeks, sometimes months, and it sits on your critical path.",
            "Determine your review category. Minimal-risk work may qualify as exempt or expedited, "
            "but that determination is made by the committee, not by you.",
            "Prepare informed consent covering: purpose, what participation involves, time required, "
            "risks and benefits, how data is stored and for how long, and the right to withdraw "
            "without penalty.",
            "For minors, expect both guardian consent and the participant's own assent.",
            "Specify data handling: what identifiers you collect, where they're stored, who has "
            "access, and when they're destroyed. Collect the minimum the question requires.",
            "If you're entering a science fair, check its rules separately - ISEF and many "
            "affiliated fairs require documented pre-approval and disqualify work that skipped it.",
        ],
        'mistakes': [
            "Collecting data before approval. Not retroactively fixable; the data typically can't "
            "be used.",
            "Assuming surveys or observational work are automatically exempt.",
            "Collecting identifiers you have no analytical use for.",
        ],
        'done_when': "Written approval or a documented exemption determination is in hand.",
        'beginner_note': (
            "This is the step where general guidance is least sufficient. Requirements are set by "
            "your institution and jurisdiction and are binding - ask the committee directly."
        ),
    },

    'sampling': {
        'label': 'Recruiting participants or selecting a sample',
        'what': (
            "Choosing who or what you study. The sampling method determines whether your results "
            "can be generalised to a wider population at all."
        ),
        'how': [
            "Decide between probability and non-probability sampling, and know what you're buying. "
            "Probability methods - simple random, systematic, stratified, cluster - give every "
            "member of the population a known chance of selection, and are the only route to "
            "statistical generalisation. Non-probability methods - convenience, purposive, "
            "snowball, quota - are practical and legitimate for exploratory work but cannot support "
            "claims about a wider population.",
            "Use stratified sampling when a subgroup matters and would otherwise be too small to "
            "analyse: divide the population into strata and sample within each.",
            "Write inclusion and exclusion criteria before recruiting and apply them unchanged.",
            "Set sample size in advance from the effect size you care about detecting, not from "
            "what's convenient. Underpowered studies fail to detect real effects.",
            "Record the recruitment funnel: approached, eligible, consented, completed, analysed. "
            "Reporting standards ask for these numbers.",
        ],
        'mistakes': [
            "A convenience sample described as if it were representative. Thirty classmates is a "
            "legitimate sample; the population it represents is 'students like your classmates'.",
            "Self-selection bias - volunteers differ systematically from non-volunteers.",
            "Excluding participants after seeing their results.",
            "Sample size chosen by what was achievable, then reported as though planned.",
        ],
        'done_when': (
            "Sample obtained, criteria documented, recruitment numbers recorded, and you can state "
            "which population your conclusions apply to."
        ),
        'beginner_note': (
            "Small non-probability samples are normal in student work and don't invalidate it. "
            "Overstating who the findings apply to does."
        ),
    },

    'collect': {
        'label': 'Collecting data',
        'what': "Executing the protocol and recording results in a form that survives to analysis.",
        'how': [
            "Keep the raw dataset read-only and never edit it. Do all cleaning into a separate "
            "file, so every processing step can be re-run or reversed.",
            "Name files consistently: project, content, date as YYYYMMDD, and a version number. "
            "Avoid spaces and avoid the word 'final' - it never is.",
            "Version by number (v01, v02), not by label, and record what changed between versions.",
            "Keep a dated log of anything that deviated from protocol, at the time it happened.",
            "Record raw values, not summaries. Averages can be computed later; discarded detail "
            "can't be recovered.",
            "Maintain a data dictionary: every column name, its units, its allowed values, and what "
            "missing data is coded as.",
            "Back up to a second location the same day. Two copies in two places.",
        ],
        'mistakes': [
            "Editing the raw file in place.",
            "Undocumented mid-study procedure changes.",
            "Excluding observations by eye rather than by a pre-defined rule.",
            "Discovering at analysis that a needed variable was never recorded.",
            "Files named 'final', 'final2', 'final_real'.",
        ],
        'done_when': (
            "A read-only raw dataset exists in two locations, with a data dictionary and a "
            "deviation log."
        ),
    },

    'analyze': {
        'label': 'Analysing the data',
        'what': (
            "Testing whether the patterns in your data are distinguishable from chance, and "
            "quantifying how large they are."
        ),
        'how': [
            "Plot the raw data before testing anything. Errors visible in a scatter plot are "
            "invisible in a p-value.",
            "Pick the test from your design and data type: two groups compared once (t-test), three "
            "or more (ANOVA), relationship between continuous variables (correlation or "
            "regression), counts across categories (chi-square). Cortex's Data & Analysis wizard "
            "recommends one and states its reasoning.",
            "Check assumptions before trusting the output - normality, equal variance, independence. "
            "Where they fail, use the non-parametric equivalent (Mann-Whitney for a t-test, "
            "Kruskal-Wallis for one-way ANOVA).",
            "Report effect size and a confidence interval alongside p. Significance says the effect "
            "probably isn't zero; effect size says whether it's large enough to matter; the "
            "interval says how precisely you've pinned it down.",
            "Run the pre-specified analysis. Anything additional is exploratory and must be "
            "labelled as such when reported.",
            "If you run many tests, correct for it (Bonferroni or similar) or say plainly that you "
            "didn't.",
        ],
        'mistakes': [
            "p-hacking: trying tests, subgroups or exclusions until something clears 0.05.",
            "Reading p > 0.05 as evidence of no effect rather than absence of detection.",
            "Reporting significance with no effect size, so the reader can't judge importance.",
            "Applying a parametric test to data that violates its assumptions.",
        ],
        'done_when': (
            "Pre-specified analyses are run, assumptions checked and reported, and every result has "
            "an effect size as well as a p-value."
        ),
        'beginner_note': (
            "A p-value is the probability of data at least this extreme if there were genuinely no "
            "effect. It is not the probability that your hypothesis is true, and not the "
            "probability the result was a fluke."
        ),
    },

    'interpret': {
        'label': 'Interpreting results',
        'what': "Stating what the numbers answer, and bounding what they can't.",
        'how': [
            "Answer the original question in one plain sentence before anything else.",
            "Match the claim to the design. Randomised assignment supports a causal claim; "
            "observational data supports an associational one. Say which you have.",
            "State the population the finding applies to - your actual sample, not the one you "
            "wish you'd had.",
            "List specific limitations with their direction: not 'small sample' but 'n=32 from one "
            "school, so age and setting are uncontrolled and the effect may not hold in older "
            "adults'.",
            "Give the alternative explanations you can't rule out, including residual confounding.",
            "Report results that contradicted your hypothesis with the same prominence as those "
            "that supported it.",
        ],
        'mistakes': [
            "Causal language from a correlational design - 'increases', 'improves', 'causes'.",
            "Generalising past the sampled population.",
            "Quietly dropping an unsupported hypothesis.",
            "Treating a non-significant result as proof of no effect.",
        ],
        'done_when': (
            "You can state the finding, the population it covers, the confidence level, and the "
            "specific study that would be needed to strengthen it."
        ),
    },

    'model': {
        'label': 'Building and validating a model',
        'what': (
            "Representing a system as equations, code or simulation, and establishing that its "
            "behaviour tracks reality before drawing conclusions from its output."
        ),
        'how': [
            "List assumptions explicitly, separating the ones made for tractability from the ones "
            "you believe are true.",
            "Validate against something with a known answer: an analytical solution, a benchmark "
            "dataset, or a published result you can reproduce.",
            "Run sensitivity analysis - vary each parameter across its plausible range and report "
            "which conclusions survive and which don't.",
            "Fix and record random seeds; confirm conclusions aren't an artefact of one seed.",
            "Version-control the code and record the exact commit and configuration behind every "
            "reported figure.",
            "Publish code and data. For computational work this is the reproducibility claim.",
        ],
        'mistakes': [
            "Presenting model output as observation of the world.",
            "Fitting parameters to the expected result, then citing the match as validation.",
            "Unrecorded configuration, so a figure can't be regenerated.",
            "No sensitivity analysis, leaving conclusions' robustness unknown.",
        ],
        'done_when': (
            "The model reproduces known cases, sensitivity to each assumption is characterised, and "
            "someone else can regenerate your figures from your repository."
        ),
    },

    'screening': {
        'label': 'Searching and screening studies',
        'what': (
            "For a review: finding all relevant studies by a documented, repeatable search, then "
            "applying written criteria to decide what's included."
        ),
        'how': [
            "Fix inclusion and exclusion criteria before screening a single record.",
            "Record the full search strategy per database - exact terms, field tags, filters, and "
            "the date run. A systematic review must be re-executable from this alone.",
            "Search multiple databases plus grey literature (theses, reports, trial registries) to "
            "limit publication bias.",
            "Screen in two stages: title/abstract, then full text. Cortex's Systematic Review page "
            "runs both and builds the PRISMA diagram from the decisions.",
            "Record a reason for every full-text exclusion - PRISMA requires reasons at this stage.",
            "Have a second screener cover at least a sample independently and record agreement.",
        ],
        'mistakes': [
            "Adjusting criteria mid-screening to admit a paper you want.",
            "A single-database search described as systematic.",
            "Exclusions logged without reasons, making the review unreproducible.",
        ],
        'done_when': "Every record has a decision and a reason, and the PRISMA counts reconcile.",
    },

    'extract': {
        'label': 'Extracting and synthesising findings',
        'what': "Pulling comparable data from each included study and combining it defensibly.",
        'how': [
            "Use one extraction form with identical fields for every study, piloted on two or three "
            "first.",
            "Extract design, sample size, effect estimate and its variance - not the authors' "
            "conclusion.",
            "Assess risk of bias with a published instrument appropriate to the design rather than "
            "by impression.",
            "Before pooling, check whether the studies are similar enough to pool at all. Quantify "
            "heterogeneity; if it's high, report it and consider whether an overall average is "
            "meaningful.",
            "Weight studies by precision, and test for publication bias (funnel plot asymmetry or "
            "equivalent).",
            "Where studies are too heterogeneous to combine statistically, synthesise narratively "
            "and say why you didn't pool.",
        ],
        'mistakes': [
            "Extracting from abstracts rather than full texts.",
            "Pooling studies that measure different constructs.",
            "Equal weighting regardless of study size or quality.",
            "Reporting a pooled estimate while ignoring high heterogeneity.",
        ],
        'done_when': (
            "Every study has a complete extraction row and a risk-of-bias rating, heterogeneity is "
            "quantified, and the synthesis reflects disagreement as well as agreement."
        ),
    },

    'write': {
        'label': 'Writing it up',
        'what': (
            "Producing a document that answers four questions in order: why you did it "
            "(Introduction), what you did (Methods), what you found (Results), what it means "
            "(Discussion). That is the IMRaD structure, and it's near-universal in the sciences."
        ),
        'how': [
            "Write Methods and Results first. They're factual and require no argument, so they're "
            "the cheapest to start and they fix the content the other two sections must serve.",
            "Introduction moves in one direction: the general problem, what's known, the specific "
            "gap, and how this study addresses it. Hypotheses go at its end.",
            "Methods must support replication: design, participants and how selected, materials, "
            "procedure, variables and how measured, and the analysis plan.",
            "Results report findings without interpreting them. Every number that appears here "
            "should have been produced by a method described above.",
            "Discussion interprets, and every point should trace back to a result already reported. "
            "No new findings appear here.",
            "Cite while drafting rather than afterwards. In Cortex, type @ in any manuscript section "
            "to insert a citation; the reference list is built from those markers.",
            "Check the reporting checklist for your design before submitting - CONSORT for "
            "randomised trials, PRISMA for systematic reviews, STROBE for observational studies, "
            "ARRIVE for animal research.",
        ],
        'mistakes': [
            "Interpretation in Results, or new results in Discussion - the most common structural "
            "correction reviewers make.",
            "Methods too thin to replicate.",
            "Abstract claiming more than the results support.",
            "Close paraphrase of a source: if the sentence structure is theirs, it needs quotation "
            "marks as well as a citation.",
        ],
        'done_when': (
            "A reader in your field could reproduce the study from the Methods and disagree with "
            "your Discussion using only the evidence in your Results."
        ),
    },

    'submit': {
        'label': 'Submitting and tracking',
        'what': "Getting the work reviewed, and handling the response.",
        'how': [
            "Match the venue to the work's scope and stage. Undergraduate and high-school research "
            "journals exist and are a legitimate first target.",
            "Read the author guidelines before formatting. Non-compliant submissions are commonly "
            "desk-rejected without review.",
            "Submit to one venue at a time - simultaneous submission is considered misconduct.",
            "Verify unfamiliar journals before paying anything: check indexing, editorial board, "
            "and the Think.Check.Submit criteria. Unsolicited invitations and same-week publication "
            "promises are the standard warning signs.",
            "Respond to reviews point by point: what you changed, or why you disagree, with reasons.",
            "Track venue, submission date, and status. That's what Cortex's Journals page holds.",
        ],
        'mistakes': [
            "Ignoring formatting requirements.",
            "Paying an article processing charge to an unverified journal.",
            "Reading rejection as a verdict rather than as routine.",
        ],
        'done_when': "Submitted, with venue, date and status recorded.",
    },

    'framework': {
        'label': 'Building a theoretical framework',
        'what': (
            "Setting out the concepts, their definitions, and the proposed relations between them - "
            "the structure the rest of the argument depends on."
        ),
        'how': [
            "Define every construct explicitly, especially terms that carry a loose everyday "
            "meaning.",
            "Draw the relations. A diagram exposes gaps and circularity that prose conceals.",
            "Separate assumptions you can test from those you're taking as given, and label them.",
            "Check for internal contradiction: two premises that conflict make everything "
            "downstream unsound.",
            "State what your framework predicts that existing ones don't - that's the contribution.",
        ],
        'mistakes': [
            "A term that shifts meaning between sections.",
            "A framework compatible with every possible observation, and therefore predicting none.",
            "Ignoring an established competing framework rather than arguing against it.",
        ],
        'done_when': (
            "Constructs are defined, relations are explicit, and the framework yields at least one "
            "checkable claim."
        ),
    },

    'case': {
        'label': 'Case study work',
        'what': (
            "Studying a single instance in depth to understand mechanism and context, rather than "
            "to estimate a population parameter."
        ),
        'how': [
            "Justify the case selection: typical, extreme, critical, or revelatory - each supports "
            "a different kind of claim.",
            "Define the case boundaries explicitly - what is inside the unit of analysis and what "
            "is context.",
            "Triangulate: use documents, interviews and observation so that key claims rest on more "
            "than one source type.",
            "Maintain a chain of evidence a reader can follow from raw source to conclusion.",
            "Compare against published accounts of similar cases to establish what generalises "
            "analytically.",
        ],
        'mistakes': [
            "Statistical generalisation from a single case.",
            "A central claim resting on one source.",
            "Selecting evidence that fits the expected narrative.",
        ],
        'done_when': (
            "Key claims are corroborated across source types, and you've stated what the case does "
            "and doesn't support beyond itself."
        ),
    },

    'general': {
        'label': 'General guidance',
        'what': "A step in your project's standard methodology.",
        'how': [
            "Record what you did and why, at the time you do it.",
            "Follow your discipline's established conventions rather than importing them from "
            "another field.",
            "Have someone experienced check the approach before you commit significant time.",
            "Keep records detailed enough to reconstruct this step in six months.",
        ],
        'mistakes': [
            "Reconstructing documentation from memory afterwards.",
            "Assuming a convention transfers across fields.",
        ],
        'done_when': "The step is complete and documented well enough to write up from.",
    },
}


# First match wins, so order encodes precedence. Tuned against the real step
# list (see the classification test); several steps sit on a boundary and
# land wrong under the obvious ordering:
#
#   "Do literature review on that theory"   must beat 'framework' on "theory"
#   "...(typology, case counts)"            must not match 'case' on "case counts"
#   "Identify broad research question or system to model"
#                                            must beat 'model' on "model"
#   "Identify limitations and gaps"          must beat 'question' on "gap"
_CLASSIFIERS: List[tuple] = [
    ('ethics',    r'ethics|irb|consent|approval|safety'),
    # Early: a literature-review step is one whatever its topic.
    ('literature', r'literature review|prior work'),
    ('screening', r'screen|inclusion and exclusion|search databases|systematically search|exclude weak'),
    ('extract',   r'extract|synthesi|pool|effect sizes|heterogeneity|risk of bias|quality'),
    # 'case' only where it names the unit of study - not "case counts".
    ('case',      r'choose \d+ case|that case|the case\b|similar cases|conduct interviews|gather documents'),
    # Specific modelling verbs, so "system to model" isn't swallowed here.
    ('model',     r'construct the model|implement the model|validate the model|model output|simulat|algorithm|\bcode\b'),
    ('framework', r'framework|concept map|logical consistency|premises|theory'),
    ('interpret', r'interpret|readiness|compare analysis|identify limitations'),
    ('question',  r'research question|research problem|identify.*gap|phenomenon|variables of interest|identify a basic-science finding'),
    ('hypothesis', r'hypothes'),
    ('design',    r'design|protocol|standardi|comparison groups|match or statistically control|define what will be measured|develop an application|prototype'),
    ('collect',   r'collect|conduct experiment|measure|observe|preclinical|bench-scale|testing|give and track|run simulations'),
    ('sampling',  r'recruit|participants|sample|cohort'),
    ('analyze',   r'analy[sz]e|statistical test|summari[sz]e|characteri[sz]e|descriptive statistics'),
    ('write',     r'draft|write|report'),
    ('submit',    r'journal|submission|rejection|acceptance'),
]


def classify_step(step_text: str) -> str:
    """Map a methodology step string to the kind of activity it describes."""
    text = (step_text or '').lower()
    for kind, pattern in _CLASSIFIERS:
        if re.search(pattern, text):
            return kind
    return 'general'


def guidance_for_step(step_text: str) -> Dict:
    kind = classify_step(step_text)
    guidance = STEP_KINDS.get(kind, STEP_KINDS['general'])
    return {'kind': kind, **guidance}


# ---------------------------------------------------------------------------
# Glossary
# ---------------------------------------------------------------------------

GLOSSARY: List[Dict] = [
    # Design
    {'term': 'Independent variable', 'category': 'Design',
     'definition': "What you deliberately vary or compare. In a caffeine study, the dose."},
    {'term': 'Dependent variable', 'category': 'Design',
     'definition': "What you measure to see whether it responded. In the same study, reaction time."},
    {'term': 'Control group', 'category': 'Design',
     'definition': "A group that doesn't receive the treatment, giving you a baseline to compare against. Without one, a change has nothing to be a change from."},
    {'term': 'Confound', 'category': 'Design',
     'definition': "A variable that changes alongside your independent variable and could produce the result instead. If the caffeine group also slept more, sleep is a confound."},
    {'term': 'Internal validity', 'category': 'Design',
     'definition': "Whether the effect you measured actually came from your independent variable rather than something else. Threatened by history, maturation, instrumentation, regression to the mean, selection, and attrition."},
    {'term': 'External validity', 'category': 'Design',
     'definition': "How far the finding generalises beyond your sample, setting and materials. Often trades off against internal validity: tighter control makes the result cleaner but less like the real world."},
    {'term': 'Construct validity', 'category': 'Design',
     'definition': "Whether your measure captures the concept you claim it does - whether a questionnaire labelled 'stress' measures stress."},
    {'term': 'Regression to the mean', 'category': 'Design',
     'definition': "Extreme scores tend to be less extreme on remeasurement, by chance alone. Select participants for being extreme and they will appear to improve without any treatment."},
    {'term': 'Attrition', 'category': 'Design',
     'definition': "Participants dropping out. A threat when dropout differs between groups, because the groups you end up comparing are no longer the ones you assigned."},
    {'term': 'Randomisation', 'category': 'Design',
     'definition': "Assigning participants to conditions by a genuine random process, so groups don't differ systematically at baseline - including on confounders you never thought of."},
    {'term': 'Blinding', 'category': 'Design',
     'definition': "Withholding condition assignment from participants (single-blind) or from participants and researchers (double-blind), so expectation can't shape results or scoring."},
    {'term': 'Placebo', 'category': 'Design',
     'definition': "An inert substitute for the control group, so the only systematic difference between groups is the active component."},
    {'term': 'Operationalisation', 'category': 'Design',
     'definition': "Turning an abstract construct into a specific measurement procedure. 'Anxiety' becomes 'score on this validated scale, administered before the task'."},
    {'term': 'Protocol', 'category': 'Design',
     'definition': "The written plan for how the study runs, fixed before data collection and detailed enough to follow without asking the author."},
    {'term': 'Reliability', 'category': 'Design',
     'definition': "Whether a measure gives consistent results on repetition. A reliable measure can still be wrong: a scale reading 3kg heavy every time is perfectly reliable."},
    {'term': 'Pilot study', 'category': 'Design',
     'definition': "A small trial run used to find procedural problems before committing to full data collection."},
    {'term': 'Replication', 'category': 'Design',
     'definition': "Repeating a study to test whether the finding holds. Direct replication repeats the method; conceptual replication tests the same claim differently."},
    {'term': 'Qualitative vs quantitative', 'category': 'Design',
     'definition': "Quantitative measures numerically and analyses statistically. Qualitative works with text, interviews and observation to understand meaning and mechanism. Mixed-methods designs use both deliberately."},
    {'term': 'Survey', 'category': 'Design',
     'definition': "Self-reported data collected via questionnaire. Scales cheaply; results are sensitive to question wording, order, and what people are willing to report."},
    {'term': 'Interview', 'category': 'Design',
     'definition': "Structured, semi-structured, or unstructured conversation used to collect qualitative data. Normally requires ethics approval and recorded consent."},
    {'term': 'Theory', 'category': 'Design',
     'definition': "In science, an explanation supported by a substantial body of evidence - not a guess. The everyday sense of 'theory' corresponds to 'hypothesis'."},
    {'term': 'Model', 'category': 'Design',
     'definition': "A simplified representation of a system used to predict or explain. Every model omits something; the question is whether it omits anything that matters for your question."},

    # Question frameworks
    {'term': 'FINER criteria', 'category': 'Design',
     'definition': "A checklist for appraising a research question: Feasible, Interesting, Novel, Ethical, Relevant. Most first questions fail on Feasible."},
    {'term': 'PICO', 'category': 'Design',
     'definition': "Population, Intervention, Comparison, Outcome - a template for structuring quantitative and clinical questions. Assumes an intervention and a comparison, so it fits exploratory or qualitative work poorly."},
    {'term': 'SPIDER', 'category': 'Design',
     'definition': "Sample, Phenomenon of Interest, Design, Evaluation, Research type - a question framework for qualitative and mixed-methods work, where PICO's intervention/comparison structure doesn't apply."},
    {'term': 'SPICE / PCC', 'category': 'Design',
     'definition': "Alternative question frameworks. SPICE (Setting, Perspective, Intervention, Comparison, Evaluation) suits evaluating a service or programme; PCC (Population, Concept, Context) suits broad scoping reviews."},

    # Sampling
    {'term': 'Probability sampling', 'category': 'Design',
     'definition': "Sampling where every population member has a known, non-zero chance of selection - simple random, systematic, stratified, cluster. The only basis for statistically generalising to the population."},
    {'term': 'Non-probability sampling', 'category': 'Design',
     'definition': "Sampling by accessibility or judgement - convenience, purposive, snowball, quota. Practical and legitimate, especially for exploratory work, but doesn't support population-level generalisation."},
    {'term': 'Stratified sampling', 'category': 'Design',
     'definition': "Dividing the population into subgroups and sampling within each, so small but important subgroups end up with enough cases to analyse."},
    {'term': 'Convenience sample', 'category': 'Design',
     'definition': "Whoever is easiest to reach. Fast and cheap; the population it represents is 'people reachable the way you recruited', which is usually narrower than intended."},
    {'term': 'Selection bias', 'category': 'Design',
     'definition': "Systematic difference between who ends up in your sample and who doesn't, in a way related to the outcome. Volunteer bias is the common case."},
    {'term': 'Sample size (n)', 'category': 'Design',
     'definition': "The number of participants or observations. Set it in advance from the smallest effect worth detecting; sample sizes chosen by convenience and reported as planned are a form of misreporting."},

    # Statistics
    {'term': 'p-value', 'category': 'Statistics',
     'definition': "The probability of data at least this extreme if there were genuinely no effect. Not the probability the hypothesis is true, and not the probability the result was a fluke."},
    {'term': 'Statistical significance', 'category': 'Statistics',
     'definition': "A convention (usually p < 0.05) for calling a result unlikely under the null hypothesis. Says nothing about the size or importance of the effect."},
    {'term': 'Effect size', 'category': 'Statistics',
     'definition': "The magnitude of the difference or relationship - Cohen's d, correlation r, odds ratio. Report alongside p: significance says probably not zero, effect size says whether it matters."},
    {'term': 'Confidence interval', 'category': 'Statistics',
     'definition': "A range of values compatible with your data. Width shows precision; a wide interval around a significant result means you've established direction but not magnitude."},
    {'term': 'Null hypothesis', 'category': 'Statistics',
     'definition': "The assumption of no effect or no association. Standard tests measure evidence against it; they never prove it true."},
    {'term': 'Type I / Type II error', 'category': 'Statistics',
     'definition': "Type I is a false positive - detecting an effect that isn't there. Type II is a false negative - missing one that is. Lowering one raises the other at fixed sample size."},
    {'term': 'Statistical power', 'category': 'Statistics',
     'definition': "The probability of detecting an effect that genuinely exists. Underpowered studies produce null results that mean nothing, and inflated effect sizes when they do hit."},
    {'term': 'Correlation', 'category': 'Statistics',
     'definition': "Two variables changing together, measured from -1 to +1. Correlation does not imply causation."},
    {'term': 'Causation', 'category': 'Statistics',
     'definition': "One variable actually producing a change in another. Supported by randomised experimental designs; observational data can establish association but not, on its own, causal direction."},
    {'term': 'Mean, median, mode', 'category': 'Statistics',
     'definition': "Averages. The mean is pulled by outliers; the median is the middle value and resists them; the mode is the most frequent. Skewed data is better summarised by the median."},
    {'term': 'Standard deviation', 'category': 'Statistics',
     'definition': "Typical distance of values from the mean. A mean reported without a measure of spread is close to uninterpretable."},
    {'term': 't-test', 'category': 'Statistics',
     'definition': "Compares the means of two groups. Independent-samples for two separate groups; paired for the same participants measured twice."},
    {'term': 'ANOVA', 'category': 'Statistics',
     'definition': "Compares means across three or more groups. A significant result indicates at least one group differs, not which - that needs a post-hoc test."},
    {'term': 'Regression', 'category': 'Statistics',
     'definition': "Models how an outcome varies with one or more predictors, giving both prediction and each predictor's estimated contribution."},
    {'term': 'Parametric vs non-parametric', 'category': 'Statistics',
     'definition': "Parametric tests (t-test, ANOVA) assume a distribution, usually normal. Non-parametric equivalents (Mann-Whitney, Kruskal-Wallis) don't, and are the fallback when assumptions fail."},
    {'term': 'Heterogeneity', 'category': 'Statistics',
     'definition': "In meta-analysis, the degree to which included studies disagree beyond chance. High heterogeneity means a pooled average may be summarising incompatible things."},
    {'term': 'p-hacking', 'category': 'Statistics',
     'definition': "Trying tests, subgroups or exclusions until a result clears significance. Generates false positives; pre-registration is the standard defence."},
    {'term': 'HARKing', 'category': 'Statistics',
     'definition': "Hypothesising After Results are Known - presenting a post-hoc hypothesis as though predicted. Invalidates the statistics reported against it."},
    {'term': 'Multiple comparisons', 'category': 'Statistics',
     'definition': "Running many tests inflates the chance of a false positive. Correct for it (Bonferroni and similar) or state that you didn't."},
    {'term': 'Outlier', 'category': 'Statistics',
     'definition': "A value far from the rest. Investigate the cause; exclude only by a rule fixed in advance, and report that you did."},
    {'term': 'Normal distribution', 'category': 'Statistics',
     'definition': "The bell curve. Several common tests assume data approximates it - check rather than assume."},

    # Publishing
    {'term': 'IMRaD', 'category': 'Publishing',
     'definition': "Introduction, Methods, Results, Discussion - the standard scientific paper structure, answering why, what you did, what you found, and what it means, in that order."},
    {'term': 'Peer review', 'category': 'Publishing',
     'definition': "Evaluation by other researchers before publication. Imperfect and slow, but the main pre-publication quality filter."},
    {'term': 'Preprint', 'category': 'Publishing',
     'definition': "A manuscript posted publicly before peer review (arXiv, bioRxiv, medRxiv). Free to read and often the way around a paywall; not yet vetted."},
    {'term': 'DOI', 'category': 'Publishing',
     'definition': "Digital Object Identifier - a permanent identifier for a document, unlike a URL, which decays."},
    {'term': 'Impact factor', 'category': 'Publishing',
     'definition': "Mean citations per paper for a journal over a window. Widely used as a proxy for quality and widely criticised for it - it says little about any individual paper."},
    {'term': 'Open access', 'category': 'Publishing',
     'definition': "Freely readable on publication. Often funded by an article processing charge paid by the author or their institution."},
    {'term': 'Predatory journal', 'category': 'Publishing',
     'definition': "Charges publication fees while providing little or no real peer review. Warning signs: unsolicited invitations, promises of publication within days, unverifiable editorial board."},
    {'term': 'Literature review', 'category': 'Publishing',
     'definition': "A survey of existing work. As a section, it motivates your study; as a standalone paper, it synthesises a field. A systematic review is the reproducible version."},
    {'term': 'Systematic review', 'category': 'Publishing',
     'definition': "A review using a pre-specified, documented, repeatable search and selection method - as distinct from a narrative review of whatever the author happened to read."},
    {'term': 'Meta-analysis', 'category': 'Publishing',
     'definition': "Statistically pooling effect estimates across studies to produce an overall estimate, weighted by precision."},
    {'term': 'PRISMA', 'category': 'Publishing',
     'definition': "The reporting standard for systematic reviews, including the flow diagram accounting for every record from identification through inclusion."},
    {'term': 'CONSORT / STROBE / ARRIVE', 'category': 'Publishing',
     'definition': "Reporting checklists by design: CONSORT for randomised trials, STROBE for observational studies, ARRIVE for animal research. The EQUATOR Network indexes them all."},
    {'term': 'Grey literature', 'category': 'Publishing',
     'definition': "Work outside commercial publishing - theses, reports, registry entries, conference abstracts. Searching it reduces publication bias."},
    {'term': 'Publication bias', 'category': 'Publishing',
     'definition': "Positive findings are published more readily than null ones, so the visible literature overstates effects. A central problem for meta-analysis."},

    # Ethics
    {'term': 'IRB / ethics committee', 'category': 'Ethics',
     'definition': "The body that reviews research involving human participants. Approval must precede data collection; it cannot be granted retroactively."},
    {'term': 'Informed consent', 'category': 'Ethics',
     'definition': "Agreement to participate given after being told the purpose, procedures, risks, data handling, and the right to withdraw without penalty."},
    {'term': 'Assent', 'category': 'Ethics',
     'definition': "A minor's own agreement to take part, required in addition to guardian consent."},
    {'term': 'Anonymised vs de-identified', 'category': 'Ethics',
     'definition': "De-identified data has direct identifiers removed but could in principle be re-linked. Anonymised data cannot be traced back at all. The distinction matters legally."},
    {'term': 'Plagiarism', 'category': 'Ethics',
     'definition': "Presenting another's words or ideas as your own. Includes close paraphrase without citation, and reusing your own previously submitted text without disclosure."},
    {'term': 'Authorship', 'category': 'Ethics',
     'definition': "Credit for substantial intellectual contribution. Criteria and ordering conventions differ sharply by field - agree them in writing early."},
    {'term': 'Conflict of interest', 'category': 'Ethics',
     'definition': "Any interest that could bias the work or appear to - funding, employment, personal stake. Disclose rather than self-assess whether it mattered."},
    {'term': 'Pre-registration', 'category': 'Ethics',
     'definition': "Publicly recording hypotheses and analysis plan before data collection (OSF, AsPredicted), which distinguishes confirmatory from exploratory results."},
    {'term': 'Reproducibility', 'category': 'Ethics',
     'definition': "Obtaining the same results from the same data and code. Distinct from replicability, which is obtaining consistent results from new data."},
    {'term': 'Data management plan', 'category': 'Ethics',
     'definition': "A written plan for how data is named, stored, backed up, documented and retained. Increasingly required by funders, and useful regardless."},
]


# ---------------------------------------------------------------------------
# Primer
# ---------------------------------------------------------------------------

BASICS: List[Dict] = [
    {
        'id': 'process',
        'title': 'The research process, end to end',
        'body': [
            "Research answers a question in a way that lets someone else check the reasoning. The "
            "checkability is what distinguishes it from an informed opinion.",
            "The sequence is broadly fixed: pick a question, find out what's known, state what you "
            "expect and why, design a study that could contradict you, get ethical approval if "
            "people or animals are involved, collect data, analyse it as planned, interpret within "
            "the limits of the design, and report it - including what didn't work.",
            "Two things move: the question narrows after the literature review, and the design "
            "changes after the pilot. Both are the process working, not failing.",
            "Your Methodology page holds the specific step sequence for your research type, and "
            "each step there explains how to do it.",
        ],
    },
    {
        'id': 'question',
        'title': 'Getting the question right',
        'body': [
            "Scope failure is the main reason first projects don't finish. The fix is mechanical: "
            "run the question through a framework until every slot is filled.",
            "For quantitative work use PICO - Population, Intervention, Comparison, Outcome. For "
            "qualitative or mixed methods use SPIDER - Sample, Phenomenon of Interest, Design, "
            "Evaluation, Research type. For evaluating a programme use SPICE; for a broad scoping "
            "question use PCC. If a slot is empty, the question isn't specified yet.",
            "Then check it against FINER: Feasible, Interesting, Novel, Ethical, Relevant. "
            "Feasible is the one that eliminates most first attempts - it means feasible with the "
            "time, access, equipment and permissions you actually have.",
            "A finished question states who, what varies, what is measured and in what units, and "
            "what it is compared against.",
        ],
    },
    {
        'id': 'reading',
        'title': 'Reading papers',
        'body': [
            "Papers are not read front to back. Use three passes and stop as soon as the paper "
            "stops being relevant.",
            "Pass 1, five to ten minutes: title, abstract, section headings, figures, conclusion. "
            "The output is a decision about whether to keep reading.",
            "Pass 2, up to an hour: figures, tables and captions read properly, plus the argument. "
            "You should be able to summarise the claim and the evidence, and flag references worth "
            "chasing. This is enough for most papers you cite.",
            "Pass 3, several hours, only for work you'll build on directly: follow the methods in "
            "enough detail to identify the assumptions and what you would challenge.",
            "Assess five things as you go: what kind of paper it is, what it responds to, whether "
            "the claims hold, what it actually adds, and how clearly it's written.",
            "Not understanding a paper on first read is normal. Read a review article on the topic "
            "first and return to it.",
        ],
    },
    {
        'id': 'validity',
        'title': 'Making the result mean something',
        'body': [
            "Design determines what you're allowed to conclude. Randomised assignment supports a "
            "causal claim; observational data supports association only. No amount of analysis "
            "upgrades one to the other.",
            "Internal validity is whether the effect came from your variable. The recognised "
            "threats have names, and checking them one by one is the practical method: history, "
            "maturation, instrumentation, regression to the mean, selection, and attrition.",
            "External validity is how far the result travels beyond your sample and setting. It "
            "usually trades against internal validity - the more tightly you control conditions, "
            "the less the situation resembles the world.",
            "Sampling determines who your conclusions cover. Probability sampling (random, "
            "stratified, cluster) supports generalisation to a population. Non-probability sampling "
            "(convenience, purposive, snowball) doesn't - it's still legitimate, but the "
            "conclusions are about people reachable the way you recruited.",
            "Decide the analysis before seeing the data. Choosing afterwards - trying tests, "
            "subgroups or exclusions until something is significant - manufactures false positives "
            "and is detectable.",
        ],
    },
    {
        'id': 'data',
        'title': 'Not losing your data',
        'body': [
            "Keep the raw dataset read-only and never edit it. Clean into a separate file so every "
            "transformation can be re-run or undone.",
            "Name files with project, content, date as YYYYMMDD, and a version number. Avoid spaces "
            "and avoid 'final' - it never is. Version as v01, v02, and record what changed.",
            "Keep a data dictionary: every column, its units, its permitted values, and the code "
            "used for missing data.",
            "Log deviations from protocol as they happen, with dates.",
            "Two copies, two locations, same day. Data loss is the most common preventable failure "
            "in student research.",
        ],
    },
    {
        'id': 'writing',
        'title': 'Writing it up',
        'body': [
            "The standard structure is IMRaD, which answers four questions in order: why did you do "
            "this (Introduction), what did you do (Methods), what did you find (Results), what does "
            "it mean (Discussion).",
            "Write Methods and Results first. They're factual, they need no argument, and they "
            "constrain what the other two sections can say.",
            "The Introduction narrows: general problem, what's known, the specific gap, what this "
            "study does about it. Hypotheses close it.",
            "Results report; Discussion interprets. No interpretation in Results, no new findings "
            "in Discussion - this is the most common structural correction reviewers make.",
            "Methods must support replication. If you're unsure whether a detail belongs, include "
            "it.",
            "Find your design's reporting checklist on the EQUATOR Network and follow it: CONSORT "
            "for randomised trials, PRISMA for systematic reviews, STROBE for observational "
            "studies, ARRIVE for animal work.",
        ],
    },
    {
        'id': 'ethics',
        'title': 'Approval, integrity and credit',
        'body': [
            "Research involving people, animals or identifiable data needs approval before it "
            "starts, from an IRB, ethics committee, or your institution's equivalent. Approval is "
            "not retroactive, and data collected without it usually cannot be used.",
            "Turnaround is weeks to months. Treat it as a scheduling constraint, not a formality at "
            "the end.",
            "Science fairs impose their own rules on top of institutional ones. ISEF and affiliated "
            "fairs require documented pre-approval for many project categories and disqualify work "
            "that skipped it - read the current rules for your specific fair.",
            "Cite anything that isn't your own idea, including rephrased ideas. If the sentence "
            "structure is the source's, it needs quotation marks as well as a citation.",
            "Agree authorship and ordering in writing before there's a manuscript. Conventions "
            "differ sharply between fields; ask what yours does.",
            "Check your institution's and target venue's policy on AI tool use, and disclose where "
            "required. These policies are changing quickly.",
        ],
    },
    {
        'id': 'help',
        'title': 'Getting help',
        'body': [
            "Mentorship matters most at two points: study design, and interpretation. Those are "
            "where errors are expensive and hardest to see from inside the project.",
            "Cold emails to researchers work more often than people expect, particularly from "
            "students. Keep it short, name the specific paper of theirs you read, and ask one "
            "concrete question.",
            "When asking for help, show what you already tried. It converts an hour-long question "
            "into a two-minute one.",
        ],
    },
    {
        'id': 'limits',
        'title': 'Limits of this guide',
        'body': [
            "This covers general methodology - what transfers across disciplines. It's enough to "
            "orient you and to ask better questions of someone who knows your field.",
            "It does not cover binding requirements, which vary by field, institution and country: "
            "ethics review, lab safety, clinical trial registration, data protection law, and "
            "discipline-specific reporting standards.",
            "Where a real standard exists, use it directly rather than this summary - the EQUATOR "
            "Network for reporting guidelines, the Cochrane Handbook for systematic reviews, PRISMA "
            "for review reporting, and your institution's own ethics guidance.",
            "Where this guide and your advisor, teacher, or ethics board disagree, they are right.",
        ],
    },
]


def get_basics() -> List[Dict]:
    return BASICS


def _search_key(text: str) -> str:
    """
    Normalise for matching: lowercase, and strip hyphens/spaces/slashes.

    Users don't reproduce our punctuation - someone looking up
    'preregistration', 'p value', 'meta analysis' or 't test' should find the
    entries filed as 'Pre-registration', 'p-value', 'Meta-analysis' and
    't-test'.
    """
    return re.sub(r'[\s\-/]+', '', (text or '').lower())


def get_glossary(query: str = '') -> List[Dict]:
    q = (query or '').strip().lower()
    if not q:
        return GLOSSARY

    q_key = _search_key(q)
    results = []
    for item in GLOSSARY:
        haystack = f"{item['term']} {item['definition']} {item['category']}"
        if q in haystack.lower() or q_key in _search_key(haystack):
            results.append(item)
    return results


def glossary_categories() -> List[str]:
    seen: List[str] = []
    for item in GLOSSARY:
        if item['category'] not in seen:
            seen.append(item['category'])
    return seen
