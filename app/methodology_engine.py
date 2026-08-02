"""
Methodology Engine for Cortex
Provides research methodology guidance for any of the 6 general research types,
independent of research discipline.
"""

import json
from typing import Dict, List
from datetime import datetime
from pathlib import Path
from app.logger import logger

GUIDANCE_TEMPLATES = {
    'theoretical': {
        'overview': 'Improve or extend a scientific theory by resolving an internal inconsistency or explanatory gap.',
        'key_considerations': [
            'State precisely which premise or prediction of the existing theory is inconsistent or incomplete',
            'Build a concept map connecting the theory\'s premises, constructs, and existing evidence',
            'Derive hypotheses that would distinguish the revised theory from the original',
            'Check the revised theory for internal logical consistency, not just plausibility',
        ],
        'timeline_estimate': '6-18 months',
        'resources_needed': ['Literature access', 'Domain expert review', 'Logical/formal modeling tools if applicable'],
        'common_pitfalls': [
            'Proposing a revision that is unfalsifiable',
            'Overlooking prior work that already addresses the same inconsistency',
            'Building a framework too vague to generate testable hypotheses',
        ]
    },
    'experimental': {
        'overview': 'Establish a causal relationship by deliberately manipulating an independent variable while controlling others.',
        'key_considerations': [
            'Ensure random assignment to minimize confounding variables',
            'Define a clear hypothesis with independent, dependent, and control variables',
            'Standardize the experimental protocol for reproducibility',
            'Plan for blinding (single-blind or double-blind) when possible',
            'Include appropriate control conditions',
        ],
        'timeline_estimate': '6-24 months',
        'resources_needed': ['Research staff', 'Equipment/materials', 'Statistical expertise', 'Ethics approval if human/animal subjects'],
        'common_pitfalls': [
            'Insufficient sample size leading to low statistical power',
            'Researcher bias affecting results',
            'Inadequate control of confounding variables',
            'Poor documentation of procedures',
        ]
    },
    'exploratory': {
        'overview': 'Investigate a single case in depth to generate insight, then compare it against known generalizations of similar cases.',
        'key_considerations': [
            'Select a case that is information-rich relative to the research question',
            'Triangulate across documents, interviews, and direct evidence',
            'Organize evidence systematically before drawing conclusions',
            'Be explicit about how this case agrees or disagrees with prior generalizations',
        ],
        'timeline_estimate': '3-12 months',
        'resources_needed': ['Access to the case/site', 'Interview or archival protocols', 'Qualitative analysis tools'],
        'common_pitfalls': [
            'Over-generalizing from a single case',
            'Confirmation bias when comparing to known generalizations',
            'Insufficiently documented evidence trail',
        ]
    },
    'pilot': {
        'overview': 'Run a small-cohort feasibility version of a larger planned study to test design, recruitment, and procedures.',
        'key_considerations': [
            'Use the pilot to test feasibility, not to confirm the hypothesis',
            'Standardize the design exactly as it would run at full scale, just smaller',
            'Record recruitment, attrition, and protocol issues encountered',
            'Use pilot results to refine sample size and procedures before the full study',
        ],
        'timeline_estimate': '2-6 months',
        'resources_needed': ['Small participant cohort', 'Same instruments as planned full study', 'Statistical expertise'],
        'common_pitfalls': [
            'Treating pilot results as confirmatory evidence',
            'Under-powered statistical claims from pilot data',
            'Skipping the feasibility questions the pilot was meant to answer',
        ]
    },
    'literature_review': {
        'overview': 'Systematically search, screen, and synthesize existing published research on a defined question.',
        'key_considerations': [
            'Define a clear, bounded research question before searching',
            'Use a reproducible, documented search strategy across databases',
            'Apply explicit inclusion/exclusion criteria when screening',
            'Synthesize findings rather than merely summarizing each paper individually',
        ],
        'timeline_estimate': '2-6 months',
        'resources_needed': ['Database access', 'Screening/extraction spreadsheet or tool', 'A second reviewer for screening if possible'],
        'common_pitfalls': [
            'Non-reproducible or undocumented search strategy',
            'Including low-quality studies without appraisal',
            'Summarizing instead of synthesizing across studies',
        ]
    },
    'clinical': {
        'overview': 'Evaluate the safety, diagnostic accuracy, or efficacy of an intervention in human participants.',
        'key_considerations': [
            'Register the study protocol prospectively where required',
            'Obtain institutional ethics approval before recruitment',
            'Define primary and secondary outcomes clearly in advance',
            'Use validated assessment instruments',
            'Monitor for adverse events continuously throughout the study',
        ],
        'timeline_estimate': '1-5 years depending on phase/scope',
        'resources_needed': ['Clinical site/access to participants', 'Ethics approval', 'Safety monitoring plan', 'Statistical expertise'],
        'common_pitfalls': [
            'Inadequate sample size',
            'Poor participant adherence to intervention',
            'Unblinded outcome assessment',
            'Inadequate safety monitoring or reporting',
        ]
    },
}


class MethodologyEngine:
    """
    Provides methodology guidance for the 6 general research types
    """

    def __init__(self, config):
        self.config = config
        self.research_types = config.RESEARCH_TYPES
        self.research_type_steps = config.RESEARCH_TYPE_STEPS
        self.data_dir = config.DATA_DIR
        self.data_dir.mkdir(exist_ok=True)
        logger.info("MethodologyEngine initialized")

    def get_research_types(self) -> Dict:
        """Get all supported research types with descriptions"""
        return self.research_types

    def select_research_type(self, type_key: str, idea: str) -> Dict:
        """
        Select a research type and return its methodology guidance

        Args:
            type_key (str): Research type key
            idea (str): Original research idea

        Returns:
            Dict: Methodology guidance for the selected research type
        """
        logger.info(f"Selecting research type: {type_key}")

        if type_key not in self.research_types:
            logger.error(f"Invalid research type: {type_key}")
            return {
                'status': 'error',
                'message': f'Invalid research type: {type_key}',
                'valid': False
            }

        research_type = self.research_types[type_key]
        steps = self.research_type_steps.get(type_key, [])

        result = {
            'status': 'success',
            'valid': True,
            'type': type_key,
            'mode': type_key,
            'mode_name': research_type['name'],
            'type_name': research_type['name'],
            'description': research_type['description'],
            'idea': idea,
            'steps': steps,
            'total_steps': len(steps),
            'guidance': GUIDANCE_TEMPLATES.get(type_key, {}),
            'timestamp': datetime.now().isoformat()
        }

        self._save_selection(type_key, idea, steps)

        return result

    def get_step_details(self, type_key: str, step_number: int) -> Dict:
        """Get detail (resources/best practices/common issues) for one step"""
        if type_key not in self.research_type_steps:
            return {'status': 'error', 'message': f'Invalid research type: {type_key}'}

        steps = self.research_type_steps[type_key]

        if step_number < 1 or step_number > len(steps):
            return {
                'status': 'error',
                'message': f'Invalid step number: {step_number}. This research type has {len(steps)} steps.'
            }

        return {
            'status': 'success',
            'type': type_key,
            'step_number': step_number,
            'total_steps': len(steps),
            'step': steps[step_number - 1],
            'resources': ['Reference/citation manager', 'Database access (Google Scholar, discipline-specific databases)'],
            'best_practices': [
                'Document all decisions and rationale',
                'Follow established guidelines and standards for your discipline',
                'Consult with domain experts',
                'Plan for reproducibility from the start',
                'Maintain detailed records as you go',
            ],
            'common_issues': [
                'Inadequate literature review leading to missed prior work',
                'Unclear or overly ambitious research question',
                'Poor specification of variables or case boundaries',
                'Insufficient time allocated for planning',
            ]
        }

    def _save_selection(self, type_key: str, idea: str, steps: List[str]):
        """Append a methodology selection to a local history log"""
        selection = {
            'timestamp': datetime.now().isoformat(),
            'type': type_key,
            'idea': idea,
            'steps_count': len(steps)
        }

        history_file = self.data_dir / 'methodology_history.jsonl'

        try:
            with open(history_file, 'a') as f:
                f.write(json.dumps(selection) + '\n')
            logger.debug("Methodology selection saved")
        except Exception as e:
            logger.error(f"Failed to save methodology selection: {str(e)}")
