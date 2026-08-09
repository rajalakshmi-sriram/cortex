"""
Reference-manager import for Cortex.

Reads BibTeX (.bib) and RIS (.ris) exports - the two formats every reference
manager can produce (Zotero, Mendeley, EndNote, Papers, JabRef) - and turns
them into the same paper dicts the Paper Library already stores, so an
existing library can be brought in without re-finding every paper by hand.

This is the mirror image of app/citation_formatter.py, which writes these
same two formats out.

Deliberately dependency-free: both formats are simple enough to parse
directly, and adding a parser library for this would be a lot of surface
area for very little gain.
"""

import re
from typing import Dict, List, Tuple

from app.logger import logger

# BibTeX escapes/among-braces markup we can safely flatten to plain text.
_LATEX_REPLACEMENTS = [
    (r'\\&', '&'), (r'\\%', '%'), (r'\\_', '_'), (r'\\\$', '$'), (r'\\#', '#'),
    (r'\\textendash\s*', '-'), (r'\\textemdash\s*', '-'),
    (r'---', '-'), (r'--', '-'),
    (r'\\"\{?([aeiouAEIOU])\}?', r'\1'),   # umlaut
    (r"\\'\{?([a-zA-Z])\}?", r'\1'),        # acute
    (r'\\`\{?([a-zA-Z])\}?', r'\1'),        # grave
    (r'\\\^\{?([a-zA-Z])\}?', r'\1'),       # circumflex
    (r'\\~\{?([a-zA-Z])\}?', r'\1'),        # tilde
    (r'\\c\{?([a-zA-Z])\}?', r'\1'),        # cedilla
]

# RIS type codes -> whether we treat the entry as a journal article. Anything
# not listed still imports; this only informs the 'source' fallback.
_RIS_TYPE_NAMES = {
    'JOUR': 'Journal Article', 'BOOK': 'Book', 'CHAP': 'Book Chapter',
    'CONF': 'Conference Paper', 'CPAPER': 'Conference Paper', 'THES': 'Thesis',
    'RPRT': 'Report', 'UNPB': 'Unpublished', 'ELEC': 'Web Page',
    'GEN': 'Generic', 'MGZN': 'Magazine Article', 'NEWS': 'Newspaper Article',
    'PAT': 'Patent', 'ABST': 'Abstract',
}


class CitationParseError(Exception):
    """Raised when a file can't be understood as BibTeX or RIS at all."""


def _clean_latex(value: str) -> str:
    text = value or ''
    for pattern, replacement in _LATEX_REPLACEMENTS:
        text = re.sub(pattern, replacement, text)
    # Braces in BibTeX protect capitalisation ({DNA}); the text is what matters.
    text = text.replace('{', '').replace('}', '')
    return re.sub(r'\s+', ' ', text).strip()


def _year_from(value: str) -> str:
    match = re.search(r'(1[5-9]\d{2}|20\d{2}|21\d{2})', value or '')
    return match.group(1) if match else ''


def _normalize_doi(value: str) -> str:
    doi = (value or '').strip()
    # Reference managers variously store bare DOIs, doi: prefixes, or full URLs.
    doi = re.sub(r'^(https?://)?(dx\.)?doi\.org/', '', doi, flags=re.I)
    doi = re.sub(r'^doi:\s*', '', doi, flags=re.I)
    return doi.strip()


# ---------------- BibTeX ----------------

def _split_bibtex_entries(text: str) -> List[Tuple[str, str]]:
    """
    Yield (entry_type, body) for each @type{...} entry, tracking brace depth
    so that braces inside field values don't end the entry early.
    """
    entries = []
    for match in re.finditer(r'@(\w+)\s*[{(]', text):
        entry_type = match.group(1).lower()
        if entry_type in ('comment', 'preamble', 'string'):
            continue

        start = match.end()
        depth = 1
        i = start
        while i < len(text) and depth > 0:
            char = text[i]
            if char == '\\':          # skip escaped char
                i += 2
                continue
            if char in '{(':
                depth += 1
            elif char in '})':
                depth -= 1
            i += 1
        entries.append((entry_type, text[start:i - 1]))
    return entries


def _parse_bibtex_fields(body: str) -> Dict[str, str]:
    """
    Pull key = value pairs out of one entry body. Values may be brace-wrapped,
    quote-wrapped, or bare (numbers), and may themselves contain braces.
    """
    fields: Dict[str, str] = {}
    i = 0
    # Skip the citation key (everything up to the first comma).
    first_comma = body.find(',')
    if first_comma != -1:
        fields['_key'] = body[:first_comma].strip()
        i = first_comma + 1

    while i < len(body):
        eq = body.find('=', i)
        if eq == -1:
            break
        name = body[i:eq].strip().strip(',').lower()
        j = eq + 1
        while j < len(body) and body[j].isspace():
            j += 1
        if j >= len(body):
            break

        if body[j] == '{':
            depth = 1
            k = j + 1
            while k < len(body) and depth > 0:
                if body[k] == '\\':
                    k += 2
                    continue
                if body[k] == '{':
                    depth += 1
                elif body[k] == '}':
                    depth -= 1
                k += 1
            value = body[j + 1:k - 1]
            i = k
        elif body[j] == '"':
            k = j + 1
            while k < len(body) and body[k] != '"':
                if body[k] == '\\':
                    k += 1
                k += 1
            value = body[j + 1:k]
            i = k + 1
        else:
            k = j
            while k < len(body) and body[k] != ',':
                k += 1
            value = body[j:k]
            i = k

        if name:
            fields[name] = _clean_latex(value)

        next_comma = body.find(',', i)
        i = next_comma + 1 if next_comma != -1 else len(body)

    return fields


def _bibtex_authors(raw: str) -> str:
    """
    BibTeX separates authors with ' and ', and each may be "Last, First" or
    "First Last". Normalise to a comma-separated "First Last" list, which is
    the shape the rest of Cortex (and citation_formatter) expects.
    """
    if not raw:
        return ''
    names = []
    for part in re.split(r'\s+and\s+', raw, flags=re.I):
        part = part.strip().rstrip(',')
        if not part:
            continue
        if ',' in part:
            last, _, first = part.partition(',')
            names.append(f'{first.strip()} {last.strip()}'.strip())
        else:
            names.append(part)
    return ', '.join(names)


def parse_bibtex(text: str) -> List[Dict]:
    papers = []
    for entry_type, body in _split_bibtex_entries(text):
        f = _parse_bibtex_fields(body)
        title = f.get('title', '')
        if not title:
            continue

        source = (
            f.get('journal') or f.get('booktitle') or f.get('publisher')
            or f.get('school') or f.get('institution') or entry_type.title()
        )

        papers.append({
            'title': title,
            'authors': _bibtex_authors(f.get('author', '') or f.get('editor', '')),
            'year': _year_from(f.get('year', '') or f.get('date', '')),
            'source': source,
            'doi': _normalize_doi(f.get('doi', '')),
            'url': f.get('url', '') or f.get('link', ''),
            'abstract': f.get('abstract', ''),
            'volume': f.get('volume', ''),
            'issue': f.get('number', '') or f.get('issue', ''),
            'pages': f.get('pages', ''),
            'keywords': f.get('keywords', ''),
        })
    return papers


# ---------------- RIS ----------------

def parse_ris(text: str) -> List[Dict]:
    """
    RIS is line-oriented: 'XX  - value', with ER marking end of record.
    Repeated tags (AU, KW) accumulate; continuation lines append to the
    previous tag's value.
    """
    papers = []
    current: Dict[str, List[str]] = {}

    def flush():
        if not current:
            return
        title = _first(current, 'TI', 'T1', 'CT', 'BT')
        if not title:
            current.clear()
            return

        entry_type = _first(current, 'TY') or 'GEN'
        source = (
            _first(current, 'JO', 'JF', 'T2', 'JA', 'PB')
            or _RIS_TYPE_NAMES.get(entry_type, 'Unknown')
        )
        year = _year_from(_first(current, 'PY', 'Y1', 'DA'))

        papers.append({
            'title': title,
            'authors': ', '.join(_normalize_ris_name(a) for a in current.get('AU', []) or current.get('A1', [])),
            'year': year,
            'source': source,
            'doi': _normalize_doi(_first(current, 'DO', 'DI')),
            'url': _first(current, 'UR', 'L1'),
            'abstract': _first(current, 'AB', 'N2'),
            'volume': _first(current, 'VL'),
            'issue': _first(current, 'IS'),
            'pages': _ris_pages(current),
            'keywords': ', '.join(current.get('KW', [])),
        })
        current.clear()

    last_tag = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue

        match = re.match(r'^([A-Z][A-Z0-9])\s{2}-\s?(.*)$', line)
        if match:
            tag, value = match.group(1), match.group(2).strip()
            if tag == 'ER':
                flush()
                last_tag = None
                continue
            current.setdefault(tag, []).append(value)
            last_tag = tag
        elif last_tag and current.get(last_tag):
            # Continuation of the previous field (wrapped abstract, etc.)
            current[last_tag][-1] += ' ' + line.strip()

    flush()  # tolerate a final record with no ER
    return papers


def _first(record: Dict[str, List[str]], *tags: str) -> str:
    for tag in tags:
        values = record.get(tag)
        if values and values[0]:
            return values[0].strip()
    return ''


def _ris_pages(record: Dict[str, List[str]]) -> str:
    start, end = _first(record, 'SP'), _first(record, 'EP')
    if start and end:
        return f'{start}-{end}'
    return start or end or ''


def _normalize_ris_name(name: str) -> str:
    """RIS names are 'Last, First M.' - flip to 'First M. Last'."""
    name = name.strip().rstrip(',')
    if ',' in name:
        last, _, first = name.partition(',')
        return f'{first.strip()} {last.strip()}'.strip()
    return name


# ---------------- dispatch ----------------

def detect_format(text: str, filename: str = '') -> str:
    lowered = (filename or '').lower()
    if lowered.endswith('.bib') or lowered.endswith('.bibtex'):
        return 'bibtex'
    if lowered.endswith('.ris') or lowered.endswith('.nbib') or lowered.endswith('.enw'):
        return 'ris'

    # Fall back to sniffing the content, so a correctly-formatted file with an
    # unexpected extension still imports.
    if re.search(r'^\s*@\w+\s*[{(]', text, re.M):
        return 'bibtex'
    if re.search(r'^\s*(TY|T1|TI|AU)\s{2}-\s', text, re.M):
        return 'ris'
    return ''


def parse_references(text: str, filename: str = '') -> Tuple[List[Dict], str]:
    """
    Parse a reference-manager export into paper dicts.

    Returns (papers, format_name). Raises CitationParseError if the file is
    neither format, or parses to zero usable entries.
    """
    fmt = detect_format(text, filename)
    if fmt == 'bibtex':
        papers = parse_bibtex(text)
    elif fmt == 'ris':
        papers = parse_ris(text)
    else:
        raise CitationParseError(
            "Couldn't recognise this file as BibTeX or RIS. Export from your "
            'reference manager as .bib or .ris and try again.'
        )

    if not papers:
        raise CitationParseError(
            f'That looks like a {fmt.upper()} file, but no entries with a title could be read from it.'
        )

    logger.info(f'Parsed {len(papers)} reference(s) from {fmt} import')
    return papers, fmt


def dedupe_against(papers: List[Dict], existing: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Split incoming papers into (new, duplicates) by DOI first, then by
    normalised title. Importing a library you've partly saved already is the
    normal case, not an edge case, so this matters.
    """
    def title_key(p):
        return re.sub(r'[^a-z0-9]+', '', (p.get('title') or '').lower())

    seen_dois = {_normalize_doi(p.get('doi', '')).lower() for p in existing if p.get('doi')}
    seen_titles = {title_key(p) for p in existing if p.get('title')}

    new, duplicates = [], []
    for paper in papers:
        doi = _normalize_doi(paper.get('doi', '')).lower()
        tkey = title_key(paper)
        if (doi and doi in seen_dois) or (tkey and tkey in seen_titles):
            duplicates.append(paper)
            continue
        new.append(paper)
        if doi:
            seen_dois.add(doi)
        if tkey:
            seen_titles.add(tkey)

    return new, duplicates
