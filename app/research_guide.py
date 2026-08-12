"""
Beginner-facing research guidance for Cortex.

Cortex's methodology checklist tells you *what* the steps are. This module
tells you *how* to actually do each one, in language aimed at a high-school
or undergraduate researcher who has never run a study before - while
staying out of the way of someone who already knows.

Three pieces:

  1. STEP_KINDS - substantive guidance per kind of step (what it means, how
     to do it, what goes wrong, how you know you're finished). Steps are
     classified into kinds rather than written out one-by-one: the 12
     research types share 69 distinct step strings but only ~16 genuinely
     different *activities*, so "Collect data from each group" and
     "Systematically observe, measure, or collect samples" get the same
     well-developed guidance instead of two thin copies.

  2. GLOSSARY - the jargon a beginner hits in the first month, defined
     plainly.

  3. BASICS - a short primer on doing research at all: choosing a question,
     ethics, reading papers, not fooling yourself with statistics, and
     authorship.

A NOTE ON SCOPE, which the UI repeats to the user: this is general research
methodology, the parts that hold across disciplines. Specific fields have
their own conventions, requirements, and regulatory obligations that
override anything here - a wet-lab protocol, an IRB submission, and a
clinical trial registration all have rules this can't encode. Everything
below points at the authoritative source where one exists, and the UI tells
beginners to confirm with a teacher, advisor, or ethics board rather than
treating Cortex as the last word.
"""

import re
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Step guidance
# ---------------------------------------------------------------------------

STEP_KINDS: Dict[str, Dict] = {
    'question': {
        'label': 'Framing the research question',
        'what': (
            "You're turning a topic you're curious about into a question narrow enough to "
            "actually answer. 'Does caffeine affect the brain?' is a topic. 'Does 200mg of "
            "caffeine reduce simple visual reaction time in healthy adults aged 18-25?' is a "
            "research question."
        ),
        'how': [
            "Write your interest as a plain sentence, then keep asking 'in whom?', 'measured how?', "
            "and 'compared to what?' until each has an answer.",
            "Name the thing you'd change or observe, and the thing you'd measure. If you can't name "
            "both, the question isn't ready.",
            "Sanity-check feasibility against what you actually have: time, participants, equipment, "
            "money, and permission. A question you can't run is not a question yet.",
            "Say out loud what result would surprise you. If no possible result would, the question "
            "may not be worth asking.",
        ],
        'mistakes': [
            "Too broad to answer in the time you have - the single most common beginner mistake.",
            "A question whose answer is already firmly established (check this in the literature "
            "review before committing).",
            "A question you can't measure: 'is X better?' needs a definition of 'better' before it "
            "means anything.",
            "Picking a question because the data is easy to get rather than because the answer matters.",
        ],
        'done_when': (
            "You can state the question in one sentence, and a friend outside your field can tell you "
            "what you'd have to measure to answer it."
        ),
        'beginner_note': (
            "It is completely normal for this to take weeks and to change after your literature "
            "review. Narrowing a question is progress, not backtracking."
        ),
    },

    'literature': {
        'label': 'Reviewing the literature',
        'what': (
            "Finding out what's already known, so you don't spend months answering a question someone "
            "settled in 2011 - and so you can position what you're doing against real prior work."
        ),
        'how': [
            "Search several databases, not just one. Cortex's Literature Review searches Europe PMC, "
            "CrossRef, arXiv, OpenAlex, Semantic Scholar and CORE together.",
            "Read strategically: title, then abstract, then figures and their captions, then the "
            "discussion. Read the full methods only for the papers that actually matter to you.",
            "Follow citations in both directions - the references of a key paper (backwards) and the "
            "papers that cite it (forwards). This finds more than keyword search alone.",
            "Take notes as you go, in your own words, with the citation attached. Cortex's annotations "
            "field on each paper is for exactly this.",
            "Look hardest for work that disagrees with your expectation. That's the work that will "
            "change your design.",
        ],
        'mistakes': [
            "Reading only what supports your idea.",
            "Collecting 80 papers and reading none of them properly. Ten papers understood beats a "
            "hundred skimmed.",
            "Copying phrasing into your notes without marking it as a quote - this is how accidental "
            "plagiarism happens months later.",
            "Trusting a paper because it agrees with you rather than because its methods are sound.",
        ],
        'done_when': (
            "You can name the handful of papers your work responds to, say what each found, and state "
            "what nobody has answered yet."
        ),
        'beginner_note': (
            "Paywalls are not a dead end. Try the preprint (arXiv, bioRxiv, medRxiv), the author's own "
            "site, your school or library login, or email the author - authors are usually glad to send "
            "a copy."
        ),
    },

    'hypothesis': {
        'label': 'Constructing a hypothesis',
        'what': (
            "A hypothesis is a specific, testable statement about what you expect and why - not a "
            "restatement of your question. It has to be capable of being wrong."
        ),
        'how': [
            "Write it as a prediction with a direction: 'Group A will have lower X than Group B', not "
            "'there will be a difference'.",
            "State the reasoning behind it in one sentence. A hypothesis without a rationale is a guess.",
            "Write down, before collecting any data, what result would count as supporting it and what "
            "result would count as contradicting it.",
            "Keep the null hypothesis in mind: the assumption that there is no effect. Your statistics "
            "will be testing against that.",
        ],
        'mistakes': [
            "Writing something unfalsifiable - if no possible data could contradict it, it isn't a "
            "hypothesis.",
            "Deciding what counts as success after seeing the data (this is called HARKing, and it "
            "invalidates your statistics).",
            "Confusing hypothesis with prediction: the hypothesis is the proposed explanation, the "
            "prediction is what you'd observe if it were true.",
        ],
        'done_when': (
            "Someone could read your hypothesis and design a study to prove you wrong."
        ),
        'beginner_note': (
            "Not all research needs a hypothesis. Exploratory and descriptive work legitimately asks "
            "'what's going on here?' instead. What matters is being honest about which you're doing - "
            "exploratory work presented as if it were confirmatory is a real problem in the literature."
        ),
    },

    'design': {
        'label': 'Designing the study',
        'what': (
            "Deciding exactly what you will do, to whom, in what order, and what you'll measure - "
            "before you start. The design is what makes your answer trustworthy."
        ),
        'how': [
            "Write the protocol as if handing it to a stranger who must reproduce your study without "
            "asking you questions.",
            "Identify your variables explicitly: what you change (independent), what you measure "
            "(dependent), and what you hold constant (controls).",
            "Plan the comparison. An effect with nothing to compare it against isn't evidence.",
            "Decide your sample size before starting, and how you'll handle dropouts, outliers, and "
            "missing data. Deciding afterwards invites bias.",
            "Where blinding or randomisation is possible, use them - they're the cheapest defences "
            "against fooling yourself.",
            "Run a small pilot first. Nearly every design has a flaw that only shows up when you try it.",
        ],
        'mistakes': [
            "No control or comparison condition.",
            "Changing several things at once, so you can't tell which one mattered.",
            "A confound: something that varies alongside your variable of interest and could explain "
            "the result instead.",
            "Deciding how to analyse the data only after seeing it.",
        ],
        'done_when': (
            "Another person could run your study from your written protocol and get comparable data."
        ),
        'beginner_note': (
            "Design conventions vary a lot by field, and this is where a mentor is most valuable. "
            "Before you commit, show your protocol to someone who has run a study in your specific "
            "discipline."
        ),
    },

    'ethics': {
        'label': 'Ethics approval and research integrity',
        'what': (
            "Formal permission to run your study, from the body responsible for protecting the people "
            "or animals involved. In the US this is an IRB (Institutional Review Board) or IACUC for "
            "animals; other countries have equivalents."
        ),
        'how': [
            "Find out early who reviews research at your school or institution - this is often weeks "
            "of lead time, not days.",
            "Prepare informed consent materials: what participants will do, what the risks are, that "
            "they can stop at any time, and how their data will be stored.",
            "For anyone under 18, expect to need parental/guardian consent plus the participant's own "
            "assent.",
            "Say how you'll protect privacy: what identifying data you collect, where it's stored, who "
            "can see it, and when it's destroyed.",
            "If you're a high-school student entering a science fair, check its rules - ISEF and many "
            "regional fairs require approval *before* experimentation begins, and will disqualify work "
            "that skipped it.",
        ],
        'mistakes': [
            "Starting data collection before approval. This is not fixable retroactively - the data "
            "usually cannot be used.",
            "Assuming a survey is exempt. Surveys involving people generally still need review.",
            "Collecting more personal information than the question requires.",
        ],
        'done_when': (
            "You have written approval (or a documented exemption determination) in hand, and your "
            "consent forms are ready."
        ),
        'beginner_note': (
            "This is the one step where Cortex's general guidance is definitely not enough. Ethics "
            "requirements are set by your institution and jurisdiction and they are binding. Ask your "
            "teacher, advisor, or the review board directly."
        ),
    },

    'sampling': {
        'label': 'Recruiting participants or selecting a sample',
        'what': (
            "Choosing who or what you'll study. Your sample determines who your conclusions can "
            "legitimately apply to."
        ),
        'how': [
            "Write your inclusion and exclusion criteria down before recruiting, and apply them "
            "consistently.",
            "Aim for a sample that resembles the population you want to draw conclusions about.",
            "Record how many you approached, how many agreed, and how many completed - you'll need "
            "these numbers when you write it up.",
            "Decide in advance how participants are assigned to groups, and use a real randomisation "
            "method rather than alternating or choosing.",
        ],
        'mistakes': [
            "A convenience sample presented as if it were representative - 30 of your classmates is a "
            "fine sample, but your conclusions are about people like your classmates.",
            "Too small a sample to detect the effect you're looking for.",
            "Self-selection bias: the people who volunteer often differ systematically from those who "
            "don't.",
            "Dropping participants after seeing their data.",
        ],
        'done_when': (
            "You have your sample, documented criteria, and the recruitment numbers written down."
        ),
        'beginner_note': (
            "Small samples are normal for student work and are not disqualifying. What matters is that "
            "you state the limitation honestly rather than overclaiming."
        ),
    },

    'collect': {
        'label': 'Collecting data',
        'what': "Actually running the study and recording what happens, consistently and honestly.",
        'how': [
            "Follow your protocol exactly. If you must deviate, write down what changed, when, and why.",
            "Keep a dated log as you go. Memory is not a data-collection instrument.",
            "Record raw data, not just summaries - you can always compute an average later, but you "
            "can't recover what you threw away.",
            "Back up your data somewhere that isn't the machine it was collected on. Do this the same "
            "day.",
            "Use consistent units, labels, and file naming from the first record onward.",
        ],
        'mistakes': [
            "Changing procedure partway through without documenting it.",
            "Overwriting your raw data with a cleaned version - keep both.",
            "Excluding data points because they look wrong, without a pre-defined rule for exclusion.",
            "Only realising at analysis time that a variable you needed was never recorded.",
        ],
        'done_when': (
            "You have a complete, backed-up dataset plus a log of anything that deviated from the plan."
        ),
        'beginner_note': (
            "Losing data is the most common preventable disaster in student research. Two copies in "
            "two places, from day one."
        ),
    },

    'analyze': {
        'label': 'Analysing the data',
        'what': (
            "Applying statistical tests to find out whether the patterns you see are likely to be real "
            "or could easily be chance."
        ),
        'how': [
            "Look at your raw data first - plot it. Many errors are visible in a scatter plot and "
            "invisible in a p-value.",
            "Choose the test based on your design and data type, not on which gives the nicer result. "
            "Cortex's Data & Analysis wizard recommends a test and explains why.",
            "Check the test's assumptions before trusting it (things like normality and equal variance).",
            "Report effect size alongside significance. 'Statistically significant' says the effect is "
            "probably not zero; effect size says whether it's big enough to care about.",
            "Run the analysis you planned. If you also run others, label them exploratory when you "
            "report them.",
        ],
        'mistakes': [
            "Trying tests until one comes out significant (p-hacking). This manufactures false "
            "positives and is detectable by reviewers.",
            "Treating p > 0.05 as proof that there's no effect. It means you didn't detect one, which "
            "isn't the same thing.",
            "Reading a correlation as evidence that one thing caused the other.",
            "Ignoring assumption violations because the test still produced a number.",
        ],
        'done_when': (
            "You've run your planned analyses, checked their assumptions, and have both significance "
            "and effect sizes."
        ),
        'beginner_note': (
            "A p-value is the probability of seeing data at least this extreme if there were genuinely "
            "no effect. It is *not* the probability that your hypothesis is true - that misreading is "
            "extremely common and worth getting right early."
        ),
    },

    'interpret': {
        'label': 'Interpreting results',
        'what': (
            "Saying what your numbers mean for your research question - and, just as importantly, what "
            "they don't mean."
        ),
        'how': [
            "Answer your original question directly and in plain language first.",
            "Put the finding next to the prior work: does it agree, disagree, or extend it?",
            "State your limitations specifically. 'Small sample' is weak; '32 participants from one "
            "school, so this may not generalise to other age groups' is useful.",
            "Separate what the data shows from what you think it implies. Both belong in the write-up, "
            "clearly distinguished.",
            "Consider alternative explanations seriously, and say why yours is better - or admit you "
            "can't rule them out.",
        ],
        'mistakes': [
            "Claiming causation from a design that can only show association.",
            "Generalising past your sample.",
            "Quietly dropping a hypothesis that wasn't supported. A negative result is a real result "
            "and worth reporting.",
            "Confusing 'not statistically significant' with 'no effect exists'.",
        ],
        'done_when': (
            "You can state what you found, how confident you are, and what would have to be done next "
            "to be more confident."
        ),
        'beginner_note': (
            "Results that contradict your hypothesis are not a failed project. Reporting them honestly "
            "is exactly what doing research means."
        ),
    },

    'model': {
        'label': 'Building and validating a model',
        'what': (
            "Expressing a system as equations, code, or a simulation, then checking that it behaves "
            "like the real thing before you draw conclusions from it."
        ),
        'how': [
            "Write down your assumptions explicitly - the ones you know are simplifications especially.",
            "Validate against something you already know the answer to: a benchmark dataset, an "
            "analytical solution, or a published result.",
            "Test sensitivity: vary your parameters and see whether conclusions survive. If they flip "
            "on a small change, say so.",
            "Version-control the code and record the exact configuration that produced each result.",
            "Publish the code and data if you can. Reproducibility is the whole argument for "
            "computational work.",
        ],
        'mistakes': [
            "Reporting model output as if it were measurement of the real world.",
            "Tuning parameters until output matches expectation, then presenting it as validation.",
            "Losing track of which code version produced which figure.",
            "Not checking whether the result is an artefact of a specific random seed.",
        ],
        'done_when': (
            "The model reproduces known cases, you know which assumptions the conclusions depend on, "
            "and someone else could re-run it."
        ),
    },

    'screening': {
        'label': 'Searching and screening studies',
        'what': (
            "For a review: systematically finding every relevant study and deciding, by consistent "
            "written rules, which ones belong."
        ),
        'how': [
            "Write inclusion and exclusion criteria before screening anything.",
            "Record your exact search terms, databases, and dates - a systematic review has to be "
            "repeatable by someone else.",
            "Screen in two passes: title/abstract first, then full text. Cortex's Systematic Review "
            "page runs this workflow and builds the PRISMA diagram from your decisions.",
            "Record a reason for every full-text exclusion. PRISMA requires this.",
            "Have a second person screen at least a sample independently, and record where you "
            "disagreed.",
        ],
        'mistakes': [
            "Changing criteria partway through to include a paper you liked.",
            "Searching one database and calling it systematic.",
            "Not logging why papers were excluded, which makes the review unreproducible.",
        ],
        'done_when': (
            "Every record has a decision and a reason, and your PRISMA numbers add up."
        ),
    },

    'extract': {
        'label': 'Extracting and synthesising findings',
        'what': (
            "Pulling comparable information out of each included study, then combining it into a "
            "coherent picture."
        ),
        'how': [
            "Build an extraction table with the same fields for every study, and fill it consistently.",
            "Capture sample size, design, effect size and its uncertainty - not just the authors' "
            "conclusion.",
            "Assess each study's quality or risk of bias with a published tool, not by impression.",
            "When pooling statistically, check heterogeneity: if studies disagree wildly, an average "
            "may be meaningless.",
            "Note publication bias - studies with null results are less likely to have been published "
            "at all.",
        ],
        'mistakes': [
            "Extracting only the studies' abstracts rather than their actual numbers.",
            "Averaging effect sizes from studies too different to be combined.",
            "Weighting all studies equally regardless of size or quality.",
        ],
        'done_when': (
            "Every included study has a complete row, quality is assessed, and your synthesis reflects "
            "the disagreement between studies as well as the agreement."
        ),
    },

    'write': {
        'label': 'Writing it up',
        'what': (
            "Turning the work into a document another researcher can follow, evaluate, and build on."
        ),
        'how': [
            "Follow the standard structure: Introduction (why), Methods (what you did), Results (what "
            "happened), Discussion (what it means).",
            "Write Methods and Results first - they're the most factual and the easiest to start.",
            "Results state findings without interpreting; Discussion interprets without introducing new "
            "results. Keeping these separate is the most common structural fix reviewers ask for.",
            "Give enough methodological detail for replication. When in doubt, include it.",
            "Cite as you write. In Cortex, type @ in any manuscript section to insert a citation and "
            "the reference list builds itself.",
            "Check whether your target journal has a reporting checklist (CONSORT for trials, PRISMA "
            "for reviews, STROBE for observational studies) and follow it.",
        ],
        'mistakes': [
            "Interpreting results in the Results section.",
            "Methods too vague to reproduce.",
            "Paraphrasing a source too closely - if the sentence structure is theirs, it needs quoting "
            "or genuine rewriting, and a citation either way.",
            "Overclaiming in the abstract relative to what the data supports.",
        ],
        'done_when': (
            "Someone in your field could read it, understand exactly what you did, and disagree with "
            "your interpretation on the evidence you gave them."
        ),
        'beginner_note': (
            "First drafts are supposed to be bad. Get the structure and the facts down, then fix the "
            "prose."
        ),
    },

    'submit': {
        'label': 'Submitting and tracking',
        'what': "Getting the work in front of a venue, and handling what comes back.",
        'how': [
            "Pick venues that match your scope and stage - many journals, conferences, and journals "
            "specifically for undergraduate or high-school research exist.",
            "Read the author guidelines before formatting anything, and follow them exactly.",
            "Submit to one venue at a time. Simultaneous submission to journals is considered "
            "misconduct.",
            "Track each submission's status and deadlines - that's what Cortex's Journals page is for.",
            "When reviews come back, respond point by point, politely, saying what you changed or why "
            "you disagree.",
        ],
        'mistakes': [
            "Ignoring formatting requirements, which gets desk-rejected before review.",
            "Taking rejection as a verdict on you - most papers are rejected somewhere first.",
            "Predatory journals: if they promise fast publication for a fee and spam you, check them "
            "against Think.Check.Submit before paying anything.",
        ],
        'done_when': "Submitted, with the date, venue, and status recorded.",
        'beginner_note': (
            "Rejection is routine. Reviewer comments, even blunt ones, are usually the most useful "
            "feedback you'll get - use them and resubmit elsewhere."
        ),
    },

    'framework': {
        'label': 'Building a theoretical framework',
        'what': (
            "Setting out the concepts, assumptions, and proposed relationships that structure your "
            "argument - the scaffolding the rest of the work hangs on."
        ),
        'how': [
            "Define every key term explicitly, especially ones used loosely in ordinary speech.",
            "Map how the concepts relate - a diagram often exposes gaps that prose hides.",
            "State the assumptions your framework rests on, including the ones you can't test.",
            "Check internal consistency: two premises that contradict each other invalidate whatever "
            "follows.",
            "Show how the framework differs from existing ones and what it explains that they don't.",
        ],
        'mistakes': [
            "Terms that shift meaning between sections.",
            "A framework that can accommodate any possible observation, and so predicts nothing.",
            "Ignoring an established competing framework rather than engaging with it.",
        ],
        'done_when': (
            "The concepts are defined, their relationships are explicit, and the framework generates at "
            "least one claim that could be checked."
        ),
    },

    'case': {
        'label': 'Case study work',
        'what': (
            "Studying one instance in depth - a person, organisation, event, or system - to understand "
            "it thoroughly rather than to generalise statistically."
        ),
        'how': [
            "Say why this case: typical, extreme, or revealing of something otherwise hidden?",
            "Define the case's boundaries - what's inside and outside the thing you're studying.",
            "Use multiple sources (documents, interviews, observation) so findings can be "
            "cross-checked. This is called triangulation.",
            "Keep a clear chain of evidence from raw source to conclusion, so a reader can trace how "
            "you got there.",
            "Compare against existing accounts of similar cases.",
        ],
        'mistakes': [
            "Generalising statistically from one case - case studies give depth, not population "
            "estimates.",
            "Relying on a single source for a key claim.",
            "Letting the narrative you expected drive which evidence you noticed.",
        ],
        'done_when': (
            "Your account is supported by several independent sources and you've said what it does and "
            "doesn't tell us beyond this case."
        ),
    },

    'general': {
        'label': 'General guidance',
        'what': "A step in your project's standard methodology.",
        'how': [
            "Write down what you did and why, while you're doing it.",
            "Follow the established conventions of your discipline.",
            "Check your approach with someone experienced before committing significant time.",
            "Keep records detailed enough that you could reconstruct this step in six months.",
        ],
        'mistakes': [
            "Skipping documentation and reconstructing it from memory later.",
            "Assuming a convention from another field carries over to yours.",
        ],
        'done_when': "The step is complete and documented well enough to write up later.",
    },
}


# First match wins, so order encodes precedence. It was tuned against the
# real step list (see the classification test) - several steps sit on a
# boundary and land in the wrong place under the obvious ordering:
#
#   "Do literature review on that theory"   must beat 'framework' on "theory"
#   "...(e.g. descriptive statistics, typology, case counts)"
#                                            must not match 'case' on "case counts"
#   "Identify broad research question or system to model"
#                                            must beat 'model' on "model"
#   "Identify limitations and gaps"          must beat 'question' on "gap"
#
# Hence: literature is checked early, 'case' requires the word to be the
# study unit rather than any use of it, and 'model' matches specific
# modelling verbs rather than the bare noun.
_CLASSIFIERS: List[tuple] = [
    ('ethics',    r'ethics|irb|consent|approval|safety'),
    # Early: a literature-review step is a literature-review step whatever
    # the topic ("...on that theory", "...on existing models").
    ('literature', r'literature review|prior work'),
    ('screening', r'screen|inclusion and exclusion|search databases|systematically search|exclude weak'),
    ('extract',   r'extract|synthesi|pool|effect sizes|heterogeneity|risk of bias|quality'),
    # 'case' only when it names the unit of study - not "case counts".
    ('case',      r'choose \d+ case|that case|the case\b|similar cases|conduct interviews|gather documents'),
    # Specific modelling verbs, so "system to model" in a question step
    # doesn't get swallowed here.
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
    # Study design
    {'term': 'Independent variable', 'category': 'Design',
     'definition': "The thing you deliberately change or compare. In 'does caffeine affect reaction time', the caffeine dose."},
    {'term': 'Dependent variable', 'category': 'Design',
     'definition': "The thing you measure to see whether it responded. In the same example, reaction time."},
    {'term': 'Control group', 'category': 'Design',
     'definition': "A comparison group that doesn't get the treatment, so you can tell whether the treatment did anything."},
    {'term': 'Confound', 'category': 'Design',
     'definition': "Something that varies alongside your independent variable and could explain your result instead. If the caffeine group also slept longer, sleep is a confound."},
    {'term': 'Randomisation', 'category': 'Design',
     'definition': "Assigning participants to groups by chance, so the groups don't differ systematically at the start."},
    {'term': 'Blinding', 'category': 'Design',
     'definition': "Keeping participants (single-blind) or both participants and researchers (double-blind) unaware of who got which condition, so expectations can't shape the result."},
    {'term': 'Placebo', 'category': 'Design',
     'definition': "An inactive substitute given to the control group so both groups have the same experience apart from the active ingredient."},
    {'term': 'Operationalisation', 'category': 'Design',
     'definition': "Turning an abstract concept into something concretely measurable. 'Stress' becomes 'score on this validated questionnaire'."},
    {'term': 'Pilot study', 'category': 'Design',
     'definition': "A small trial run of your study, done to find problems in the procedure before the real thing."},
    {'term': 'Replication', 'category': 'Design',
     'definition': "Repeating a study to see whether the finding holds. Central to science working, and chronically under-rewarded."},
    {'term': 'Protocol', 'category': 'Design',
     'definition': "The written plan for exactly how the study will be run. Written before you start, and detailed enough that someone else could follow it without asking you questions."},
    {'term': 'Validity', 'category': 'Design',
     'definition': "Whether you're measuring what you think you're measuring. Internal validity is whether your result really comes from your variable; external validity is whether it generalises beyond your sample."},
    {'term': 'Reliability', 'category': 'Design',
     'definition': "Whether a measurement gives consistent results when repeated. A reliable measure can still be invalid - a scale that's always 3kg heavy is perfectly reliable and perfectly wrong."},
    {'term': 'Sample size (n)', 'category': 'Design',
     'definition': "How many participants, samples, or observations you have. Bigger samples give more precise estimates; too-small samples miss real effects. Decide it before you start."},
    {'term': 'Qualitative vs quantitative', 'category': 'Design',
     'definition': "Quantitative research measures things numerically and analyses statistically. Qualitative research works with non-numerical data (interviews, text, observation) to understand meaning and context. Many strong projects use both."},
    {'term': 'Survey', 'category': 'Design',
     'definition': "Collecting self-reported data via a questionnaire. Cheap and scalable, but answers depend heavily on how questions are worded, and people don't always report accurately."},
    {'term': 'Interview', 'category': 'Design',
     'definition': "Structured (fixed questions), semi-structured (a guide plus follow-ups), or unstructured conversation used to collect qualitative data. Usually needs ethics approval and recorded consent."},
    {'term': 'Theory', 'category': 'Design',
     'definition': "In science, a well-substantiated explanation supported by a large body of evidence - not a guess. That everyday sense of 'theory' is closer to 'hypothesis'."},
    {'term': 'Model', 'category': 'Design',
     'definition': "A simplified representation of a system - equations, code, or a simulation - used to make predictions. Every model omits things; the useful question is whether it omits anything that matters for your question."},

    # Statistics
    {'term': 'p-value', 'category': 'Statistics',
     'definition': "The probability of getting data at least this extreme if there were genuinely no effect. It is NOT the probability that your hypothesis is true."},
    {'term': 'Statistical significance', 'category': 'Statistics',
     'definition': "A convention (usually p < 0.05) for calling a result unlikely to be chance. It says nothing about whether the effect is large or important."},
    {'term': 'Effect size', 'category': 'Statistics',
     'definition': "How big the difference or relationship actually is. Report this alongside p-values - significance says an effect probably isn't zero, effect size says whether it matters."},
    {'term': 'Null hypothesis', 'category': 'Statistics',
     'definition': "The default assumption that there is no effect or no difference. Statistical tests are set up to try to reject it."},
    {'term': 'Confidence interval', 'category': 'Statistics',
     'definition': "A range of plausible values for the true effect. A wide interval means your estimate is imprecise - often more informative than a p-value."},
    {'term': 'Type I error', 'category': 'Statistics',
     'definition': "A false positive: concluding there's an effect when there isn't."},
    {'term': 'Type II error', 'category': 'Statistics',
     'definition': "A false negative: missing a real effect, usually because the sample was too small."},
    {'term': 'Statistical power', 'category': 'Statistics',
     'definition': "The chance your study detects an effect that's really there. Low power is why small studies often find nothing."},
    {'term': 'Correlation', 'category': 'Statistics',
     'definition': "Two things varying together. Correlation does not imply causation - they may share a common cause, or the arrow may point the other way."},
    {'term': 'Causation', 'category': 'Statistics',
     'definition': "One thing actually bringing about another. Showing causation needs a design that rules out alternatives - typically a randomised experiment. Observational data can show two things move together, but not that one caused the other."},
    {'term': 'Mean, median, mode', 'category': 'Statistics',
     'definition': "Three kinds of average. The mean is the arithmetic average and is dragged around by outliers; the median is the middle value and resists them; the mode is the most common value. Skewed data is usually better summarised by the median."},
    {'term': 'Standard deviation', 'category': 'Statistics',
     'definition': "How spread out the data is around the mean. A small SD means values cluster tightly; a large one means they're scattered. Report it alongside the mean - an average with no spread is close to meaningless."},
    {'term': 't-test', 'category': 'Statistics',
     'definition': "Tests whether the means of two groups differ more than you'd expect by chance. Independent-samples for two separate groups, paired for the same group measured twice."},
    {'term': 'ANOVA', 'category': 'Statistics',
     'definition': "Analysis of Variance - compares means across three or more groups. A significant result says at least one group differs, not which; that needs a follow-up (post-hoc) test."},
    {'term': 'Regression', 'category': 'Statistics',
     'definition': "Models how one variable changes with others, letting you predict an outcome and estimate each predictor's contribution. Linear regression fits a straight line; multiple regression uses several predictors at once."},
    {'term': 'Parametric vs non-parametric', 'category': 'Statistics',
     'definition': "Parametric tests (t-test, ANOVA) assume your data follows a particular distribution, usually normal. Non-parametric ones (Mann-Whitney, Kruskal-Wallis) don't, and are the fallback when those assumptions fail."},
    {'term': 'p-hacking', 'category': 'Statistics',
     'definition': "Trying analyses until something crosses p < 0.05. It manufactures false positives, and pre-registering your analysis plan is the standard defence."},
    {'term': 'HARKing', 'category': 'Statistics',
     'definition': "Hypothesising After Results are Known - presenting a hypothesis invented after seeing the data as if it had been predicted."},
    {'term': 'Outlier', 'category': 'Statistics',
     'definition': "A data point far from the rest. Investigate it; only exclude it by a rule you set in advance, and say that you did."},
    {'term': 'Normal distribution', 'category': 'Statistics',
     'definition': "The bell curve. Many common tests assume your data roughly follows it - check rather than assume."},
    {'term': 'Descriptive vs inferential statistics', 'category': 'Statistics',
     'definition': "Descriptive summarises the data you have (means, spread). Inferential draws conclusions about a wider population from it."},

    # Literature and publishing
    {'term': 'Peer review', 'category': 'Publishing',
     'definition': "Other researchers in the field evaluating a paper before publication. Imperfect, but the main quality filter science has."},
    {'term': 'Preprint', 'category': 'Publishing',
     'definition': "A paper posted publicly before peer review (arXiv, bioRxiv, medRxiv). Free to read, but not yet vetted."},
    {'term': 'DOI', 'category': 'Publishing',
     'definition': "Digital Object Identifier - a permanent address for a paper. More reliable than a URL, which rots."},
    {'term': 'Impact factor', 'category': 'Publishing',
     'definition': "Average citations per paper for a journal. Widely used, widely criticised - it says little about any individual paper."},
    {'term': 'Open access', 'category': 'Publishing',
     'definition': "Freely readable without a subscription. Some open-access journals charge authors a publication fee."},
    {'term': 'Predatory journal', 'category': 'Publishing',
     'definition': "A journal that charges fees while providing no real peer review. Check unfamiliar venues against Think.Check.Submit before paying."},
    {'term': 'Literature review', 'category': 'Publishing',
     'definition': "A survey of what's already known on a topic. As a section it sets up your study; as a paper in its own right it synthesises a field. A systematic review is the rigorous, reproducible version."},
    {'term': 'Systematic review', 'category': 'Publishing',
     'definition': "A review that finds and appraises all relevant studies by a pre-specified, reproducible method - as opposed to a narrative review of whatever the author happened to read."},
    {'term': 'Meta-analysis', 'category': 'Publishing',
     'definition': "Statistically combining results from multiple studies to estimate an overall effect."},
    {'term': 'PRISMA', 'category': 'Publishing',
     'definition': "The reporting standard for systematic reviews, including the flow diagram showing how many records were found, screened, and included."},
    {'term': 'Grey literature', 'category': 'Publishing',
     'definition': "Work outside commercial publishing - theses, government reports, conference abstracts. Often worth searching, easily missed."},
    {'term': 'Publication bias', 'category': 'Publishing',
     'definition': "Positive results get published more than null ones, so the literature overstates effects. A known problem for meta-analyses."},

    # Ethics and integrity
    {'term': 'IRB', 'category': 'Ethics',
     'definition': "Institutional Review Board - the committee that reviews research involving human participants. Approval is required before you start, not after."},
    {'term': 'Informed consent', 'category': 'Ethics',
     'definition': "Participants agreeing to take part after being told what's involved, what the risks are, and that they can withdraw at any time."},
    {'term': 'Assent', 'category': 'Ethics',
     'definition': "A minor's own agreement to participate, required in addition to a parent or guardian's consent."},
    {'term': 'Anonymised vs de-identified', 'category': 'Ethics',
     'definition': "De-identified data has identifiers removed but could be re-linked; anonymised data cannot be traced back at all."},
    {'term': 'Plagiarism', 'category': 'Ethics',
     'definition': "Presenting someone else's words or ideas as your own. Includes close paraphrase without citation, and reusing your own prior text without saying so."},
    {'term': 'Authorship', 'category': 'Ethics',
     'definition': "Credit for substantial intellectual contribution. Conventions vary by field; agree the author list and order early, in writing, before it becomes awkward."},
    {'term': 'Conflict of interest', 'category': 'Ethics',
     'definition': "Anything that could bias your work or appear to - funding, employment, personal stake. Disclose rather than judge for yourself whether it mattered."},
    {'term': 'Pre-registration', 'category': 'Ethics',
     'definition': "Publicly recording your hypotheses and analysis plan before collecting data, so you can't be accused of inventing them afterwards."},
    {'term': 'Reproducibility', 'category': 'Ethics',
     'definition': "Someone else getting your results from your data and methods. Sharing code and data is the practical version of this."},
]


# ---------------------------------------------------------------------------
# Beginner primer
# ---------------------------------------------------------------------------

BASICS: List[Dict] = [
    {
        'id': 'what-is-research',
        'title': 'What research actually is',
        'body': [
            "Research is producing an answer to a question in a way that lets other people check your "
            "reasoning. That last part is what separates it from having an opinion.",
            "The shape is nearly always the same: notice something unresolved, find out what's already "
            "known, make a specific claim or question, gather evidence in a way that could contradict "
            "you, and report honestly what you found - including the parts that didn't work.",
            "Almost nobody's first project goes to plan. Changing your question after the literature "
            "review, discovering your method doesn't work during a pilot, and getting a null result "
            "are all normal parts of the process rather than signs you've failed.",
        ],
    },
    {
        'id': 'choosing',
        'title': 'Choosing something you can actually finish',
        'body': [
            "The most common reason student projects stall is a question that was too big from the "
            "start. Scope is the single most valuable thing to get right.",
            "A good test: can you say, in one sentence, what you would measure and what you would "
            "compare it to? If not, keep narrowing.",
            "Be realistic about what you have. A question requiring equipment you can't access, "
            "participants you can't recruit, or approval you won't get in time is not a question you "
            "can answer this year - and a small, well-executed study beats an ambitious abandoned one.",
            "It is fine, and normal, for your question to change after you read the literature. That's "
            "the literature review doing its job.",
        ],
    },
    {
        'id': 'reading',
        'title': 'How to read a paper without drowning',
        'body': [
            "You are not supposed to read academic papers start to finish on the first pass. Almost "
            "nobody does.",
            "Three passes works well. First: title, abstract, and figures - decide in about five "
            "minutes whether this paper matters to you. Second: introduction and discussion, for the "
            "argument and the context. Third, only for papers you'll rely on: methods and results in "
            "full, checking whether you actually believe the conclusion.",
            "Read figures and their captions carefully. A paper's real content is often there, and "
            "captions are usually written to stand alone.",
            "Keep notes in your own words with the citation attached, and mark direct quotes as quotes "
            "immediately. This is how you avoid accidental plagiarism months later when you can't "
            "remember which phrases were yours.",
            "Not understanding a paper on first reading is normal and says nothing about your ability. "
            "Look up the terms, read a review article on the topic first, and come back.",
        ],
    },
    {
        'id': 'evidence',
        'title': 'Not fooling yourself',
        'body': [
            "The hardest part of research is avoiding being convinced by your own expectations. Every "
            "safeguard in methodology exists for this reason.",
            "Decide what would change your mind before you look at the data, and write it down. It is "
            "remarkably hard to be honest about this afterwards.",
            "Correlation is not causation. Two things moving together can share a common cause, or the "
            "causal arrow can run the other way. Only certain designs support causal claims.",
            "A result that isn't statistically significant means you didn't detect an effect - not that "
            "there isn't one. Small studies miss real effects routinely.",
            "Look for the strongest evidence against your position, not the weakest. If you only ever "
            "argue against weak counterexamples, you haven't tested your idea.",
        ],
    },
    {
        'id': 'ethics',
        'title': 'Ethics, permission, and credit',
        'body': [
            "If your research involves people, animals, or identifiable data, you almost certainly need "
            "approval before you start - from an IRB, an ethics committee, or your school's equivalent. "
            "Approval cannot be obtained retroactively, and data collected without it usually can't be "
            "used.",
            "Science fairs have their own rules on top of this. ISEF and many regional fairs require "
            "documented approval before experimentation begins and will disqualify entries that skipped "
            "it - check the current rules for the specific fair you're entering.",
            "Cite everything that isn't your own idea, including ideas you rephrased. Close paraphrase "
            "without citation still counts as plagiarism.",
            "Agree authorship early. Who is an author, and in what order, is a genuine source of "
            "conflict, and it is far easier to settle before there's a paper to argue over. Conventions "
            "differ sharply between fields - ask what yours does.",
            "If you use AI tools in your work, check the policy of your school, fair, or target journal, "
            "and disclose use where required. Policies are changing quickly.",
        ],
    },
    {
        'id': 'help',
        'title': 'Getting help',
        'body': [
            "Research is not meant to be done alone, and asking for help is not cheating. Find someone "
            "who has done it before: a teacher, a lab you can volunteer in, a university student, a "
            "researcher whose paper you liked.",
            "Cold emails to researchers work more often than people expect, especially from students. "
            "Be brief, be specific about what you've read of theirs, and ask one concrete question.",
            "When you ask for help, show what you've already tried. It's the difference between a "
            "question someone can answer in two minutes and one that needs an hour.",
            "A mentor matters most at study design and interpretation - the two points where mistakes "
            "are expensive and hardest to see from inside.",
        ],
    },
    {
        'id': 'limits',
        'title': 'What this guide can and can\'t tell you',
        'body': [
            "Everything here is general research methodology - the parts that hold across disciplines. "
            "It should orient you and help you ask better questions.",
            "It cannot substitute for the specific requirements of your field, institution, or "
            "jurisdiction. Lab safety protocols, IRB requirements, clinical trial registration, data "
            "protection law, and field-specific reporting standards all have binding rules that this "
            "cannot encode and that vary by where you are.",
            "Where a real standard exists, Cortex links to it - CONSORT for trials, PRISMA for reviews, "
            "STROBE for observational studies, and the reporting guidelines listed on your project's "
            "Methodology page. Read the actual standard for anything you're submitting.",
            "When this guide and your advisor, teacher, or ethics board disagree, they are right.",
        ],
    },
]


def get_basics() -> List[Dict]:
    return BASICS


def get_glossary(query: str = '') -> List[Dict]:
    q = (query or '').strip().lower()
    if not q:
        return GLOSSARY
    return [
        item for item in GLOSSARY
        if q in item['term'].lower() or q in item['definition'].lower() or q in item['category'].lower()
    ]


def glossary_categories() -> List[str]:
    seen: List[str] = []
    for item in GLOSSARY:
        if item['category'] not in seen:
            seen.append(item['category'])
    return seen
