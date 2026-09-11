import { fetchLineage } from './api.js';
import { renderRiver } from './river.js';
import { renderDashboard } from './dashboard.js';
import { renderTopology } from './topology.js';

async function init() {
  try {
    // For MVP demonstration, loading a hardcoded cluster ID
    // In production, this would be driven by route params or the dashboard selection
    const demoClusterId = "demo-cluster-uuid"; 
    
    // Fetch unified lineage response
    const lineageData = await fetchLineage(demoClusterId);
    
    // Initialize components
    renderTopology(lineageData.topology, document.getElementById('topology-container'));
    renderDashboard(lineageData, document.getElementById('dashboard-panel'));
    renderRiver(lineageData, '#mutation-river');
    
  } catch (error) {
    console.error("Initialization failed:", error);
  }
}

document.addEventListener('DOMContentLoaded', init);