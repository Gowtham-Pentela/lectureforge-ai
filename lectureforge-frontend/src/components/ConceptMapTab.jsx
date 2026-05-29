import React, { memo, useMemo, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
} from "reactflow";
import { ExternalLink, Focus, PlayCircle } from "lucide-react";
import { buildYouTubeJumpUrl, formatTime } from "../lib/youtube";

const nodeTypes = {
  mindMapNode: memo(MindMapNode),
};

export default function ConceptMapTab({
  conceptMap,
  outline = [],
  keyConcepts = [],
  sourceVideoUrl = "",
}) {
  const [selectedNode, setSelectedNode] = useState(null);
  const lectureGraph = useMemo(
    () => buildLectureGraph(conceptMap, outline, keyConcepts),
    [conceptMap, outline, keyConcepts]
  );

  const flowNodes = useMemo(
    () => buildLayout(lectureGraph.nodes),
    [lectureGraph.nodes]
  );

  const flowEdges = useMemo(
    () => lectureGraph.edges.map((edge, index) => buildFlowEdge(edge, index)),
    [lectureGraph.edges]
  );

  const activeNode = selectedNode || lectureGraph.nodes[0];
  const activeStart = Math.floor(Number(activeNode?.timestamp || 0));
  const jumpUrl = buildYouTubeJumpUrl(sourceVideoUrl, activeStart);

  if (!lectureGraph.nodes.length) {
    return (
      <div className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] p-5 text-sm text-[var(--app-muted)]">
        No mind map was generated for this lecture.
      </div>
    );
  }

  return (
    <section className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.24em] text-[var(--app-soft)]">
            Mind map · {lectureGraph.nodes.length} nodes ·{" "}
            {lectureGraph.edges.length} links
          </p>
          <h2 className="mt-2 font-serif text-2xl font-semibold text-[var(--app-text)]">
            How ideas connect through the video
          </h2>
        </div>

        {jumpUrl && (
          <a
            href={jumpUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center justify-center gap-2 rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] px-3 py-2 text-sm font-bold text-[var(--app-accent)] transition hover:bg-[var(--app-panel-muted)]"
          >
            <PlayCircle className="h-4 w-4" />
            Watch selected moment
          </a>
        )}
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_18rem]">
        <div className="h-[640px] overflow-hidden rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] shadow-[0_12px_35px_rgba(15,23,42,0.10)]">
          <ReactFlow
            nodes={flowNodes}
            edges={flowEdges}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.18 }}
            minZoom={0.25}
            maxZoom={1.45}
            onNodeClick={(_, node) => setSelectedNode(node.data.raw)}
          >
            <Background color="var(--app-border)" gap={28} />
            <Controls />
            <MiniMap
              pannable
              zoomable
              nodeColor={(node) => node.data.minimap}
              maskColor="rgba(148, 163, 184, 0.16)"
            />
          </ReactFlow>
        </div>

        <aside className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] p-4">
          <div className="mb-4 flex items-center gap-2 text-[var(--app-accent)]">
            <Focus className="h-4 w-4" />
            <p className="text-xs font-bold uppercase tracking-[0.22em]">
              Focus
            </p>
          </div>

          <h3 className="font-serif text-xl font-semibold leading-snug text-[var(--app-text)]">
            {activeNode?.label}
          </h3>

          <p className="mt-2 font-mono text-xs font-bold text-[var(--app-accent)]">
            {activeNode?.timeLabel || formatTime(activeStart)}
          </p>

          {activeNode?.summary && (
            <p className="mt-4 text-sm leading-6 text-[var(--app-muted)]">
              {activeNode.summary}
            </p>
          )}

          {activeNode?.chapterLabel && activeNode.kind === "concept" && (
            <div className="mt-4 rounded-md border border-[var(--app-border)] bg-[var(--app-panel-muted)] px-3 py-2 text-xs font-semibold leading-5 text-[var(--app-muted)]">
              Connected to: {activeNode.chapterLabel}
            </div>
          )}

          {jumpUrl && (
            <a
              href={jumpUrl}
              target="_blank"
              rel="noreferrer"
              className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-md bg-[var(--app-accent)] px-3 py-2 text-sm font-bold text-white transition hover:bg-[var(--app-accent-strong)]"
            >
              <ExternalLink className="h-4 w-4" />
              Open at moment
            </a>
          )}
        </aside>
      </div>
    </section>
  );
}

function MindMapNode({ data }) {
  return (
    <div
      className="relative w-[210px] rounded-md border px-3 py-2 shadow-[0_8px_24px_rgba(15,23,42,0.10)]"
      style={{
        background: data.background,
        borderColor: data.border,
        color: data.text,
      }}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!h-2 !w-2 !border-0 !bg-[var(--app-accent)]"
      />
      <Handle
        type="source"
        position={Position.Right}
        className="!h-2 !w-2 !border-0 !bg-[var(--app-accent)]"
      />

      <div className="line-clamp-2 min-h-[2.5rem] font-serif text-base font-semibold leading-5">
        {data.label}
      </div>
      <div className="mt-2 flex items-center justify-between gap-2">
        <span className="font-mono text-[10px] font-bold uppercase opacity-70">
          {data.kind}
        </span>
        {data.timeLabel && (
          <span className="rounded bg-[var(--app-accent-soft)] px-1.5 py-0.5 font-mono text-[10px] font-bold text-[var(--app-accent-strong)]">
            {data.timeLabel}
          </span>
        )}
      </div>
    </div>
  );
}

function buildLectureGraph(conceptMap, outline, keyConcepts) {
  if (!outline.length && !keyConcepts.length && !conceptMap?.nodes?.length) {
    return { nodes: [], edges: [] };
  }

  const root = {
    id: "lecture-root",
    kind: "lecture",
    label: "Lecture arc",
    timestamp: 0,
    timeLabel: "00:00",
    summary:
      "Follow the main video timeline from left to right, then branch into the concepts introduced inside each chapter.",
  };

  const chapterNodes = outline.map((item, index) => ({
    id: `chapter-${index + 1}`,
    kind: "chapter",
    label: item.title || `Chapter ${index + 1}`,
    timestamp: Number(item.start || 0),
    end: Number(item.end || item.start || 0),
    timeLabel: item.start_time || formatTime(item.start),
    summary: item.summary || "",
    order: index,
    branchColor: getBranchColor(index),
  }));

  const conceptNodes = keyConcepts.map((item, index) => {
    const chapter = findChapterForTimestamp(
      Number(item.timestamp || 0),
      chapterNodes
    );

    return {
      id: `concept-${index + 1}`,
      kind: "concept",
      label: item.concept || `Concept ${index + 1}`,
      timestamp: Number(item.timestamp || chapter?.timestamp || 0),
      timeLabel: item.timestamp_time || formatTime(item.timestamp),
      summary: item.explanation || "",
      chapterId: chapter?.id || chapterNodes[0]?.id || root.id,
      chapterLabel: chapter?.label || "Lecture arc",
      order: index,
      branchColor: chapter?.branchColor || getBranchColor(index),
    };
  });

  const nodes = [root, ...chapterNodes, ...conceptNodes];
  const edges = [];

  chapterNodes.forEach((chapter) => {
    edges.push({
      source: root.id,
      target: chapter.id,
      label: "branch",
      relation: "branch",
      branchColor: chapter.branchColor,
    });
  });

  chapterNodes.forEach((chapter, index) => {
    const nextChapter = chapterNodes[index + 1];

    if (nextChapter) {
      edges.push({
        source: chapter.id,
        target: nextChapter.id,
        label: "then",
        relation: "timeline",
      });
    }
  });

  conceptNodes.forEach((concept) => {
    edges.push({
      source: concept.chapterId,
      target: concept.id,
      label: "introduces",
      relation: "chapter-concept",
      branchColor: concept.branchColor,
    });
  });

  addSemanticConceptEdges({
    conceptMap,
    conceptNodes,
    chapterNodes,
    edges,
  });

  return {
    nodes,
    edges: dedupeEdges(edges),
  };
}

function addSemanticConceptEdges({
  conceptMap,
  conceptNodes,
  chapterNodes,
  edges,
}) {
  const rawEdges = Array.isArray(conceptMap?.edges) ? conceptMap.edges : [];
  const rawNodes = Array.isArray(conceptMap?.nodes) ? conceptMap.nodes : [];
  const rawNodeById = new Map(rawNodes.map((node) => [node.id, node]));
  const searchableNodes = [...conceptNodes, ...chapterNodes];

  rawEdges.forEach((edge) => {
    const sourceLabel = rawNodeById.get(edge.source)?.label || edge.source;
    const targetLabel = rawNodeById.get(edge.target)?.label || edge.target;
    const source = findBestNodeMatch(sourceLabel, searchableNodes);
    const target = findBestNodeMatch(targetLabel, searchableNodes);

    if (!source || !target || source.id === target.id) {
      return;
    }

    edges.push({
      source: source.id,
      target: target.id,
      label: edge.label || "relates",
      relation: "semantic",
    });
  });

  conceptNodes.forEach((concept, index) => {
    const nextConcept = conceptNodes[index + 1];

    if (!nextConcept || concept.chapterId !== nextConcept.chapterId) {
      return;
    }

    edges.push({
      source: concept.id,
      target: nextConcept.id,
      label: "builds",
      relation: "semantic",
    });
  });
}

function buildFlowEdge(edge, index) {
  const isTimeline = edge.relation === "timeline";
  const isSemantic = edge.relation === "semantic";
  const edgeColor =
    edge.branchColor ||
    (isSemantic ? "var(--app-graph-3)" : "var(--app-accent)");

  return {
    id: `${edge.source}-${edge.target}-${edge.relation}-${index}`,
    source: edge.source,
    target: edge.target,
    label: edge.label,
    type: "smoothstep",
    animated: isTimeline,
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: edgeColor,
    },
    labelStyle: {
      fill: "var(--app-muted)",
      fontSize: 11,
      fontWeight: 700,
    },
    style: {
      stroke: edgeColor,
      strokeWidth: edge.relation === "branch" ? 3 : 2,
      strokeDasharray: isSemantic || isTimeline ? "5 5" : undefined,
    },
  };
}

function buildLayout(nodes) {
  const chapterNodes = nodes.filter((node) => node.kind === "chapter");
  const conceptNodes = nodes.filter((node) => node.kind === "concept");
  const rootX = 420;
  const rootY = 360;
  const chapterRadiusX = 330;
  const chapterRadiusY = 230;
  const conceptsByChapter = conceptNodes.reduce((acc, concept) => {
    acc.set(concept.chapterId, [...(acc.get(concept.chapterId) || []), concept]);
    return acc;
  }, new Map());

  return nodes.map((node) => {
    const palette = getNodePalette(node.kind);
    let position = { x: 0, y: 0 };

    if (node.kind === "lecture") {
      position = {
        x: rootX,
        y: rootY,
      };
    }

    if (node.kind === "chapter") {
      const angle = getBranchAngle(node.order, chapterNodes.length);

      position = {
        x: rootX + Math.cos(angle) * chapterRadiusX,
        y: rootY + Math.sin(angle) * chapterRadiusY,
      };
    }

    if (node.kind === "concept") {
      const chapter = chapterNodes.find((item) => item.id === node.chapterId);
      const siblings = conceptsByChapter.get(node.chapterId) || [];
      const siblingIndex = siblings.findIndex((item) => item.id === node.id);
      const angle = getBranchAngle(chapter?.order || 0, chapterNodes.length);
      const outwardX = Math.cos(angle);
      const outwardY = Math.sin(angle);
      const tangentX = -Math.sin(angle);
      const tangentY = Math.cos(angle);
      const siblingOffset = (siblingIndex - (siblings.length - 1) / 2) * 105;

      position = {
        x:
          rootX +
          outwardX * (chapterRadiusX + 270) +
          tangentX * siblingOffset,
        y:
          rootY +
          outwardY * (chapterRadiusY + 160) +
          tangentY * siblingOffset,
      };
    }

    const branchColor = node.branchColor;
    return {
      id: node.id,
      type: "mindMapNode",
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      data: {
        raw: node,
        label: node.label,
        kind: node.kind,
        timeLabel: node.timeLabel,
        ...palette,
        border: branchColor || palette.border,
        minimap: branchColor || palette.minimap,
      },
      position,
    };
  });
}

function getNodePalette(kind) {
  if (kind === "lecture") {
    return {
      background: "var(--app-graph-1)",
      border: "var(--app-graph-1)",
      text: "var(--app-bg)",
      minimap: "var(--app-graph-1)",
    };
  }

  if (kind === "chapter") {
    return {
      background: "var(--app-panel)",
      border: "var(--app-accent)",
      text: "var(--app-text)",
      minimap: "var(--app-accent)",
    };
  }

  return {
    background: "var(--app-panel-muted)",
    border: "var(--app-border)",
    text: "var(--app-text)",
    minimap: "var(--app-graph-3)",
  };
}

function getBranchColor(index) {
  const colors = [
    "var(--app-graph-2)",
    "var(--app-graph-3)",
    "var(--app-graph-4)",
    "var(--app-graph-5)",
    "var(--app-accent)",
  ];

  return colors[index % colors.length];
}

function getBranchAngle(index, total) {
  if (total <= 1) {
    return 0;
  }

  const start = -Math.PI * 0.82;
  const end = Math.PI * 0.82;

  return start + (index / (total - 1)) * (end - start);
}

function findChapterForTimestamp(timestamp, chapterNodes) {
  return (
    chapterNodes.find(
      (chapter) => timestamp >= chapter.timestamp && timestamp <= chapter.end
    ) ||
    [...chapterNodes]
      .reverse()
      .find((chapter) => timestamp >= chapter.timestamp) ||
    chapterNodes[0]
  );
}

function findBestNodeMatch(label, nodes) {
  const normalizedLabel = normalize(label);

  return nodes.find((node) => normalize(node.label) === normalizedLabel)
    || nodes.find((node) => normalizedLabel.includes(normalize(node.label)))
    || nodes.find((node) => normalize(node.label).includes(normalizedLabel));
}

function dedupeEdges(edges) {
  const seen = new Set();

  return edges.filter((edge) => {
    const key = `${edge.source}-${edge.target}-${edge.label}`;

    if (seen.has(key)) {
      return false;
    }

    seen.add(key);
    return true;
  });
}

function normalize(value = "") {
  return String(value).toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}
