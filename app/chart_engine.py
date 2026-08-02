"""
Chart Engine for Cortex
Generates simple charts from a user-selected slice of a project dataset,
returned as a base64 PNG so the desktop GUI can display it without needing
its own charting toolkit. The user controls chart type, columns (including
multiple Y series for line/scatter), axis limits, tick spacing, and color.
"""

from __future__ import annotations

import base64
import io
from typing import Dict, List, Optional

CHART_TYPES = ['bar', 'line', 'scatter', 'histogram', 'box', 'heatmap', 'pie']

# Trendlines available for scatter plots - fit with numpy.polyfit at the
# matching degree, drawn over the observed x-range, labeled with its
# equation and R².
SCATTER_TRENDLINES = ['none', 'linear', 'quadratic']

# matplotlib/pandas/numpy are only imported the first time a chart is
# actually generated (see _ensure_deps) rather than at process startup -
# they're sizeable (tens of MB of Python/C extension code) and most app
# sessions never touch charting at all, so paying that cost on every launch
# would only inflate idle memory for no benefit.
plt = None
pd = None
np = None
MultipleLocator = None


def _ensure_deps():
    global plt, pd, np, MultipleLocator
    if plt is None:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as _plt
        from matplotlib.ticker import MultipleLocator as _MultipleLocator
        import pandas as _pd
        import numpy as _np
        plt, pd, np, MultipleLocator = _plt, _pd, _np, _MultipleLocator

_ACCENTS = ['#c97b66', '#7c9a72', '#6f93b3', '#b8923f', '#a37bc9', '#4f9a94']


def _apply_row_range(df: pd.DataFrame, row_range: Optional[List[int]]) -> pd.DataFrame:
    if not row_range:
        return df
    return df.iloc[row_range[0]:row_range[1]]


def _apply_axes_options(ax, params: Dict):
    """Apply user-chosen axis limits and tick spacing/rotation, if provided"""
    xlim = params.get('xlim')
    if xlim and len(xlim) == 2:
        ax.set_xlim(xlim[0], xlim[1])

    ylim = params.get('ylim')
    if ylim and len(ylim) == 2:
        ax.set_ylim(ylim[0], ylim[1])

    x_tick_interval = params.get('x_tick_interval')
    if x_tick_interval:
        ax.xaxis.set_major_locator(MultipleLocator(float(x_tick_interval)))

    y_tick_interval = params.get('y_tick_interval')
    if y_tick_interval:
        ax.yaxis.set_major_locator(MultipleLocator(float(y_tick_interval)))

    tick_rotation = params.get('tick_rotation')
    if tick_rotation:
        for label in ax.get_xticklabels():
            label.set_rotation(float(tick_rotation))
            label.set_ha('right' if float(tick_rotation) > 0 else 'center')


def _draw_trendline(ax, x, y, degree: int, color: str, label_prefix: str):
    """
    Fit and draw a polynomial trendline (degree 1 = linear, 2 = quadratic)
    over a scatter series, annotated with its equation and R². Silently
    skips if there isn't enough valid data to fit (e.g. all-NaN column).
    """
    mask = (~x.isna()) & (~y.isna())
    x_valid, y_valid = x[mask].to_numpy(dtype=float), y[mask].to_numpy(dtype=float)
    if len(x_valid) < degree + 2:
        return

    coeffs = np.polyfit(x_valid, y_valid, degree)
    poly = np.poly1d(coeffs)

    predicted = poly(x_valid)
    ss_res = np.sum((y_valid - predicted) ** 2)
    ss_tot = np.sum((y_valid - np.mean(y_valid)) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    if degree == 1:
        equation = f"y = {coeffs[0]:.3g}x + {coeffs[1]:.3g}"
    else:
        equation = f"y = {coeffs[0]:.3g}x² + {coeffs[1]:.3g}x + {coeffs[2]:.3g}"

    x_line = np.linspace(x_valid.min(), x_valid.max(), 100)
    ax.plot(x_line, poly(x_line), color=color, linestyle='--', linewidth=1.6,
            label=f"{label_prefix}{equation} (R²={r_squared:.3f})")


def generate_chart(df: pd.DataFrame, chart_type: str, params: Dict) -> str:
    """
    Generate a chart and return it as a base64-encoded PNG data string.

    Args:
        df (pd.DataFrame): The full dataset
        chart_type (str): One of CHART_TYPES
        params (Dict): x_column, y_column or y_columns (list, line/scatter only),
                        group_column (optional), row_range (optional),
                        color (optional hex, single-series only),
                        xlim/ylim (optional [min, max]),
                        x_tick_interval/y_tick_interval (optional numeric spacing),
                        tick_rotation (optional degrees), title (optional)

    Returns:
        str: base64-encoded PNG image bytes
    """
    if chart_type not in CHART_TYPES:
        raise ValueError(f"Unknown chart type: {chart_type}")

    _ensure_deps()
    df = _apply_row_range(df, params.get('row_range'))
    x_column = params.get('x_column')
    y_column = params.get('y_column')
    y_columns = params.get('y_columns') or ([y_column] if y_column else [])
    custom_color = params.get('color')

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=140)
    fig.patch.set_facecolor('#fffdf8')
    ax.set_facecolor('#fffdf8')

    if chart_type == 'bar':
        if y_column:
            grouped = df.groupby(x_column)[y_column].mean()
            grouped.plot(kind='bar', ax=ax, color=custom_color or _ACCENTS[0])
            ax.set_ylabel(f"mean({y_column})")
        else:
            df[x_column].value_counts().plot(kind='bar', ax=ax, color=custom_color or _ACCENTS[0])
            ax.set_ylabel('count')
        ax.set_xlabel(x_column)

    elif chart_type == 'line':
        for i, col in enumerate(y_columns):
            numeric_y = pd.to_numeric(df[col], errors='coerce')
            color = custom_color if (custom_color and len(y_columns) == 1) else _ACCENTS[i % len(_ACCENTS)]
            ax.plot(df[x_column], numeric_y, color=color, marker='o', markersize=3, label=col)
        ax.set_xlabel(x_column)
        ax.set_ylabel(', '.join(y_columns))
        if len(y_columns) > 1:
            ax.legend()

    elif chart_type == 'scatter':
        trendline = params.get('trendline', 'none')
        x = pd.to_numeric(df[x_column], errors='coerce')
        for i, col in enumerate(y_columns):
            y = pd.to_numeric(df[col], errors='coerce')
            color = custom_color if (custom_color and len(y_columns) == 1) else _ACCENTS[i % len(_ACCENTS)]
            ax.scatter(x, y, color=color, alpha=0.75, edgecolors='none', label=col)
            label_prefix = f"{col}: " if len(y_columns) > 1 else ''
            if trendline == 'linear':
                _draw_trendline(ax, x, y, degree=1, color=color, label_prefix=label_prefix)
            elif trendline == 'quadratic':
                _draw_trendline(ax, x, y, degree=2, color=color, label_prefix=label_prefix)
        ax.set_xlabel(x_column)
        ax.set_ylabel(', '.join(y_columns))
        if len(y_columns) > 1 or trendline != 'none':
            ax.legend(fontsize=8)

    elif chart_type == 'histogram':
        values = pd.to_numeric(df[x_column], errors='coerce').dropna()
        ax.hist(values, bins=min(20, max(5, int(len(values) ** 0.5))), color=custom_color or _ACCENTS[1], edgecolor='#fffdf8')
        ax.set_xlabel(x_column)
        ax.set_ylabel('count')

    elif chart_type == 'box':
        group_column = params.get('group_column')
        if group_column:
            groups = df[group_column].dropna().unique().tolist()
            data = [pd.to_numeric(df[df[group_column] == g][x_column], errors='coerce').dropna() for g in groups]
            ax.boxplot(data, tick_labels=[str(g) for g in groups])
            ax.set_xlabel(group_column)
        else:
            values = pd.to_numeric(df[x_column], errors='coerce').dropna()
            ax.boxplot([values])
            ax.set_xticklabels([x_column])
        ax.set_ylabel(x_column)

    elif chart_type == 'heatmap':
        columns = params.get('columns') or []
        if len(columns) < 2:
            raise ValueError('Select at least 2 columns for a correlation heatmap.')
        numeric_df = df[columns].apply(pd.to_numeric, errors='coerce')
        corr = numeric_df.corr()

        im = ax.imshow(corr.values, cmap='RdBu_r', vmin=-1, vmax=1)
        ax.set_xticks(range(len(columns)))
        ax.set_yticks(range(len(columns)))
        ax.set_xticklabels(columns)
        ax.set_yticklabels(columns)
        for i in range(len(columns)):
            for j in range(len(columns)):
                value = corr.values[i, j]
                text_color = 'white' if abs(value) > 0.6 else '#2a2a2a'
                ax.text(j, i, f"{value:.2f}", ha='center', va='center', color=text_color, fontsize=9)
        fig.colorbar(im, ax=ax, label='Correlation (r)')

    elif chart_type == 'pie':
        counts = df[x_column].value_counts()
        colors = [_ACCENTS[i % len(_ACCENTS)] for i in range(len(counts))]
        ax.pie(counts.values, labels=[str(v) for v in counts.index], colors=colors, autopct='%1.1f%%',
               textprops={'fontsize': 9})
        ax.set_ylabel('')

    ax.set_title(params.get('title') or f"{chart_type.title()} chart")
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)

    _apply_axes_options(ax, params)

    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', facecolor=fig.get_facecolor())
    plt.close(fig)
    buffer.seek(0)

    return base64.b64encode(buffer.read()).decode('ascii')
