/**
 * Epistemic Fact Knowledge Layer (EFKL) - Reactive Frontend Controller
 */

let currentState = null;
let currentFilter = 'ALL';
let searchQuery = '';
let selectedFile = null;

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
  fetchState();
});

async function fetchState() {
  try {
    const res = await fetch('/api/state');
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    currentState = await res.json();
    renderDashboard();
  } catch (err) {
    console.error('Failed to fetch state:', err);
    document.getElementById('verdictsList').innerHTML = `
      <div class="verdict-card" style="border-color: #EF4444;">
        <h4 style="color: #EF4444; margin-bottom: 0.5rem;">Connection Error</h4>
        <p style="color: #94A3B8; font-size: 0.85rem;">Could not connect to EFKL backend. Ensure FastAPI server is running.</p>
      </div>
    `;
  }
}

function renderDashboard() {
  if (!currentState) return;

  // 1. Update Metrics Banner
  document.getElementById('statDocs').textContent = currentState.documents.length;
  document.getElementById('statFacts').textContent = currentState.total_facts;
  document.getElementById('statCorroborated').textContent = currentState.verdict_counts.CORROBORATED || 0;
  document.getElementById('statContradictions').textContent = currentState.verdict_counts.GENUINE_CONTRADICTION || 0;
  document.getElementById('statApparent').textContent = currentState.verdict_counts.APPARENT_CONTRADICTION || 0;
  document.getElementById('statFailures').textContent = currentState.verdict_counts.EXTRACTION_FAILURE || 0;

  // 2. Filter Verdicts
  let filtered = currentState.verdicts;
  if (currentFilter !== 'ALL') {
    filtered = filtered.filter(v => v.verdict_type === currentFilter);
  }

  if (searchQuery.trim()) {
    const q = searchQuery.toLowerCase();
    filtered = filtered.filter(v => 
      v.topic.toLowerCase().includes(q) ||
      v.summary.toLowerCase().includes(q) ||
      v.explanation.toLowerCase().includes(q) ||
      v.facts.some(f => f.quote.toLowerCase().includes(q) || f.value_raw.toLowerCase().includes(q))
    );
  }

  // 3. Render Verdicts List
  const container = document.getElementById('verdictsList');
  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="verdict-card" style="text-align: center; padding: 3rem;">
        <p style="color: #94A3B8;">No reconciliation verdicts found matching the selected filter or search.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(verdict => renderVerdictCard(verdict)).join('');
}

function renderVerdictCard(v) {
  const typeMap = {
    CORROBORATED: { badgeClass: 'badge-corr', label: 'Case 1: Corroborated' },
    GENUINE_CONTRADICTION: { badgeClass: 'badge-gen', label: 'Case 2: Genuine Contradiction' },
    APPARENT_CONTRADICTION: { badgeClass: 'badge-app', label: 'Case 3: Apparent Contradiction (Context Reconciled)' },
    EXTRACTION_FAILURE: { badgeClass: 'badge-fail', label: 'Case 4: Audited Extraction Failure' },
  };

  const meta = typeMap[v.verdict_type] || { badgeClass: '', label: v.verdict_type };

  const dimensionBadge = v.divergence_dimension && v.divergence_dimension !== 'NONE'
    ? `<span class="badge badge-dimension">Dimension: ${v.divergence_dimension}</span>`
    : '';

  const evidencePanes = v.facts.map((fact, idx) => `
    <div class="evidence-pane">
      <div class="evidence-meta">
        <span class="doc-name" title="${fact.document_id}">Doc ${String.fromCharCode(65 + idx)}: ${fact.document_id}</span>
        <span class="page-badge">Page ${fact.page_number}</span>
      </div>
      <div class="evidence-tags">
        ${fact.temporal_anchor ? `<span class="tag">⏱️ ${fact.temporal_anchor}</span>` : ''}
        ${fact.scope ? `<span class="tag">🔍 ${fact.scope}</span>` : ''}
        <span class="tag" style="color: #38BDF8; font-weight: bold;">Val: ${fact.value_raw}</span>
      </div>
      <div class="evidence-quote">
        "${fact.quote}"
      </div>
      <button class="btn-audit" onclick="auditFact('${fact.id}')">
        🔬 Audit Quote Provenance
      </button>
    </div>
  `).join('');

  return `
    <div class="verdict-card verdict-${v.verdict_type.toLowerCase()}">
      <div class="verdict-header">
        <div class="verdict-title-area">
          <span class="badge ${meta.badgeClass}">${meta.label}</span>
          ${dimensionBadge}
          <h3 class="verdict-topic">${v.topic}</h3>
        </div>
      </div>
      <div class="verdict-summary">${v.summary}</div>
      <div class="verdict-explanation">
        <strong>Dialectic Reasoning:</strong> ${v.explanation}
      </div>
      <div class="evidence-grid">
        ${evidencePanes}
      </div>
    </div>
  `;
}

function setFilter(filterType) {
  currentFilter = filterType;
  document.querySelectorAll('.filter-pills .pill').forEach(btn => {
    if (btn.getAttribute('data-filter') === filterType) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
  renderDashboard();
}

function handleSearch() {
  searchQuery = document.getElementById('searchInput').value;
  renderDashboard();
}

async function loadBenchmark(datasetName) {
  document.getElementById('btnLoadDelhivery').classList.toggle('active', datasetName.includes('delhi'));
  document.getElementById('btnLoadMacro').classList.toggle('active', datasetName.includes('macro'));

  try {
    const res = await fetch(`/api/load-dataset/${datasetName}`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to load dataset');
    const data = await res.json();
    currentState = data.state;
    renderDashboard();
  } catch (err) {
    alert(`Error loading benchmark: ${err.message}`);
  }
}

async function auditFact(factId) {
  const drawer = document.getElementById('auditDrawer');
  const content = document.getElementById('auditDrawerContent');
  drawer.classList.remove('hidden');
  content.innerHTML = `<p style="color: #94A3B8;">Auditing quote against source document bounding blocks...</p>`;

  try {
    const res = await fetch(`/api/audit-provenance/${factId}`);
    if (!res.ok) throw new Error('Failed to audit fact');
    const data = await res.json();

    const verified = data.provenance_audit.status === 'VERIFIED';
    const statusColor = verified ? '#10B981' : '#F43F5E';

    let trapHtml = '';
    if (data.failure_trap_diagnosis) {
      trapHtml = `
        <div style="background: rgba(168, 85, 247, 0.15); border: 1px solid #A855F7; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
          <h4 style="color: #C084FC; margin-bottom: 0.4rem;">Audited Cognitive Trap: ${data.failure_trap_diagnosis.failure_type}</h4>
          <p style="font-size: 0.8rem; color: #E2E8F0; margin-bottom: 0.5rem;">${data.failure_trap_diagnosis.description}</p>
          <strong style="font-size: 0.75rem; color: #38BDF8;">Remediation:</strong>
          <p style="font-size: 0.78rem; color: #94A3B8;">${data.failure_trap_diagnosis.remediation}</p>
        </div>
      `;
    }

    content.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 0.75rem;">
        <div>
          <span style="font-size: 0.75rem; color: #64748B; text-transform: uppercase;">Grounding Status</span>
          <h4 style="color: ${statusColor}; font-family: var(--font-mono);">${data.provenance_audit.status}</h4>
        </div>
        <div style="font-size: 0.8rem; color: #94A3B8;">
          <strong>Target Document:</strong> ${data.fact.document_id} (Page ${data.fact.page_number})
        </div>
        <div style="font-size: 0.8rem; color: #94A3B8;">
          <strong>Extracted Claim:</strong> ${data.fact.entity} - ${data.fact.attribute}
        </div>
        <div style="font-size: 0.8rem; color: #94A3B8;">
          <strong>Value:</strong> <code style="color: #38BDF8;">${data.fact.value_raw}</code>
        </div>
        <div style="background: #0D131F; border: 1px solid #26354D; padding: 0.75rem; border-radius: 6px;">
          <span style="font-size: 0.7rem; color: #64748B; display: block; margin-bottom: 0.2rem;">VERBATIM QUOTE TESTED:</span>
          <p style="font-size: 0.82rem; font-style: italic; color: #F9FAFB;">"${data.fact.quote}"</p>
        </div>
        ${trapHtml}
      </div>
    `;
  } catch (err) {
    content.innerHTML = `<p style="color: #EF4444;">Error auditing provenance: ${err.message}</p>`;
  }
}

function closeAuditDrawer() {
  document.getElementById('auditDrawer').classList.add('hidden');
}

/* Modal Functions */
function openUploadModal() {
  document.getElementById('uploadModal').classList.remove('hidden');
  selectedFile = null;
  document.getElementById('selectedFileName').textContent = '';
  document.getElementById('btnUploadSubmit').disabled = true;
  document.getElementById('uploadProgress').classList.add('hidden');
}

function closeUploadModal() {
  document.getElementById('uploadModal').classList.add('hidden');
}

function handleFileSelect(e) {
  if (e.target.files && e.target.files[0]) {
    selectedFile = e.target.files[0];
    document.getElementById('selectedFileName').textContent = `Selected: ${selectedFile.name} (${(selectedFile.size / 1024).toFixed(1)} KB)`;
    document.getElementById('btnUploadSubmit').disabled = false;
  }
}

async function submitUpload() {
  if (!selectedFile) return;

  const btn = document.getElementById('btnUploadSubmit');
  btn.disabled = true;
  document.getElementById('uploadProgress').classList.remove('hidden');

  const formData = new FormData();
  formData.append('file', selectedFile);

  try {
    const res = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    });

    if (!res.ok) {
      let errMsg = 'Upload failed';
      try {
        const errData = await res.json();
        errMsg = errData.detail || errMsg;
      } catch {
        const rawText = await res.text();
        errMsg = rawText || errMsg;
      }
      throw new Error(errMsg);
    }

    const result = await res.json();
    alert(`Successfully ingested ${selectedFile.name}!\nPages: ${result.pages_processed}\nFacts: ${result.facts_extracted}\nTotal Reconciled Verdicts: ${result.total_verdicts}`);
    closeUploadModal();
    fetchState();
  } catch (err) {
    alert(`Upload failed: ${err.message}`);
  } finally {
    btn.disabled = false;
    document.getElementById('uploadProgress').classList.add('hidden');
  }
}
