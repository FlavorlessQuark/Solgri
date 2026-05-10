import React, { useEffect, useRef } from 'react';
import { Network } from 'vis-network/standalone';

export interface Node {
  id: number;
  type: 'gen' | 'battery' | 'load' | 'grid' | 'wind';
  status: number;
  output: number;
  charge_level?: number;
  priority?: number;
  targets: number[];
  energy_received: number;
  energy_sent: number;
  shortage: number;
  served: boolean;
  action: string;
  max_generation_capacity: number;
  predicted_generation: number;
}

interface GridVisualizationProps {
  nodes: Node[];
  width?: number;
  height?: number;
}

const GridVisualization: React.FC<GridVisualizationProps> = ({
  nodes,
  width = 800,
  height = 500,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<Network | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const icons: { [key: string]: string } = {
      solar: '☀️',
      battery: '🔋',
      load: '🏢',
      grid: '⚡',
      wind: '💨',
    };

    const visNodes = nodes.map((n) => ({
      id: String(n.id),
      label: `${icons[n.type]}\n${n.type.toUpperCase()}\n${n.output}W`,
      title: `${n.type} - Output: ${n.output}W`,
      color: n.status === 1 ? '#667eea' : '#555555',
    }));

    const visEdges = nodes.flatMap((n) =>
      n.targets.map((t) => ({ from: String(n.id), to: String(t) , arrows: 'to', color: '#83ff61' }))
    );

    const data = { nodes: visNodes, edges: visEdges };
    const options = {
      physics: { enabled: true, stabilization: { iterations: 200 } },
      nodes: { shape: 'dot', scaling: { label: { enabled: true } }, font: { size: 14, color: '#ffffff' } },
    };

    if (networkRef.current) networkRef.current.destroy();
    networkRef.current = new Network(containerRef.current, data, options);
  }, [nodes]);

  return (
    <div
      ref={containerRef}
      style={{
        width,
        height,
        border: '2px solid #667eea',
        borderRadius: '8px',
        backgroundColor: '#1a1a2e',
      }}
    />
  );
};

export default GridVisualization;
