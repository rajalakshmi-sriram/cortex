"""
Tool Recommendations for Cortex
Curated, manually-maintained suggestions of external tools commonly used at
each stage of the research process (e.g. Zotero/Elicit for literature review).
These are reference suggestions only - the user can also attach their own
custom tool links to any step (see ProjectStore.add_step_tool).
"""

import re
from typing import Dict, List

# category -> (keyword patterns to match against step text, tool list)
STEP_TOOL_CATEGORIES = {
    'literature_review': {
        'keywords': ['literature', 'search databases', 'screen', 'gather documents',
                     'extract information', 'synthesize findings'],
        'tools': [
            # Discovery & search
            {'name': 'Semantic Scholar', 'url': 'https://www.semanticscholar.org', 'description': 'AI-powered search across 200M+ papers with TL;DR summaries'},
            {'name': 'Consensus', 'url': 'https://consensus.app', 'description': 'Answers research questions from peer-reviewed evidence, shows scientific consensus'},
            {'name': 'Elicit', 'url': 'https://elicit.com', 'description': 'AI research assistant - automates systematic reviews, extracts data into tables'},
            {'name': 'Google Scholar', 'url': 'https://scholar.google.com', 'description': 'General academic search'},
            # Literature mapping
            {'name': 'Research Rabbit', 'url': 'https://www.researchrabbit.ai', 'description': '"Spotify for research" - visual maps of related papers/authors'},
            {'name': 'Litmaps', 'url': 'https://www.litmaps.com', 'description': 'Visualize citation networks, find gaps, track a field\'s evolution'},
            {'name': 'Connected Papers', 'url': 'https://www.connectedpapers.com', 'description': 'Visual citation graph explorer'},
            # Reading & annotation
            {'name': 'SciSpace', 'url': 'https://scispace.com', 'description': 'AI PDF reader - explains text, equations, and methods in real time'},
            {'name': 'NotebookLM', 'url': 'https://notebooklm.google.com', 'description': 'Upload multiple PDFs to build study guides & explore sources interactively'},
            # Citation management
            {'name': 'Zotero', 'url': 'https://www.zotero.org', 'description': 'Reference manager & citation library, integrates with Word/Google Docs'},
            {'name': 'EndNote', 'url': 'https://endnote.com', 'description': 'Reference manager for large libraries & team sharing'},
        ],
    },
    'idea_generation': {
        'keywords': ['hypothes', 'identify gap', 'inconsistency', 'research problem', 'research question'],
        'tools': [
            {'name': 'Elicit', 'url': 'https://elicit.com', 'description': 'AI research assistant for idea generation & hypothesis brainstorming'},
            {'name': 'Zotero', 'url': 'https://www.zotero.org', 'description': 'Browse your saved literature for gaps'},
        ],
    },
    'concept_map': {
        'keywords': ['framework', 'concept map'],
        'tools': [
            {'name': 'Miro', 'url': 'https://miro.com', 'description': 'Visual whiteboard for concept maps'},
            {'name': 'Coggle', 'url': 'https://coggle.it', 'description': 'Simple mind-mapping tool'},
            {'name': 'Lucidchart', 'url': 'https://www.lucidchart.com', 'description': 'Diagramming & flowcharts'},
        ],
    },
    'data_collection': {
        'keywords': ['recruit participants', 'conduct experiment', 'conduct interviews',
                     'collect data', 'collect observational', 'give and track interventions'],
        'tools': [
            {'name': 'Qualtrics', 'url': 'https://www.qualtrics.com', 'description': 'Survey design & distribution'},
            {'name': 'REDCap', 'url': 'https://www.project-redcap.org', 'description': 'Secure clinical/research data capture'},
            {'name': 'Google Forms', 'url': 'https://forms.google.com', 'description': 'Simple free survey forms'},
        ],
    },
    'data_analysis': {
        'keywords': ['analyze', 'analyse', 'statistical'],
        'tools': [
            {'name': 'JASP', 'url': 'https://jasp-stats.org', 'description': 'Free spreadsheet-style stats software'},
            {'name': 'jamovi', 'url': 'https://www.jamovi.org', 'description': 'Free stats software built on R'},
            {'name': 'RStudio', 'url': 'https://posit.co/products/open-source/rstudio/', 'description': 'R programming IDE for statistics'},
        ],
    },
    'ethics': {
        'keywords': ['ethics approval'],
        'tools': [
            {'name': 'Your institution\'s IRB portal', 'url': '', 'description': 'Ethics approval is institution-specific - check your IRB/ethics board site'},
        ],
    },
    'manuscript': {
        'keywords': ['draft the manuscript', 'draft manuscript', 'draft review', 'draft systematic review'],
        'tools': [
            {'name': 'Overleaf', 'url': 'https://www.overleaf.com', 'description': 'Collaborative LaTeX manuscript editor'},
            {'name': 'Scite', 'url': 'https://scite.ai', 'description': 'Smart Citations - shows whether other papers support or contradict a finding'},
            {'name': 'Jenni AI', 'url': 'https://jenni.ai', 'description': 'AI writing editor with suggested in-text citations from your references'},
            {'name': 'Paperpal', 'url': 'https://paperpal.com', 'description': 'Academic writing assistant - grammar, tone, journal submission readiness'},
            {'name': 'Grammarly', 'url': 'https://www.grammarly.com', 'description': 'Writing/grammar assistant'},
        ],
    },
}


# Reporting-standard / regulatory guidance tied to the *type of study design*
# itself (research_type), as distinct from STEP_TOOL_CATEGORIES above which is
# about the general research *process* (searching, writing, etc). E.g. a
# Clinical Research project needs IRB/GCP/CONSORT guidance regardless of which
# process step is active; a Literature Review (systematic review/meta-analysis)
# needs PRISMA regardless of which process step is active.
RESEARCH_TYPE_METHODOLOGY_TOOLS = {
    'theoretical': [
        {'name': 'EQUATOR Network', 'url': 'https://www.equator-network.org', 'description': 'Central library of reporting guidelines across research types'},
    ],
    'experimental': [
        {'name': 'CONSORT Statement', 'url': 'http://www.consort-statement.org', 'description': 'Reporting guideline for randomized controlled trials'},
        {'name': 'APA JARS', 'url': 'https://apastyle.apa.org/jars', 'description': 'Journal Article Reporting Standards for quantitative research'},
        {'name': 'Research Randomizer', 'url': 'https://www.randomizer.org', 'description': 'Free tool for random assignment/sampling'},
    ],
    'exploratory': [
        {'name': 'COREQ', 'url': 'https://www.equator-network.org/reporting-guidelines/coreq/', 'description': 'Reporting guideline for qualitative research (interviews/case studies)'},
        {'name': 'EQUATOR Network', 'url': 'https://www.equator-network.org', 'description': 'Central library of reporting guidelines - browse case study/qualitative methodology resources'},
    ],
    'pilot': [
        {'name': 'CONSORT Extension for Pilot Trials', 'url': 'http://www.consort-statement.org/extensions/overview/pilotandfeasibility', 'description': 'Reporting guideline specific to pilot & feasibility studies'},
        {'name': 'Research Randomizer', 'url': 'https://www.randomizer.org', 'description': 'Free tool for random assignment/sampling'},
    ],
    'literature_review': [
        {'name': 'PRISMA Statement', 'url': 'https://www.prisma-statement.org', 'description': 'Reporting guideline for systematic reviews & meta-analyses'},
        {'name': 'PRISMA Flow Diagram Generator', 'url': 'https://estech.shinyapps.io/prisma_flowdiagram/', 'description': 'Generate the PRISMA study-selection flow diagram'},
        {'name': 'PROSPERO', 'url': 'https://www.crd.york.ac.uk/prospero/', 'description': 'International registry for systematic review protocols'},
        {'name': 'Cochrane Handbook', 'url': 'https://training.cochrane.org/handbook', 'description': 'Standard methodology reference for systematic reviews'},
    ],
    'clinical': [
        {'name': 'ICH-GCP Guidelines', 'url': 'https://ichgcp.net', 'description': 'International Good Clinical Practice standards for clinical trials'},
        {'name': 'CONSORT Statement', 'url': 'http://www.consort-statement.org', 'description': 'Reporting guideline for randomized controlled trials'},
        {'name': 'SPIRIT Statement', 'url': 'https://www.spirit-statement.org', 'description': 'Guideline for clinical trial protocols'},
        {'name': 'ClinicalTrials.gov', 'url': 'https://clinicaltrials.gov', 'description': 'Required public registration for clinical trials'},
        {'name': 'Declaration of Helsinki', 'url': 'https://www.wma.net/policies-post/wma-declaration-of-helsinki/', 'description': 'Ethical principles for medical research involving human subjects'},
        {'name': 'Your institution\'s IRB portal', 'url': '', 'description': 'Ethics/IRB approval is institution-specific - check your IRB/ethics board site'},
    ],
}


def get_methodology_guidelines(research_type: str) -> List[Dict]:
    """
    Return curated reporting-standard/regulatory guidance for a research
    TYPE (study design), independent of which process step is active.
    """
    return RESEARCH_TYPE_METHODOLOGY_TOOLS.get(research_type, [])


def get_recommended_tools(step_text: str) -> List[Dict]:
    """
    Return curated tool suggestions for a methodology step, based on keyword
    matching against the step's text. A step may match multiple categories.
    """
    text = step_text.lower()
    seen_names = set()
    tools = []

    for category in STEP_TOOL_CATEGORIES.values():
        if any(re.search(re.escape(kw), text) for kw in category['keywords']):
            for tool in category['tools']:
                if tool['name'] not in seen_names:
                    seen_names.add(tool['name'])
                    tools.append(tool)

    return tools
