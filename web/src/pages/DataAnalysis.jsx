import { useState, useEffect, useCallback } from 'react';
import { useProject } from './Workspace';
import { api } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { ToolChips } from '../components/ToolChips';
import { AiChatPanel } from '../components/AiChatPanel';
import { PageInstructions } from '../components/PageInstructions';
import { PAGE_TOOLS } from '../data/pageTools';
import './DataAnalysis.css';

const STAT_TESTS = [
  ['descriptive', 'Descriptive Statistics', 'one_col', 'Column', null],
  ['ttest_ind', 'Independent Samples t-test', 'two_col', 'Value Column', 'Group Column (2 groups)'],
  ['ttest_paired', 'Paired Samples t-test', 'two_col', 'Column A', 'Column B'],
  ['one_sample_ttest', 'One-Sample t-test', 'one_col_plus_value', 'Column', 'Test Value (number)'],
  ['anova', 'One-Way ANOVA', 'two_col', 'Value Column', 'Group Column'],
  ['mann_whitney', 'Mann-Whitney U Test (non-parametric)', 'two_col', 'Value Column', 'Group Column (2 groups)'],
  ['wilcoxon', 'Wilcoxon Signed-Rank Test (non-parametric)', 'two_col', 'Column A', 'Column B'],
  ['kruskal', 'Kruskal-Wallis Test (non-parametric)', 'two_col', 'Value Column', 'Group Column'],
  ['pearson', 'Pearson Correlation', 'two_col', 'Column A', 'Column B'],
  ['spearman', 'Spearman Correlation', 'two_col', 'Column A', 'Column B'],
  ['correlation_matrix', 'Correlation Matrix (3+ columns)', 'multi_col', 'Columns (ctrl/cmd-click to select multiple)', null],
  ['chi2', 'Chi-Square Test of Independence', 'two_col', 'Column A', 'Column B'],
  ['linregress', 'Simple Linear Regression', 'two_col', 'X Column', 'Y Column'],
  ['multiple_regression', 'Multiple Linear Regression (2+ predictors)', 'multi_col_plus_y', 'Predictor Columns (ctrl/cmd-click to select multiple)', 'Y Column (outcome)'],
];

const TWO_COL_PARAM_KEYS = {
  ttest_ind: ['value_column', 'group_column'],
  ttest_paired: ['column_a', 'column_b'],
  anova: ['value_column', 'group_column'],
  mann_whitney: ['value_column', 'group_column'],
  wilcoxon: ['column_a', 'column_b'],
  kruskal: ['value_column', 'group_column'],
  pearson: ['column_a', 'column_b'],
  spearman: ['column_a', 'column_b'],
  chi2: ['column_a', 'column_b'],
  linregress: ['x_column', 'y_column'],
};

const CHART_TYPES = [
  ['bar', 'Bar Chart', 'X Column (category)', 'Y Column (numeric, optional = count)', false, false],
  ['line', 'Line Chart', 'X Column', 'Y Column(s) - select 1 or more', true, false],
  ['scatter', 'Scatter Plot', 'X Column', 'Y Column(s) - select 1 or more', true, false],
  ['histogram', 'Histogram', 'Column', null, false, false],
  ['box', 'Box Plot', 'Value Column', null, false, true],
  ['pie', 'Pie Chart', 'Category Column', null, false, false],
  ['heatmap', 'Heatmap (Correlation Matrix)', 'Columns (ctrl/cmd-click to select 2+)', null, false, false, true],
];

const SCATTER_TRENDLINES = [
  ['none', 'None'],
  ['linear', 'Linear (best-fit line)'],
  ['quadratic', 'Quadratic (curve fit)'],
];

export function DataAnalysis() {
  const { project } = useProject();
  const [datasets, setDatasets] = useState([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState(null);
  const [rowStart, setRowStart] = useState('');
  const [rowEnd, setRowEnd] = useState('');

  const [importName, setImportName] = useState('');
  const [importText, setImportText] = useState('');
  const [importStatus, setImportStatus] = useState('');
  const [analysisVersion, setAnalysisVersion] = useState(0);

  const refresh = useCallback(async () => {
    if (!project.id) return;
    const data = await api.listDatasets(project.id);
    setDatasets(data.datasets || []);
  }, [project.id]);

  useEffect(() => { refresh(); }, [refresh]);

  const selectedDataset = datasets.find((d) => d.id === selectedDatasetId);
  const columns = selectedDataset?.columns || [];

  function rowRange() {
    if (!rowStart && !rowEnd) return null;
    return [rowStart ? parseInt(rowStart, 10) : 0, rowEnd ? parseInt(rowEnd, 10) : 1e9];
  }

  async function importDataset(e) {
    e.preventDefault();
    if (!importText.trim()) return;
    try {
      await api.importDataset(project.id, { name: importName.trim() || 'Untitled Dataset', csv_text: importText });
      setImportName('');
      setImportText('');
      setImportStatus('Imported ✓');
      refresh();
    } catch (e) {
      setImportStatus('');
      alert(e.message);
    }
  }

  async function importDatasetFile(e) {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;
    try {
      await api.importDatasetFile(project.id, file, importName.trim());
      setImportName('');
      setImportStatus('Imported ✓');
      refresh();
    } catch (e) {
      setImportStatus('');
      alert(e.message);
    }
  }

  async function deleteDataset() {
    if (!selectedDatasetId) return;
    await api.deleteDataset(project.id, selectedDatasetId);
    setSelectedDatasetId(null);
    refresh();
  }

  return (
    <div>
      <PageInstructions
        accent="blue"
        items={[
          'Paste CSV/tab-separated data with a header row and click Import Dataset. It appears under "Your Datasets" — select it to work with it.',
          'Pick a statistical test and the columns it should run on, then click Run Test. Do the same under "Generate a Chart" for a visual.',
          'Once you\'ve run at least one test, use "Interpret These Results with AI" to get a plain-language interpretation related to your project\'s hypotheses.',
        ]}
      />
      <Card
        title="Import Data"
        hint="Paste CSV/tab-separated data, or upload a .csv, .tsv, or Excel (.xlsx) file. First row = column headers. Nothing is sent anywhere except your own local Cortex server."
        accent="blue"
      >
        <label htmlFor="dataset-name">Dataset name</label>
        <input id="dataset-name" type="text" value={importName} onChange={(e) => setImportName(e.target.value)} placeholder='e.g. "Experiment 1 raw data"' />

        <form onSubmit={importDataset}>
          <label htmlFor="dataset-csv">Paste data</label>
          <textarea
            id="dataset-csv"
            value={importText}
            onChange={(e) => setImportText(e.target.value)}
            placeholder={'subject,group,score\n1,control,88\n2,treatment,95\n...'}
            style={{ minHeight: 100, fontFamily: 'monospace', fontSize: 12 }}
          />
          <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 12 }}>
            <Button type="submit" accent="blue">Import Dataset</Button>
            {importStatus && <span role="status">{importStatus}</span>}
          </div>
        </form>

        <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>— or —</span>
          <label className="btn btn--secondary" style={{ '--btn-accent-tint': 'var(--accent3-tint)', '--btn-accent-text': 'var(--accent3-text)' }}>
            Upload File (.csv, .tsv, .xlsx)
            <input
              type="file"
              accept=".csv,.tsv,.xlsx,.xls,text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
              onChange={importDatasetFile}
              style={{ display: 'none' }}
            />
          </label>
        </div>
      </Card>

      <Card title="Your Datasets" hint="Select a dataset to run a test or make a chart from it." accent="blue" data-tour="datasets-list">
        {datasets.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No datasets yet — import one above.</p>}
        <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 6 }}>
          {datasets.map((d) => (
            <li key={d.id}>
              <button
                onClick={() => setSelectedDatasetId(d.id === selectedDatasetId ? null : d.id)}
                style={{
                  width: '100%', textAlign: 'left', cursor: 'pointer', fontSize: 13,
                  background: d.id === selectedDatasetId ? 'var(--accent3-tint)' : 'var(--surface-alt)',
                  border: `1px solid ${d.id === selectedDatasetId ? 'var(--accent3-text)' : 'var(--border)'}`,
                  borderRadius: 10, padding: '10px 12px',
                }}
              >
                {d.name} ({d.row_count} rows &times; {d.col_count} cols)
              </button>
            </li>
          ))}
        </ul>
        {selectedDataset && (
          <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Row range (optional):</span>
            <input type="text" value={rowStart} onChange={(e) => setRowStart(e.target.value)} placeholder="start" style={{ width: 70 }} />
            <span>to</span>
            <input type="text" value={rowEnd} onChange={(e) => setRowEnd(e.target.value)} placeholder="end" style={{ width: 70 }} />
            <Button variant="ghost" accent="rose" onClick={deleteDataset}>Delete Dataset</Button>
          </div>
        )}
      </Card>

      {selectedDataset && (
        <TestWizardCard
          projectId={project.id}
          dataset={selectedDataset}
          columns={columns}
          onAnalysisSaved={() => setAnalysisVersion((v) => v + 1)}
        />
      )}

      {selectedDataset && (
        <StatsCard
          projectId={project.id}
          dataset={selectedDataset}
          columns={columns}
          rowRange={rowRange}
          onAnalysisSaved={() => setAnalysisVersion((v) => v + 1)}
        />
      )}
      {selectedDataset && <ChartCard projectId={project.id} dataset={selectedDataset} columns={columns} rowRange={rowRange} />}
      {selectedDataset && <InterpretCard projectId={project.id} dataset={selectedDataset} refreshSignal={analysisVersion} />}

      <Card title="Recommended Tools" accent="blue">
        <ToolChips tools={PAGE_TOOLS.data_analysis} />
      </Card>
    </div>
  );
}

function TestWizardCard({ projectId, dataset, columns, onAnalysisSaved }) {
  const [valueColumn, setValueColumn] = useState('');
  const [groupColumn, setGroupColumn] = useState('');
  const [recommendation, setRecommendation] = useState(null);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState('');
  const [runResult, setRunResult] = useState(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    setValueColumn(columns[0] || '');
    setGroupColumn(columns[1] || columns[0] || '');
    setRecommendation(null);
    setRunResult(null);
  }, [dataset.id]); // eslint-disable-line react-hooks/exhaustive-deps

  async function checkAssumptions(e) {
    e.preventDefault();
    setError('');
    setRunResult(null);
    if (!valueColumn || !groupColumn) return setError('Select both columns.');
    setChecking(true);
    try {
      const data = await api.recommendTest(projectId, dataset.id, valueColumn, groupColumn);
      setRecommendation(data.recommendation);
    } catch (e) {
      setError(e.message);
      setRecommendation(null);
    } finally {
      setChecking(false);
    }
  }

  async function runRecommended() {
    if (!recommendation) return;
    setRunning(true);
    setError('');
    try {
      const data = await api.runAnalysis(projectId, dataset.id, recommendation.recommended_test, recommendation.recommended_params);
      setRunResult(data.analysis.result);
      onAnalysisSaved?.();
    } catch (e) {
      setError(e.message);
    } finally {
      setRunning(false);
    }
  }

  return (
    <Card
      title="Which Test Should I Use?"
      hint="Pick a numeric column and a grouping column - Cortex checks normality and sample size, then recommends (and can run) the matching test, like a stats calculator's guided mode."
      accent="sand"
      data-tour="stats-wizard"
    >
      <form onSubmit={checkAssumptions}>
        <label htmlFor="wizard-value">Numeric column</label>
        <select id="wizard-value" value={valueColumn} onChange={(e) => setValueColumn(e.target.value)}>
          {columns.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>

        <label htmlFor="wizard-group">Group column</label>
        <select id="wizard-group" value={groupColumn} onChange={(e) => setGroupColumn(e.target.value)}>
          {columns.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>

        <div style={{ marginTop: 12 }}>
          <Button type="submit" accent="sand" disabled={checking}>{checking ? 'Checking…' : 'Check Assumptions'}</Button>
        </div>
        {error && <p role="alert" style={{ color: 'var(--accent1-text)' }}>{error}</p>}
      </form>

      {recommendation && (
        <div style={{ marginTop: 16 }}>
          <p><strong>Recommended: {recommendation.recommended_test_name}</strong></p>
          <p style={{ color: 'var(--text-muted)' }}>{recommendation.reasoning}</p>

          <table style={{ width: '100%', fontSize: 13, borderCollapse: 'collapse', marginTop: 8 }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left' }}>Group</th>
                <th style={{ textAlign: 'left' }}>n</th>
                <th style={{ textAlign: 'left' }}>Normal? (Shapiro-Wilk p)</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(recommendation.groups).map(([g, info]) => (
                <tr key={g}>
                  <td>{g}</td>
                  <td>{info.n}</td>
                  <td>
                    {info.normality
                      ? `${info.is_normal ? 'Yes' : 'No'} (p=${info.normality.p_value.toFixed(4)})`
                      : 'Too few values to check'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {recommendation.variance_homogeneity && (
            <p style={{ marginTop: 8, fontSize: 13 }}>
              Variance homogeneity (Levene's test): {recommendation.variance_homogeneity.equal_variance ? 'equal' : 'unequal'} (p={recommendation.variance_homogeneity.p_value.toFixed(4)})
            </p>
          )}

          {recommendation.warnings.length > 0 && (
            <ul style={{ marginTop: 8, fontSize: 13, color: 'var(--accent1-text)' }}>
              {recommendation.warnings.map((w, i) => <li key={i}>{w}</li>)}
            </ul>
          )}

          <div style={{ marginTop: 12 }}>
            <Button accent="sand" onClick={runRecommended} disabled={running}>
              {running ? 'Running…' : `Run ${recommendation.recommended_test_name}`}
            </Button>
          </div>
        </div>
      )}

      {runResult && <StatsResult result={runResult} />}
    </Card>
  );
}

function StatsCard({ projectId, dataset, columns, rowRange, onAnalysisSaved }) {
  const [testKey, setTestKey] = useState(STAT_TESTS[0][0]);
  const [field1, setField1] = useState('');
  const [field2, setField2] = useState('');
  const [multiSelected, setMultiSelected] = useState([]);
  const [testValue, setTestValue] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [running, setRunning] = useState(false);

  const testDef = STAT_TESTS.find(([k]) => k === testKey);
  const [, , kind, label1, label2] = testDef;

  useEffect(() => {
    setField1(columns[0] || '');
    setField2(columns[1] || columns[0] || '');
    setMultiSelected([]);
  }, [testKey, dataset.id]); // eslint-disable-line react-hooks/exhaustive-deps

  function toggleMulti(col) {
    setMultiSelected((prev) => (prev.includes(col) ? prev.filter((c) => c !== col) : [...prev, col]));
  }

  async function runTest(e) {
    e.preventDefault();
    setError('');
    let params = {};

    if (kind === 'one_col') {
      if (!field1) return setError('Select a column.');
      params = { value_columns: [field1] };
    } else if (kind === 'two_col') {
      if (!field1 || !field2) return setError('Select both columns.');
      const [k1, k2] = TWO_COL_PARAM_KEYS[testKey];
      params = { [k1]: field1, [k2]: field2 };
    } else if (kind === 'one_col_plus_value') {
      if (!field1 || testValue === '') return setError('Select a column and enter a test value.');
      params = { value_column: field1, test_value: parseFloat(testValue) };
    } else if (kind === 'multi_col') {
      if (multiSelected.length < 2) return setError('Select at least 2 columns.');
      params = { columns: multiSelected };
    } else if (kind === 'multi_col_plus_y') {
      if (multiSelected.length < 1 || !field2) return setError('Select at least 1 predictor and a Y column.');
      params = { x_columns: multiSelected, y_column: field2 };
    }

    const rr = rowRange();
    if (rr) params.row_range = rr;

    setRunning(true);
    try {
      const data = await api.runAnalysis(projectId, dataset.id, testKey, params);
      setResult(data.analysis.result);
      onAnalysisSaved?.();
    } catch (e) {
      setError(e.message);
      setResult(null);
    } finally {
      setRunning(false);
    }
  }

  return (
    <Card title="Run a Statistical Test" hint="Pick the test and which columns it should run on - you choose everything." accent="sage">
      <form onSubmit={runTest}>
        <label htmlFor="test-select">Test</label>
        <select id="test-select" value={testKey} onChange={(e) => setTestKey(e.target.value)}>
          {STAT_TESTS.map(([key, name]) => <option key={key} value={key}>{name}</option>)}
        </select>

        {(kind === 'one_col' || kind === 'two_col' || kind === 'one_col_plus_value') && (
          <>
            <label htmlFor="field1">{label1}</label>
            <select id="field1" value={field1} onChange={(e) => setField1(e.target.value)}>
              {columns.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </>
        )}

        {kind === 'one_col_plus_value' && (
          <>
            <label htmlFor="test-value">{label2}</label>
            <input id="test-value" type="text" value={testValue} onChange={(e) => setTestValue(e.target.value)} placeholder="e.g. 0" />
          </>
        )}

        {kind === 'two_col' && (
          <>
            <label htmlFor="field2">{label2}</label>
            <select id="field2" value={field2} onChange={(e) => setField2(e.target.value)}>
              {columns.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </>
        )}

        {(kind === 'multi_col' || kind === 'multi_col_plus_y') && (
          <>
            <label htmlFor="multi-select">{label1}</label>
            <select id="multi-select" multiple value={multiSelected} onChange={(e) => setMultiSelected([...e.target.selectedOptions].map((o) => o.value))} style={{ minHeight: 100 }}>
              {columns.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </>
        )}

        {kind === 'multi_col_plus_y' && (
          <>
            <label htmlFor="field2b">{label2}</label>
            <select id="field2b" value={field2} onChange={(e) => setField2(e.target.value)}>
              {columns.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </>
        )}

        <div style={{ marginTop: 12 }}>
          <Button type="submit" accent="sage" disabled={running}>{running ? 'Running…' : 'Run Test'}</Button>
        </div>
        {error && <p role="alert" style={{ color: 'var(--accent1-text)' }}>{error}</p>}
      </form>

      {result && <StatsResult result={result} />}
    </Card>
  );
}

function StatsResult({ result }) {
  return (
    <div className="stats-result" aria-live="polite">
      <p className="stats-result__interpretation">{result.interpretation}</p>
      {result.statistic !== undefined && (
        <p className="stats-result__stat">
          statistic = {result.statistic.toFixed(4)}
          {result.p_value !== undefined && `, p = ${result.p_value.toFixed(4)}`}
        </p>
      )}
      {result.groups && (
        <table className="stats-table">
          <tbody>
            {Object.entries(result.groups).map(([name, stats]) => (
              <tr key={name}>
                <td><strong>{name}</strong></td>
                {Object.entries(stats).map(([k, v]) => (
                  <td key={k}>{k}={typeof v === 'number' ? v.toPrecision(4) : v}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {result.coefficients && (
        <table className="stats-table">
          <tbody>
            {Object.entries(result.coefficients).map(([name, c]) => (
              <tr key={name}>
                <td><strong>{name}</strong></td>
                <td>coef={c.coef.toPrecision(4)}</td>
                <td>se={c.se.toPrecision(4)}</td>
                <td>t={c.t.toFixed(3)}</td>
                <td>p={c.p_value.toFixed(4)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {result.matrix && (
        <div style={{ overflowX: 'auto' }}>
          <table className="stats-table">
            <thead>
              <tr>
                <th></th>
                {Object.keys(result.matrix).map((c) => <th key={c}>{c}</th>)}
              </tr>
            </thead>
            <tbody>
              {Object.keys(result.matrix).map((rowKey) => (
                <tr key={rowKey}>
                  <td><strong>{rowKey}</strong></td>
                  {Object.keys(result.matrix).map((colKey) => (
                    <td key={colKey}>{result.matrix[colKey][rowKey]?.toFixed(2)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {result.columns && typeof result.columns === 'object' && (
        <table className="stats-table">
          <tbody>
            {Object.entries(result.columns).map(([col, stats]) => (
              <tr key={col}>
                <td><strong>{col}</strong></td>
                {stats.error
                  ? <td>{stats.error}</td>
                  : Object.entries(stats).map(([k, v]) => <td key={k}>{k}={typeof v === 'number' ? v.toPrecision(4) : v}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function ChartCard({ projectId, dataset, columns, rowRange }) {
  const [chartType, setChartType] = useState(CHART_TYPES[0][0]);
  const [xColumn, setXColumn] = useState('');
  const [yColumn, setYColumn] = useState('');
  const [yMulti, setYMulti] = useState([]);
  const [columnsMulti, setColumnsMulti] = useState([]);
  const [groupColumn, setGroupColumn] = useState('');
  const [trendline, setTrendline] = useState('none');
  const [title, setTitle] = useState('');
  const [xMin, setXMin] = useState('');
  const [xMax, setXMax] = useState('');
  const [yMin, setYMin] = useState('');
  const [yMax, setYMax] = useState('');
  const [xTick, setXTick] = useState('');
  const [yTick, setYTick] = useState('');
  const [tickRotation, setTickRotation] = useState('');
  const [color, setColor] = useState('');
  const [image, setImage] = useState(null);
  const [error, setError] = useState('');
  const [generating, setGenerating] = useState(false);

  const chartDef = CHART_TYPES.find(([k]) => k === chartType);
  const [, , xLabel, yLabel, multiY, showGroup, multiColumns] = chartDef;

  useEffect(() => {
    setXColumn(columns[0] || '');
    setYColumn(columns[1] || columns[0] || '');
    setYMulti([]);
    setColumnsMulti([]);
    setGroupColumn('');
    setTrendline('none');
  }, [chartType, dataset.id]); // eslint-disable-line react-hooks/exhaustive-deps

  async function generate(e) {
    e.preventDefault();
    setError('');

    const params = {};
    if (multiColumns) {
      if (columnsMulti.length < 2) return setError('Select at least 2 columns.');
      params.columns = columnsMulti;
    } else {
      if (!xColumn) return setError('Select an X column.');
      params.x_column = xColumn;
      if (yLabel && multiY) {
        if (yMulti.length === 0) return setError('Select at least 1 Y column.');
        params.y_columns = yMulti;
      } else if (yLabel && yColumn) {
        params.y_column = yColumn;
      }
      if (showGroup && groupColumn) params.group_column = groupColumn;
      if (chartType === 'scatter' && trendline !== 'none') params.trendline = trendline;
    }
    if (title.trim()) params.title = title.trim();

    const rr = rowRange();
    if (rr) params.row_range = rr;

    if (xMin && xMax) params.xlim = [parseFloat(xMin), parseFloat(xMax)];
    if (yMin && yMax) params.ylim = [parseFloat(yMin), parseFloat(yMax)];
    if (xTick) params.x_tick_interval = parseFloat(xTick);
    if (yTick) params.y_tick_interval = parseFloat(yTick);
    if (tickRotation) params.tick_rotation = parseFloat(tickRotation);
    if (color) params.color = color;

    setGenerating(true);
    try {
      const data = await api.generateChart(projectId, dataset.id, chartType, params);
      setImage(data.chart.image_base64);
    } catch (e) {
      setError(e.message);
      setImage(null);
    } finally {
      setGenerating(false);
    }
  }

  return (
    <Card title="Generate a Chart" hint="Pick a chart type and which columns to plot." accent="sand">
      <form onSubmit={generate}>
        <label htmlFor="chart-type">Chart type</label>
        <select id="chart-type" value={chartType} onChange={(e) => setChartType(e.target.value)}>
          {CHART_TYPES.map(([key, name]) => <option key={key} value={key}>{name}</option>)}
        </select>

        {multiColumns ? (
          <>
            <label htmlFor="chart-columns-multi">{xLabel}</label>
            <select id="chart-columns-multi" multiple value={columnsMulti} onChange={(e) => setColumnsMulti([...e.target.selectedOptions].map((o) => o.value))} style={{ minHeight: 100 }}>
              {columns.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </>
        ) : (
          <>
            <label htmlFor="chart-x">{xLabel}</label>
            <select id="chart-x" value={xColumn} onChange={(e) => setXColumn(e.target.value)}>
              {columns.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </>
        )}

        {chartType === 'scatter' && (
          <>
            <label htmlFor="chart-trendline">Trendline (optional)</label>
            <select id="chart-trendline" value={trendline} onChange={(e) => setTrendline(e.target.value)}>
              {SCATTER_TRENDLINES.map(([key, name]) => <option key={key} value={key}>{name}</option>)}
            </select>
          </>
        )}

        {!multiColumns && yLabel && !multiY && (
          <>
            <label htmlFor="chart-y">{yLabel}</label>
            <select id="chart-y" value={yColumn} onChange={(e) => setYColumn(e.target.value)}>
              <option value="">(none = count)</option>
              {columns.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </>
        )}

        {!multiColumns && yLabel && multiY && (
          <>
            <label htmlFor="chart-y-multi">{yLabel}</label>
            <select id="chart-y-multi" multiple value={yMulti} onChange={(e) => setYMulti([...e.target.selectedOptions].map((o) => o.value))} style={{ minHeight: 90 }}>
              {columns.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </>
        )}

        {!multiColumns && showGroup && (
          <>
            <label htmlFor="chart-group">Group Column (optional)</label>
            <select id="chart-group" value={groupColumn} onChange={(e) => setGroupColumn(e.target.value)}>
              <option value="">(none)</option>
              {columns.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </>
        )}

        <label htmlFor="chart-title">Chart title (optional)</label>
        <input id="chart-title" type="text" value={title} onChange={(e) => setTitle(e.target.value)} />

        {chartType !== 'pie' && chartType !== 'heatmap' && (
          <>
            <label>Axis Range (optional)</label>
            <div className="data-analysis__row">
              <input type="text" value={xMin} onChange={(e) => setXMin(e.target.value)} placeholder="x min" aria-label="X axis minimum" />
              <input type="text" value={xMax} onChange={(e) => setXMax(e.target.value)} placeholder="x max" aria-label="X axis maximum" />
              <input type="text" value={yMin} onChange={(e) => setYMin(e.target.value)} placeholder="y min" aria-label="Y axis minimum" />
              <input type="text" value={yMax} onChange={(e) => setYMax(e.target.value)} placeholder="y max" aria-label="Y axis maximum" />
            </div>

            <label>Tick Marks (optional)</label>
            <div className="data-analysis__row">
              <input type="text" value={xTick} onChange={(e) => setXTick(e.target.value)} placeholder="x tick spacing" aria-label="X tick spacing" />
              <input type="text" value={yTick} onChange={(e) => setYTick(e.target.value)} placeholder="y tick spacing" aria-label="Y tick spacing" />
              <input type="text" value={tickRotation} onChange={(e) => setTickRotation(e.target.value)} placeholder="x label rotation (°)" aria-label="X tick label rotation" />
            </div>
          </>
        )}

        {chartType !== 'heatmap' && (
          <>
            <label htmlFor="chart-color">Color (optional)</label>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <input id="chart-color" type="color" value={color || '#c97b66'} onChange={(e) => setColor(e.target.value)} style={{ width: 44, padding: 2 }} />
              <Button type="button" variant="ghost" accent="sand" onClick={() => setColor('')}>Auto</Button>
            </div>
          </>
        )}

        <div style={{ marginTop: 14 }}>
          <Button type="submit" accent="sand" disabled={generating}>{generating ? 'Generating…' : 'Generate Chart'}</Button>
        </div>
        {error && <p role="alert" style={{ color: 'var(--accent1-text)' }}>{error}</p>}
      </form>

      {image && (
        <div style={{ marginTop: 16 }}>
          <img src={`data:image/png;base64,${image}`} alt={title || `${chartType} chart`} style={{ maxWidth: '100%', borderRadius: 10, border: '1px solid var(--border)' }} />
        </div>
      )}
    </Card>
  );
}

function InterpretCard({ projectId, dataset, refreshSignal }) {
  const [analyses, setAnalyses] = useState([]);
  const [hypotheses, setHypotheses] = useState([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    setLoaded(false);
    Promise.all([
      api.listCollection(projectId, 'analyses').catch(() => ({ analyses: [] })),
      api.listCollection(projectId, 'hypotheses').catch(() => ({ hypotheses: [] })),
    ]).then(([a, h]) => {
      setAnalyses((a.analyses || []).filter((item) => item.dataset_id === dataset.id));
      setHypotheses(h.hypotheses || []);
      setLoaded(true);
    });
  }, [projectId, dataset.id, refreshSignal]);

  const hypothesesText = hypotheses.map((h) => `- ${h.text} [${h.status}]`).join('\n');

  return (
    <Card
      title="Interpret Results with AI"
      hint="Get a plain-language interpretation of the statistical tests you've already run on this dataset, related to this project's hypotheses if any — grounded only in results you've actually computed."
      accent="sage"
    >
      {!loaded ? (
        <p style={{ color: 'var(--text-muted)' }}>Loading…</p>
      ) : (
        <AiChatPanel
          key={dataset.id + analyses.length}
          contextType="data_interpretation"
          context={{ dataset_name: dataset.name, analyses, hypotheses: hypothesesText }}
          kickoffMessage="Please interpret the results I've computed on this dataset and relate them to my hypothesis if I have one."
          triggerLabel="Interpret These Results with AI"
          accent="sage"
          disabled={analyses.length === 0}
          disabledReason="Run at least one statistical test above first."
        />
      )}
    </Card>
  );
}
