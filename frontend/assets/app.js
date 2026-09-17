const API = '/api';
const state = { clusters: [], selected: null, searchQuery: '', filterTopology: 'all' };
async function request(path, options={}) { const res = await fetch(API + path, {headers:{'Content-Type':'application/json','X-API-Key':localStorage.getItem('claimtrace_api_key')||''}, ...options}); if(!res.ok) throw new Error(`${res.status}: ${await res.text()}`); return res.json(); }
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
function topology(c){const t=c?.topology?.external||'unclassified'; return `<span class="badge ${t==='organic'?'teal':t==='coordinated'?'amber':t==='bot_amplified'?'pink':'muted'}">${esc(t.replace('_',' '))}</span>`}
async function loadClusters(){ state.clusters=await request('/clusters/?page_size=100'); return state.clusters; }
function nav(route){document.querySelectorAll('nav a').forEach(a=>a.classList.toggle('active',a.dataset.route===route));}

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
  setTimeout(() => toast.classList.remove('show'), 2000);
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

async function overview(){
  nav('overview');
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
  return `<div class="table-wrap"><table><thead><tr><th>Cluster</th><th>Topology</th><th>Members</th><th>First seen</th><th></th></tr></thead><tbody>${rows.map(c=>`<tr><td><div class="cluster-id-wrap"><strong class="mono" title="${esc(c.id)}">${esc(c.id).slice(0,12)}…</strong><button class="copy-btn" data-copy="${esc(c.id)}" title="Copy full Cluster UUID">📋</button></div></td><td><div class="topology-stack">${topology(c)}<span class="muted mono topology-sub">${esc(c.topology?.internal)}</span></div></td><td class="mono">${c.member_count}</td><td class="muted mono">${esc(new Date(c.first_seen).toLocaleString())}</td><td><button data-open="${esc(c.id)}">Inspect river</button></td></tr>`).join('')}</tbody></table></div>`;
}

async function clusters(){
  nav('clusters');
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
  document.querySelector('#app').innerHTML='<div class="loading">Reconstructing mutation river…</div>';
  try{
    const [graph, rclaim, lag]=await Promise.all([request(`/clusters/${id}/lineage`),request(`/clusters/${id}/r_claim`),request(`/clusters/${id}/debunk-lag`)]);
    
    // Map edges to child messages for easy lookup
    const edgeMap = {};
    (graph.edges || []).forEach(e => {
      edgeMap[e.child_message_id] = e;
    });

    const timelineNodes = (graph.nodes || []).map((n, i) => {
      const edge = edgeMap[n.id];
      const similarityBadge = edge ? `<span class="edge-pill" title="Similarity Score: ${edge.similarity}">Sim: ${(edge.similarity * 100).toFixed(0)}% · Decay: ${edge.decay || '0.00'}</span>` : '<span class="edge-pill origin">Root Seed</span>';
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
        </div>
      `;
    }).join('') || '<div class="empty">No messages found in this cluster cascade.</div>';

    // R_claim velocity list
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
        ${topology(graph)}
      </div>
      <div class="grid">
        <div class="card"><label>Nodes in River</label><div class="metric purple">${graph.node_count}</div></div>
        <div class="card"><label>Mutation Edges</label><div class="metric teal">${graph.edge_count}</div></div>
        <div class="card"><label>R_claim Velocity Samples</label><div class="metric amber">${validRclaim.length}</div></div>
        <div class="card"><label>Debunk Lag Metric</label><div class="metric-gauge">${debunkLagGauge(lag)}</div></div>
      </div>

      <h2>Cascade Timeline &amp; Mutation Hops</h2>
      <div class="cascade-river">${timelineNodes}</div>

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

async function alerts(){
  nav('alerts');
  try{
    const rows=await request('/watchlists/alerts?page_size=100');
    document.querySelector('#app').innerHTML=`
      <div class="eyebrow2">WATCHLIST MONITOR</div>
      <h1>Alerts</h1>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Alert</th><th>Cluster</th><th>Status</th><th>Evidence</th></tr></thead>
          <tbody>${rows.length?rows.map(a=>`<tr><td class="mono">${esc(a.id)}</td><td class="mono"><div class="cluster-id-wrap"><span>${esc(a.cluster_id).slice(0,12)}…</span><button class="copy-btn" data-copy="${esc(a.cluster_id)}" title="Copy Cluster ID">📋</button></div></td><td>${a.is_read?'Read':'<span class="pink">Unread</span>'}</td><td><pre>${esc(JSON.stringify(a.detail_json||{},null,2))}</pre></td></tr>`).join(''):'<tr><td colspan="4" class="empty">No active alerts.</td></tr>'}</tbody>
        </table>
      </div>
      <p class="muted">Coordinated signals are automatically watched and appear here with their signal and edge evidence.</p>`;
  }catch(e){error(e)}
}

function error(e){
  document.querySelector('#app').innerHTML=`<div class="detail"><h2>Backend unavailable</h2><p class="muted">${esc(e.message)}</p><p class="muted">Start the API and ensure the database is migrated, then refresh this page.</p></div>`;
}

function route(){
  const hash=location.hash.slice(1)||'overview';
  if(hash==='clusters')clusters();
  else if(hash==='alerts')alerts();
  else if(hash.startsWith('lineage/'))lineage(hash.split('/')[1]);
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
document.addEventListener('click', e => {
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
  if(e.target.id==='new-watch') location.hash='alerts';
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
  if ((e.key === '/' || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k')) && document.activeElement !== searchInput) {
    e.preventDefault();
    if (searchInput) {
      searchInput.focus();
      searchInput.select();
    }
  }
});

window.addEventListener('hashchange', route);
route();

// Auto-sync polling every 5s
setInterval(()=>{
  const hash=location.hash.slice(1);
  if(!hash || hash==='overview') overview();
  else if(hash==='clusters') clusters();
  else if(hash==='alerts') alerts();
}, 5000);


