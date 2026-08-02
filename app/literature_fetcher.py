"""
Literature Fetcher for Cortex
Fetches and aggregates published research from multiple sources, across any
research discipline (Europe PMC covers PubMed/PMC/preprints across all
fields of science and medicine; arXiv covers physics, CS, quantitative
biology, and related quantitative fields).
"""

import json
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional
from datetime import datetime
from app.logger import logger
from app.literature_settings_store import LiteratureSettingsStore


class LiteratureFetcher:
    """
    Fetches and aggregates research papers relevant to a query, regardless
    of research discipline
    """

    def __init__(self, config):
        """
        Initialize literature fetcher

        Args:
            config: Configuration object
        """
        self.config = config
        self.timeout = config.API_TIMEOUT
        self.paper_cache = {}
        self.settings_store = LiteratureSettingsStore(config)
        self._settings = self.settings_store.load()  # refreshed at the top of each fetch_relevant_papers() call
        logger.info("LiteratureFetcher initialized")
    
    def fetch_relevant_papers(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Fetch relevant papers from multiple sources

        Args:
            query (str): Search query
            max_results (int): Maximum number of results

        Returns:
            List[Dict]: List of relevant papers
        """
        logger.info(f"Fetching papers for query: {query}")

        # Re-read on every search (not just at startup) so a key added via
        # the Literature Sources settings panel takes effect immediately,
        # without restarting the app.
        self._settings = self.settings_store.load()

        # Free/public sources - always active.
        fetchers = [
            self._fetch_europepmc,   # PubMed, PMC, bioRxiv/medRxiv preprints (life sciences/medicine)
            self._fetch_arxiv,       # physics, CS, quant-bio, and other quantitative fields
            self._fetch_crossref,    # journal metadata across all disciplines
            self._fetch_eric,        # education research
            self._fetch_semantic_scholar,  # broad multidisciplinary index
            self._fetch_openalex,    # large open scholarly graph, strong humanities/social-science coverage
        ]

        # Paid/keyed sources - only queried if the user has added the corresponding
        # key (via Literature Sources settings, or a .env fallback for dev use).
        if self._settings.get('elsevier_api_key'):
            fetchers.append(self._fetch_elsevier)
        if self._settings.get('wos_api_key'):
            fetchers.append(self._fetch_web_of_science)
        if self._settings.get('ieee_api_key'):
            fetchers.append(self._fetch_ieee)
        if self._settings.get('springer_api_key'):
            fetchers.append(self._fetch_springer)
        if self._settings.get('core_api_key'):
            fetchers.append(self._fetch_core)

        # All fetchers are independent HTTP calls - run them concurrently so
        # total latency is ~max(), not sum(), of however many are active.
        all_papers = []
        with ThreadPoolExecutor(max_workers=len(fetchers)) as executor:
            futures = [executor.submit(fetch, query, max_results) for fetch in fetchers]
            for future in futures:
                all_papers.extend(future.result())

        # Deduplicate papers
        papers = self._deduplicate_papers(all_papers)

        # Only keep papers with enough text to meaningfully compare against
        papers = [p for p in papers if len(p.get('abstract', '')) > 20]

        # Sort by relevance (most recent first)
        papers.sort(
            key=lambda x: x.get('year', 0),
            reverse=True
        )

        logger.info(f"Fetched {len(papers)} unique papers")

        return papers[:max_results]

    def _fetch_europepmc(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Fetch papers from Europe PMC (covers PubMed, PMC, bioRxiv/medRxiv preprints)

        Args:
            query (str): Search query
            max_results (int): Maximum results

        Returns:
            List[Dict]: Europe PMC papers
        """
        try:
            search_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

            params = {
                'query': query,
                'format': 'json',
                'pageSize': max_results,
                'resultType': 'core'
            }

            response = requests.get(
                search_url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            papers = []

            for result in data.get('resultList', {}).get('result', []):
                # authorString ends with a trailing period after the last
                # author's initials (e.g. "...Batterink LJ.") - strip it
                # before splitting so the last author's name isn't corrupted.
                author_string = (result.get('authorString', '') or '').rstrip('.')
                authors = [a.strip() for a in author_string.split(',') if a.strip()][:5]

                source_map = {'MED': 'PubMed', 'PMC': 'PubMed Central', 'PPR': 'Preprint (bioRxiv/medRxiv)'}

                doi = result.get('doi', '')
                paper = {
                    'title': result.get('title', 'Unknown').rstrip('.'),
                    'authors': authors,
                    'abstract': result.get('abstractText', ''),
                    'year': int(result.get('pubYear', 2000)) if result.get('pubYear') else 2000,
                    'source': source_map.get(result.get('source'), result.get('source', 'Europe PMC')),
                    'doi': doi,
                    'url': f'https://doi.org/{doi}' if doi else '',
                }

                papers.append(paper)

            logger.info(f"Fetched {len(papers)} papers from Europe PMC")
            return papers

        except Exception as e:
            logger.error(f"Error fetching from Europe PMC: {str(e)}")
            return []

    def _fetch_crossref(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Fetch paper metadata from CrossRef, which indexes journal articles
        across all research disciplines (not just life sciences) - social
        science, economics, humanities, engineering, physical sciences, etc.

        Args:
            query (str): Search query
            max_results (int): Maximum results

        Returns:
            List[Dict]: CrossRef papers
        """
        try:
            import re

            search_url = "https://api.crossref.org/works"

            params = {
                'query': query,
                'rows': max_results,
                'select': 'title,author,abstract,published,published-print,published-online,DOI,container-title',
            }
            headers = {'User-Agent': 'CortexResearchApp/1.0 (mailto:cortex-app@example.com)'}

            response = requests.get(
                search_url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            papers = []

            for item in data.get('message', {}).get('items', []):
                title_list = item.get('title', [])
                if not title_list:
                    continue

                authors = [
                    f"{a.get('given', '')} {a.get('family', '')}".strip()
                    for a in item.get('author', [])[:5]
                    if a.get('family')
                ]

                date_parts = (
                    item.get('published', {}).get('date-parts')
                    or item.get('published-print', {}).get('date-parts')
                    or item.get('published-online', {}).get('date-parts')
                    or [[2000]]
                )
                year = date_parts[0][0] if date_parts and date_parts[0] else 2000

                # CrossRef abstracts are wrapped in JATS XML tags (<jats:p>...)
                abstract = re.sub(r'<[^>]+>', ' ', item.get('abstract', '') or '')
                abstract = ' '.join(abstract.split())

                doi = item.get('DOI', '')
                paper = {
                    'title': title_list[0],
                    'authors': authors,
                    'abstract': abstract,
                    'year': int(year) if year else 2000,
                    'source': item.get('container-title', ['CrossRef'])[0] if item.get('container-title') else 'CrossRef',
                    'doi': doi,
                    'url': f'https://doi.org/{doi}' if doi else '',
                }

                papers.append(paper)

            logger.info(f"Fetched {len(papers)} papers from CrossRef")
            return papers

        except Exception as e:
            logger.error(f"Error fetching from CrossRef: {str(e)}")
            return []

    def _fetch_arxiv(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Fetch papers from arXiv (physics, CS, quantitative biology, and other
        quantitative research fields)

        Args:
            query (str): Search query
            max_results (int): Maximum results

        Returns:
            List[Dict]: arXiv papers
        """
        try:
            # arXiv API
            search_url = "http://export.arxiv.org/api/query"

            params = {
                'search_query': f'all:({query})',
                'max_results': max_results,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            response = requests.get(
                search_url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse Atom feed
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            papers = []
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                authors_elems = entry.findall('{http://www.w3.org/2005/Atom}author')
                published_elem = entry.find('{http://www.w3.org/2005/Atom}published')
                summary_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
                id_elem = entry.find('{http://www.w3.org/2005/Atom}id')
                
                paper = {
                    'title': title_elem.text if title_elem is not None else 'Unknown',
                    'authors': [
                        author.find('{http://www.w3.org/2005/Atom}name').text
                        for author in authors_elems[:5]
                        if author.find('{http://www.w3.org/2005/Atom}name') is not None
                    ],
                    'abstract': summary_elem.text if summary_elem is not None else '',
                    'year': int(published_elem.text[:4]) if published_elem is not None else 2000,
                    'source': 'arXiv',
                    'url': id_elem.text if id_elem is not None else ''
                }
                
                papers.append(paper)
            
            logger.info(f"Fetched {len(papers)} papers from arXiv")
            return papers

        except Exception as e:
            logger.error(f"Error fetching from arXiv: {str(e)}")
            return []

    def _fetch_eric(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Fetch papers from ERIC (Education Resources Information Center) -
        free, public API covering education research literature.

        Args:
            query (str): Search query
            max_results (int): Maximum results

        Returns:
            List[Dict]: ERIC papers
        """
        try:
            search_url = "https://api.ies.ed.gov/eric/"

            params = {
                'search': query,
                'format': 'json',
                'rows': max_results,
            }

            response = requests.get(search_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            papers = []

            for doc in data.get('response', {}).get('docs', []):
                description = doc.get('description', '')
                if isinstance(description, list):
                    description = ' '.join(description)

                eric_id = doc.get('id', '')
                paper = {
                    'title': doc.get('title', 'Unknown'),
                    'authors': doc.get('author', [])[:5] if isinstance(doc.get('author'), list) else [],
                    'abstract': description or '',
                    'year': int(doc.get('publicationdateyear', 2000)) if doc.get('publicationdateyear') else 2000,
                    'source': 'ERIC',
                    'doi': '',
                    'url': f'https://eric.ed.gov/?id={eric_id}' if eric_id else '',
                }
                papers.append(paper)

            logger.info(f"Fetched {len(papers)} papers from ERIC")
            return papers

        except Exception as e:
            logger.error(f"Error fetching from ERIC: {str(e)}")
            return []

    def _fetch_semantic_scholar(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Fetch papers from Semantic Scholar - broad multidisciplinary index,
        the closest free/legal proxy to Google Scholar's coverage. The
        anonymous tier is rate-limited, so failures here are expected and
        non-fatal; other sources still cover the query.

        Args:
            query (str): Search query
            max_results (int): Maximum results

        Returns:
            List[Dict]: Semantic Scholar papers
        """
        try:
            search_url = "https://api.semanticscholar.org/graph/v1/paper/search"

            params = {
                'query': query,
                'limit': max_results,
                'fields': 'title,abstract,year,authors,externalIds,venue',
            }
            headers = {}
            if self._settings.get('semantic_scholar_api_key'):
                headers['x-api-key'] = self._settings['semantic_scholar_api_key']

            response = requests.get(search_url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            papers = []

            for item in data.get('data', []):
                if not item.get('abstract'):
                    continue

                external_ids = item.get('externalIds') or {}
                doi = external_ids.get('DOI', '')

                paper = {
                    'title': item.get('title', 'Unknown'),
                    'authors': [a.get('name', '') for a in (item.get('authors') or [])[:5]],
                    'abstract': item.get('abstract', ''),
                    'year': item.get('year') or 2000,
                    'source': item.get('venue') or 'Semantic Scholar',
                    'doi': doi,
                    'url': f'https://doi.org/{doi}' if doi else f'https://www.semanticscholar.org/paper/{item.get("paperId", "")}',
                }
                papers.append(paper)

            logger.info(f"Fetched {len(papers)} papers from Semantic Scholar")
            return papers

        except Exception as e:
            logger.warning(f"Semantic Scholar unavailable (often rate-limited without an API key): {str(e)}")
            return []

    def _fetch_openalex(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Fetch papers from OpenAlex - a large, free, keyless open scholarly
        graph (successor to Microsoft Academic Graph) with strong coverage
        outside the life sciences (social science, humanities, engineering).

        Args:
            query (str): Search query
            max_results (int): Maximum results

        Returns:
            List[Dict]: OpenAlex papers
        """
        try:
            search_url = "https://api.openalex.org/works"

            params = {
                'search': query,
                'per_page': max_results,
                'mailto': 'cortex-app@example.com',  # OpenAlex "polite pool" - faster, more reliable responses
            }

            response = requests.get(search_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            papers = []

            for item in data.get('results', []):
                abstract = self._reconstruct_openalex_abstract(item.get('abstract_inverted_index'))
                if not abstract:
                    continue

                authors = [
                    a.get('author', {}).get('display_name', '')
                    for a in (item.get('authorships') or [])[:5]
                ]

                doi = (item.get('doi') or '').replace('https://doi.org/', '')
                source_name = (item.get('primary_location') or {}).get('source') or {}

                paper = {
                    'title': item.get('title') or item.get('display_name') or 'Unknown',
                    'authors': authors,
                    'abstract': abstract,
                    'year': item.get('publication_year') or 2000,
                    'source': source_name.get('display_name', 'OpenAlex'),
                    'doi': doi,
                    'url': item.get('doi') or f"https://openalex.org/{item.get('id', '').rsplit('/', 1)[-1]}",
                }
                papers.append(paper)

            logger.info(f"Fetched {len(papers)} papers from OpenAlex")
            return papers

        except Exception as e:
            logger.error(f"Error fetching from OpenAlex: {str(e)}")
            return []

    @staticmethod
    def _reconstruct_openalex_abstract(inverted_index: Optional[Dict]) -> str:
        """OpenAlex returns abstracts as {word: [positions]} to save space - rebuild the plain text"""
        if not inverted_index:
            return ''

        max_position = max((pos for positions in inverted_index.values() for pos in positions), default=-1)
        words = [''] * (max_position + 1)
        for word, positions in inverted_index.items():
            for pos in positions:
                words[pos] = word

        return ' '.join(words)

    def _fetch_elsevier(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Fetch papers from Scopus + ScienceDirect via the Elsevier API.
        Only called when config.ELSEVIER_API_KEY is set - register free at
        https://dev.elsevier.com.

        Args:
            query (str): Search query
            max_results (int): Maximum results

        Returns:
            List[Dict]: Elsevier (Scopus/ScienceDirect) papers
        """
        try:
            search_url = "https://api.elsevier.com/content/search/scopus"

            headers = {
                'X-ELS-APIKey': self._settings.get('elsevier_api_key', ''),
                'Accept': 'application/json',
            }
            params = {
                'query': query,
                'count': max_results,
            }

            response = requests.get(search_url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            papers = []

            for entry in data.get('search-results', {}).get('entry', []):
                doi = entry.get('prism:doi', '')
                paper = {
                    'title': entry.get('dc:title', 'Unknown'),
                    'authors': [entry.get('dc:creator', '')] if entry.get('dc:creator') else [],
                    'abstract': entry.get('dc:description', ''),
                    'year': int(entry.get('prism:coverDate', '2000')[:4]) if entry.get('prism:coverDate') else 2000,
                    'source': entry.get('prism:publicationName', 'Scopus'),
                    'doi': doi,
                    'url': f'https://doi.org/{doi}' if doi else entry.get('link', [{}])[0].get('@href', ''),
                }
                papers.append(paper)

            logger.info(f"Fetched {len(papers)} papers from Scopus/ScienceDirect")
            return papers

        except Exception as e:
            logger.error(f"Error fetching from Elsevier (Scopus/ScienceDirect): {str(e)}")
            return []

    def _fetch_web_of_science(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Fetch papers from Web of Science. Only called when config.WOS_API_KEY
        is set - requires institutional Clarivate access.

        Args:
            query (str): Search query
            max_results (int): Maximum results

        Returns:
            List[Dict]: Web of Science papers
        """
        try:
            search_url = "https://api.clarivate.com/apis/wos-starter/v1/documents"

            headers = {'X-ApiKey': self._settings.get('wos_api_key', '')}
            params = {
                'q': f'TS=({query})',
                'limit': max_results,
            }

            response = requests.get(search_url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            papers = []

            for doc in data.get('hits', []):
                identifiers = doc.get('identifiers', {}) or {}
                doi = identifiers.get('doi', '')
                names = doc.get('names', {}).get('authors', []) or []

                paper = {
                    'title': doc.get('title', 'Unknown'),
                    'authors': [a.get('displayName', '') for a in names[:5]],
                    'abstract': '',  # WoS Starter API does not return abstracts
                    'year': int(doc.get('source', {}).get('publishYear', 2000) or 2000),
                    'source': doc.get('source', {}).get('sourceTitle', 'Web of Science'),
                    'doi': doi,
                    'url': f'https://doi.org/{doi}' if doi else '',
                }
                papers.append(paper)

            logger.info(f"Fetched {len(papers)} papers from Web of Science")
            return papers

        except Exception as e:
            logger.error(f"Error fetching from Web of Science: {str(e)}")
            return []

    def _fetch_ieee(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Fetch papers from IEEE Xplore. Only called when the user has added
        an IEEE Xplore API key - register free at
        https://developer.ieee.org.

        Args:
            query (str): Search query
            max_results (int): Maximum results

        Returns:
            List[Dict]: IEEE Xplore papers
        """
        try:
            search_url = "http://ieeexploreapi.ieee.org/api/v1/search/articles"
            params = {
                'apikey': self._settings.get('ieee_api_key', ''),
                'querytext': query,
                'max_records': max_results,
                'format': 'json',
            }

            response = requests.get(search_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            papers = []

            for article in data.get('articles', []):
                doi = article.get('doi', '')
                authors = [a.get('full_name', '') for a in (article.get('authors') or {}).get('authors', [])[:5]]
                paper = {
                    'title': article.get('title', 'Unknown'),
                    'authors': authors,
                    'abstract': article.get('abstract', ''),
                    'year': int(article.get('publication_year', 2000) or 2000),
                    'source': article.get('publication_title', 'IEEE Xplore'),
                    'doi': doi,
                    'url': f'https://doi.org/{doi}' if doi else article.get('pdf_url', ''),
                }
                papers.append(paper)

            logger.info(f"Fetched {len(papers)} papers from IEEE Xplore")
            return papers

        except Exception as e:
            logger.error(f"Error fetching from IEEE Xplore: {str(e)}")
            return []

    def _fetch_springer(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Fetch papers from Springer Nature. Only called when the user has
        added a Springer Nature API key - register free at
        https://dev.springernature.com.

        Args:
            query (str): Search query
            max_results (int): Maximum results

        Returns:
            List[Dict]: Springer Nature papers
        """
        try:
            search_url = "http://api.springernature.com/metadata/json"
            params = {
                'q': query,
                'api_key': self._settings.get('springer_api_key', ''),
                'p': max_results,
            }

            response = requests.get(search_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            papers = []

            for record in data.get('records', []):
                doi = record.get('doi', '')
                authors = [c.get('creator', '') for c in record.get('creators', [])[:5]]
                pub_date = record.get('publicationDate', '')
                year = int(pub_date[:4]) if pub_date[:4].isdigit() else 2000
                url_entries = record.get('url', []) or []
                paper = {
                    'title': record.get('title', 'Unknown'),
                    'authors': authors,
                    'abstract': record.get('abstract', ''),
                    'year': year,
                    'source': record.get('publicationName', 'Springer Nature'),
                    'doi': doi,
                    'url': f'https://doi.org/{doi}' if doi else (url_entries[0].get('value', '') if url_entries else ''),
                }
                papers.append(paper)

            logger.info(f"Fetched {len(papers)} papers from Springer Nature")
            return papers

        except Exception as e:
            logger.error(f"Error fetching from Springer Nature: {str(e)}")
            return []

    def _fetch_core(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Fetch papers from CORE (open access aggregator). Only called when
        the user has added a CORE API key - register free at
        https://core.ac.uk/services/api.

        Args:
            query (str): Search query
            max_results (int): Maximum results

        Returns:
            List[Dict]: CORE papers
        """
        try:
            search_url = "https://api.core.ac.uk/v3/search/works"
            headers = {'Authorization': f"Bearer {self._settings.get('core_api_key', '')}"}
            params = {'q': query, 'limit': max_results}

            response = requests.get(search_url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            papers = []

            for result in data.get('results', []):
                doi = result.get('doi', '')
                authors = [a.get('name', '') for a in (result.get('authors') or [])[:5]]
                paper = {
                    'title': result.get('title', 'Unknown'),
                    'authors': authors,
                    'abstract': result.get('abstract', '') or '',
                    'year': int(result.get('yearPublished', 2000) or 2000),
                    'source': result.get('publisher', 'CORE'),
                    'doi': doi,
                    'url': f'https://doi.org/{doi}' if doi else result.get('downloadUrl', ''),
                }
                papers.append(paper)

            logger.info(f"Fetched {len(papers)} papers from CORE")
            return papers

        except Exception as e:
            logger.error(f"Error fetching from CORE: {str(e)}")
            return []

    def _deduplicate_papers(self, papers: List[Dict]) -> List[Dict]:
        """
        Remove duplicate papers
        
        Args:
            papers (List[Dict]): List of papers
        
        Returns:
            List[Dict]: Deduplicated papers
        """
        seen_titles = set()
        unique_papers = []
        
        for paper in papers:
            title = paper.get('title', '').lower().strip()
            
            if title not in seen_titles:
                seen_titles.add(title)
                unique_papers.append(paper)
        
        return unique_papers
