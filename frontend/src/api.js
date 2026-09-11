export async function fetchLineage(clusterId) {
  const response = await fetch(`/api/clusters/${clusterId}/lineage`);
  if (!response.ok) throw new Error('Failed to fetch lineage data');
  return response.json();
}

export async function fetchAlerts() {
  const response = await fetch('/api/alerts');
  if (!response.ok) throw new Error('Failed to fetch alerts');
  return response.json();
}