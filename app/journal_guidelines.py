"""
Journal Guidelines reference for Cortex
A small curated lookup of well-known journals' publicly documented submission
requirements. This is manually curated reference data (not fetched from any
API - no such API exists), meant as a starting-point summary. The researcher
should always confirm current requirements on the journal's own author
guidelines page before submitting, since journals revise these periodically.
"""

from typing import Dict, Optional

JOURNAL_GUIDELINES = {
    'nature': {
        'name': 'Nature',
        'citation_style': 'Nature (numbered, superscript)',
        'word_limit': 'Articles ~3,000-5,000 words; Letters shorter',
        'structure': 'Abstract (~150 words), Introduction, Results, Discussion, Methods, References',
        'notes': 'No dedicated "Methods" section length limit but should be concise; figures separate from main text.',
        'homepage': 'https://www.nature.com/nature/for-authors',
    },
    'science': {
        'name': 'Science',
        'citation_style': 'Science (numbered)',
        'word_limit': 'Research Articles ~4,500 words including refs',
        'structure': 'Abstract (125 words), Introduction, Results, Discussion, Materials and Methods, References',
        'notes': 'Strict figure/table count limits; supplementary materials handled separately.',
        'homepage': 'https://www.science.org/content/page/science-information-authors',
    },
    'cell': {
        'name': 'Cell',
        'citation_style': 'Cell Press (numbered)',
        'word_limit': 'Varies by article type; Articles typically <45,000 characters',
        'structure': 'Summary, Introduction, Results, Discussion, STAR Methods, References',
        'notes': 'Uses structured STAR Methods format for reproducibility.',
        'homepage': 'https://www.cell.com/cell/authors',
    },
    'plos one': {
        'name': 'PLOS ONE',
        'citation_style': 'Vancouver (numbered)',
        'word_limit': 'No strict limit, but concise writing encouraged',
        'structure': 'Abstract, Introduction, Materials and Methods, Results, Discussion, Conclusions, References',
        'notes': 'Open access; reviews on technical soundness rather than perceived impact.',
        'homepage': 'https://journals.plos.org/plosone/s/submission-guidelines',
    },
    'pnas': {
        'name': 'PNAS (Proceedings of the National Academy of Sciences)',
        'citation_style': 'PNAS (numbered)',
        'word_limit': 'Research Articles ~6 published pages (~4,000-5,000 words)',
        'structure': 'Abstract (250 words), Introduction, Results, Discussion, Materials and Methods, References',
        'notes': 'Significance statement required (120 words) for a general audience.',
        'homepage': 'https://www.pnas.org/author-center',
    },
    'nejm': {
        'name': 'New England Journal of Medicine (NEJM)',
        'citation_style': 'Vancouver (numbered)',
        'word_limit': 'Original Articles ~2,700 words + abstract 250 words',
        'structure': 'Abstract (structured), Introduction, Methods, Results, Discussion, References',
        'notes': 'Requires clinical trial registration and CONSORT reporting for RCTs.',
        'homepage': 'https://www.nejm.org/author-center/new-manuscripts',
    },
    'jama': {
        'name': 'JAMA',
        'citation_style': 'AMA (numbered)',
        'word_limit': 'Original Investigations ~3,000 words + abstract 350 words',
        'structure': 'Structured Abstract, Introduction, Methods, Results, Discussion, References',
        'notes': 'Requires adherence to reporting guidelines (CONSORT, STROBE, PRISMA) matched to study design.',
        'homepage': 'https://jamanetwork.com/journals/jama/pages/instructions-for-authors',
    },
    'the lancet': {
        'name': 'The Lancet',
        'citation_style': 'Vancouver (numbered)',
        'word_limit': 'Articles ~3,000-4,500 words + abstract 300 words (structured)',
        'structure': 'Structured Summary, Introduction, Methods, Results, Discussion, References',
        'notes': 'Requires a "Research in context" panel summarizing evidence before/after the study.',
        'homepage': 'https://www.thelancet.com/for-authors',
    },
    'ieee': {
        'name': 'IEEE Transactions (general)',
        'citation_style': 'IEEE (numbered, bracketed)',
        'word_limit': 'Typically 6-8 double-column pages including figures/references',
        'structure': 'Abstract, Index Terms, Introduction, Related Work, Methods, Experiments/Results, Conclusion, References',
        'notes': 'Uses IEEEtran LaTeX template; strict on structure of related-work section.',
        'homepage': 'https://www.ieee.org/publications/authors/author-templates.html',
    },
    'acm': {
        'name': 'ACM Journals/Conferences (general)',
        'citation_style': 'ACM Reference Format (numbered or author-year depending on venue)',
        'word_limit': 'Varies widely by venue; conferences often page-limited (e.g. 8-12 pages)',
        'structure': 'Abstract, Introduction, Related Work, Methods, Evaluation, Discussion, Conclusion, References',
        'notes': 'Uses the acmart LaTeX template; check specific venue call for page limits.',
        'homepage': 'https://www.acm.org/publications/authors/information-for-authors',
    },
    'frontiers': {
        'name': 'Frontiers (general)',
        'citation_style': 'Frontiers (author-year)',
        'word_limit': 'Varies by article type, typically 8,000-12,000 words for Original Research',
        'structure': 'Abstract, Introduction, Materials and Methods, Results, Discussion, References',
        'notes': 'Open access with open peer review option; collaborative review platform.',
        'homepage': 'https://www.frontiersin.org/guidelines/author-guidelines',
    },
    'apa': {
        'name': 'APA Journals (general, e.g. psychology)',
        'citation_style': 'APA 7th edition (author-year)',
        'word_limit': 'Varies by journal, often ~35 pages double-spaced including references',
        'structure': 'Abstract (250 words), Introduction, Method, Results, Discussion, References',
        'notes': 'Follow APA Style formatting exactly (headings, tables, statistics reporting).',
        'homepage': 'https://apastyle.apa.org/instructional-aids/journal-article-reporting-standards',
    },
}

GENERIC_GUIDANCE = {
    'name': 'General guidance (journal not in our curated list)',
    'citation_style': 'Check the journal\'s official author guidelines - common styles are APA, MLA, Chicago, Vancouver, IEEE, and journal-specific "numbered" formats',
    'word_limit': 'Varies widely by journal and article type - always check the specific journal\'s current guidelines',
    'structure': 'Most journals expect: Abstract, Introduction, Methods, Results, Discussion, Conclusion, References '
                 '(qualitative/theoretical work often differs - check journal scope)',
    'notes': (
        'This journal is not in Cortex\'s curated reference list. Search "<journal name> author guidelines" '
        'or "instructions for authors" to find the current official requirements before submitting - '
        'journals revise word limits, formatting, and structure periodically.'
    ),
    'homepage': '',
}


def lookup_guidelines(journal_name: str) -> Dict:
    """
    Look up curated guidelines for a journal by fuzzy name match.
    Falls back to generic guidance if the journal isn't in the curated list.
    """
    if not journal_name:
        return GENERIC_GUIDANCE

    normalized = journal_name.strip().lower()

    if normalized in JOURNAL_GUIDELINES:
        return JOURNAL_GUIDELINES[normalized]

    for key, guideline in JOURNAL_GUIDELINES.items():
        if key in normalized or normalized in key:
            return guideline

    return GENERIC_GUIDANCE


def list_known_journals() -> Dict[str, str]:
    """Return {key: display_name} for all curated journals, for a picker UI"""
    return {key: g['name'] for key, g in JOURNAL_GUIDELINES.items()}
