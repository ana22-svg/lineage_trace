/**
 * Renders the topology label.
 * Enforces Rule: Topology label must match pitch vocabulary[cite: 1].
 * Shows external label primarily, internal label on hover[cite: 1].
 */
export function renderTopology(topologyData, containerElement) {
  if (!topologyData || !containerElement) return;

  // Render the external (pitch-vocabulary) label as the primary text[cite: 1]
  const externalLabel = topologyData.external.replace('_', ' ');
  containerElement.innerText = externalLabel;
  
  // Render the internal (graph-theoretic) label as hover/title text[cite: 1]
  containerElement.title = `Technical Shape: ${topologyData.internal}`;

  // Apply basic color coding based on the external label
  if (topologyData.external === 'organic') {
    containerElement.style.backgroundColor = 'var(--organic)';
  } else if (topologyData.external === 'coordinated') {
    containerElement.style.backgroundColor = 'var(--coordinated)';
  } else if (topologyData.external === 'bot_amplified') {
    containerElement.style.backgroundColor = 'var(--bot-amplified)';
  } else {
    containerElement.style.backgroundColor = '#757575'; // unclassified
  }
}