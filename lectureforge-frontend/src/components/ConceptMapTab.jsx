import React, { useMemo } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  MarkerType,
} from "reactflow";

function buildLayout(nodes, edges) {
  const levels = {
    main_topic: 0,
    subtopic: 1,
    detail: 2,
  };

  const grouped = nodes.reduce((acc, node) => {
    const level = levels[node.type] ?? 2;
    if (!acc[level]) acc[level] = [];
    acc[level].push(node);
    return acc;
  }, {});

  return nodes.map((node) => {
    const level = levels[node.type] ?? 2;
    const group = grouped[level] || [];
    const index = group.findIndex((item) => item.id === node.id);
    const total = group.length;

    return {
      id: node.id,
      data: {
        label: (
          <div>
            <div>{node.label}</div>
            <div className="mt-1 text-[10px] font-semibold uppercase tracking-wide text-slate-400">
              {node.type?.replace("_", " ")}
            </div>
          </div>
        ),
      },
      position: {
        x: level * 320,
        y: index * 110 - (total * 55),
      },
      type: "default",
    };
  });
}

export default function ConceptMapTab({ conceptMap }) {
  const flowNodes = useMemo(() => {
    return buildLayout(conceptMap?.nodes || [], conceptMap?.edges || []);
  }, [conceptMap]);

  const flowEdges = useMemo(() => {
    return (conceptMap?.edges || []).map((edge, index) => ({
      id: `${edge.source}-${edge.target}-${index}`,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      animated: false,
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
      style: {
        strokeWidth: 2,
      },
    }));
  }, [conceptMap]);

  return (
    <section className="h-[620px] overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        fitView
        fitViewOptions={{ padding: 0.25 }}
      >
        <Background />
        <Controls />
        <MiniMap pannable zoomable />
      </ReactFlow>
    </section>
  );
}
