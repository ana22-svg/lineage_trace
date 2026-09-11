/**
 * Renders the dashboard panel containing stats and debunk-lag info.
 * Enforces Rule: Debunk-lag estimation method must be visible[cite: 1].
 */
export function renderDashboard(lineageData, containerElement) {
  const statsDiv = document.getElementById('cluster-stats');
  const caveatBanner = document.getElementById('debunk-caveat-banner');

  // Check the explicitly surfaced estimation_method and render caveat if it is the fallback[cite: 1]
  if (lineageData.debunk_lag && lineageData.debunk_lag.estimation_method === "fallback_first_seen") {
    caveatBanner.classList.remove('hidden');
  } else {
    caveatBanner.classList.add('hidden');
  }

  // Render basic stats
  statsDiv.innerHTML = `
    <h3>Cluster Statistics</h3>
    <p><strong>Nodes:</strong> ${lineageData.node_count}</p>
    <p><strong>Edges:</strong> ${lineageData.edge_count}</p>
    
    <h3>Debunk Metrics</h3>
    <p><strong>Has Debunk:</strong> ${lineageData.debunk_lag?.has_debunk ? 'Yes' : 'No'}</p>
    ${lineageData.debunk_lag?.has_debunk ? 
      `<p><strong>Debunk Lag:</strong> ${lineageData.debunk_lag.debunk_lag_hours} hrs</p>
       <p><strong>Pre-debunk Reach:</strong> ${lineageData.debunk_lag.pre_debunk_reach} nodes</p>` : ''
    }
  `;
}