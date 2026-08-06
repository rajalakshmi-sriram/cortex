"""
Statistics Engine for Cortex
Runs a user-selected statistical test on user-selected columns/rows of a
project dataset - a manual, spreadsheet-like analysis flow (the user picks
the test and the data, nothing is decided automatically).
"""

from __future__ import annotations

from typing import Dict, List, Optional

# numpy/pandas/scipy are only imported the first time a test is actually run
# (see _ensure_deps in run_analysis) rather than at process startup - most
# app sessions never open Data & Analysis at all, so paying for these
# imports on every launch would only inflate idle memory for no benefit.
np = None
pd = None
scipy_stats = None


def _ensure_deps():
    global np, pd, scipy_stats
    if np is None:
        import numpy as _np
        import pandas as _pd
        from scipy import stats as _scipy_stats
        np, pd, scipy_stats = _np, _pd, _scipy_stats


TEST_CATALOG = {
    'descriptive': {'name': 'Descriptive Statistics', 'columns_needed': ['value_columns']},
    'ttest_ind': {'name': 'Independent Samples t-test', 'columns_needed': ['value_column', 'group_column']},
    'ttest_paired': {'name': 'Paired Samples t-test', 'columns_needed': ['column_a', 'column_b']},
    'one_sample_ttest': {'name': 'One-Sample t-test', 'columns_needed': ['value_column', 'test_value']},
    'anova': {'name': 'One-Way ANOVA', 'columns_needed': ['value_column', 'group_column']},
    'mann_whitney': {'name': 'Mann-Whitney U Test (non-parametric)', 'columns_needed': ['value_column', 'group_column']},
    'wilcoxon': {'name': 'Wilcoxon Signed-Rank Test (non-parametric)', 'columns_needed': ['column_a', 'column_b']},
    'kruskal': {'name': 'Kruskal-Wallis Test (non-parametric)', 'columns_needed': ['value_column', 'group_column']},
    'pearson': {'name': 'Pearson Correlation', 'columns_needed': ['column_a', 'column_b']},
    'spearman': {'name': 'Spearman Correlation', 'columns_needed': ['column_a', 'column_b']},
    'correlation_matrix': {'name': 'Correlation Matrix (3+ columns)', 'columns_needed': ['columns']},
    'chi2': {'name': 'Chi-Square Test of Independence', 'columns_needed': ['column_a', 'column_b']},
    'linregress': {'name': 'Simple Linear Regression', 'columns_needed': ['x_column', 'y_column']},
    'multiple_regression': {'name': 'Multiple Linear Regression (2+ predictors)', 'columns_needed': ['x_columns', 'y_column']},
}


def _apply_row_range(df: pd.DataFrame, row_range: Optional[List[int]]) -> pd.DataFrame:
    if not row_range:
        return df
    start, end = row_range[0], row_range[1]
    return df.iloc[start:end]


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors='coerce').dropna()


def run_analysis(df: pd.DataFrame, test: str, params: Dict) -> Dict:
    """
    Run the requested statistical test.

    Args:
        df (pd.DataFrame): The full dataset
        test (str): One of TEST_CATALOG keys
        params (Dict): column selections plus optional 'row_range': [start, end]

    Returns:
        Dict: result with 'statistic', 'p_value' (where applicable), details, and
              a plain-language 'interpretation'
    """
    if test not in TEST_CATALOG:
        raise ValueError(f"Unknown test: {test}")

    _ensure_deps()
    df = _apply_row_range(df, params.get('row_range'))

    if test == 'descriptive':
        return _descriptive(df, params['value_columns'])
    if test == 'ttest_ind':
        return _ttest_ind(df, params['value_column'], params['group_column'])
    if test == 'ttest_paired':
        return _ttest_paired(df, params['column_a'], params['column_b'])
    if test == 'one_sample_ttest':
        return _one_sample_ttest(df, params['value_column'], params['test_value'])
    if test == 'anova':
        return _anova(df, params['value_column'], params['group_column'])
    if test == 'mann_whitney':
        return _mann_whitney(df, params['value_column'], params['group_column'])
    if test == 'wilcoxon':
        return _wilcoxon(df, params['column_a'], params['column_b'])
    if test == 'kruskal':
        return _kruskal(df, params['value_column'], params['group_column'])
    if test == 'pearson':
        return _correlation(df, params['column_a'], params['column_b'], method='pearson')
    if test == 'spearman':
        return _correlation(df, params['column_a'], params['column_b'], method='spearman')
    if test == 'correlation_matrix':
        return _correlation_matrix(df, params['columns'])
    if test == 'chi2':
        return _chi2(df, params['column_a'], params['column_b'])
    if test == 'linregress':
        return _linregress(df, params['x_column'], params['y_column'])
    if test == 'multiple_regression':
        return _multiple_regression(df, params['x_columns'], params['y_column'])

    raise ValueError(f"Unhandled test: {test}")


def recommend_test(df: pd.DataFrame, value_column: str, group_column: str, row_range: Optional[List[int]] = None) -> Dict:
    """
    Guided "which test should I use?" mode: given a numeric value column and
    a grouping column, check the assumptions each test relies on (normality
    per group via Shapiro-Wilk, sample size) and recommend the matching test
    from TEST_CATALOG - a t-test/ANOVA if the data looks normal enough, the
    non-parametric equivalent (Mann-Whitney/Kruskal-Wallis) otherwise. This
    doesn't run the test itself - see run_analysis() for that, using the
    'recommended_test'/'recommended_params' this returns.
    """
    _ensure_deps()
    df = _apply_row_range(df, row_range)

    groups = df[group_column].dropna().unique().tolist()
    if len(groups) < 2:
        raise ValueError(f"Need at least 2 groups in '{group_column}' to compare, found {len(groups)}")

    group_stats = {}
    warnings = []
    all_normal = True

    for g in groups:
        series = _numeric(df[df[group_column] == g][value_column])
        n = int(series.count())
        entry = {'n': n}

        if n < 3:
            entry['normality'] = None
            entry['is_normal'] = False
            all_normal = False
            warnings.append(f"Group '{g}' has only {n} value(s) - too few to test normality (need at least 3).")
        else:
            stat, p = scipy_stats.shapiro(series)
            is_normal = bool(p > 0.05)
            entry['normality'] = {'statistic': float(stat), 'p_value': float(p)}
            entry['is_normal'] = is_normal
            if not is_normal:
                all_normal = False
            if n < 10:
                warnings.append(f"Group '{g}' has a small sample size (n={n}) - test results may be unreliable regardless of which test is used.")

        group_stats[str(g)] = entry

    variance_check = None
    numeric_groups = [_numeric(df[df[group_column] == g][value_column]) for g in groups]
    numeric_groups = [s for s in numeric_groups if len(s) >= 2]
    if len(numeric_groups) >= 2:
        lev_stat, lev_p = scipy_stats.levene(*numeric_groups)
        variance_check = {'statistic': float(lev_stat), 'p_value': float(lev_p), 'equal_variance': bool(lev_p > 0.05)}

    two_groups = len(groups) == 2
    if all_normal:
        recommended = 'ttest_ind' if two_groups else 'anova'
        reasoning = (
            f"All {len(groups)} group(s) look approximately normally distributed (Shapiro-Wilk p > 0.05), "
            f"so a {'t-test' if two_groups else 'one-way ANOVA'} is appropriate."
        )
    else:
        recommended = 'mann_whitney' if two_groups else 'kruskal'
        reasoning = (
            "At least one group doesn't look normally distributed (or was too small to check), so the "
            f"non-parametric {'Mann-Whitney U test' if two_groups else 'Kruskal-Wallis test'} is safer than "
            f"assuming normality."
        )

    if not two_groups and len(groups) > 2 and all_normal and variance_check and not variance_check['equal_variance']:
        warnings.append(
            "Group variances look unequal (Levene's test p ≤ 0.05) - standard ANOVA assumes equal variances, "
            "so treat the result with some caution."
        )

    return {
        'value_column': value_column,
        'group_column': group_column,
        'groups': group_stats,
        'variance_homogeneity': variance_check,
        'recommended_test': recommended,
        'recommended_test_name': TEST_CATALOG[recommended]['name'],
        'recommended_params': {'value_column': value_column, 'group_column': group_column},
        'reasoning': reasoning,
        'warnings': warnings,
    }


def _descriptive(df: pd.DataFrame, value_columns: List[str]) -> Dict:
    stats_by_column = {}
    for col in value_columns:
        series = _numeric(df[col])
        if series.empty:
            stats_by_column[col] = {'error': 'No numeric data in this column'}
            continue
        stats_by_column[col] = {
            'n': int(series.count()),
            'mean': float(series.mean()),
            'std': float(series.std()) if series.count() > 1 else 0.0,
            'min': float(series.min()),
            'max': float(series.max()),
            'median': float(series.median()),
        }

    lines = [f"{col}: n={s['n']}, mean={s['mean']:.3g}, sd={s['std']:.3g}" for col, s in stats_by_column.items() if 'error' not in s]
    return {
        'test': 'descriptive',
        'columns': stats_by_column,
        'interpretation': "Descriptive statistics computed for: " + "; ".join(lines) if lines else "No numeric data found."
    }


def _ttest_ind(df: pd.DataFrame, value_column: str, group_column: str) -> Dict:
    groups = df[group_column].dropna().unique().tolist()
    if len(groups) != 2:
        raise ValueError(
            f"Independent t-test needs exactly 2 groups in '{group_column}', found {len(groups)}: {groups}. "
            f"Use 'One-Way ANOVA' to compare all {len(groups)} groups at once, or set a row range to isolate just 2 of them."
        )

    a = _numeric(df[df[group_column] == groups[0]][value_column])
    b = _numeric(df[df[group_column] == groups[1]][value_column])

    if a.empty or b.empty:
        raise ValueError("One or both groups have no numeric data")

    statistic, p_value = scipy_stats.ttest_ind(a, b, equal_var=False)

    return {
        'test': 'ttest_ind',
        'groups': {str(groups[0]): {'n': int(a.count()), 'mean': float(a.mean()), 'std': float(a.std())},
                   str(groups[1]): {'n': int(b.count()), 'mean': float(b.mean()), 'std': float(b.std())}},
        'statistic': float(statistic),
        'p_value': float(p_value),
        'interpretation': (
            f"Welch's t-test comparing '{value_column}' between {groups[0]} (mean={a.mean():.3g}) and "
            f"{groups[1]} (mean={b.mean():.3g}): t={statistic:.3f}, p={p_value:.4f}. "
            f"{'Statistically significant at α=0.05.' if p_value < 0.05 else 'Not statistically significant at α=0.05.'}"
        )
    }


def _ttest_paired(df: pd.DataFrame, column_a: str, column_b: str) -> Dict:
    paired = df[[column_a, column_b]].apply(pd.to_numeric, errors='coerce').dropna()
    if paired.empty:
        raise ValueError("No valid numeric paired rows found")

    statistic, p_value = scipy_stats.ttest_rel(paired[column_a], paired[column_b])

    return {
        'test': 'ttest_paired',
        'n_pairs': int(len(paired)),
        'mean_diff': float((paired[column_a] - paired[column_b]).mean()),
        'statistic': float(statistic),
        'p_value': float(p_value),
        'interpretation': (
            f"Paired t-test between '{column_a}' and '{column_b}' (n={len(paired)}): t={statistic:.3f}, p={p_value:.4f}. "
            f"{'Statistically significant at α=0.05.' if p_value < 0.05 else 'Not statistically significant at α=0.05.'}"
        )
    }


def _anova(df: pd.DataFrame, value_column: str, group_column: str) -> Dict:
    groups = df[group_column].dropna().unique().tolist()
    if len(groups) < 2:
        raise ValueError(f"ANOVA needs at least 2 groups in '{group_column}'")

    samples = [_numeric(df[df[group_column] == g][value_column]) for g in groups]
    samples = [s for s in samples if not s.empty]
    if len(samples) < 2:
        raise ValueError("Fewer than 2 groups have numeric data")

    statistic, p_value = scipy_stats.f_oneway(*samples)

    return {
        'test': 'anova',
        'groups': {str(g): {'n': int(s.count()), 'mean': float(s.mean())} for g, s in zip(groups, samples)},
        'statistic': float(statistic),
        'p_value': float(p_value),
        'interpretation': (
            f"One-way ANOVA of '{value_column}' across {len(samples)} groups of '{group_column}': "
            f"F={statistic:.3f}, p={p_value:.4f}. "
            f"{'Statistically significant at α=0.05.' if p_value < 0.05 else 'Not statistically significant at α=0.05.'}"
        )
    }


def _correlation(df: pd.DataFrame, column_a: str, column_b: str, method: str) -> Dict:
    paired = df[[column_a, column_b]].apply(pd.to_numeric, errors='coerce').dropna()
    if len(paired) < 3:
        raise ValueError("Need at least 3 valid numeric paired rows to compute correlation")

    func = scipy_stats.pearsonr if method == 'pearson' else scipy_stats.spearmanr
    statistic, p_value = func(paired[column_a], paired[column_b])

    return {
        'test': method,
        'n': int(len(paired)),
        'statistic': float(statistic),
        'p_value': float(p_value),
        'interpretation': (
            f"{method.title()} correlation between '{column_a}' and '{column_b}' (n={len(paired)}): "
            f"r={statistic:.3f}, p={p_value:.4f}. "
            f"{'Statistically significant at α=0.05.' if p_value < 0.05 else 'Not statistically significant at α=0.05.'}"
        )
    }


def _chi2(df: pd.DataFrame, column_a: str, column_b: str) -> Dict:
    paired = df[[column_a, column_b]].dropna()
    if paired.empty:
        raise ValueError("No valid paired rows found")

    contingency = pd.crosstab(paired[column_a], paired[column_b])
    statistic, p_value, dof, _expected = scipy_stats.chi2_contingency(contingency)

    return {
        'test': 'chi2',
        'contingency_table': contingency.to_dict(),
        'degrees_of_freedom': int(dof),
        'statistic': float(statistic),
        'p_value': float(p_value),
        'interpretation': (
            f"Chi-square test of independence between '{column_a}' and '{column_b}': "
            f"χ²={statistic:.3f}, df={dof}, p={p_value:.4f}. "
            f"{'Statistically significant association at α=0.05.' if p_value < 0.05 else 'No statistically significant association at α=0.05.'}"
        )
    }


def _linregress(df: pd.DataFrame, x_column: str, y_column: str) -> Dict:
    paired = df[[x_column, y_column]].apply(pd.to_numeric, errors='coerce').dropna()
    if len(paired) < 3:
        raise ValueError("Need at least 3 valid numeric paired rows to run a regression")

    result = scipy_stats.linregress(paired[x_column], paired[y_column])

    return {
        'test': 'linregress',
        'n': int(len(paired)),
        'slope': float(result.slope),
        'intercept': float(result.intercept),
        'r_squared': float(result.rvalue ** 2),
        'p_value': float(result.pvalue),
        'std_err': float(result.stderr),
        'interpretation': (
            f"Linear regression of '{y_column}' on '{x_column}' (n={len(paired)}): "
            f"y = {result.slope:.3g}x + {result.intercept:.3g}, R²={result.rvalue**2:.3f}, p={result.pvalue:.4f}."
        )
    }


def _one_sample_ttest(df: pd.DataFrame, value_column: str, test_value) -> Dict:
    series = _numeric(df[value_column])
    if series.empty:
        raise ValueError(f"No numeric data in '{value_column}'")

    test_value = float(test_value)
    statistic, p_value = scipy_stats.ttest_1samp(series, test_value)

    return {
        'test': 'one_sample_ttest',
        'n': int(series.count()),
        'sample_mean': float(series.mean()),
        'test_value': test_value,
        'statistic': float(statistic),
        'p_value': float(p_value),
        'interpretation': (
            f"One-sample t-test of '{value_column}' (mean={series.mean():.3g}, n={series.count()}) "
            f"against test value {test_value:.3g}: t={statistic:.3f}, p={p_value:.4f}. "
            f"{'Statistically significant at α=0.05.' if p_value < 0.05 else 'Not statistically significant at α=0.05.'}"
        )
    }


def _mann_whitney(df: pd.DataFrame, value_column: str, group_column: str) -> Dict:
    groups = df[group_column].dropna().unique().tolist()
    if len(groups) != 2:
        raise ValueError(
            f"Mann-Whitney U test needs exactly 2 groups in '{group_column}', found {len(groups)}: {groups}. "
            f"Use 'Kruskal-Wallis' to compare all {len(groups)} groups at once."
        )

    a = _numeric(df[df[group_column] == groups[0]][value_column])
    b = _numeric(df[df[group_column] == groups[1]][value_column])
    if a.empty or b.empty:
        raise ValueError("One or both groups have no numeric data")

    statistic, p_value = scipy_stats.mannwhitneyu(a, b, alternative='two-sided')

    return {
        'test': 'mann_whitney',
        'groups': {str(groups[0]): {'n': int(a.count()), 'median': float(a.median())},
                   str(groups[1]): {'n': int(b.count()), 'median': float(b.median())}},
        'statistic': float(statistic),
        'p_value': float(p_value),
        'interpretation': (
            f"Mann-Whitney U test comparing '{value_column}' between {groups[0]} (median={a.median():.3g}) and "
            f"{groups[1]} (median={b.median():.3g}): U={statistic:.3f}, p={p_value:.4f}. "
            f"{'Statistically significant at α=0.05.' if p_value < 0.05 else 'Not statistically significant at α=0.05.'}"
        )
    }


def _wilcoxon(df: pd.DataFrame, column_a: str, column_b: str) -> Dict:
    paired = df[[column_a, column_b]].apply(pd.to_numeric, errors='coerce').dropna()
    if paired.empty:
        raise ValueError("No valid numeric paired rows found")

    statistic, p_value = scipy_stats.wilcoxon(paired[column_a], paired[column_b])

    return {
        'test': 'wilcoxon',
        'n_pairs': int(len(paired)),
        'statistic': float(statistic),
        'p_value': float(p_value),
        'interpretation': (
            f"Wilcoxon signed-rank test between '{column_a}' and '{column_b}' (n={len(paired)}): "
            f"W={statistic:.3f}, p={p_value:.4f}. "
            f"{'Statistically significant at α=0.05.' if p_value < 0.05 else 'Not statistically significant at α=0.05.'}"
        )
    }


def _kruskal(df: pd.DataFrame, value_column: str, group_column: str) -> Dict:
    groups = df[group_column].dropna().unique().tolist()
    if len(groups) < 2:
        raise ValueError(f"Kruskal-Wallis needs at least 2 groups in '{group_column}'")

    samples = [(g, _numeric(df[df[group_column] == g][value_column])) for g in groups]
    samples = [(g, s) for g, s in samples if not s.empty]
    if len(samples) < 2:
        raise ValueError("Fewer than 2 groups have numeric data")

    statistic, p_value = scipy_stats.kruskal(*[s for _, s in samples])

    return {
        'test': 'kruskal',
        'groups': {str(g): {'n': int(s.count()), 'median': float(s.median())} for g, s in samples},
        'statistic': float(statistic),
        'p_value': float(p_value),
        'interpretation': (
            f"Kruskal-Wallis test of '{value_column}' across {len(samples)} groups of '{group_column}': "
            f"H={statistic:.3f}, p={p_value:.4f}. "
            f"{'Statistically significant at α=0.05.' if p_value < 0.05 else 'Not statistically significant at α=0.05.'}"
        )
    }


def _correlation_matrix(df: pd.DataFrame, columns: List[str]) -> Dict:
    if len(columns) < 2:
        raise ValueError("Select at least 2 columns to compute a correlation matrix")

    numeric_df = df[columns].apply(pd.to_numeric, errors='coerce')
    corr = numeric_df.corr(method='pearson').round(4)

    strongest = []
    for i, col_a in enumerate(columns):
        for col_b in columns[i + 1:]:
            value = corr.loc[col_a, col_b]
            if pd.notna(value):
                strongest.append((col_a, col_b, value))
    strongest.sort(key=lambda x: abs(x[2]), reverse=True)
    top_line = "; ".join(f"{a}~{b}: r={v:.2f}" for a, b, v in strongest[:3])

    return {
        'test': 'correlation_matrix',
        'columns': columns,
        'matrix': corr.to_dict(),
        'interpretation': f"Pearson correlation matrix across {len(columns)} columns. Strongest pairs: {top_line}." if top_line else "No valid numeric pairs found."
    }


def _multiple_regression(df: pd.DataFrame, x_columns: List[str], y_column: str) -> Dict:
    if len(x_columns) < 1:
        raise ValueError("Select at least 1 predictor column")

    subset = df[x_columns + [y_column]].apply(pd.to_numeric, errors='coerce').dropna()
    n = len(subset)
    p = len(x_columns) + 1  # + intercept

    if n <= p:
        raise ValueError(f"Need more than {p} valid numeric rows for {len(x_columns)} predictors, got {n}")

    X = np.column_stack([np.ones(n), subset[x_columns].values])
    y = subset[y_column].values

    beta, _residuals, _rank, _sv = np.linalg.lstsq(X, y, rcond=None)
    y_pred = X @ beta
    residuals = y - y_pred
    ss_res = float(np.sum(residuals ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    dof = n - p
    adj_r_squared = 1 - (1 - r_squared) * (n - 1) / dof if dof > 0 else r_squared

    sigma2 = ss_res / dof if dof > 0 else 0.0
    try:
        xtx_inv = np.linalg.inv(X.T @ X)
    except np.linalg.LinAlgError:
        raise ValueError("Predictor columns are perfectly collinear with each other - remove a redundant column")

    se = np.sqrt(np.maximum(np.diag(sigma2 * xtx_inv), 0))
    t_stats = beta / se
    p_values = [2 * (1 - scipy_stats.t.cdf(abs(t), dof)) for t in t_stats] if dof > 0 else [1.0] * p

    if dof > 0 and r_squared < 1 and len(x_columns) > 0:
        f_statistic = (r_squared / len(x_columns)) / ((1 - r_squared) / dof)
        f_p_value = float(1 - scipy_stats.f.cdf(f_statistic, len(x_columns), dof))
    else:
        f_statistic, f_p_value = float('nan'), float('nan')

    coefficients = {
        'intercept': {'coef': float(beta[0]), 'se': float(se[0]), 't': float(t_stats[0]), 'p_value': float(p_values[0])}
    }
    for i, col in enumerate(x_columns, start=1):
        coefficients[col] = {'coef': float(beta[i]), 'se': float(se[i]), 't': float(t_stats[i]), 'p_value': float(p_values[i])}

    coef_summary = ", ".join(f"{col}={c['coef']:.3g} (p={c['p_value']:.3f})" for col, c in coefficients.items() if col != 'intercept')

    return {
        'test': 'multiple_regression',
        'n': int(n),
        'r_squared': float(r_squared),
        'adj_r_squared': float(adj_r_squared),
        'f_statistic': float(f_statistic),
        'f_p_value': float(f_p_value),
        'coefficients': coefficients,
        'interpretation': (
            f"Multiple regression of '{y_column}' on {len(x_columns)} predictor(s) (n={n}): "
            f"R²={r_squared:.3f}, adj. R²={adj_r_squared:.3f}, F={f_statistic:.3f}, p={f_p_value:.4f}. "
            f"Coefficients: {coef_summary}."
        )
    }
