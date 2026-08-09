"""
Systematic-review screening and PRISMA flow counts.

Implements the two-stage screening every systematic review runs on:

  1. Title/abstract screening - fast pass over everything identified.
  2. Full-text eligibility - the survivors, read properly, with a recorded
     reason for each exclusion (PRISMA requires reasons at this stage).

Screening state lives on the paper record itself (a 'screening' key) rather
than in a parallel collection, so a paper and its decision can't get out of
sync, and exporting the project carries the review state with it.

The counts that genuinely can't be derived from the library - duplicates
removed by your reference manager before import, records removed by
automation tools, reports you couldn't obtain - are stored per project in
screening.json, because only the reviewer knows them.

Reference: PRISMA 2020 statement (Page et al., BMJ 2021), the flow diagram
in Figure 1.
"""

from typing import Dict, List

STAGES = ('title_abstract', 'full_text')
DECISIONS = ('pending', 'include', 'exclude')

# Exclusion reasons at full-text stage. PRISMA wants these reported with
# counts, so they're a fixed list plus free text rather than only free text -
# otherwise you get 40 spellings of "wrong population" and can't total them.
COMMON_EXCLUSION_REASONS = [
    'Wrong population',
    'Wrong intervention/exposure',
    'Wrong comparator',
    'Wrong outcomes',
    'Wrong study design',
    'Wrong publication type',
    'Duplicate record',
    'Full text not in an accessible language',
    'Insufficient data reported',
    'Other',
]

# Manual counts the library can't know about. Keys match PRISMA 2020 boxes.
MANUAL_COUNT_FIELDS = [
    ('duplicates_removed', 'Duplicate records removed before screening'),
    ('removed_ineligible_automation', 'Records marked ineligible by automation tools'),
    ('removed_other', 'Records removed for other reasons'),
    ('registers_identified', 'Records identified from registers'),
    ('other_sources_identified', 'Records identified from other sources (citation searching, etc.)'),
    ('reports_not_retrieved', 'Reports sought for retrieval but not retrieved'),
]


def default_state() -> Dict:
    return {
        'enabled': False,
        'review_question': '',
        'inclusion_criteria': '',
        'exclusion_criteria': '',
        'counts': {key: 0 for key, _ in MANUAL_COUNT_FIELDS},
    }


def paper_screening(paper: Dict) -> Dict:
    """Screening state for a paper, defaulting to 'not yet screened'."""
    state = paper.get('screening') or {}
    return {
        'stage': state.get('stage', 'title_abstract'),
        'decision': state.get('decision', 'pending'),
        'reason': state.get('reason', ''),
        'notes': state.get('notes', ''),
        'decided_at': state.get('decided_at', ''),
    }


def apply_decision(paper: Dict, decision: str, reason: str = '', notes: str = '') -> Dict:
    """
    Record a screening decision and work out what stage the paper is now in.

    Including at title/abstract doesn't finish the paper - it promotes it to
    full-text review, still pending. That two-step promotion is what makes the
    PRISMA middle boxes ("sought for retrieval", "assessed for eligibility")
    mean anything.
    """
    from datetime import datetime

    if decision not in DECISIONS:
        raise ValueError(f'Unknown decision: {decision}')

    current = paper_screening(paper)
    stage = current['stage']

    if decision == 'include' and stage == 'title_abstract':
        return {
            'stage': 'full_text',
            'decision': 'pending',
            'reason': '',
            'notes': notes or current['notes'],
            'decided_at': datetime.now().isoformat(),
        }

    return {
        'stage': stage,
        'decision': decision,
        'reason': reason if decision == 'exclude' else '',
        'notes': notes or current['notes'],
        'decided_at': datetime.now().isoformat(),
    }


def reset_decision(paper: Dict) -> Dict:
    """Send a paper back to the start of screening."""
    return {'stage': 'title_abstract', 'decision': 'pending', 'reason': '', 'notes': paper_screening(paper)['notes'], 'decided_at': ''}


def compute_prisma(papers: List[Dict], state: Dict) -> Dict:
    """
    Build every number in the PRISMA 2020 flow diagram.

    Derived from the library wherever possible so the diagram can't disagree
    with the actual screening decisions; only the boxes the library genuinely
    can't know are read from the manually-entered counts.
    """
    counts = {**{key: 0 for key, _ in MANUAL_COUNT_FIELDS}, **(state.get('counts') or {})}

    def as_int(value):
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return 0

    counts = {k: as_int(v) for k, v in counts.items()}

    screened_papers = [p for p in papers]
    identified_db = len(screened_papers)

    excluded_ta = 0
    excluded_ft = 0
    included = 0
    pending_ta = 0
    pending_ft = 0
    exclusion_reasons: Dict[str, int] = {}

    for paper in screened_papers:
        s = paper_screening(paper)
        if s['stage'] == 'title_abstract':
            if s['decision'] == 'exclude':
                excluded_ta += 1
            else:
                pending_ta += 1
        else:  # full_text
            if s['decision'] == 'exclude':
                excluded_ft += 1
                reason = s['reason'] or 'Reason not given'
                exclusion_reasons[reason] = exclusion_reasons.get(reason, 0) + 1
            elif s['decision'] == 'include':
                included += 1
            else:
                pending_ft += 1

    # Everything that reached full-text review, whatever happened next.
    reached_full_text = excluded_ft + included + pending_ft
    sought_for_retrieval = reached_full_text + counts['reports_not_retrieved']

    # The library holds records that survived de-duplication - Cortex's own
    # importer drops duplicates on the way in, and a reference manager will
    # have done the same before that. So the library size *is* the number
    # screened, and "identified" has to add the removed records back on;
    # deriving it the other way round produces a diagram whose boxes don't
    # add up (screened < excluded + still-pending), which is worse than no
    # diagram at all in a manuscript.
    removed_before_screening = (
        counts['duplicates_removed'] + counts['removed_ineligible_automation'] + counts['removed_other']
    )
    screened = len(screened_papers)
    identified_total = screened + removed_before_screening

    # Records the reviewer says came from registers/other sources are part of
    # that total, not extra on top of it; the rest are attributed to databases.
    from_registers = min(counts['registers_identified'], identified_total)
    from_other = min(counts['other_sources_identified'], identified_total - from_registers)
    from_databases = identified_total - from_registers - from_other

    return {
        'identified_databases': from_databases,
        'identified_registers': from_registers,
        'identified_other': from_other,
        'identified_total': identified_total,
        'duplicates_removed': counts['duplicates_removed'],
        'removed_ineligible_automation': counts['removed_ineligible_automation'],
        'removed_other': counts['removed_other'],
        'records_screened': screened,
        'records_excluded': excluded_ta,
        'reports_sought': sought_for_retrieval,
        'reports_not_retrieved': counts['reports_not_retrieved'],
        'reports_assessed': reached_full_text,
        'reports_excluded': excluded_ft,
        'exclusion_reasons': sorted(
            [{'reason': r, 'count': c} for r, c in exclusion_reasons.items()],
            key=lambda x: (-x['count'], x['reason']),
        ),
        'studies_included': included,
        'pending_title_abstract': pending_ta,
        'pending_full_text': pending_ft,
        'total_papers': identified_db,
    }


def screening_summary(papers: List[Dict]) -> Dict:
    """Progress counters for the screening UI."""
    prisma_like = {'title_abstract': {'pending': 0, 'exclude': 0}, 'full_text': {'pending': 0, 'include': 0, 'exclude': 0}}
    for paper in papers:
        s = paper_screening(paper)
        bucket = prisma_like[s['stage']]
        bucket[s['decision']] = bucket.get(s['decision'], 0) + 1
    return prisma_like
