"""
Idea Validation Engine for Cortex
Validates research ideas for novelty against existing published literature,
across any research discipline.
"""

import json
from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path
from app.logger import logger
from app.nlp_engine import SemanticAnalyzer
from app.literature_fetcher import LiteratureFetcher


class IdeaValidator:
    """
    Validates research ideas for uniqueness and relevance
    """

    def __init__(self, config):
        """
        Initialize idea validator

        Args:
            config: Configuration object
        """
        self.config = config
        self.semantic_analyzer = SemanticAnalyzer()
        self.literature_fetcher = LiteratureFetcher(config)
        self.validation_history = []
        self.data_dir = config.DATA_DIR
        self.data_dir.mkdir(exist_ok=True)
        
    def validate_idea(self, idea: str) -> Dict:
        """
        Validate a research idea for uniqueness and relevance
        
        Args:
            idea (str): The research idea to validate
        
        Returns:
            Dict: Validation result with status, similarity scores, and recommendations
        """
        logger.info(f"Validating idea: {idea[:100]}...")
        
        # 1. Input validation
        validation_input = self._validate_input(idea)
        if not validation_input['valid']:
            return {
                'status': 'invalid',
                'message': validation_input['message'],
                'valid': False
            }
        
        # 2. Fetch existing literature
        logger.info("Fetching existing research literature...")
        papers = self.literature_fetcher.fetch_relevant_papers(idea)
        
        if not papers:
            return {
                'status': 'unique',
                'message': 'Congratulations! Your idea appears to be unique. No similar research found in current databases.',
                'valid': True,
                'papers': [],
                'similarity_score': 0.0
            }
        
        # 3. Calculate semantic similarity
        logger.info(f"Analyzing similarity with {len(papers)} papers...")
        similarity_results = self._calculate_similarity(idea, papers)
        
        # 4. Determine if idea is duplicate/similar
        result = self._determine_uniqueness(idea, similarity_results)
        
        # 5. Save validation history
        self._save_validation_history(idea, result)
        
        return result
    
    def _validate_input(self, idea: str) -> Dict:
        """
        Validate input idea format and length
        
        Args:
            idea (str): Input idea
        
        Returns:
            Dict: Validation status
        """
        if not idea or not isinstance(idea, str):
            return {
                'valid': False,
                'message': 'Idea must be a non-empty string'
            }
        
        idea_length = len(idea.strip())
        if idea_length < self.config.MIN_IDEA_LENGTH:
            return {
                'valid': False,
                'message': f'Idea must be at least {self.config.MIN_IDEA_LENGTH} characters long'
            }
        
        if idea_length > self.config.MAX_IDEA_LENGTH:
            return {
                'valid': False,
                'message': f'Idea must not exceed {self.config.MAX_IDEA_LENGTH} characters. Current length: {idea_length}'
            }
        
        return {'valid': True}
    
    def _calculate_similarity(self, idea: str, papers: List[Dict]) -> List[Dict]:
        """
        Calculate similarity between idea and papers using a blended metric:
        TF-IDF cosine similarity (captures overall topical/semantic overlap)
        plus keyword Jaccard overlap (captures literal shared terminology),
        with a small bonus for shared neuroscience-specific vocabulary.

        Args:
            idea (str): Research idea
            papers (List[Dict]): List of research papers

        Returns:
            List[Dict]: Similarity scores for each paper, sorted descending
        """
        paper_texts = [
            f"{paper.get('title', '')}. {paper.get('abstract', '')}"
            for paper in papers
        ]

        scores = self.semantic_analyzer.combined_score(idea, paper_texts)

        results = []
        for paper, score in zip(papers, scores):
            results.append({
                'paper': paper,
                'similarity_score': score['combined_score'],
                'tfidf_score': score['tfidf_score'],
                'keyword_overlap': score['keyword_overlap'],
                'title': paper.get('title', ''),
                'authors': paper.get('authors', []),
                'year': paper.get('year', ''),
                'doi': paper.get('doi', ''),
                'url': paper.get('url', ''),
                'source': paper.get('source', '')
            })

        results.sort(key=lambda x: x['similarity_score'], reverse=True)

        return results
    
    def _determine_uniqueness(self, idea: str, similarity_results: List[Dict]) -> Dict:
        """
        Determine if idea is unique or duplicate based on similarity scores
        
        Args:
            idea (str): Research idea
            similarity_results (List[Dict]): Similarity analysis results
        
        Returns:
            Dict: Uniqueness determination
        """
        if not similarity_results:
            return {
                'status': 'unique',
                'message': 'Congratulations! Your idea appears to be unique.',
                'valid': True,
                'papers': [],
                'similarity_score': 0.0,
                'confidence': 'No comparable literature found'
            }

        top_result = similarity_results[0]
        max_similarity = top_result['similarity_score']

        # Thresholds calibrated empirically against real fetched literature
        # across multiple disciplines (neuroscience, biology, economics,
        # climate science). combined_score (0.7 * TF-IDF cosine + 0.3 *
        # keyword Jaccard overlap) is naturally lower for a short idea
        # compared against long abstracts, and the achievable ceiling varies
        # by field, so these thresholds are intentionally conservative.
        DUPLICATE_THRESHOLD = 0.18
        MODERATE_THRESHOLD = 0.08

        # Surface all fetched papers worth reviewing/tracking (not just a top-5
        # preview), so the researcher can save the full relevant set to their library.
        MAX_TRACKED_PAPERS = 20

        if max_similarity >= DUPLICATE_THRESHOLD:
            similar_papers = [
                r for r in similarity_results
                if r['similarity_score'] >= MODERATE_THRESHOLD
            ]

            return {
                'status': 'similar',
                'message': (
                    f'Your idea closely overlaps with existing research. '
                    f'Maximum similarity score: {max_similarity:.1%}. '
                    f'Please refine your idea to be more specific and differentiated.'
                ),
                'valid': False,
                'confidence': 'High overlap detected',
                'similar_papers': similar_papers[:MAX_TRACKED_PAPERS],
                'max_similarity_score': max_similarity,
                'top_match_breakdown': {
                    'tfidf_score': top_result['tfidf_score'],
                    'keyword_overlap': top_result['keyword_overlap'],
                },
                'next_action': 'Please refine your idea and try again'
            }

        else:
            related_papers = similarity_results[:MAX_TRACKED_PAPERS]
            confidence = (
                'Moderate overlap found - review related work below'
                if max_similarity >= MODERATE_THRESHOLD
                else 'Low overlap - idea appears novel'
            )

            return {
                'status': 'unique',
                'message': 'Congratulations! Your idea appears to be unique. We found some related research that may be of interest.',
                'valid': True,
                'confidence': confidence,
                'related_papers': related_papers,
                'max_similarity_score': max_similarity,
                'top_match_breakdown': {
                    'tfidf_score': top_result['tfidf_score'],
                    'keyword_overlap': top_result['keyword_overlap'],
                },
                'next_action': 'Proceed to methodology selection'
            }
    
    def _save_validation_history(self, idea: str, result: Dict):
        """
        Save validation history to file
        
        Args:
            idea (str): Research idea
            result (Dict): Validation result
        """
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'idea': idea,
            'status': result.get('status'),
            'similarity_score': result.get('max_similarity_score', 0),
            'message': result.get('message')
        }
        
        self.validation_history.append(history_entry)
        
        # Save to file
        history_file = self.data_dir / 'validation_history.jsonl'
        try:
            with open(history_file, 'a') as f:
                f.write(json.dumps(history_entry) + '\n')
            logger.debug(f"Validation history saved to {history_file}")
        except Exception as e:
            logger.error(f"Failed to save validation history: {str(e)}")
    
    def get_validation_history(self) -> List[Dict]:
        """
        Get validation history
        
        Returns:
            List[Dict]: List of validation history entries
        """
        return self.validation_history
