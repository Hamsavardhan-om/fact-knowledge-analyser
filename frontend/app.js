/**
 * Epistemic Fact Knowledge Layer (EFKL) - Reactive Frontend Controller
 */

let currentState = null;
let currentDocuments = [];
let currentView = 'landing'; // 'landing' | 'reconcile' | 'documents' | 'facts'
let currentFilter = 'ALL';
let searchQuery = '';
let factsSearchQuery = '';
let selectedFile = null;
let expandedDocIds = new Set();

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
  switchView('landing');
  fetchState();
  fetchDocuments();
  initAmbientBackground();

  // Press Enter anywhere on the landing page to proceed
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && currentView === 'landing') {
      const activeEl = document.activeElement;
      // Only proceed if user is not typing in an input/textarea
      if (activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA')) {
        return;
      }
      switchView('reconcile');
    }
  });
});

async function fetchState() {
  try {
    const res = await fetch('/api/state');
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    currentState = await res.json();
    renderDashboard();
    renderFactsView();
    updateNavCounts();
  } catch (err) {
    console.error('Failed to fetch state:', err);
    const container = document.getElementById('verdictsList');
    if (container) {
      container.innerHTML = `
        <div class="verdict-card" style="border-color: #EF4444;">
          <h4 style="color: #EF4444; margin-bottom: 0.5rem;">Connection Error</h4>
          <p style="color: #64748B; font-size: 0.85rem;">Could not connect to EFKL backend. Ensure FastAPI server is running.</p>
        </div>
      `;
    }
  }
}

async function fetchDocuments() {
  try {
    const res = await fetch('/api/documents');
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    currentDocuments = await res.json();
    renderDocumentsView();
    updateNavCounts();
  } catch (err) {
    console.error('Failed to fetch documents:', err);
  }
}

function updateNavCounts() {
  const docCount = currentDocuments.length || (currentState ? currentState.documents.length : 0);
  const factCount = currentState ? currentState.total_facts : 0;
  
  const navDoc = document.getElementById('navDocCount');
  const navFact = document.getElementById('navFactCount');
  if (navDoc) navDoc.textContent = docCount;
  if (navFact) navFact.textContent = factCount;
}

function switchView(viewName) {
  currentView = viewName;
  const isLanding = (viewName === 'landing');

  // Toggle navbar links & controls: HIDDEN on landing, visible in knowledge layer
  const mainNavbar = document.getElementById('mainNavbar');
  const mainNavLinks = document.getElementById('mainNavLinks');
  const mainNavControls = document.getElementById('mainNavControls');

  if (mainNavbar) mainNavbar.classList.toggle('landing-navbar', isLanding);
  if (mainNavLinks) mainNavLinks.classList.toggle('hidden', isLanding);
  if (mainNavControls) mainNavControls.classList.toggle('hidden', isLanding);

  // Update navbar links active state
  const navLanding = document.getElementById('navLanding');
  const navReconcile = document.getElementById('navReconcile');
  const navDocuments = document.getElementById('navDocuments');
  const navFacts = document.getElementById('navFacts');

  if (navLanding) navLanding.classList.toggle('active', viewName === 'landing');
  if (navReconcile) navReconcile.classList.toggle('active', viewName === 'reconcile');
  if (navDocuments) navDocuments.classList.toggle('active', viewName === 'documents');
  if (navFacts) navFacts.classList.toggle('active', viewName === 'facts');

  // Toggle view sections
  const viewLanding = document.getElementById('viewLanding');
  const viewReconcile = document.getElementById('viewReconcile');
  const viewDocuments = document.getElementById('viewDocuments');
  const viewFacts = document.getElementById('viewFacts');
  const metricsSection = document.getElementById('metricsSection');

  if (viewLanding) viewLanding.classList.toggle('hidden', !isLanding);
  if (viewReconcile) viewReconcile.classList.toggle('hidden', viewName !== 'reconcile');
  if (viewDocuments) viewDocuments.classList.toggle('hidden', viewName !== 'documents');
  if (viewFacts) viewFacts.classList.toggle('hidden', viewName !== 'facts');

  // Metrics banner is hidden on landing page, shown on explorer views
  if (metricsSection) {
    metricsSection.classList.toggle('hidden', isLanding);
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });

  if (viewName === 'documents') {
    fetchDocuments();
  } else if (viewName === 'facts') {
    renderFactsView();
  } else if (viewName === 'reconcile') {
    renderDashboard();
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

/* Render Ingested Documents Page */
function renderDocumentsView() {
  const container = document.getElementById('documentsList');
  if (!container) return;

  if (currentDocuments.length === 0) {
    container.innerHTML = `
      <div class="doc-card" style="text-align: center; padding: 3rem;">
        <p style="color: #94A3B8;">No documents ingested yet. Upload a PDF to begin knowledge extraction.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = currentDocuments.map(doc => {
    const isExpanded = expandedDocIds.has(doc.document_id);
    const sizeKb = (doc.file_size_bytes / 1024).toFixed(1);
    const dateFormatted = new Date(doc.upload_timestamp).toLocaleString([], {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });

    let factsListHtml = '';
    if (isExpanded) {
      if (!doc.facts || doc.facts.length === 0) {
        factsListHtml = `
          <div class="doc-facts-box">
            <p style="color: #94A3B8; font-size: 0.82rem;">No facts extracted or verified for this document yet.</p>
          </div>
        `;
      } else {
        const items = doc.facts.map(f => `
          <div class="fact-item-card">
            <div class="fact-item-header">
              <span class="fact-item-title">${f.entity} &bull; ${f.attribute}</span>
              <span class="page-badge">Page ${f.page_number}</span>
            </div>
            <div style="display: flex; gap: 0.5rem; margin-bottom: 0.4rem; align-items: center;">
              <span class="fact-item-val">${f.value_raw}</span>
              ${f.temporal_anchor ? `<span class="tag">⏱️ ${f.temporal_anchor}</span>` : ''}
              ${f.scope ? `<span class="tag">🔍 ${f.scope}</span>` : ''}
            </div>
            <div class="evidence-quote">
              "${f.quote}"
            </div>
            <button class="btn-audit" style="margin-top: 0.4rem;" onclick="auditFact('${f.id}')">
              🔬 Audit Quote Provenance
            </button>
          </div>
        `).join('');

        factsListHtml = `
          <div class="doc-facts-box">
            <h4>
              <span>Extracted Epistemic Fact Atoms (${doc.facts.length})</span>
              <span style="font-size: 0.72rem; color: #94A3B8; text-transform: none;">Click any fact to audit provenance</span>
            </h4>
            ${items}
          </div>
        `;
      }
    }

    return `
      <div class="doc-card" id="doc-${doc.document_id}">
        <div class="doc-card-header">
          <div class="doc-card-title-group">
            <div class="doc-file-icon">📄</div>
            <div>
              <h3 class="doc-card-title">${doc.document_id}</h3>
              <div class="doc-card-sub">
                <span>📅 Ingested: ${dateFormatted}</span>
                <span>📦 Size: ${sizeKb} KB</span>
              </div>
            </div>
          </div>
          <div class="doc-meta-pills">
            <span class="meta-pill">📄 ${doc.total_pages} Pages</span>
            <span class="meta-pill meta-pill-highlight">⚡ ${doc.extracted_facts_count} Facts</span>
            <span class="meta-pill">✓ Grounded</span>
          </div>
        </div>
        <div class="doc-actions">
          <button class="btn btn-sm btn-outline" onclick="toggleDocFacts('${doc.document_id}')">
            ${isExpanded ? '▲ Hide Extracted Facts' : `▼ Inspect Extracted Facts (${doc.extracted_facts_count})`}
          </button>
        </div>
        ${factsListHtml}
      </div>
    `;
  }).join('');
}

function toggleDocFacts(docId) {
  if (expandedDocIds.has(docId)) {
    expandedDocIds.delete(docId);
  } else {
    expandedDocIds.add(docId);
  }
  renderDocumentsView();
}

/* Render All Facts Registry View */
function renderFactsView() {
  const container = document.getElementById('factsTableContainer');
  if (!container || !currentState) return;

  let facts = currentState.all_facts || [];
  if (factsSearchQuery.trim()) {
    const q = factsSearchQuery.toLowerCase();
    facts = facts.filter(f => 
      f.entity.toLowerCase().includes(q) ||
      f.attribute.toLowerCase().includes(q) ||
      f.value_raw.toLowerCase().includes(q) ||
      f.quote.toLowerCase().includes(q) ||
      f.document_id.toLowerCase().includes(q)
    );
  }

  if (facts.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 3rem;">
        <p style="color: #94A3B8;">No facts found matching search query.</p>
      </div>
    `;
    return;
  }

  const rows = facts.map(f => `
    <tr>
      <td style="font-family: var(--font-mono); font-size: 0.78rem; color: #38BDF8;">${f.id}</td>
      <td style="font-weight: 600;">${f.entity}</td>
      <td>${f.attribute}</td>
      <td style="font-family: var(--font-mono); font-weight: 700; color: #38BDF8;">${f.value_raw}</td>
      <td><span class="tag">${f.temporal_anchor || '—'}</span></td>
      <td><span class="tag">${f.scope || '—'}</span></td>
      <td style="max-width: 280px; font-size: 0.8rem; font-style: italic; color: #94A3B8;">"${f.quote}"</td>
      <td>
        <span class="page-badge">P${f.page_number}</span>
        <div style="font-size: 0.72rem; color: #64748B; margin-top: 2px;">${f.document_id}</div>
      </td>
      <td>
        <button class="btn-audit" onclick="auditFact('${f.id}')">Audit</button>
      </td>
    </tr>
  `).join('');

  container.innerHTML = `
    <table class="data-table">
      <thead>
        <tr>
          <th>Fact ID</th>
          <th>Entity</th>
          <th>Attribute</th>
          <th>Value</th>
          <th>Temporal</th>
          <th>Scope</th>
          <th>Evidence Quote</th>
          <th>Document</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
    </table>
  `;
}

function handleFactsSearch() {
  factsSearchQuery = document.getElementById('factsSearchInput').value;
  renderFactsView();
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
    fetchDocuments();
    showToast(`Loaded ${datasetName} benchmark!`);
  } catch (err) {
    showToast(`Error: ${err.message}`);
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
    closeUploadModal();
    
    // Automatically expand the newly uploaded document
    expandedDocIds.add(selectedFile.name);

    // Refresh state and documents list
    await fetchState();
    await fetchDocuments();

    // Switch to dedicated Ingested Documents page!
    switchView('documents');

    showToast(`Successfully ingested "${selectedFile.name}"! (${result.pages_processed} pages, ${result.facts_extracted} facts)`);
  } catch (err) {
    showToast(`Upload failed: ${err.message}`);
  } finally {
    btn.disabled = false;
    document.getElementById('uploadProgress').classList.add('hidden');
  }
}

function showToast(message) {
  const toast = document.getElementById('toastNotification');
  const msgEl = document.getElementById('toastMessage');
  if (!toast || !msgEl) return;

  msgEl.textContent = message;
  toast.classList.remove('hidden');

  setTimeout(() => {
    toast.classList.add('hidden');
  }, 4500);
}

/* ==========================================================================
   Passive Epistemic Knowledge Graph Canvas (Continuous across ALL pages)
   ========================================================================== */
let ambientAnimationId = null;
let ambientNodes = [];
let ambientMouse = { x: -9999, y: -9999, radius: 150 };
let ambientCanvasInitialized = false;

function initAmbientBackground() {
  const canvas = document.getElementById('ambientBackgroundCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let width = 0;
  let height = 0;

  function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);
    createNodes();
  }

  function createNodes() {
    ambientNodes = [];
    const count = Math.min(65, Math.max(35, Math.floor((width * height) / 20000)));
    const colors = [
      '#38BDF8', // Sky / Claim
      '#10B981', // Emerald / Grounded
      '#818CF8', // Indigo / Entity
      '#F59E0B', // Amber / Dialectic
      '#94A3B8'  // Slate / Provenance
    ];

    for (let i = 0; i < count; i++) {
      ambientNodes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        baseRadius: Math.random() * 2.2 + 1.8,
        color: colors[Math.floor(Math.random() * colors.length)],
        pulsePhase: Math.random() * Math.PI * 2,
        pulseSpeed: 0.02 + Math.random() * 0.02,
        hasRing: Math.random() > 0.6,
        driftPhase: Math.random() * Math.PI * 2
      });
    }
  }

  if (!ambientCanvasInitialized) {
    window.addEventListener('resize', resize);
    window.addEventListener('mousemove', (e) => {
      ambientMouse.x = e.clientX;
      ambientMouse.y = e.clientY;
    });
    window.addEventListener('mouseleave', () => {
      ambientMouse.x = -9999;
      ambientMouse.y = -9999;
    });
    ambientCanvasInitialized = true;
  }

  resize();

  let lastTime = performance.now();

  function render(now) {
    const dt = Math.min(32, now - lastTime) / 16.66;
    lastTime = now;

    ctx.clearRect(0, 0, width, height);

    const len = ambientNodes.length;

    // Update and draw nodes
    for (let i = 0; i < len; i++) {
      const n = ambientNodes[i];
      n.pulsePhase += n.pulseSpeed * dt;
      n.driftPhase += 0.008 * dt;

      // Gentle floating physics + subtle harmonic sway
      n.x += (n.vx + Math.sin(n.driftPhase) * 0.12) * dt;
      n.y += (n.vy + Math.cos(n.driftPhase * 0.8) * 0.12) * dt;

      if (n.x < -20) n.x = width + 20;
      if (n.x > width + 20) n.x = -20;
      if (n.y < -20) n.y = height + 20;
      if (n.y > height + 20) n.y = -20;

      // Mouse proximity interaction (soft repulsion / magnetic glide)
      const dxM = ambientMouse.x - n.x;
      const dyM = ambientMouse.y - n.y;
      const distM = Math.hypot(dxM, dyM);
      if (distM < ambientMouse.radius && distM > 0) {
        const force = (1 - distM / ambientMouse.radius) * 1.0;
        n.x -= (dxM / distM) * force * dt;
        n.y -= (dyM / distM) * force * dt;
      }

      // Draw node core
      const pulseFactor = 1 + Math.sin(n.pulsePhase) * 0.15;
      const r = n.baseRadius * pulseFactor;
      ctx.beginPath();
      ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
      ctx.fillStyle = n.color;
      ctx.globalAlpha = 0.7;
      ctx.fill();

      // Outer halo/ring
      if (n.hasRing) {
        const ringR = r + 3.2 + Math.sin(n.pulsePhase) * 1.8;
        ctx.beginPath();
        ctx.arc(n.x, n.y, ringR, 0, Math.PI * 2);
        ctx.strokeStyle = n.color;
        ctx.lineWidth = 0.75;
        ctx.globalAlpha = 0.22;
        ctx.stroke();
      }

      // Draw connecting constellation lines
      for (let j = i + 1; j < len; j++) {
        const n2 = ambientNodes[j];
        const dx = n.x - n2.x;
        const dy = n.y - n2.y;
        const dist = Math.hypot(dx, dy);
        const maxDist = 130;

        if (dist < maxDist) {
          const alpha = (1 - dist / maxDist) * 0.18;
          ctx.beginPath();
          ctx.moveTo(n.x, n.y);
          ctx.lineTo(n2.x, n2.y);
          ctx.strokeStyle = '#94A3B8';
          ctx.globalAlpha = alpha;
          ctx.lineWidth = 0.75;
          ctx.stroke();
        }
      }

      // Cursor connection line
      if (distM < 120) {
        const alpha = (1 - distM / 120) * 0.28;
        ctx.beginPath();
        ctx.moveTo(n.x, n.y);
        ctx.lineTo(ambientMouse.x, ambientMouse.y);
        ctx.strokeStyle = '#38BDF8';
        ctx.globalAlpha = alpha;
        ctx.lineWidth = 0.85;
        ctx.stroke();
      }
    }

    ctx.globalAlpha = 1.0;
    ambientAnimationId = requestAnimationFrame(render);
  }

  if (ambientAnimationId) {
    cancelAnimationFrame(ambientAnimationId);
  }
  ambientAnimationId = requestAnimationFrame(render);
}

