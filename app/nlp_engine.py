"""
NLP Engine for Cortex
Handles semantic similarity scoring between a research idea and existing literature
"""

from typing import List, Dict
from app.logger import logger

# scikit-learn is only imported the first time a similarity score is actually
# requested, not at process startup - it's a sizeable dependency (with its
# own numpy/scipy/joblib chain) and most app sessions don't run a literature
# search in every launch, so paying for it upfront would only inflate idle
# memory for no benefit.

STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'should', 'could', 'may', 'might', 'can', 'this', 'that', 'these',
    'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
    'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both',
    'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 'if', 'as',
}


class SemanticAnalyzer:
    """
    Scores how closely a research idea matches existing paper abstracts using
    a TF-IDF vector space model (term frequency-inverse document frequency),
    the standard classical baseline for document similarity, with a small
    boost for shared neuroscience-specific terminology.
    """

    def __init__(self):
        logger.info("SemanticAnalyzer initialized")

    def score_against_corpus(self, idea: str, documents: List[str]) -> List[float]:
        """
        Compute similarity between the idea and each document in one shared
        TF-IDF vector space (required so the scores are actually comparable to
        each other rather than each computed against a different embedding space).

        Args:
            idea (str): The research idea text
            documents (List[str]): Paper title+abstract texts to compare against

        Returns:
            List[float]: TF-IDF cosine similarity scores, one per document
        """
        if not documents:
            return []

        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity as sk_cosine_similarity

        corpus = [idea] + documents

        try:
            vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                sublinear_tf=True,
            )
            tfidf_matrix = vectorizer.fit_transform(corpus)
        except ValueError:
            # Empty vocabulary (e.g. idea/papers contain only stopwords)
            return [0.0] * len(documents)

        idea_vector = tfidf_matrix[0:1]
        doc_vectors = tfidf_matrix[1:]

        similarities = sk_cosine_similarity(idea_vector, doc_vectors)[0]
        return [max(0.0, min(1.0, float(s))) for s in similarities]

    def keyword_overlap(self, text_a: str, text_b: str) -> float:
        """
        Jaccard overlap between the significant (non-stopword) keyword sets of
        two texts. Used as a secondary, more literal-minded signal alongside
        the TF-IDF score since TF-IDF alone can under-weight short overlaps.

        Args:
            text_a (str): First text
            text_b (str): Second text

        Returns:
            float: Jaccard similarity between 0 and 1
        """
        keywords_a = set(self._extract_keywords(text_a))
        keywords_b = set(self._extract_keywords(text_b))

        if not keywords_a or not keywords_b:
            return 0.0

        intersection = keywords_a & keywords_b
        union = keywords_a | keywords_b

        return len(intersection) / len(union) if union else 0.0

    def combined_score(self, idea: str, documents: List[str]) -> List[Dict[str, float]]:
        """
        Compute a blended similarity score for the idea against each document:
        70% TF-IDF cosine similarity + 30% keyword (Jaccard) overlap. Both
        signals are domain-agnostic so this works for any research field.

        Args:
            idea (str): Research idea text
            documents (List[str]): Paper texts to compare against

        Returns:
            List[Dict]: Per-document dict with 'tfidf_score', 'keyword_overlap',
                        and 'combined_score'
        """
        tfidf_scores = self.score_against_corpus(idea, documents)

        results = []
        for doc, tfidf_score in zip(documents, tfidf_scores):
            overlap = self.keyword_overlap(idea, doc)
            combined = min(1.0, 0.7 * tfidf_score + 0.3 * overlap)

            results.append({
                'tfidf_score': tfidf_score,
                'keyword_overlap': overlap,
                'combined_score': combined,
            })

        return results

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract lowercase, non-stopword keywords longer than 2 characters"""
        if not text:
            return []

        words = text.lower().replace('-', ' ').split()
        cleaned = (word.strip('.,;:()[]{}"\'') for word in words)
        return [
            word for word in cleaned
            if word not in STOPWORDS and len(word) > 2 and word.isalpha()
        ]


class TextProcessor:
    """Text processing utilities"""

    @staticmethod
    def clean_text(text: str) -> str:
        """Remove extra whitespace and lowercase for analysis"""
        if not text:
            return ""
        return ' '.join(text.split()).lower()

    @staticmethod
    def truncate_text(text: str, max_length: int = 500) -> str:
        """Truncate text to a maximum length"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
