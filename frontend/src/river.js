import * as d3 from 'd3';

/**
 * Renders the D3.js Mutation River visualization.
 * It is timeline-based (x-axis = time) rather than a 3D force-directed graph[cite: 2].
 */
export function renderRiver(lineageData, selector) {
  const container = document.querySelector(selector);
  const width = container.clientWidth || 800;
  const height = container.clientHeight || 500;
  const margin = { top: 20, right: 20, bottom: 30, left: 50 };

  const svg = d3.select(selector)
    .append('svg')
    .attr('width', width)
    .attr('height', height);

  // Parse ISO timestamps into JS Dates
  const nodes = lineageData.nodes.map(d => ({ ...d, date: new Date(d.timestamp) }));
  const edges = lineageData.edges;

  // Timeline-based X scale
  const xScale = d3.scaleTime()
    .domain(d3.extent(nodes, d => d.date))
    .range([margin.left, width - margin.right]);

  // Abstract Y scale for separation (simplified for MVP)
  const yScale = d3.scaleLinear()
    .domain([0, nodes.length])
    .range([margin.top, height - margin.bottom]);

  // Give nodes a random Y within bounds just for separation in this demo snippet
  nodes.forEach((n, i) => n.yPos = yScale(i));

  // Draw Edges first so they sit behind nodes
  svg.selectAll('.edge')
    .data(edges)
    .enter()
    .append('line')
    // Set classes based on pipeline rules: dashed if flagged gap[cite: 1]
    .attr('class', d => d.is_flagged_gap ? 'edge flagged-gap' : 'edge')
    .attr('stroke', d => d.danger_score > 0.7 ? 'var(--danger-high)' : '#aaa')
    .attr('x1', d => {
      const parent = nodes.find(n => n.id === d.parent_message_id);
      return xScale(parent.date);
    })
    .attr('y1', d => {
      const parent = nodes.find(n => n.id === d.parent_message_id);
      return parent.yPos;
    })
    .attr('x2', d => {
      const child = nodes.find(n => n.id === d.child_message_id);
      return xScale(child.date);
    })
    .attr('y2', d => {
      const child = nodes.find(n => n.id === d.child_message_id);
      return child.yPos;
    });

  // Draw Nodes
  svg.selectAll('.node')
    .data(nodes)
    .enter()
    .append('circle')
    .attr('class', 'node')
    .attr('cx', d => xScale(d.date))
    .attr('cy', d => d.yPos)
    .attr('r', 5)
    .append('title')
    .text(d => `Time: ${d.date.toISOString()}\nRole: ${d.metadata?.role || 'standard'}`);
    
  // Add Timeline Axis
  const xAxis = d3.axisBottom(xScale);
  svg.append('g')
    .attr('transform', `translate(0,${height - margin.bottom})`)
    .call(xAxis);
}