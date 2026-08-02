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
    'jacs': {
        'name': 'JACS (Journal of the American Chemical Society)',
        'citation_style': 'ACS (numbered)',
        'word_limit': 'Communications ~4 pages; Articles no strict word limit but concise',
        'structure': 'TOC graphic, Introduction, Results and Discussion, Conclusions, Experimental/Methods, References',
        'notes': 'Requires a table-of-contents (TOC) graphic; supporting information (SI) submitted separately.',
        'homepage': 'https://pubs.acs.org/page/jacsat/submission/authors.html',
    },
    'angewandte chemie': {
        'name': 'Angewandte Chemie',
        'citation_style': 'Wiley/ACS-style (numbered)',
        'word_limit': 'Communications ~5 printed pages; Reviews longer',
        'structure': 'Graphical abstract, Introduction, Results and Discussion, Conclusion, Experimental Section, References',
        'notes': 'Known for its graphical-abstract ("frontispiece") requirement and "Very Important Paper" (VIP) designation for top submissions.',
        'homepage': 'https://onlinelibrary.wiley.com/page/journal/15213773/homepage/forauthors.html',
    },
    'chemical science': {
        'name': 'Chemical Science (Royal Society of Chemistry)',
        'citation_style': 'RSC (numbered)',
        'word_limit': 'No strict word limit; concise preferred, typically ~6-8 pages',
        'structure': 'Abstract, Introduction, Results and Discussion, Conclusions, Experimental, References',
        'notes': 'Fully open access, published by the RSC; no page charges for most authors.',
        'homepage': 'https://www.rsc.org/journals-books-databases/journal-authors-reviewers/author-responsibilities/preparing-manuscript/',
    },
    'nature chemistry': {
        'name': 'Nature Chemistry',
        'citation_style': 'Nature (numbered, superscript)',
        'word_limit': 'Articles ~3,000-4,000 words',
        'structure': 'Abstract (~150 words), Introduction, Results, Discussion, Methods, References',
        'notes': 'Part of the Nature family - same general submission philosophy as Nature.',
        'homepage': 'https://www.nature.com/nchem/for-authors',
    },
    'analytical chemistry': {
        'name': 'Analytical Chemistry (ACS)',
        'citation_style': 'ACS (numbered)',
        'word_limit': 'Articles typically 6,000-8,000 words; no strict cap',
        'structure': 'Abstract, Introduction, Experimental Section, Results and Discussion, Conclusions, References',
        'notes': 'Strong focus on methodological rigor and validation of analytical methods.',
        'homepage': 'https://pubs.acs.org/page/ancham/submission/authors.html',
    },
    'jbc': {
        'name': 'Journal of Biological Chemistry (JBC)',
        'citation_style': 'ASBMB (numbered)',
        'word_limit': 'No strict word limit; concise writing encouraged',
        'structure': 'Abstract, Introduction, Results, Discussion, Experimental Procedures, References',
        'notes': 'Published by ASBMB; emphasizes mechanistic detail and reproducibility.',
        'homepage': 'https://www.jbc.org/content/authorinfo',
    },
    'elife': {
        'name': 'eLife',
        'citation_style': 'eLife house style (numbered)',
        'word_limit': 'No strict word limit; Research Articles typically ~4,000-6,000 words',
        'structure': 'Abstract, Introduction, Results, Discussion, Materials and Methods, References',
        'notes': 'Public peer review model - reviews and author responses are published alongside the paper.',
        'homepage': 'https://elifesciences.org/for-authors',
    },
    'embo journal': {
        'name': 'The EMBO Journal',
        'citation_style': 'EMBO house style (numbered)',
        'word_limit': 'Articles typically <45,000 characters',
        'structure': 'Synopsis, Abstract, Introduction, Results, Discussion, Materials and Methods, References',
        'notes': 'Requires a "Synopsis" and graphical summary; strong focus on molecular/cell biology mechanism.',
        'homepage': 'https://www.embopress.org/authorguide',
    },
    'nature biotechnology': {
        'name': 'Nature Biotechnology',
        'citation_style': 'Nature (numbered, superscript)',
        'word_limit': 'Articles ~3,000-4,000 words',
        'structure': 'Abstract, Introduction, Results, Discussion, Methods, References',
        'notes': 'Part of the Nature family; strong translational/applied biotech focus.',
        'homepage': 'https://www.nature.com/nbt/for-authors',
    },
    'plos biology': {
        'name': 'PLOS Biology',
        'citation_style': 'Vancouver (numbered)',
        'word_limit': 'No strict limit; concise preferred',
        'structure': 'Abstract, Introduction, Results, Discussion, Materials and Methods, References',
        'notes': 'Open access; higher selectivity/perceived-impact bar than PLOS ONE.',
        'homepage': 'https://journals.plos.org/plosbiology/s/submission-guidelines',
    },
    'nature communications': {
        'name': 'Nature Communications',
        'citation_style': 'Nature (numbered, superscript)',
        'word_limit': 'No strict word limit; typically ~5,000 words',
        'structure': 'Abstract (~150 words), Introduction, Results, Discussion, Methods, References',
        'notes': 'Open access, part of the Nature family; reviews for technical soundness rather than perceived impact.',
        'homepage': 'https://www.nature.com/ncomms/submission-guidelines',
    },
    'scientific reports': {
        'name': 'Scientific Reports',
        'citation_style': 'Nature (numbered, superscript)',
        'word_limit': 'No strict word limit',
        'structure': 'Abstract, Introduction, Results, Discussion, Methods, References',
        'notes': 'Open access, part of the Nature family; reviews for technical soundness, similar philosophy to PLOS ONE.',
        'homepage': 'https://www.nature.com/srep/author-instructions',
    },
    'bmj': {
        'name': 'BMJ (British Medical Journal)',
        'citation_style': 'Vancouver (numbered)',
        'word_limit': 'Research articles ~2,700-4,000 words + structured abstract',
        'structure': 'Structured Abstract, Introduction, Methods, Results, Discussion, References',
        'notes': 'Requires adherence to the relevant reporting guideline (CONSORT/STROBE/PRISMA) and trial registration for RCTs.',
        'homepage': 'https://www.bmj.com/about-bmj/resources-authors',
    },
    'annals of internal medicine': {
        'name': 'Annals of Internal Medicine',
        'citation_style': 'Vancouver (numbered)',
        'word_limit': 'Original Research ~2,700-3,500 words + structured abstract',
        'structure': 'Structured Abstract, Introduction, Methods, Results, Discussion, References',
        'notes': 'Requires reporting-guideline adherence matched to study design (CONSORT/STROBE/PRISMA).',
        'homepage': 'https://www.acpjournals.org/authors/annals-author-instructions',
    },
    'physical review letters': {
        'name': 'Physical Review Letters (PRL)',
        'citation_style': 'APS (numbered)',
        'word_limit': 'Letters limited to ~3,750 words or 4 published pages',
        'structure': 'Abstract, Letter body (no rigid section headers required), References',
        'notes': 'Very strict length limit; uses APS\'s own REVTeX LaTeX template.',
        'homepage': 'https://journals.aps.org/prl/authors',
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

    # Prefer the longest (most specific) matching key rather than the first
    # one found by insertion order - otherwise a query like "nature
    # chemistry" would incorrectly match the plain "nature" entry, since
    # "nature" is a substring of it and was added to the dict first.
    matches = [key for key in JOURNAL_GUIDELINES if key in normalized or normalized in key]
    if matches:
        return JOURNAL_GUIDELINES[max(matches, key=len)]

    return GENERIC_GUIDANCE


def list_known_journals() -> Dict[str, str]:
    """Return {key: display_name} for all curated journals, for a picker UI"""
    return {key: g['name'] for key, g in JOURNAL_GUIDELINES.items()}
