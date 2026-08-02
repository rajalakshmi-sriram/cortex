"""
Data import utilities for Cortex
Parses pasted/uploaded CSV text or manually entered rows into a JSON-serializable
table (columns + rows) that can be stored as a project dataset.
"""

from __future__ import annotations

import io
from typing import Dict, List

# pandas is only imported the first time a dataset is actually touched (see
# _ensure_deps) rather than at process startup - most app sessions never
# open Data & Analysis at all, so paying for this import (which also pulls
# in numpy) on every launch would only inflate idle memory for no benefit.
pd = None


def _ensure_deps():
    global pd
    if pd is None:
        import pandas as _pd
        pd = _pd


def _dataframe_to_table(df: 'pd.DataFrame') -> Dict:
    """Convert a DataFrame into JSON-safe columns/rows"""
    df = df.where(pd.notnull(df), None)
    columns = [str(c) for c in df.columns]
    rows = df.values.tolist()
    # numpy scalar types aren't JSON serializable - coerce to native python
    rows = [[_to_native(v) for v in row] for row in rows]
    return {'columns': columns, 'rows': rows, 'row_count': len(rows), 'col_count': len(columns)}


def _to_native(value):
    if value is None:
        return None
    if hasattr(value, 'item'):
        try:
            value = value.item()
        except (ValueError, AttributeError):
            return str(value)
    if isinstance(value, float) and value != value:  # NaN != NaN
        return None
    return value


def parse_csv_text(csv_text: str) -> Dict:
    """Parse raw CSV/TSV text (from a pasted clipboard or uploaded file) into a table"""
    if not csv_text or not csv_text.strip():
        raise ValueError("No CSV content provided")

    _ensure_deps()
    sep = '\t' if csv_text.count('\t') > csv_text.count(',') else ','
    df = pd.read_csv(io.StringIO(csv_text), sep=sep)
    if df.shape[1] == 0:
        raise ValueError("Could not detect any columns in the provided data")

    return _dataframe_to_table(df)


def parse_rows(rows: List[Dict]) -> Dict:
    """Parse a list of {column: value} dicts (manual row-by-row entry) into a table"""
    if not rows:
        raise ValueError("No rows provided")

    _ensure_deps()
    df = pd.DataFrame(rows)
    return _dataframe_to_table(df)


def table_to_dataframe(dataset: Dict) -> 'pd.DataFrame':
    """Reconstruct a pandas DataFrame from a stored dataset's columns/rows"""
    _ensure_deps()
    return pd.DataFrame(dataset.get('rows', []), columns=dataset.get('columns', []))
