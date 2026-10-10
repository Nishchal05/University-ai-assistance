/**
 * Single API Client for HCLTech AI University Assistant
 * THE ONLY place that communicates with the backend HTTP API.
 * Conforms strictly to docs/API_CONTRACT.md.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

/**
 * Normalizes any fetch or HTTP error into a unified UI-friendly shape.
 */
function normalizeError(err) {
  if (err && err.response && err.response.detail) {
    const d = err.response.detail;
    return typeof d === 'string' ? d : JSON.stringify(d);
  }
  if (err && err.message) {
    if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
      return 'Unable to reach university backend server. Please verify the backend is running.';
    }
    return err.message;
  }
  return 'An unexpected error occurred while communicating with the assistant.';
}

/**
 * Core HTTP fetch wrapper with error handling and identity header injection.
 */
async function apiRequest(endpoint, { method = 'GET', headers = {}, body = null, studentId = null } = {}) {
  const reqHeaders = { ...headers };

  // Attach X-Student-Id ONLY when studentId is explicitly provided
  if (studentId && String(studentId).trim()) {
    reqHeaders['X-Student-Id'] = String(studentId).trim();
  }

  const options = {
    method,
    headers: reqHeaders,
  };

  if (body) {
    if (body instanceof FormData) {
      options.body = body;
    } else {
      reqHeaders['Content-Type'] = 'application/json';
      options.body = JSON.stringify(body);
    }
  }

  try {
    const url = `${BASE_URL}${endpoint}`;
    const res = await fetch(url, options);

    if (!res.ok) {
      let errBody = null;
      try {
        errBody = await res.json();
      } catch (e) {
        errBody = { detail: await res.text() };
      }
      const error = new Error(`Request failed with status ${res.status}`);
      error.status = res.status;
      error.response = errBody;
      throw error;
    }

    return await res.json();
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw new Error(normalizeError(error));
  }
}

/**
 * Health check: GET /health
 */
export async function checkHealth() {
  return apiRequest('/health');
}

/**
 * Ask query: POST /ask
 * @param {string} question - query text
 * @param {string|null} asOfDate - optional YYYY-MM-DD
 * @param {string|null} studentId - attached ONLY via X-Student-Id header
 */
export async function askQuestion(question, asOfDate = null, studentId = null) {
  return apiRequest('/ask', {
    method: 'POST',
    body: {
      question,
      as_of_date: asOfDate || undefined,
    },
    studentId,
  });
}

/**
 * Get Source Register: GET /sources
 */
export async function getSources() {
  return apiRequest('/sources');
}

/**
 * Get Audit Trace: GET /audit/{trace_id}
 */
export async function getAuditRecord(traceId) {
  return apiRequest(`/audit/${encodeURIComponent(traceId)}`);
}

/**
 * Live Document Ingestion: POST /ingest
 */
export async function ingestDocument(file, metadata) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('metadata', typeof metadata === 'string' ? metadata : JSON.stringify(metadata));

  return apiRequest('/ingest', {
    method: 'POST',
    body: formData,
  });
}

/**
 * Load Judge/Test Students: POST /admin/load_students
 */
export async function loadStudents({ studentsFile, coursesFile, attendanceFile, resultsFile }) {
  const formData = new FormData();
  if (studentsFile) formData.append('students_csv', studentsFile);
  if (coursesFile) formData.append('courses_csv', coursesFile);
  if (attendanceFile) formData.append('attendance_csv', attendanceFile);
  if (resultsFile) formData.append('results_csv', resultsFile);

  return apiRequest('/admin/load_students', {
    method: 'POST',
    body: formData,
  });
}

/**
 * Get Student Profile: GET /student/profile
 */
export async function getStudentProfile(studentId) {
  return apiRequest('/student/profile', {
    studentId,
  });
}

/**
 * Get All Synthetic Student IDs: GET /student/all_ids
 */
export async function getAllStudentIds() {
  return apiRequest('/student/all_ids');
}
