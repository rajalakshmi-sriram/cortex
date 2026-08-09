// In the Tauri desktop shell, the Rust host injects window.__CORTEX_API_BASE__
// (the backend's dynamically-picked port) before this script runs, since the
// webview's own origin isn't the backend's origin there. Everywhere else
// (browser dev via the Vite proxy, the app served over plain http/https)
// this is unset and relative requests work as before.
const BASE = (typeof window !== 'undefined' && window.__CORTEX_API_BASE__)
  ? `${window.__CORTEX_API_BASE__}/api/v1`
  : '/api/v1';

async function request(path, { method = 'GET', body } = {}) {
  const response = await fetch(`${BASE}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const data = await response.json();
      message = data.message || message;
    } catch {
      /* non-JSON error body */
    }
    throw new Error(message);
  }

  if (response.status === 204) return null;
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) return response.json();
  return response.text();
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: 'POST', body }),
  put: (path, body) => request(path, { method: 'PUT', body }),
  del: (path) => request(path, { method: 'DELETE' }),

  // Projects
  listProjects: () => request('/projects'),
  createProject: (data) => request('/projects', { method: 'POST', body: data }),
  createSampleProject: () => request('/projects/sample', { method: 'POST' }),
  getProject: (id) => request(`/projects/${id}`),
  updateProject: (id, data) => request(`/projects/${id}`, { method: 'PUT', body: data }),
  deleteProject: (id) => request(`/projects/${id}`, { method: 'DELETE' }),
  exportProjectUrl: (id) => `${BASE}/projects/${id}/export`,
  importProject: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${BASE}/projects/import`, { method: 'POST', body: formData });
    if (!response.ok) {
      let message = `HTTP ${response.status}`;
      try {
        const data = await response.json();
        message = data.message || message;
      } catch {
        /* non-JSON error body */
      }
      throw new Error(message);
    }
    return response.json();
  },

  // Research types / methodology
  getResearchTypes: () => request('/research-types'),
  getMethodology: (projectId) => request(`/projects/${projectId}/methodology`),
  setMethodologyStep: (projectId, index, completed) =>
    request(`/projects/${projectId}/methodology/${index}`, { method: 'PUT', body: { completed } }),
  addMethodologyTool: (projectId, index, name, url) =>
    request(`/projects/${projectId}/methodology/${index}/tools`, { method: 'POST', body: { name, url } }),
  removeMethodologyTool: (projectId, index, toolId) =>
    request(`/projects/${projectId}/methodology/${index}/tools/${toolId}`, { method: 'DELETE' }),

  // Literature
  validateIdea: (idea) => request('/ideas/validate', { method: 'POST', body: { idea } }),
  validateIdeaWithAI: (idea) => request('/ideas/validate-with-ai', { method: 'POST', body: { idea } }),
  aiStatus: () => request('/ai/status'),
  suggestSearchTerms: (topic) => request('/ai/suggest-search-terms', { method: 'POST', body: { topic } }),
  getAiSettings: () => request('/settings/ai'),
  updateAiSettings: (settings) => request('/settings/ai', { method: 'POST', body: settings }),
  getLiteratureSettings: () => request('/settings/literature'),
  updateLiteratureSettings: (settings) => request('/settings/literature', { method: 'POST', body: settings }),

  // Google Docs (optional, for AI Feedback on a linked Google Doc)
  getGoogleSettings: () => request('/settings/google'),
  saveGoogleCredentials: (clientId, clientSecret) =>
    request('/settings/google', { method: 'POST', body: { client_id: clientId, client_secret: clientSecret } }),
  disconnectGoogle: () => request('/settings/google/disconnect', { method: 'POST' }),
  getGoogleAuthorizeUrl: () => request('/settings/google/oauth/authorize-url'),
  getGoogleDocContent: (docId) => request(`/google/docs/${docId}/content`),
  aiConverse: (contextType, context, messages) =>
    request('/ai/converse', { method: 'POST', body: { context_type: contextType, context, messages } }),

  // Papers / citations
  listPapers: (projectId) => request(`/projects/${projectId}/papers`),
  addPaper: (projectId, paper) => request(`/projects/${projectId}/papers`, { method: 'POST', body: paper }),
  updatePaper: (projectId, paperId, data) =>
    request(`/projects/${projectId}/papers/${paperId}`, { method: 'PUT', body: data }),
  deletePaper: (projectId, paperId) => request(`/projects/${projectId}/papers/${paperId}`, { method: 'DELETE' }),
  getCitations: (projectId, style) => request(`/projects/${projectId}/papers/citations?style=${style}`),
  getCiteIndex: (projectId, style) => request(`/projects/${projectId}/papers/cite-index?style=${style}`),
  bibtexUrl: (projectId) => `${BASE}/projects/${projectId}/papers/bibtex`,
  risUrl: (projectId) => `${BASE}/projects/${projectId}/papers/ris`,
  importReferences: async (projectId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${BASE}/projects/${projectId}/papers/import`, { method: 'POST', body: formData });
    if (!response.ok) {
      let message = `HTTP ${response.status}`;
      try {
        const data = await response.json();
        message = data.message || message;
      } catch {
        /* non-JSON error body */
      }
      throw new Error(message);
    }
    return response.json();
  },

  // Sub-collections (hypotheses, tasks, journals, notes, datasets, analyses, charts)
  listCollection: (projectId, name) => request(`/projects/${projectId}/${name}`),
  addToCollection: (projectId, name, data) => request(`/projects/${projectId}/${name}`, { method: 'POST', body: data }),
  updateInCollection: (projectId, name, id, data) =>
    request(`/projects/${projectId}/${name}/${id}`, { method: 'PUT', body: data }),
  deleteFromCollection: (projectId, name, id) => request(`/projects/${projectId}/${name}/${id}`, { method: 'DELETE' }),

  // Manuscript
  getManuscript: (projectId) => request(`/projects/${projectId}/manuscript`),
  updateManuscript: (projectId, sections) => request(`/projects/${projectId}/manuscript`, { method: 'PUT', body: sections }),

  // Journal guidelines
  getJournalGuidelines: (name) => request(`/journal-guidelines?name=${encodeURIComponent(name)}`),

  // Datasets / stats / charts
  importDataset: (projectId, data) => request(`/projects/${projectId}/datasets/import`, { method: 'POST', body: data }),
  importDatasetFile: async (projectId, file, name) => {
    const formData = new FormData();
    formData.append('file', file);
    if (name) formData.append('name', name);
    const response = await fetch(`${BASE}/projects/${projectId}/datasets/import`, { method: 'POST', body: formData });
    if (!response.ok) {
      let message = `HTTP ${response.status}`;
      try {
        const data = await response.json();
        message = data.message || message;
      } catch {
        /* non-JSON error body */
      }
      throw new Error(message);
    }
    return response.json();
  },
  listDatasets: (projectId) => request(`/projects/${projectId}/datasets`),
  deleteDataset: (projectId, id) => request(`/projects/${projectId}/datasets/${id}`, { method: 'DELETE' }),
  runAnalysis: (projectId, datasetId, test, params) =>
    request(`/projects/${projectId}/datasets/${datasetId}/analyze`, { method: 'POST', body: { test, params } }),
  recommendTest: (projectId, datasetId, valueColumn, groupColumn) =>
    request(`/projects/${projectId}/datasets/${datasetId}/recommend-test`, {
      method: 'POST', body: { value_column: valueColumn, group_column: groupColumn },
    }),
  generateChart: (projectId, datasetId, chartType, params) =>
    request(`/projects/${projectId}/datasets/${datasetId}/chart`, { method: 'POST', body: { chart_type: chartType, params } }),
};
