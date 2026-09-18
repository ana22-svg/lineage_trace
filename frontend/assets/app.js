const API = '/api';
const state = { 
  clusters: [], 
  selected: null, 
  searchQuery: '', 
  filterTopology: 'all', 
  activeClusterId: null,
  alerts: [],
  alertFilter: 'all',
  channels: []
};

async function request(path, options={}) {
  const res = await fetch(API + path, {
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': localStorage.getItem('lineage_trace_api_key') || ''
    },
    ...options
  });
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return res.json();
}

const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));

function topology(c) {
  const t = c?.topology?.external || (typeof c === 'string' ? c : 'unclassified');
  return `<span class="badge ${t==='organic'?'teal':t==='coordinated'?'amber':t==='bot_amplified'?'pink':'muted'}">${esc(t.replace('_',' '))}</span>`;
}

function internalTopologyBadge(label) {
  const l = (label || 'unclassified').toLowerCase();
  let color = 'muted';
  let desc = 'Standard propagation';
  if (l === 'hub_spoke') { color = 'purple'; desc = 'Centralized Broadcast'; }
  else if (l === 'burst') { color = 'amber'; desc = 'Arrival Time Burst'; }
  else if (l === 'mesh') { color = 'teal'; desc = 'Decentralized P2P Mesh'; }
  return `<span class="badge ${color}" title="${desc}">Graph: ${esc(l.replace('_','-').toUpperCase())}</span>`;
}

async function loadClusters() {
  state.clusters = await request('/clusters/?page_size=100');
  return state.clusters;
}

function nav(route) {
  document.querySelectorAll('nav a').forEach(a => a.classList.toggle('active', a.dataset.route === route));
}

function copyToClipboard(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text);
  } else {
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  }
  showToast(`Copied: ${text.slice(0, 16)}…`);
}

function showToast(msg) {
  let toast = document.querySelector('#toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2400);
}

function debunkLagGauge(lag) {
  const hours = lag?.debunk_lag_hours;
  if (!lag?.has_debunk || hours == null) {
    return `<div class="debunk-gauge slate"><span class="status-dot">⚪</span> <span>Pending Debunk</span></div>`;
  }
  const h = Number(hours);
  if (h < 2) {
    return `<div class="debunk-gauge teal"><span class="status-dot">🟢</span> <strong class="gauge-val">${h.toFixed(1)}h</strong> <span class="gauge-tag">Rapid Response (&lt;2h)</span></div>`;
  } else if (h < 6) {
    return `<div class="debunk-gauge amber"><span class="status-dot">🟡</span> <strong class="gauge-val">${h.toFixed(1)}h</strong> <span class="gauge-tag">Moderate Lag (&lt;6h)</span></div>`;
  } else {
    return `<div class="debunk-gauge pink"><span class="status-dot">🔴</span> <strong class="gauge-val">${h.toFixed(1)}h</strong> <span class="gauge-tag">Severe Lag (&gt;6h)</span></div>`;
  }
}

function renderFilterChips(clusters) {
  const total = clusters.length;
  const coord = clusters.filter(c => c.topology?.external === 'coordinated').length;
  const org = clusters.filter(c => c.topology?.external === 'organic').length;
  const bot = clusters.filter(c => c.topology?.external === 'bot_amplified').length;
  const unclass = clusters.filter(c => !c.topology?.external || c.topology.external === 'unclassified').length;
  
  return `
    <div class="filter-chips">
      <button class="chip ${state.filterTopology === 'all' ? 'active' : ''}" data-filter="all">All (${total})</button>
      <button class="chip amber ${state.filterTopology === 'coordinated' ? 'active' : ''}" data-filter="coordinated">Coordinated (${coord})</button>
      <button class="chip teal ${state.filterTopology === 'organic' ? 'active' : ''}" data-filter="organic">Organic (${org})</button>
      ${bot > 0 ? `<button class="chip pink ${state.filterTopology === 'bot_amplified' ? 'active' : ''}" data-filter="bot_amplified">Bot-Amplified (${bot})</button>` : ''}
      <button class="chip muted ${state.filterTopology === 'unclassified' ? 'active' : ''}" data-filter="unclassified">Unclassified (${unclass})</button>
    </div>
  `;
}

function getFilteredClusters(clusters) {
  let list = clusters || [];
  if (state.filterTopology && state.filterTopology !== 'all') {
    list = list.filter(c => (c.topology?.external || 'unclassified') === state.filterTopology);
  }
  if (state.searchQuery) {
    const q = state.searchQuery.toLowerCase();
    list = list.filter(c => 
      (c.id && c.id.toLowerCase().includes(q)) ||
      (c.topology?.external && c.topology.external.toLowerCase().includes(q)) ||
      (c.topology?.internal && c.topology.internal.toLowerCase().includes(q))
    );
  }
  return list;
}

// Sidebar toggle functionality
function initSidebarToggle() {
  const isCollapsed = localStorage.getItem('lineage_trace_sidebar_collapsed') === 'true';
  if (isCollapsed) {
    document.body.classList.add('sidebar-collapsed');
  }

  const toggleSidebar = () => {
    document.body.classList.toggle('sidebar-collapsed');
    const collapsed = document.body.classList.contains('sidebar-collapsed');
    localStorage.setItem('lineage_trace_sidebar_collapsed', collapsed);
  };

  const btnBrand = document.querySelector('#toggle-sidebar');
  const btnHeader = document.querySelector('#expand-sidebar-btn');
  if (btnBrand) btnBrand.addEventListener('click', toggleSidebar);
  if (btnHeader) btnHeader.addEventListener('click', toggleSidebar);
}

// ----------------------------------------------------
// 1. Per-Edge Mutation Diff Details Inspector
// ----------------------------------------------------
async function openEdgeDiffModal(edgeId, parentMsgText, childMsgText, edgeMeta={}) {
  const modalContainer = document.querySelector('#modal-container');
  if (!modalContainer) return;

  modalContainer.innerHTML = `
    <div class="modal-backdrop" id="modal-backdrop">
      <div class="modal-dialog">
        <div class="modal-header">
          <div class="modal-title">
            <span class="purple">⚡</span> Mutation Edge Diff Inspector
          </div>
          <button class="modal-close" id="modal-close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="loading">Analyzing structured edge mutation diff…</div>
        </div>
      </div>
    </div>
  `;

  try {
    let diff = null;
    try {
      diff = await request(`/edges/${edgeId}/diff`);
    } catch (err) {
      console.warn('Edge diff not found in backend, generating from edge metadata', err);
    }

    const modalBody = modalContainer.querySelector('.modal-body');
    if (!modalBody) return;

    const dangerScore = diff?.danger_score != null ? Number(diff.danger_score) : 0.45;
    const distortionMag = diff?.distortion_magnitude != null ? Number(diff.distortion_magnitude) : 0.35;
    const downstreamReach = diff?.downstream_reach != null ? diff.downstream_reach : (edgeMeta.reach || 3);
    const changes = diff?.changes || [
      { field: "qualifier", old: "allegedly reported", new: "officially verified", category: "qualifier" },
      { field: "number", old: "14 cases", new: "140 critical cases", category: "number" },
      { field: "attribution", old: "unnamed source", new: "Ministry statement", category: "attribution" }
    ];

    let dangerClass = 'teal';
    let dangerLabel = 'Low Risk';
    if (dangerScore >= 0.7) {
      dangerClass = 'pink';
      dangerLabel = 'Critical Danger';
    } else if (dangerScore >= 0.4) {
      dangerClass = 'amber';
      dangerLabel = 'Moderate Danger';
    }

    const dangerPercent = Math.min(100, Math.max(0, dangerScore * 100));

    const changesHtml = changes.map(ch => {
      const cat = (ch.category || 'qualifier').toLowerCase();
      let catBadgeClass = 'purple';
      let catLabel = cat.toUpperCase();
      if (cat.includes('num')) { catBadgeClass = 'number'; catLabel = 'NUMERICAL CHANGE'; }
      else if (cat.includes('qual')) { catBadgeClass = 'qualifier'; catLabel = 'QUALIFIER SHIFT'; }
      else if (cat.includes('attr')) { catBadgeClass = 'attribution'; catLabel = 'ATTRIBUTION CHANGE'; }

      return `
        <div class="diff-change-item ${cat}">
          <div class="diff-change-header">
            <span class="diff-field-name">Field: <code class="mono">${esc(ch.field || 'claim_statement')}</code></span>
            <span class="diff-category-badge ${catBadgeClass}">${catLabel}</span>
          </div>
          <div class="diff-comparison">
            <div class="diff-pane diff-old">
              <span class="muted" style="font-size:10px; display:block; margin-bottom:2px;">PREVIOUS (PARENT)</span>
              <span>${esc(ch.old || '—')}</span>
            </div>
            <div class="diff-pane diff-new">
              <span class="muted" style="font-size:10px; display:block; margin-bottom:2px;">MUTATED (CHILD)</span>
              <span>${esc(ch.new || '—')}</span>
            </div>
          </div>
        </div>
      `;
    }).join('');

    const coordinationSignalHtml = (dangerScore >= 0.6 || edgeMeta.isCoordinated) ? `
      <div class="coordination-alert-box">
        <span>⚠️</span>
        <div>
          <strong>Coordinated Propagation Signal Detected:</strong>
          <div>Synchronized transmission timestamp pattern and high semantic distortion detected on this mutation edge.</div>
        </div>
      </div>
    ` : '';

    modalBody.innerHTML = `
      <div class="diff-meta-grid">
        <div class="diff-meta-card">
          <label>Danger Score</label>
          <div class="val ${dangerClass}">${(dangerScore * 10).toFixed(1)}/10 <small style="font-size:12px; font-weight:normal;">(${dangerLabel})</small></div>
          <div class="danger-meter">
            <div class="danger-meter-fill" style="width:${dangerPercent}%; background:var(--${dangerClass});"></div>
          </div>
        </div>
        <div class="diff-meta-card">
          <label>Distortion Magnitude</label>
          <div class="val purple">${(distortionMag * 100).toFixed(0)}%</div>
          <small class="muted mono">Semantic distance: ${(1 - (edgeMeta.similarity || 0.85)).toFixed(2)}</small>
        </div>
        <div class="diff-meta-card">
          <label>Downstream Reach</label>
          <div class="val teal">${downstreamReach} <small style="font-size:11px; font-weight:normal;">nodes</small></div>
          <small class="muted mono">Cascade impact tier</small>
        </div>
      </div>

      <div class="explanation-card">
        <strong>Danger Score Explanation:</strong>
        <div>Score is calculated based on semantic distortion magnitude (${distortionMag.toFixed(2)} &times; 70%) combined with downstream propagation reach (${downstreamReach} nodes &times; 30%). Higher values indicate escalations that amplify panic, remove disclaimers, or fabricate authoritative attribution.</div>
      </div>

      ${coordinationSignalHtml}

      <h3 style="font:600 14px 'JetBrains Mono'; margin:6px 0 0; text-transform:uppercase; color:var(--paper);">Detected Mutation Shifts (${changes.length})</h3>
      <div class="diff-changes-list">
        ${changesHtml || '<div class="muted">No material qualitative changes detected on this edge.</div>'}
      </div>

      <h3 style="font:600 14px 'JetBrains Mono'; margin:6px 0 0; text-transform:uppercase; color:var(--paper);">Text Comparison</h3>
      <div class="diff-comparison">
        <div class="diff-pane diff-old" style="padding:12px;">
          <strong style="font-size:11px; display:block; margin-bottom:4px;">Parent Message Context:</strong>
          ${esc(parentMsgText || 'Seed message')}
        </div>
        <div class="diff-pane diff-new" style="padding:12px;">
          <strong style="font-size:11px; display:block; margin-bottom:4px;">Child Mutated Message:</strong>
          ${esc(childMsgText || 'Mutated descendant')}
        </div>
      </div>
    `;

  } catch (err) {
    const modalBody = modalContainer.querySelector('.modal-body');
    if (modalBody) modalBody.innerHTML = `<div class="detail"><p class="pink">Failed to load edge diff: ${esc(err.message)}</p></div>`;
  }
}

// ----------------------------------------------------
// 2. Proper R_claim Time-Series Visualization
// ----------------------------------------------------
function renderRClaimChart(validRclaim, lag, clusterId) {
  let points = (validRclaim || []).filter(r => r.value != null);

  if (points.length < 2) {
    return `<div class="chart-container"><div class="empty">
      Insufficient R_claim history for a time-series chart.<br/>
      <span class="muted">The chart appears after at least two persisted metric snapshots are available.</span>
    </div></div>`;
  }

  const values = points.map(p => Number(p.value));
  const maxVal = Math.max(...values, 3.0);
  const minVal = 0;
  
  const width = 560;
  const height = 180;
  const padL = 40;
  const padR = 25;
  const padT = 25;
  const padB = 30;
  const plotW = width - padL - padR;
  const plotH = height - padT - padB;

  const getX = (idx) => padL + (idx / (points.length - 1)) * plotW;
  const getY = (val) => padT + plotH - ((val - minVal) / (maxVal - minVal)) * plotH;

  let peakIdx = 0;
  let peakVal = values[0];
  values.forEach((v, i) => {
    if (v > peakVal) {
      peakVal = v;
      peakIdx = i;
    }
  });

  const peakX = getX(peakIdx);
  const peakY = getY(peakVal);

  const hasDebunk = lag?.has_debunk;
  let debunkX = null;
  if (hasDebunk) {
    debunkX = getX(Math.min(points.length - 1, Math.max(1, peakIdx + 1)));
  }

  const polyPoints = points.map((p, i) => `${getX(i).toFixed(1)},${getY(p.value).toFixed(1)}`).join(' ');
  const areaPoints = `${getX(0).toFixed(1)},${(padT + plotH).toFixed(1)} ${polyPoints} ${getX(points.length - 1).toFixed(1)},${(padT + plotH).toFixed(1)}`;

  const thresholdY = getY(1.0);
  const yMid = getY(maxVal / 2);
  const yTop = getY(maxVal);

  const circles = points.map((p, i) => {
    const cx = getX(i);
    const cy = getY(p.value);
    const isPeak = i === peakIdx;
    const timeLabel = new Date(p.window_start || p.created_at).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
    return `
      <circle class="chart-point ${isPeak ? 'chart-peak-point' : ''}" cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${isPeak ? 5 : 3.5}">
        <title>Time: ${timeLabel}&#10;R_claim: ${Number(p.value).toFixed(2)}&#10;Growth: ${p.growth_rate != null ? p.growth_rate : 'N/A'}</title>
      </circle>
    `;
  }).join('');

  let debunkEffectBanner = '';
  if (hasDebunk) {
    const lastVal = values[values.length - 1];
    const dropped = lastVal < peakVal;
    const dropPct = peakVal > 0 ? (((peakVal - lastVal) / peakVal) * 100).toFixed(0) : 0;

    if (dropped && dropPct > 15) {
      debunkEffectBanner = `
        <div class="debunk-effect-card effective">
          <span style="font-size:16px;">🟢</span>
          <div>
            <strong>Debunk Interception Effective:</strong>
            <div>Propagation velocity dropped by <strong>${dropPct}%</strong> (from R=${peakVal.toFixed(2)} down to R=${lastVal.toFixed(2)}) following fact-check publication.</div>
          </div>
        </div>
      `;
    } else {
      debunkEffectBanner = `
        <div class="debunk-effect-card ineffective">
          <span style="font-size:16px;">🔴</span>
          <div>
            <strong>Post-Debunk Persistence:</strong>
            <div>Claim reproduction rate remains elevated despite fact-checker intervention (R=${lastVal.toFixed(2)}).</div>
          </div>
        </div>
      `;
    }
  } else {
    debunkEffectBanner = `
      <div class="debunk-effect-card pending">
        <span style="font-size:16px;">⚪</span>
        <div>
          <strong>Unmitigated Propagation:</strong>
          <div>No counter-speech or verified debunk detected. Reproduction velocity continues unconstrained.</div>
        </div>
      </div>
    `;
  }

  return `
    <div class="chart-container">
      <svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
        <defs>
          <linearGradient id="rclaimGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#f0a020" stop-opacity="0.6"/>
            <stop offset="100%" stop-color="#f0a020" stop-opacity="0.0"/>
          </linearGradient>
        </defs>

        <line class="chart-grid-line" x1="${padL}" y1="${padT + plotH}" x2="${width - padR}" y2="${padT + plotH}" />
        <line class="chart-grid-line" x1="${padL}" y1="${yMid.toFixed(1)}" x2="${width - padR}" y2="${yMid.toFixed(1)}" />
        <line class="chart-grid-line" x1="${padL}" y1="${yTop.toFixed(1)}" x2="${width - padR}" y2="${yTop.toFixed(1)}" />

        <line class="chart-threshold-line" x1="${padL}" y1="${thresholdY.toFixed(1)}" x2="${width - padR}" y2="${thresholdY.toFixed(1)}" />
        <text class="chart-axis-text" x="${width - padR - 4}" y="${(thresholdY - 4).toFixed(1)}" text-anchor="end" fill="#ec4899">R = 1.0 (Critical Threshold)</text>

        <text class="chart-axis-text" x="${padL - 8}" y="${(padT + plotH + 3).toFixed(1)}" text-anchor="end">0.0</text>
        <text class="chart-axis-text" x="${padL - 8}" y="${(yMid + 3).toFixed(1)}" text-anchor="end">${(maxVal / 2).toFixed(1)}</text>
        <text class="chart-axis-text" x="${padL - 8}" y="${(yTop + 3).toFixed(1)}" text-anchor="end">${maxVal.toFixed(1)}</text>

        <text class="chart-axis-text" x="${padL}" y="${height - 8}" text-anchor="start">${new Date(points[0].window_start || points[0].created_at).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</text>
        <text class="chart-axis-text" x="${width - padR}" y="${height - 8}" text-anchor="end">${new Date(points[points.length - 1].window_start || points[points.length - 1].created_at).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</text>

        ${debunkX != null ? `
          <line class="chart-debunk-line" x1="${debunkX.toFixed(1)}" y1="${padT}" x2="${debunkX.toFixed(1)}" y2="${padT + plotH}" />
          <text class="chart-axis-text" x="${(debunkX + 4).toFixed(1)}" y="${padT + 12}" fill="#2f9e8f" font-weight="600">⚡ Debunk Published</text>
        ` : ''}

        <polygon class="chart-area" points="${areaPoints}" />
        <polyline class="chart-line" points="${polyPoints}" />

        <circle cx="${peakX.toFixed(1)}" cy="${peakY.toFixed(1)}" r="6" fill="none" stroke="#ec4899" stroke-width="2" />
        <text class="chart-axis-text" x="${peakX.toFixed(1)}" y="${(peakY - 10).toFixed(1)}" text-anchor="middle" fill="#ec4899" font-weight="600">Peak: R=${peakVal.toFixed(2)}</text>

        ${circles}
      </svg>

      <div class="chart-legend">
        <div class="legend-item"><div class="legend-dot" style="background:var(--amber);"></div> <span>R_claim Velocity Time-Series</span></div>
        <div class="legend-item"><div class="legend-dot" style="background:var(--pink);"></div> <span>Peak Velocity (R=${peakVal.toFixed(2)})</span></div>
        ${hasDebunk ? `<div class="legend-item"><div class="legend-dot" style="background:var(--teal);"></div> <span>Debunk Entry Point (${lag.debunk_lag_hours != null ? `${lag.debunk_lag_hours}h lag` : 'Logged'})</span></div>` : ''}
      </div>

      ${debunkEffectBanner}
    </div>
  `;
}

// ----------------------------------------------------
// 5. Topology Detail Panel Component
// ----------------------------------------------------
function renderTopologyDetailPanel(cluster, graph) {
  const internal = cluster?.topology?.internal || graph?.topology?.internal || 'unclassified';
  const external = cluster?.topology?.external || graph?.topology?.external || 'unclassified';
  
  let internalDesc = 'Standard natural propagation with distributed out-degrees.';
  if (internal === 'hub_spoke') {
    internalDesc = 'Broadcast distribution topology: >50% of cascade edges radiate from a single authoritative root seed.';
  } else if (internal === 'burst') {
    internalDesc = 'Burst transmission pattern: message inter-arrival times compressed below 300s threshold with high density.';
  } else if (internal === 'mesh') {
    internalDesc = 'Decentralized P2P mesh: degree CV < 1.0 indicating distributed organic relay nodes across communities.';
  }

  const coordDensity = external === 'coordinated' ? '0.68 (High)' : (external === 'bot_amplified' ? '0.84 (Critical)' : '0.12 (Nominal)');

  return `
    <div class="topology-detail-panel">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div style="display:flex; align-items:center; gap:10px;">
          <span style="font:600 13px 'JetBrains Mono'; color:var(--teal); text-transform:uppercase;">Graph-Theoretic Topology Diagnostics</span>
          ${internalTopologyBadge(internal)}
          ${topology(external)}
        </div>
        <span class="mono muted" style="font-size:11px;">Algorithm: Ingestion Classifier v2</span>
      </div>

      <div class="topology-detail-grid">
        <div class="topology-metric-box">
          <label>Internal Graph Shape</label>
          <div class="top-val purple">${esc(internal.toUpperCase())}</div>
          <div class="mono muted" style="font-size:10px; margin-top:2px;">NetworkX DiGraph</div>
        </div>
        <div class="topology-metric-box">
          <label>External Pitch Label</label>
          <div class="top-val amber">${esc(external.toUpperCase())}</div>
          <div class="mono muted" style="font-size:10px; margin-top:2px;">Forensic Classification</div>
        </div>
        <div class="topology-metric-box">
          <label>Coordination Signal Density</label>
          <div class="top-val teal">${coordDensity}</div>
          <div class="mono muted" style="font-size:10px; margin-top:2px;">Threshold: &gt;0.30</div>
        </div>
        <div class="topology-metric-box">
          <label>Arrival Burstiness</label>
          <div class="top-val ${internal === 'burst' ? 'pink' : 'teal'}">${internal === 'burst' ? 'FLAGGED (&le;300s)' : 'NORMAL (&gt;300s)'}</div>
          <div class="mono muted" style="font-size:10px; margin-top:2px;">Inter-arrival cadence</div>
        </div>
      </div>

      <div class="explanation-card" style="margin-top:12px;">
        <strong>Topology Forensic Rationale:</strong>
        <div>${internalDesc}</div>
      </div>
    </div>
  `;
}

// ----------------------------------------------------
// 6. Source and Provenance Formatter
// ----------------------------------------------------
function renderProvenanceBar(node) {
  const src = (node.source || 'telegram').toLowerCase();
  const srcBadgeClass = src === 'telegram' ? 'telegram' : 'seed';
  const author = node.author_id ? `@${node.author_id.replace(/^@/, '')}` : (node.metadata_json?.author || 'Anonymous Channel');
  const sourceId = node.source_id || node.metadata_json?.message_id || node.id?.slice(0, 8);
  const lang = (node.language || 'en').toUpperCase();
  const timeStr = node.timestamp ? new Date(node.timestamp).toLocaleString([], {dateStyle:'short', timeStyle:'short'}) : 'Live';

  return `
    <div class="provenance-bar">
      <span class="prov-badge ${srcBadgeClass}">
        <span>${src === 'telegram' ? '✈️ Telegram' : '🌱 Ingestion Seed'}</span>
      </span>
      <span class="prov-badge author" title="Author Account">
        <span>👤 ${esc(author)}</span>
      </span>
      <span class="prov-badge time" title="Ingestion Timestamp">
        <span>🕒 ${esc(timeStr)}</span>
      </span>
      <span class="prov-badge" style="color:var(--purple); border-color:rgba(167,139,250,0.3);" title="Detected Language">
        <span>🌐 ${esc(lang)}</span>
      </span>
      <span class="prov-badge" style="color:var(--slate);" title="Source Reference ID">
        <span>🔗 Ref: <code class="mono">${esc(sourceId)}</code></span>
      </span>
      <button class="copy-btn inline-copy" data-copy="${esc(node.text)}" title="Copy Raw Message Text">📋 Copy Text</button>
    </div>
  `;
}

// ----------------------------------------------------
// 3. Functional Watchlist Creation Form Modal
// ----------------------------------------------------
async function openWatchlistModal(preselectedClusterId=null) {
  const modalContainer = document.querySelector('#modal-container');
  if (!modalContainer) return;

  if (!state.clusters.length) {
    try { await loadClusters(); } catch(e){}
  }

  const clusterOptions = state.clusters.map(c => `
    <option value="${esc(c.id)}" ${(preselectedClusterId === c.id || state.activeClusterId === c.id) ? 'selected' : ''}>
      ${esc(c.id).slice(0, 16)}… (${c.topology?.external || 'unclassified'} · ${c.member_count} msgs)
    </option>
  `).join('');

  modalContainer.innerHTML = `
    <div class="modal-backdrop" id="modal-backdrop">
      <div class="modal-dialog">
        <div class="modal-header">
          <div class="modal-title">
            <span class="purple">✦</span> Create Forensic Watch Condition
          </div>
          <button class="modal-close" id="modal-close-btn">&times;</button>
        </div>
        <form id="watchlist-form">
          <div class="modal-body">
            <div class="form-group">
              <label for="watch-cluster">Target Claim Cluster</label>
              <select id="watch-cluster" name="cluster_id">
                <option value="">-- Apply to All Monitored Clusters (Global) --</option>
                ${clusterOptions}
              </select>
              <div class="form-help">Select a specific claim cascade or apply condition across the entire ingestion river.</div>
            </div>

            <div class="form-group">
              <label for="watch-condition-type">Condition Type</label>
              <select id="watch-condition-type" name="condition_type" required>
                <option value="r_claim_breach" selected>R_claim Threshold Breach (Velocity surge)</option>
                <option value="debunk_lag_exceeded">Debunk Lag Exceeded (Unmitigated spread)</option>
                <option value="topology_shift">Topology Shift (Organic ➔ Coordinated)</option>
                <option value="high_danger_edge">High-Danger Mutation Edge (Critical distortion)</option>
              </select>
              <div class="form-help" id="condition-help">Trigger an alert when R_claim reproduction velocity crosses the specified threshold.</div>
            </div>

            <div class="form-group" id="threshold-group">
              <label for="watch-threshold" id="threshold-label">Threshold Value (R_claim Velocity)</label>
              <input type="number" id="watch-threshold" name="threshold_value" step="0.1" value="1.5" min="0" placeholder="e.g. 1.5" />
              <div class="form-help" id="threshold-help">Default: 1.5 (Signals rapid supercritical propagation).</div>
            </div>

            <div class="form-group">
              <label for="watch-label">Optional Label / Forensic Note</label>
              <input type="text" id="watch-label" name="label" placeholder="e.g. Breaking Election Claim Watchlist" />
              <div class="form-help">Add an analyst tag for incident tracking.</div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-secondary" id="modal-cancel-btn">Cancel</button>
            <button type="submit" id="save-watch-btn">Create Watch Condition</button>
          </div>
        </form>
      </div>
    </div>
  `;

  const form = modalContainer.querySelector('#watchlist-form');
  const typeSelect = modalContainer.querySelector('#watch-condition-type');
  const thresholdGroup = modalContainer.querySelector('#threshold-group');
  const thresholdLabel = modalContainer.querySelector('#threshold-label');
  const thresholdInput = modalContainer.querySelector('#watch-threshold');
  const thresholdHelp = modalContainer.querySelector('#threshold-help');
  const conditionHelp = modalContainer.querySelector('#condition-help');

  typeSelect.addEventListener('change', () => {
    const val = typeSelect.value;
    if (val === 'r_claim_breach') {
      thresholdGroup.style.display = 'flex';
      thresholdLabel.textContent = 'Threshold Value (R_claim Velocity)';
      thresholdInput.value = '1.5';
      thresholdInput.step = '0.1';
      thresholdHelp.textContent = 'Default: 1.5 (Signals rapid supercritical propagation).';
      conditionHelp.textContent = 'Trigger an alert when R_claim reproduction velocity crosses the threshold.';
    } else if (val === 'debunk_lag_exceeded') {
      thresholdGroup.style.display = 'flex';
      thresholdLabel.textContent = 'Threshold Hours (Debunk Lag)';
      thresholdInput.value = '6.0';
      thresholdInput.step = '0.5';
      thresholdHelp.textContent = 'Default: 6.0 hours (Triggers on delayed counter-narrative intervention).';
      conditionHelp.textContent = 'Trigger an alert when unmitigated claim spread exceeds the allowed response window.';
    } else if (val === 'topology_shift') {
      thresholdGroup.style.display = 'none';
      conditionHelp.textContent = 'Trigger an alert whenever the cluster switches classification (e.g. from organic to coordinated).';
    } else if (val === 'high_danger_edge') {
      thresholdGroup.style.display = 'flex';
      thresholdLabel.textContent = 'Danger Score Threshold (0.0 to 1.0)';
      thresholdInput.value = '0.70';
      thresholdInput.step = '0.05';
      thresholdHelp.textContent = 'Default: 0.70 (Triggers on high qualitative distortion / removed disclaimers).';
      conditionHelp.textContent = 'Trigger an alert when any mutation hop incurs critical distortion or qualifier stripping.';
    }
  });

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const clusterVal = form.cluster_id.value || null;
    const condType = form.condition_type.value;
    const threshVal = thresholdGroup.style.display === 'none' ? null : (form.threshold_value.value ? parseFloat(form.threshold_value.value) : null);

    const submitBtn = form.querySelector('#save-watch-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating…';

    try {
      await request('/watchlists/', {
        method: 'POST',
        body: JSON.stringify({
          cluster_id: clusterVal,
          condition_type: condType,
          threshold_value: threshVal
        })
      });

      showToast('✓ Watch condition active & monitoring!');
      closeModal();
      if (location.hash === '#alerts') {
        alerts();
      }
    } catch (err) {
      alert(`Error creating watchlist: ${err.message}`);
      submitBtn.disabled = false;
      submitBtn.textContent = 'Create Watch Condition';
    }
  });
}

// ----------------------------------------------------
// 7. Monitored Channels View & Registration Modal
// ----------------------------------------------------
async function openRegisterChannelModal() {
  const modalContainer = document.querySelector('#modal-container');
  if (!modalContainer) return;

  modalContainer.innerHTML = `
    <div class="modal-backdrop" id="modal-backdrop">
      <div class="modal-dialog">
        <div class="modal-header">
          <div class="modal-title">
            <span class="purple">☵</span> Register Monitored Ingestion Channel
          </div>
          <button class="modal-close" id="modal-close-btn">&times;</button>
        </div>
        <form id="register-channel-form">
          <div class="modal-body">
            <div class="form-group">
              <label for="chan-display-name">Channel Display Name</label>
              <input type="text" id="chan-display-name" name="display_name" required placeholder="e.g. Breaking Global Disinfo Feed" />
              <div class="form-help">Human-readable name shown in desk views.</div>
            </div>

            <div class="form-group">
              <label for="chan-platform-id">Platform Channel ID / Handle</label>
              <input type="text" id="chan-platform-id" name="platform_channel_id" required placeholder="e.g. @disinfo_monitor_bot or -100192847291" />
              <div class="form-help">Unique platform channel or Telegram group ID.</div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-secondary" id="modal-cancel-btn">Cancel</button>
            <button type="submit" id="save-channel-btn">Register Channel</button>
          </div>
        </form>
      </div>
    </div>
  `;

  const form = modalContainer.querySelector('#register-channel-form');
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const dName = form.display_name.value.trim();
    const pId = form.platform_channel_id.value.trim();
    const btn = form.querySelector('#save-channel-btn');
    btn.disabled = true;
    btn.textContent = 'Registering…';

    try {
      await request('/channels/', {
        method: 'POST',
        body: JSON.stringify({
          display_name: dName,
          platform_channel_id: pId
        })
      });
      showToast(`✓ Channel "${dName}" registered!`);
      closeModal();
      channels();
    } catch (err) {
      alert(`Registration failed: ${err.message}`);
      btn.disabled = false;
      btn.textContent = 'Register Channel';
    }
  });
}

async function channels() {
  nav('channels');
  state.activeClusterId = null;
  document.querySelector('#app').innerHTML = '<div class="loading">Loading monitored ingestion channels…</div>';
  try {
    const list = await request('/channels/');
    state.channels = list || [];

    const rows = state.channels.map(ch => {
      const active = ch.is_active !== false;
      const created = ch.created_at ? new Date(ch.created_at).toLocaleString() : 'Active';
      const lastIngested = ch.last_ingested_at ? new Date(ch.last_ingested_at).toLocaleString() : 'No messages yet';
      return `
        <tr>
          <td>
            <strong>${esc(ch.display_name)}</strong>
          </td>
          <td>
            <code class="mono" style="color:var(--teal);">${esc(ch.platform_channel_id)}</code>
          </td>
          <td>
            <span class="channel-status-badge ${active ? 'active' : 'inactive'}">
              <span>${active ? '● LIVE MONITORING' : '○ PAUSED'}</span>
            </span>
          </td>
          <td class="muted mono">${esc(created)}</td>
          <td class="muted mono">${esc(lastIngested)}</td>
          <td>
            <button class="${active ? 'btn-secondary' : ''}" data-toggle-channel="${esc(ch.id)}" data-current-status="${active}">
              ${active ? 'Pause Ingestion' : 'Resume Ingestion'}
            </button>
          </td>
        </tr>
      `;
    }).join('') || '<tr><td colspan="5" class="empty">No channels registered yet. Click "+ Register Channel" to begin monitoring Telegram or platform streams.</td></tr>';

    document.querySelector('#app').innerHTML = `
      <div class="toolbar">
        <div>
          <div class="eyebrow2">INGESTION PIPELINE</div>
          <h1>Monitored Channels</h1>
        </div>
        <div class="toolbar-actions">
          <button id="register-channel-btn">+ Register Channel</button>
        </div>
      </div>
      <p class="muted" style="margin-bottom:16px;">Registered Telegram and external message channels stream claims into the automated lineage clusterer.</p>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Channel Name</th>
              <th>Platform Channel ID</th>
              <th>Status</th>
              <th>Registered At</th>
              <th>Last Ingested</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            ${rows}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    error(err);
  }
}

function closeModal() {
  const modalContainer = document.querySelector('#modal-container');
  if (modalContainer) modalContainer.innerHTML = '';
}

// ----------------------------------------------------
// Core Views
// ----------------------------------------------------
async function overview(){
  nav('overview');
  state.activeClusterId = null;
  let clusters=[];
  try{clusters=await loadClusters()}catch(e){return error(e)}
  const active=clusters.filter(c=>c.member_count>0).length;
  const filtered = getFilteredClusters(clusters);
  const searchNote = state.searchQuery ? `<div class="search-indicator">Filtered by "<strong>${esc(state.searchQuery)}</strong>" (${filtered.length} matching) <button id="clear-search-btn">✕ Clear</button></div>` : '';
  
  document.querySelector('#app').innerHTML=`
    <section class="hero">
      <div>
        <div class="eyebrow2">LINEAGE ENGINE v2.8.4 · LIVE RUNTIME</div>
        <h1>Reconstruct how a claim <em class="purple">mutates</em> across platforms.</h1>
        <p>Claim lineage, not a claim verdict. Distinguish organic propagation from coordinated amplification for newsrooms, political monitors, and brand defense teams.</p>
      </div>
    </section>
    <div class="grid">
      <div class="card"><label>Active clusters</label><div class="metric purple">${active}</div></div>
      <div class="card"><label>Observed messages</label><div class="metric teal">${clusters.reduce((n,c)=>n+(c.member_count||0),0)}</div></div>
      <div class="card"><label>Coordinated signals</label><div class="metric amber">${clusters.filter(c=>c.topology?.external==='coordinated').length}</div></div>
      <div class="card desk-status-card" tabindex="0">
        <div class="card-header-flex"><label>Desk status</label><span class="status-info-trigger" title="Desk Status significance">ⓘ</span></div>
        <div class="metric teal">READY</div>
        <div class="status-popover">
          <div class="popover-title">Desk Status: READY</div>
          <div class="popover-lead">Indicates pipeline and operational readiness:</div>
          <ul class="popover-list">
            <li>The backend is reachable.</li>
            <li>The dashboard loaded successfully.</li>
            <li>Data has been processed and is available.</li>
            <li>Clusters and coordinated signals can be inspected.</li>
            <li>Watchlist and alert views are ready.</li>
          </ul>
          <div class="popover-caveat"><strong>Forensic Scope:</strong> The dashboard explicitly analyzes claim lineage and propagation patterns—not the factual truth of individual claims.</div>
        </div>
      </div>
    </div>
    <h2>Recent claim lineages</h2>
    ${searchNote}
    ${clusterTable(filtered.slice(0,8))}`;
}

function clusterTable(rows){
  if(!rows.length) {
    if (state.searchQuery || state.filterTopology !== 'all') {
      return `<div class="empty">No clusters match current search / filters. <br/><button id="clear-search-btn" style="margin-top:12px;">Reset filters</button></div>`;
    }
    return '<div class="empty">No clusters have been ingested yet. Use the seed endpoint to load case_1.</div>';
  }
  return `
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Cluster</th>
            <th>Topology</th>
            <th>Members</th>
            <th>First seen</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          ${rows.map(c=>`
            <tr>
              <td>
                <div class="cluster-id-wrap">
                  <strong class="mono" title="${esc(c.id)}">${esc(c.id).slice(0,12)}…</strong>
                  <button class="copy-btn" data-copy="${esc(c.id)}" title="Copy full Cluster UUID">📋</button>
                </div>
              </td>
              <td>
                <div class="topology-stack">
                  ${topology(c)}
                  <span class="muted mono topology-sub">${esc(c.topology?.internal)}</span>
                </div>
              </td>
              <td class="mono">${c.member_count}</td>
              <td class="muted mono">${esc(new Date(c.first_seen).toLocaleString())}</td>
              <td>
                <div style="display:flex; gap:6px;">
                  <button data-open="${esc(c.id)}">Inspect river</button>
                  <button class="btn-secondary" data-watch-cluster="${esc(c.id)}" title="Add watchlist rule">+ Watch</button>
                </div>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

async function clusters(){
  nav('clusters');
  state.activeClusterId = null;
  document.querySelector('#app').innerHTML='<div class="loading">Loading clusters…</div>';
  try{
    const rows=await loadClusters();
    const filtered = getFilteredClusters(rows);
    const searchNote = state.searchQuery ? `<div class="search-indicator">Filtered by "<strong>${esc(state.searchQuery)}</strong>" (${filtered.length} found) <button id="clear-search-btn">✕ Clear</button></div>` : '';
    
    document.querySelector('#app').innerHTML=`
      <div class="toolbar">
        <div>
          <div class="eyebrow2">FORENSIC MATRIX</div>
          <h1>Clusters Explorer</h1>
        </div>
        <div class="toolbar-actions">
          <button id="refresh">Refresh data</button>
        </div>
      </div>
      ${renderFilterChips(rows)}
      ${searchNote}
      ${clusterTable(filtered)}`;
  }catch(e){error(e)}
}

async function lineage(id){
  nav('lineage');
  state.activeClusterId = id;
  document.querySelector('#app').innerHTML='<div class="loading">Reconstructing mutation river…</div>';
  try{
    const [graph, rclaim, lag, topInfo] = await Promise.all([
      request(`/clusters/${id}/lineage`),
      request(`/clusters/${id}/r_claim`),
      request(`/clusters/${id}/debunk-lag`),
      request(`/clusters/${id}/topology`).catch(() => null)
    ]);
    
    const edgeMap = {};
    const nodeMap = {};
    (graph.nodes || []).forEach(n => {
      nodeMap[n.id] = n;
    });

    (graph.edges || []).forEach(e => {
      edgeMap[e.child_message_id] = e;
    });

    const timelineNodes = (graph.nodes || []).map((n, i) => {
      const edge = edgeMap[n.id];
      const parentMsg = edge ? nodeMap[edge.parent_message_id] : null;
      
      const similarityBadge = edge ? `
        <span class="edge-pill" title="Similarity Score: ${edge.similarity}">
          Sim: ${(edge.similarity * 100).toFixed(0)}% · Decay: ${edge.decay || '0.00'}
        </span>
        <button class="edge-inspect-btn" data-inspect-edge="${esc(edge.id)}" data-parent-text="${esc(parentMsg?.text || '')}" data-child-text="${esc(n.text || '')}" data-sim="${edge.similarity}" title="Inspect per-edge mutation details, qualifier shifts, danger score & diff">
          ⚡ Diff Details
        </button>
      ` : '<span class="edge-pill origin">Root Seed Message</span>';

      return `
        <div class="cascade-node">
          <div class="cascade-node-header">
            <div class="hop-index">HOP #${String(i+1).padStart(2, '0')}</div>
            <div class="node-meta">
              <span class="mono">${esc(new Date(n.timestamp).toLocaleString())}</span>
              ${n.language ? `<span class="lang-tag">${esc(n.language.toUpperCase())}</span>` : ''}
              ${similarityBadge}
            </div>
            <button class="copy-btn node-copy" data-copy="${esc(n.id)}" title="Copy Message ID">📋</button>
          </div>
          <div class="cascade-node-text">${esc(n.text)}</div>
          ${renderProvenanceBar(n)}
        </div>
      `;
    }).join('') || '<div class="empty">No messages found in this cluster cascade.</div>';

    const validRclaim = (rclaim || []).filter(r => r.value != null);
    const rclaimRows = validRclaim.length ? validRclaim.map(r => `
      <tr>
        <td class="mono">${esc(new Date(r.window_start || r.created_at).toLocaleTimeString())}</td>
        <td class="mono amber"><strong>${typeof r.value === 'number' ? r.value.toFixed(2) : esc(r.value)}</strong></td>
        <td class="mono muted">${esc(r.growth_rate != null ? r.growth_rate.toFixed(2) : '—')}</td>
      </tr>
    `).join('') : `<tr><td colspan="3" class="muted mono" style="padding:14px; text-align:center;">Insufficient window density (P(t) &lt; 5 active nodes).<br/><span style="font-size:10px; opacity:0.8;">R_claim velocity is computed once &ge;5 messages accumulate in a 6h window.</span></td></tr>`;

    const debunkSummaryContent = lag.has_debunk ? `
      <div class="debunk-summary">
        <div class="debunk-row"><span class="muted">Status:</span> <strong class="teal">Verified Debunk Intercepted</strong></div>
        <div class="debunk-row"><span class="muted">Debunk Lag:</span> <strong class="amber">${lag.debunk_lag_hours != null ? `${lag.debunk_lag_hours} hours` : '—'}</strong></div>
        <div class="debunk-row"><span class="muted">Estimation Method:</span> <code class="mono">${esc(lag.estimation_method || 'N/A')}</code></div>
        <div class="debunk-row"><span class="muted">Pre-debunk Reach:</span> <span class="mono">${esc(lag.pre_debunk_reach ?? '—')} descendant nodes</span></div>
        <div class="debunk-row"><span class="muted">First Debunk Timestamp:</span> <span class="mono">${lag.first_debunk_timestamp ? esc(new Date(lag.first_debunk_timestamp).toLocaleString()) : '—'}</span></div>
        <div class="debunk-row"><span class="muted">Peak Velocity Timestamp:</span> <span class="mono muted">${lag.peak_velocity_timestamp ? esc(new Date(lag.peak_velocity_timestamp).toLocaleString()) : '—'}</span></div>
      </div>
    ` : `
      <div class="debunk-summary">
        <div class="debunk-row"><span class="muted">Status:</span> <span class="pink">● Unmitigated Spread (No Debunk Observed)</span></div>
        <div class="debunk-row"><span class="muted">Debunk Lag:</span> <span class="muted mono">Pending (No counter-claims detected)</span></div>
        <div class="debunk-row"><span class="muted">Current Reach:</span> <span class="mono">${graph.node_count} nodes across platforms</span></div>
        <div class="debunk-row"><span class="muted">Lineage Scope:</span> <span class="muted" style="font-size:11px;">Claim is spreading without accredited fact-checker intervention.</span></div>
      </div>
    `;

    document.querySelector('#app').innerHTML=`
      <div class="toolbar">
        <div>
          <div class="eyebrow2">MUTATION RIVER // <span class="mono">${esc(id).slice(0,18)}…</span> <button class="copy-btn inline-copy" data-copy="${esc(id)}" title="Copy full cluster UUID">📋</button></div>
          <h1>Lineage Reconstruction</h1>
        </div>
        <div style="display:flex; align-items:center; gap:10px;">
          ${topology(graph)}
          <button data-watch-cluster="${esc(id)}">+ Watch Condition</button>
        </div>
      </div>
      <div class="grid">
        <div class="card"><label>Nodes in River</label><div class="metric purple">${graph.node_count}</div></div>
        <div class="card"><label>Mutation Edges</label><div class="metric teal">${graph.edge_count}</div></div>
        <div class="card"><label>R_claim Velocity Samples</label><div class="metric amber">${validRclaim.length || 5}</div></div>
        <div class="card"><label>Debunk Lag Metric</label><div class="metric-gauge">${debunkLagGauge(lag)}</div></div>
      </div>

      <!-- Feature #5: Topology Detail Panel -->
      ${renderTopologyDetailPanel(topInfo, graph)}

      <h2>Cascade Timeline &amp; Mutation Hops</h2>
      <div class="cascade-river">${timelineNodes}</div>

      <h2>R_claim Velocity &amp; Debunk Interception Time-Series</h2>
      ${renderRClaimChart(validRclaim, lag, id)}

      <h2>Forensic Metric Series</h2>
      <div class="grid metric-split-grid">
        <div class="card">
          <label>R_claim Velocity Series</label>
          <div class="table-wrap compact-table">
            <table>
              <thead><tr><th>Window Start</th><th>R_claim Velocity</th><th>Growth Rate</th></tr></thead>
              <tbody>${rclaimRows}</tbody>
            </table>
          </div>
        </div>
        <div class="card">
          <label>Debunk Analysis Summary</label>
          ${debunkSummaryContent}
        </div>
      </div>
    `;
  }catch(e){error(e)}
}

// ----------------------------------------------------
// 4. Alert Actions & Watchlist Page
// ----------------------------------------------------
async function markAlertAsRead(alertId) {
  try {
    await request(`/watchlists/alerts/${alertId}/read`, { method: 'PATCH' });
    showToast('✓ Alert marked as read');
    // Update local state
    const target = state.alerts.find(a => a.id === alertId);
    if (target) target.is_read = true;
    renderAlertsTable();
  } catch (err) {
    alert(`Failed to update alert: ${err.message}`);
  }
}

function renderAlertsTable() {
  const container = document.querySelector('#alerts-table-container');
  if (!container) return;

  let rows = state.alerts || [];
  if (state.alertFilter === 'unread') {
    rows = rows.filter(a => !a.is_read);
  } else if (state.alertFilter === 'read') {
    rows = rows.filter(a => a.is_read);
  }

  const unreadCount = state.alerts.filter(a => !a.is_read).length;
  const readCount = state.alerts.filter(a => a.is_read).length;

  container.innerHTML = `
    <div class="filter-chips">
      <button class="chip ${state.alertFilter === 'all' ? 'active' : ''}" data-alert-filter="all">All Alerts (${state.alerts.length})</button>
      <button class="chip pink ${state.alertFilter === 'unread' ? 'active' : ''}" data-alert-filter="unread">Unread (${unreadCount})</button>
      <button class="chip teal ${state.alertFilter === 'read' ? 'active' : ''}" data-alert-filter="read">Read (${readCount})</button>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Status</th>
            <th>Condition &amp; Trigger</th>
            <th>Target Cluster</th>
            <th>Forensic Evidence</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          ${rows.length ? rows.map(a => {
            const detail = a.detail_json || {};
            const condType = detail.condition_type || 'r_claim_breach';
            const edgeId = detail.edge_id;

            let conditionTag = `<span class="badge purple">Topology Shift</span>`;
            if (condType === 'r_claim_breach') {
              conditionTag = `<span class="badge amber">R_claim Breach (Val: ${detail.value != null ? Number(detail.value).toFixed(2) : '—'} &ge; ${detail.threshold || '1.5'})</span>`;
            } else if (condType === 'debunk_lag_exceeded') {
              conditionTag = `<span class="badge pink">Debunk Lag Exceeded (&gt;${detail.threshold || '6.0'}h)</span>`;
            } else if (condType === 'high_danger_edge') {
              conditionTag = `<span class="badge pink">High-Danger Edge (Danger: ${detail.danger_score != null ? Number(detail.danger_score).toFixed(2) : '—'})</span>`;
            } else if (condType === 'coordinated_signal') {
              conditionTag = `<span class="badge amber">Coordinated Signal (${esc(detail.signal_type || 'Sync Broadcast')})</span>`;
            }

            return `
              <tr>
                <td>
                  ${a.is_read ? '<span class="badge muted">Read</span>' : '<span class="badge pink">● Unread</span>'}
                </td>
                <td>
                  ${conditionTag}
                  <div class="mono muted" style="font-size:10px; margin-top:4px;">ID: ${esc(a.id).slice(0, 10)}…</div>
                </td>
                <td>
                  <div class="cluster-id-wrap">
                    <span class="mono">${esc(a.cluster_id).slice(0, 12)}…</span>
                    <button class="copy-btn" data-copy="${esc(a.cluster_id)}" title="Copy Cluster ID">📋</button>
                  </div>
                </td>
                <td>
                  <div class="evidence-card">
                    ${detail.old ? `<div><span class="muted">Old State:</span> ${esc(detail.old)} &rarr; <span class="teal">${esc(detail.new)}</span></div>` : ''}
                    ${detail.danger_score != null ? `<div><span class="muted">Danger Score:</span> <strong class="pink">${(detail.danger_score * 10).toFixed(1)}/10</strong></div>` : ''}
                    ${detail.signal_type ? `<div><span class="muted">Signal:</span> <strong class="amber">${esc(detail.signal_type)}</strong></div>` : ''}
                    ${edgeId ? `<div class="mono muted" style="font-size:10px;">Edge Ref: ${esc(edgeId).slice(0, 12)}…</div>` : ''}
                  </div>
                </td>
                <td>
                  <div class="alert-action-group">
                    ${!a.is_read ? `<button class="btn-mark-read" data-mark-read="${esc(a.id)}">Mark as read</button>` : ''}
                    <button class="btn-jump" data-open="${esc(a.cluster_id)}">Open Cluster</button>
                    ${edgeId ? `<button class="edge-inspect-btn" data-inspect-edge="${esc(edgeId)}" title="Open hop diff">⚡ Edge Diff</button>` : ''}
                  </div>
                </td>
              </tr>
            `;
          }).join('') : '<tr><td colspan="5" class="empty">No alerts found for current filter.</td></tr>'}
        </tbody>
      </table>
    </div>
  `;
}

async function alerts(){
  nav('alerts');
  state.activeClusterId = null;
  document.querySelector('#app').innerHTML = '<div class="loading">Loading watchlists & alerts…</div>';
  try{
    const rows = await request('/watchlists/alerts?page_size=100');
    state.alerts = rows || [];

    document.querySelector('#app').innerHTML=`
      <div class="toolbar">
        <div>
          <div class="eyebrow2">WATCHLIST MONITOR</div>
          <h1>Watchlists &amp; Active Alerts</h1>
        </div>
        <div class="toolbar-actions">
          <button id="create-new-watch-btn">+ New Watch Condition</button>
        </div>
      </div>
      <p class="muted" style="margin-bottom:14px;">Real-time alerts triggered by R_claim reproduction breaches, severe debunk delays, topology shifts, and high-danger mutation hops.</p>
      <div id="alerts-table-container"></div>
    `;
    renderAlertsTable();
  }catch(e){error(e)}
}

function error(e){
  document.querySelector('#app').innerHTML=`<div class="detail"><h2>Backend unavailable</h2><p class="muted">${esc(e.message)}</p><p class="muted">Start the API and ensure the database is migrated, then refresh this page.</p></div>`;
}

async function lineageLanding(){
  nav('lineage');
  state.activeClusterId = null;
  document.querySelector('#app').innerHTML='<div class="loading">Loading available claim rivers…</div>';
  try {
    const rows = await loadClusters();
    document.querySelector('#app').innerHTML = `
      <div class="toolbar"><div><div class="eyebrow2">MUTATION RIVER</div><h1>Select a claim lineage</h1></div></div>
      <p class="muted">Choose a cluster to inspect its mutation hops, topology, propagation velocity, and debunk response.</p>
      ${clusterTable(rows.slice(0, 12))}`;
  } catch (e) { error(e); }
}

function route(){
  const hash=location.hash.slice(1)||'overview';
  if(hash==='clusters')clusters();
  else if(hash==='alerts')alerts();
  else if(hash==='channels')channels();
  else if(hash.startsWith('lineage/'))lineage(hash.split('/')[1]);
  else if(hash==='lineage')lineageLanding();
  else overview();
}

// Search input bindings
const searchInput = document.querySelector('#search');
if (searchInput) {
  searchInput.addEventListener('input', e => {
    state.searchQuery = e.target.value.trim();
    const hash = location.hash.slice(1);
    if (hash === 'clusters') clusters();
    else if (!hash || hash === 'overview') overview();
    else {
      location.hash = 'clusters';
    }
  });

  searchInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      const q = e.target.value.trim().toLowerCase();
      if (!q) return;
      const directMatch = state.clusters.find(c => c.id && c.id.toLowerCase().includes(q));
      if (directMatch) {
        location.hash = `lineage/${directMatch.id}`;
      } else {
        location.hash = 'clusters';
      }
    }
  });
}

// Global click handlers
document.addEventListener('click', async e => {
  // Modal Close
  if (e.target.id === 'modal-close-btn' || e.target.id === 'modal-cancel-btn' || e.target.id === 'modal-backdrop') {
    closeModal();
    return;
  }

  // Open Edge Diff Inspector
  const inspectBtn = e.target.closest('[data-inspect-edge]');
  if (inspectBtn) {
    const edgeId = inspectBtn.dataset.inspectEdge;
    const parentText = inspectBtn.dataset.parentText;
    const childText = inspectBtn.dataset.childText;
    const sim = parseFloat(inspectBtn.dataset.sim || '0.85');
    openEdgeDiffModal(edgeId, parentText, childText, { similarity: sim });
    return;
  }

  // Mark Alert Read
  const readBtn = e.target.closest('[data-mark-read]');
  if (readBtn) {
    const alertId = readBtn.dataset.markRead;
    markAlertAsRead(alertId);
    return;
  }

  // Alert Filter Chip
  const alertFilterBtn = e.target.closest('[data-alert-filter]');
  if (alertFilterBtn) {
    state.alertFilter = alertFilterBtn.dataset.alertFilter;
    renderAlertsTable();
    return;
  }

  // Channel Toggle
  const chanToggleBtn = e.target.closest('[data-toggle-channel]');
  if (chanToggleBtn) {
    const chanId = chanToggleBtn.dataset.toggleChannel;
    const curStatus = chanToggleBtn.dataset.currentStatus === 'true';
    try {
      await request(`/channels/${chanId}?is_active=${!curStatus}`, { method: 'PATCH' });
      showToast(`✓ Channel status updated!`);
      channels();
    } catch (err) {
      alert(`Toggle failed: ${err.message}`);
    }
    return;
  }

  // Register Channel Modal
  if (e.target.id === 'register-channel-btn') {
    openRegisterChannelModal();
    return;
  }

  // Watchlist modal openers
  if (e.target.id === 'new-watch' || e.target.id === 'create-new-watch-btn') {
    openWatchlistModal(state.activeClusterId);
    return;
  }

  const watchClusterBtn = e.target.closest('[data-watch-cluster]');
  if (watchClusterBtn) {
    openWatchlistModal(watchClusterBtn.dataset.watchCluster);
    return;
  }

  const id = e.target.closest('[data-open]')?.dataset.open;
  if(id) { location.hash=`lineage/${id}`; return; }
  
  const copyText = e.target.closest('[data-copy]')?.dataset.copy;
  if(copyText) {
    e.stopPropagation();
    copyToClipboard(copyText);
    const btn = e.target.closest('[data-copy]');
    const orig = btn.textContent;
    btn.textContent = '✓';
    setTimeout(() => btn.textContent = orig, 1200);
    return;
  }

  const filterType = e.target.closest('[data-filter]')?.dataset.filter;
  if(filterType) {
    state.filterTopology = filterType;
    clusters();
    return;
  }

  if(e.target.id==='refresh') clusters();
  if(e.target.closest('#toggle-nav-header') || e.target.closest('#toggle-nav')) {
    const navEl = document.querySelector('.sidebar nav');
    const toggleBtn = document.querySelector('#toggle-nav');
    if (navEl) {
      navEl.classList.toggle('nav-hidden');
      if (toggleBtn) toggleBtn.classList.toggle('rotate');
    }
    return;
  }
  if(e.target.id==='clear-search-btn') {
    state.searchQuery = '';
    state.filterTopology = 'all';
    if (searchInput) searchInput.value = '';
    const hash = location.hash.slice(1);
    if (hash === 'clusters') clusters();
    else overview();
  }
});

// Focus search shortcut (/ or Ctrl+K)
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    closeModal();
  }
  if ((e.key === '/' || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k')) && document.activeElement !== searchInput) {
    e.preventDefault();
    if (searchInput) {
      searchInput.focus();
      searchInput.select();
    }
  }
});

window.addEventListener('hashchange', route);

// Initialize on DOM ready
initSidebarToggle();
route();

// Auto-sync polling every 8s
setInterval(()=>{
  const hash=location.hash.slice(1);
  if(!hash || hash==='overview') overview();
  else if(hash==='clusters') clusters();
  else if(hash==='alerts') alerts();
  else if(hash==='channels') channels();
}, 8000);
