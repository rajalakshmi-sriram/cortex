"""
Citation Formatter for Cortex
Formats saved papers into common citation styles (for copy/paste elsewhere)
and exports the whole Paper Library as a .bib file for LaTeX/reference
managers. Purely mechanical string formatting - no AI involved.
"""

import re
from typing import Dict, List

CITATION_STYLES = ['apa', 'mla', 'chicago', 'vancouver', 'bibtex']


def _parse_name(name: str) -> tuple:
    """
    Split a name into (last_name, initials), handling both conventions our
    sources return: "First Middle Last" (CrossRef, arXiv, OpenAlex, Semantic
    Scholar) and PubMed/Europe PMC's compact "Last II" form (e.g.
    "Sabaghypour S", "Batterink LJ") where the final token is bare initials.
    """
    # Europe PMC's authorString often ends the whole list with a trailing
    # period after the final author's initials (e.g. "Batterink LJ.") -
    # strip it before splitting so it doesn't corrupt the last name/initials
    # detection below.
    parts = name.strip().rstrip('.').split()
    if not parts:
        return ('Unknown', '')
    if len(parts) == 1:
        return (parts[0], '')

    last_token = parts[-1]
    if last_token.isalpha() and last_token.isupper() and len(last_token) <= 3:
        # PubMed-style: "Farkhondeh Tale Navi F" -> last="Farkhondeh Tale Navi", initials="F."
        last = ' '.join(parts[:-1])
        initials = '.'.join(list(last_token)) + '.'
    else:
        # "First Middle Last" -> last="Last", initials="F.M."
        last = last_token
        initials = ' '.join(f"{p[0]}." for p in parts[:-1] if p)

    return (last, initials)


def _display_name(name: str) -> str:
    """Render a name as 'Last, F.' regardless of which convention it came in as"""
    last, initials = _parse_name(name)
    return f"{last}, {initials}" if initials else last


def _authors_apa(authors: List[str]) -> str:
    if not authors:
        return 'Unknown Author'
    formatted = [_display_name(name) for name in authors]
    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) <= 20:
        return ', '.join(formatted[:-1]) + ', & ' + formatted[-1]
    return ', '.join(formatted[:19]) + ', ... ' + formatted[-1]


def _authors_mla(authors: List[str]) -> str:
    if not authors:
        return 'Unknown Author'

    def mla_name(name):
        last, initials = _parse_name(name)
        return f"{last}, {initials}" if initials else last

    if len(authors) == 1:
        return mla_name(authors[0])
    if len(authors) == 2:
        return f"{mla_name(authors[0])}, and {authors[1]}"
    return f"{mla_name(authors[0])}, et al"


def _authors_vancouver(authors: List[str]) -> str:
    if not authors:
        return 'Unknown Author'
    formatted = []
    for name in authors[:6]:
        last, initials = _parse_name(name)
        formatted.append(f"{last} {initials.replace('.', '')}" if initials else last)
    result = ', '.join(formatted)
    if len(authors) > 6:
        result += ', et al'
    return result


def format_citation(paper: Dict, style: str) -> str:
    """
    Format a single saved paper into the requested citation style.

    Args:
        paper (Dict): a paper record (title, authors, year, source, doi, url)
        style (str): one of CITATION_STYLES

    Returns:
        str: the formatted citation
    """
    title = paper.get('title', 'Untitled')
    authors_raw = paper.get('authors', '')
    authors = [a.strip() for a in authors_raw.split(',')] if isinstance(authors_raw, str) else (authors_raw or [])
    year = paper.get('year', 'n.d.')
    source = paper.get('source', '')
    doi = paper.get('doi', '')
    doi_str = f"https://doi.org/{doi}" if doi and not str(doi).startswith('http') else doi

    if style == 'apa':
        cite = f"{_authors_apa(authors)} ({year}). {title}."
        if source:
            cite += f" {source}."
        if doi_str:
            cite += f" {doi_str}"
        return cite

    if style == 'mla':
        cite = f"{_authors_mla(authors)}. \"{title}.\""
        if source:
            cite += f" {source},"
        cite += f" {year}."
        if doi_str:
            cite += f" {doi_str}."
        return cite

    if style == 'chicago':
        cite = f"{_authors_apa(authors)}. \"{title}.\""
        if source:
            cite += f" {source}"
        cite += f" ({year})."
        if doi_str:
            cite += f" {doi_str}."
        return cite

    if style == 'vancouver':
        cite = f"{_authors_vancouver(authors)}. {title}."
        if source:
            cite += f" {source}."
        cite += f" {year}."
        if doi_str:
            cite += f" Available from: {doi_str}"
        return cite

    if style == 'bibtex':
        return _to_bibtex_entry(paper)

    raise ValueError(f"Unknown citation style: {style}")


def _bibtex_key(paper: Dict) -> str:
    authors_raw = paper.get('authors', '')
    authors = [a.strip() for a in authors_raw.split(',')] if isinstance(authors_raw, str) else (authors_raw or [])
    first_author_last = _parse_name(authors[0])[0] if authors else 'Unknown'
    first_author_last = re.sub(r'[^A-Za-z]', '', first_author_last) or 'Unknown'
    year = paper.get('year', 'nd')
    title_word = re.sub(r'[^A-Za-z]', '', (paper.get('title', '').split() or ['ref'])[0])
    return f"{first_author_last}{year}{title_word}"


def _to_bibtex_entry(paper: Dict) -> str:
    key = _bibtex_key(paper)
    title = paper.get('title', 'Untitled').replace('{', '').replace('}', '')
    authors_raw = paper.get('authors', '')
    authors = [a.strip() for a in authors_raw.split(',')] if isinstance(authors_raw, str) else (authors_raw or [])
    authors_bibtex = ' and '.join(authors) if authors else 'Unknown'
    year = paper.get('year', '')
    source = paper.get('source', '')
    doi = paper.get('doi', '')
    url = paper.get('url', '')

    entry_type = 'article'
    fields = [
        f'  title = {{{title}}}',
        f'  author = {{{authors_bibtex}}}',
        f'  year = {{{year}}}',
    ]
    if source:
        fields.append(f'  journal = {{{source}}}')
    if doi:
        fields.append(f'  doi = {{{doi}}}')
    if url:
        fields.append(f'  url = {{{url}}}')

    return f"@{entry_type}{{{key},\n" + ',\n'.join(fields) + "\n}"


def papers_to_bibtex(papers: List[Dict]) -> str:
    """Export a whole paper list as one .bib file's contents"""
    entries = [_to_bibtex_entry(p) for p in papers]
    return '\n\n'.join(entries) + '\n'
