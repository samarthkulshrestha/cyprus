import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { sankey, sankeyLinkHorizontal, SankeyGraph } from 'd3-sankey';

// --- Type Definitions for Sankey Data ---
export interface SankeyNodeExtraProperties { name: string; }
export interface SankeyLinkExtraProperties {}
export type SankeyData = SankeyGraph<SankeyNodeExtraProperties, SankeyLinkExtraProperties>;

interface SankeyChartProps {
  data: SankeyData;
}

const SankeyChart = ({ data }: SankeyChartProps) => {
  const ref = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (ref.current && data) {
      const width = 800;
      const height = 400;

      // Clear previous render
      d3.select(ref.current).selectAll("*").remove();

      const svg = d3.select(ref.current)
        .attr("width", width)
        .attr("height", height)
        .style("width", "100%")
        .style("height", "auto");

      // console.log('Raw data size:', {
      //   nodes: data.nodes?.length || 0,
      //   links: data.links?.length || 0,
        // totalMemory: JSON.stringify(data).length + ' characters'
      // });

      const sankeyGenerator = sankey<SankeyNodeExtraProperties, SankeyLinkExtraProperties>()
        .nodeWidth(15)
        .nodePadding(10)
        .extent([[1, 1], [width - 1, height - 6]]);

      const { nodes, links } = sankeyGenerator(data);

      // Nodes
      svg.append("g")
        .selectAll("rect")
        .data(nodes)
        .join("rect")
          .attr("x", d => d.x0!)
          .attr("y", d => d.y0!)
          .attr("height", d => d.y1! - d.y0! > 0 ? d.y1! - d.y0! : 0) // Prevent negative height
          .attr("width", d => d.x1! - d.x0!)
          .attr("fill", "#69b3a2")
        .append("title")
          .text(d => `${d.name}\nModels: ${d.value}`);

      // Links
      svg.append("g")
        .attr("fill", "none")
        .attr("stroke-opacity", 0.5)
        .selectAll("g")
        .data(links)
        .join("path")
          .attr("d", sankeyLinkHorizontal())
          .attr("stroke", "#aaa")
          .attr("stroke-width", d => Math.max(1, d.width!));
          
      // Node Labels
      svg.append("g")
        .style("font", "12px sans-serif")
        .selectAll("text")
        .data(nodes)
        .join("text")
          .attr("x", d => d.x0! < width / 2 ? d.x1! + 6 : d.x0! - 6)
          .attr("y", d => (d.y1! + d.y0!) / 2)
          .attr("dy", "0.35em")
          .attr("text-anchor", d => d.x0! < width / 2 ? "start" : "end")
          .text(d => d.name);
    }
  }, [data]); // Re-run the effect if data changes

  return <svg ref={ref}></svg>;
};

export default SankeyChart;
