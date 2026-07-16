"use client";

import cytoscape, { Core, ElementDefinition } from "cytoscape";
import {
  CircleAlert,
  Focus,
  LoaderCircle,
  Maximize2,
  Network,
  RefreshCw,
  Search,
  ZoomIn,
  ZoomOut
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

type GraphElement = {
  data: {
    id: string;
    label: string;
    type: string;
    source?: string | null;
    target?: string | null;
    description?: string | null;
  };
};

type GraphResponse = {
  paper_id: string;
  title: string;
  elements: GraphElement[];
};

type SelectedNode = {
  id: string;
  label: string;
  type: string;
  description?: string | null;
};

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

const TYPE_LABELS: Record<string, string> = {
  paper: "Paper",
  author: "Author",
  population: "Population",
  location: "Location",
  pollutant: "Pollutant",
  exposure_assessment: "Exposure assessment",
  health_outcome: "Health outcome",
  study_design: "Study design",
  statistical_method: "Statistical method",
  effect_estimate: "Effect estimate",
  relationship: "Relationship",
  conclusion: "Conclusion",
  limitation: "Limitation",
  data_source: "Data source",
  covariate: "Covariate"
};

function displayType(type: string) {
  return TYPE_LABELS[type] ?? type.replaceAll("_", " ");
}

async function getGraph(paperId: string): Promise<GraphResponse> {
  const url = `${API_BASE}/api/papers/${paperId}/knowledge-graph/cytoscape`;
  let response = await fetch(url, { cache: "no-store" });

  if (response.status === 404) {
    const createResponse = await fetch(
      `${API_BASE}/api/papers/${paperId}/knowledge-graph`,
      { method: "POST" }
    );

    if (!createResponse.ok) {
      const message = await createResponse.text();
      throw new Error(message || "Knowledge graph generation failed.");
    }

    response = await fetch(url, { cache: "no-store" });
  }

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Could not load the knowledge graph.");
  }

  return response.json();
}

const demoGraph: GraphResponse = {
  paper_id: "demo-1",
  title: "Long-Term PM2.5 Exposure and Cardiovascular Mortality",
  elements: [
    { data: { id: "paper:demo", label: "Long-Term PM2.5 Exposure and Cardiovascular Mortality", type: "paper" } },
    { data: { id: "author:martinez", label: "Elena Martinez", type: "author" } },
    { data: { id: "population:older", label: "Adults aged 65 years and older", type: "population" } },
    { data: { id: "location:us", label: "United States", type: "location" } },
    { data: { id: "pollutant:pm25", label: "PM2.5", type: "pollutant" } },
    { data: { id: "assessment:model", label: "Monitor + satellite ensemble model", type: "exposure_assessment" } },
    { data: { id: "outcome:cvd", label: "Cardiovascular mortality", type: "health_outcome" } },
    { data: { id: "design:cohort", label: "Retrospective cohort", type: "study_design" } },
    { data: { id: "method:cox", label: "Cox proportional hazards model", type: "statistical_method" } },
    { data: { id: "covariate:age", label: "Age", type: "covariate" } },
    { data: { id: "effect:hr", label: "HR 1.08 (95% CI 1.05–1.11)", type: "effect_estimate", description: "An 8% higher cardiovascular mortality risk per 10 µg/m³ increase in annual PM2.5." } },
    { data: { id: "relationship:risk", label: "Increased risk", type: "relationship" } },
    { data: { id: "limitation:misclassification", label: "Exposure misclassification", type: "limitation" } },
    { data: { id: "source:epa", label: "EPA Air Quality System", type: "data_source" } },
    { data: { id: "edge:1", label: "authored by", type: "authored_by", source: "paper:demo", target: "author:martinez" } },
    { data: { id: "edge:2", label: "studied population", type: "studied_population", source: "paper:demo", target: "population:older" } },
    { data: { id: "edge:3", label: "conducted in", type: "conducted_in", source: "paper:demo", target: "location:us" } },
    { data: { id: "edge:4", label: "examined exposure", type: "examined_exposure", source: "paper:demo", target: "pollutant:pm25" } },
    { data: { id: "edge:5", label: "assessed by", type: "assessed_by", source: "pollutant:pm25", target: "assessment:model" } },
    { data: { id: "edge:6", label: "measured outcome", type: "measured_outcome", source: "paper:demo", target: "outcome:cvd" } },
    { data: { id: "edge:7", label: "used design", type: "used_design", source: "paper:demo", target: "design:cohort" } },
    { data: { id: "edge:8", label: "used method", type: "used_method", source: "paper:demo", target: "method:cox" } },
    { data: { id: "edge:9", label: "adjusted for", type: "adjusted_for", source: "method:cox", target: "covariate:age" } },
    { data: { id: "edge:10", label: "reported effect", type: "reported_effect", source: "paper:demo", target: "effect:hr" } },
    { data: { id: "edge:11", label: "effect for exposure", type: "effect_for_exposure", source: "effect:hr", target: "pollutant:pm25" } },
    { data: { id: "edge:12", label: "effect on outcome", type: "effect_on_outcome", source: "effect:hr", target: "outcome:cvd" } },
    { data: { id: "edge:13", label: "found relationship", type: "found_relationship", source: "paper:demo", target: "relationship:risk" } },
    { data: { id: "edge:14", label: "has limitation", type: "has_limitation", source: "paper:demo", target: "limitation:misclassification" } },
    { data: { id: "edge:15", label: "used data source", type: "used_data_source", source: "paper:demo", target: "source:epa" } }
  ]
};

export function KnowledgeGraph({ paperId }: { paperId: string }) {
  const graphContainer = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const [selected, setSelected] = useState<SelectedNode | null>(null);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [error, setError] = useState("");

  async function load() {
    setStatus("loading");
    setError("");

    try {
      const result = paperId.startsWith("demo")
        ? demoGraph
        : await getGraph(paperId);
      setGraph(result);
      setStatus("ready");
    } catch (cause) {
      setError(
        cause instanceof Error ? cause.message : "Could not load the graph."
      );
      setStatus("error");
    }
  }

  useEffect(() => {
    load();
  }, [paperId]);

  useEffect(() => {
    if (!graphContainer.current || !graph) return;

    const elements: ElementDefinition[] = graph.elements.map((element) => ({
      data: element.data
    }));

    const cy = cytoscape({
      container: graphContainer.current,
      elements,
      layout: {
        name: "cose",
        animate: true,
        randomize: true,
        nodeRepulsion: () => 8500,
        idealEdgeLength: () => 120,
        edgeElasticity: () => 100,
        gravity: 0.3,
        numIter: 900,
        fit: true,
        padding: 44
      },
      wheelSensitivity: 0.18,
      minZoom: 0.22,
      maxZoom: 2.8,
      style: [
        {
          selector: "node",
          style: {
            "background-color": "#64748b",
            label: "data(label)",
            color: "#dbeafe",
            "font-size": 10,
            "font-weight": 500,
            "text-wrap": "wrap",
            "text-max-width": "120px",
            "text-valign": "bottom",
            "text-margin-y": 9,
            width: 35,
            height: 35,
            "border-width": 2,
            "border-color": "rgba(255,255,255,.18)",
            "overlay-opacity": 0
          }
        },
        {
          selector: 'node[type = "paper"]',
          style: {
            "background-color": "#67e8f9",
            color: "#f8fafc",
            width: 62,
            height: 62,
            "font-size": 12,
            "font-weight": 700,
            "text-max-width": "190px",
            "border-color": "#cffafe",
            "border-width": 3
          }
        },
        {
          selector: 'node[type = "pollutant"]',
          style: { "background-color": "#fbbf24" }
        },
        {
          selector: 'node[type = "health_outcome"]',
          style: { "background-color": "#fb7185" }
        },
        {
          selector: 'node[type = "population"]',
          style: { "background-color": "#a78bfa" }
        },
        {
          selector: 'node[type = "effect_estimate"]',
          style: {
            "background-color": "#6ee7b7",
            width: 48,
            height: 48
          }
        },
        {
          selector: 'node[type = "limitation"]',
          style: { "background-color": "#f87171" }
        },
        {
          selector: 'node[type = "data_source"]',
          style: { "background-color": "#60a5fa" }
        },
        {
          selector: 'node[type = "statistical_method"]',
          style: { "background-color": "#c084fc" }
        },
        {
          selector: 'node[type = "author"]',
          style: { "background-color": "#94a3b8", width: 27, height: 27 }
        },
        {
          selector: "edge",
          style: {
            width: 1.4,
            "line-color": "rgba(148,163,184,.36)",
            "target-arrow-color": "rgba(148,163,184,.55)",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            label: "data(label)",
            color: "#718096",
            "font-size": 7,
            "text-rotation": "autorotate",
            "text-background-color": "#07111d",
            "text-background-opacity": 0.78,
            "text-background-padding": "2px",
            "arrow-scale": 0.7,
            "overlay-opacity": 0
          }
        },
        {
          selector: "node:selected",
          style: {
            "border-width": 5,
            "border-color": "#ffffff",
            "underlay-color": "#67e8f9",
            "underlay-opacity": 0.15,
            "underlay-padding": 8
          }
        },
        {
          selector: ".dimmed",
          style: { opacity: 0.12 }
        },
        {
          selector: ".highlighted",
          style: {
            opacity: 1,
            "border-width": 4,
            "border-color": "#ffffff"
          }
        }
      ]
    });

    cy.on("tap", "node", (event) => {
      const node = event.target;
      setSelected({
        id: node.id(),
        label: String(node.data("label")),
        type: String(node.data("type")),
        description: node.data("description")
      });

      cy.elements().addClass("dimmed");
      node.closedNeighborhood().removeClass("dimmed").addClass("highlighted");
    });

    cy.on("tap", (event) => {
      if (event.target === cy) {
        setSelected(null);
        cy.elements().removeClass("dimmed highlighted");
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [graph]);

  const nodeCounts = useMemo(() => {
    if (!graph) return [];
    const counts = new Map<string, number>();

    graph.elements
      .filter((element) => !element.data.source)
      .forEach((element) => {
        counts.set(
          element.data.type,
          (counts.get(element.data.type) ?? 0) + 1
        );
      });

    return Array.from(counts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8);
  }, [graph]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.elements().removeClass("dimmed highlighted");

    const query = search.trim().toLowerCase();
    if (!query) return;

    const matches = cy.nodes().filter((node) => {
      const label = String(node.data("label") ?? "").toLowerCase();
      const type = String(node.data("type") ?? "").toLowerCase();
      return label.includes(query) || type.includes(query);
    });

    if (matches.length > 0) {
      cy.elements().addClass("dimmed");
      matches.removeClass("dimmed").addClass("highlighted");
      cy.animate({ fit: { eles: matches, padding: 110 }, duration: 350 });
    }
  }, [search]);

  if (status === "loading") {
    return (
      <div className="glass grid min-h-[620px] place-items-center rounded-[2rem]">
        <div className="text-center">
          <LoaderCircle className="mx-auto animate-spin text-cyan-200" size={38} />
          <p className="mt-4 font-medium">Building paper knowledge graph</p>
          <p className="mt-2 text-sm text-slate-400">
            Connecting exposures, outcomes, methods, findings, and evidence.
          </p>
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="glass grid min-h-[520px] place-items-center rounded-[2rem] p-8">
        <div className="max-w-lg text-center">
          <CircleAlert className="mx-auto text-rose-300" size={40} />
          <h3 className="mt-4 text-lg font-semibold">Graph unavailable</h3>
          <p className="mt-3 text-sm leading-6 text-slate-400">{error}</p>
          <button
            onClick={load}
            className="mt-6 inline-flex items-center gap-2 rounded-2xl bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950"
          >
            <RefreshCw size={16} />
            Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <section className="glass overflow-hidden rounded-[2rem]">
      <div className="border-b border-white/10 px-5 py-5 md:px-7">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <div>
            <div className="flex items-center gap-2 text-cyan-200">
              <Network size={18} />
              <span className="text-xs font-semibold uppercase tracking-[0.18em]">
                Paper knowledge graph
              </span>
            </div>
            <h3 className="mt-2 text-xl font-semibold">{graph?.title}</h3>
            <p className="mt-1 text-sm text-slate-400">
              Click a node to inspect it and highlight its immediate relationships.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search
                size={15}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
              />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search graph"
                className="w-56 rounded-xl border border-white/10 bg-slate-950/35 py-2.5 pl-9 pr-3 text-sm outline-none transition placeholder:text-slate-600 focus:border-cyan-300/35"
              />
            </div>
            <GraphButton
              title="Zoom in"
              onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 1.2)}
              icon={ZoomIn}
            />
            <GraphButton
              title="Zoom out"
              onClick={() => cyRef.current?.zoom(cyRef.current.zoom() / 1.2)}
              icon={ZoomOut}
            />
            <GraphButton
              title="Fit graph"
              onClick={() => cyRef.current?.fit(undefined, 55)}
              icon={Focus}
            />
            <GraphButton
              title="Re-run layout"
              onClick={() => {
                const cy = cyRef.current;
                if (!cy) return;
                cy.layout({
                  name: "cose",
                  animate: true,
                  randomize: true,
                  fit: true,
                  padding: 45
                }).run();
              }}
              icon={RefreshCw}
            />
          </div>
        </div>
      </div>

      <div className="grid min-h-[680px] xl:grid-cols-[1fr_300px]">
        <div className="relative min-h-[620px] border-b border-white/10 xl:border-b-0 xl:border-r">
          <div

            ref={graphContainer}

            className="absolute inset-0 h-full w-full min-h-[620px]"

          />
          <div className="pointer-events-none absolute bottom-4 left-4 rounded-xl border border-white/10 bg-slate-950/65 px-3 py-2 text-[11px] text-slate-400 backdrop-blur">
            Scroll to zoom · drag to pan · click background to reset
          </div>
        </div>

        <aside className="scrollbar max-h-[680px] overflow-y-auto p-5">
          {selected ? (
            <div>
              <div className="text-xs uppercase tracking-[0.18em] text-cyan-200">
                Selected node
              </div>
              <div className="mt-4 rounded-2xl border border-white/10 bg-white/[.025] p-4">
                <span className="rounded-full bg-cyan-300/10 px-2.5 py-1 text-[11px] text-cyan-200">
                  {displayType(selected.type)}
                </span>
                <h4 className="mt-4 font-semibold leading-6">{selected.label}</h4>
                {selected.description && (
                  <p className="mt-3 text-sm leading-6 text-slate-400">
                    {selected.description}
                  </p>
                )}
                <div className="mt-4 break-all text-[11px] text-slate-600">
                  {selected.id}
                </div>
              </div>
            </div>
          ) : (
            <div>
              <div className="text-xs uppercase tracking-[0.18em] text-slate-500">
                Graph summary
              </div>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <SummaryMetric
                  label="Nodes"
                  value={String(
                    graph?.elements.filter((element) => !element.data.source)
                      .length ?? 0
                  )}
                />
                <SummaryMetric
                  label="Edges"
                  value={String(
                    graph?.elements.filter((element) => element.data.source)
                      .length ?? 0
                  )}
                />
              </div>

              <div className="mt-7 text-xs uppercase tracking-[0.18em] text-slate-500">
                Entity types
              </div>
              <div className="mt-3 space-y-2">
                {nodeCounts.map(([type, count]) => (
                  <div
                    key={type}
                    className="flex items-center justify-between rounded-xl border border-white/5 bg-white/[.02] px-3 py-2.5"
                  >
                    <span className="text-sm text-slate-300">
                      {displayType(type)}
                    </span>
                    <span className="rounded-full bg-white/5 px-2 py-0.5 text-xs text-slate-400">
                      {count}
                    </span>
                  </div>
                ))}
              </div>

              <div className="mt-7 rounded-2xl border border-cyan-300/10 bg-cyan-300/5 p-4">
                <Maximize2 size={17} className="text-cyan-200" />
                <p className="mt-3 text-xs leading-5 text-slate-400">
                  Select a node to isolate its local neighborhood and inspect
                  the extracted scientific relationship.
                </p>
              </div>
            </div>
          )}
        </aside>
      </div>
    </section>
  );
}

function GraphButton({
  title,
  onClick,
  icon: Icon
}: {
  title: string;
  onClick: () => void;
  icon: typeof ZoomIn;
}) {
  return (
    <button
      title={title}
      onClick={onClick}
      className="grid h-10 w-10 place-items-center rounded-xl border border-white/10 bg-white/[.025] text-slate-400 transition hover:bg-white/10 hover:text-white"
    >
      <Icon size={17} />
    </button>
  );
}

function SummaryMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[.025] p-4 text-center">
      <div className="text-2xl font-semibold">{value}</div>
      <div className="mt-1 text-xs text-slate-500">{label}</div>
    </div>
  );
}
