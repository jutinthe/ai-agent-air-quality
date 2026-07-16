from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from app.schemas.extraction import EffectEstimate, PaperExtraction
from app.schemas.knowledge_graph import (
    CytoscapeElement,
    CytoscapeElementData,
    CytoscapeGraph,
    EdgeType,
    KnowledgeGraphEdge,
    KnowledgeGraphNode,
    NodeType,
    PaperKnowledgeGraph,
)


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    if not cleaned:
        cleaned = "item"
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    return f"{cleaned[:55]}-{digest}"


class GraphBuilder:
    def __init__(self, paper_id: UUID, extraction: PaperExtraction) -> None:
        self.paper_id = paper_id
        self.extraction = extraction
        self.nodes: dict[str, KnowledgeGraphNode] = {}
        self.edges: dict[str, KnowledgeGraphEdge] = {}
        self.paper_node_id = f"paper:{paper_id}"

    def add_node(
        self,
        node_type: NodeType,
        label: str,
        description: str | None = None,
        attributes: dict[str, str | int | float | bool | None] | None = None,
        fixed_id: str | None = None,
    ) -> str:
        node_id = fixed_id or f"{node_type.value}:{_slug(label)}"

        if node_id not in self.nodes:
            self.nodes[node_id] = KnowledgeGraphNode(
                id=node_id,
                type=node_type,
                label=label,
                description=description,
                attributes=attributes or {},
            )

        return node_id

    def add_edge(
        self,
        source: str,
        target: str,
        edge_type: EdgeType,
        label: str,
        attributes: dict[str, str | int | float | bool | None] | None = None,
    ) -> str:
        edge_seed = f"{source}|{edge_type.value}|{target}"
        edge_id = f"edge:{hashlib.sha1(edge_seed.encode()).hexdigest()[:14]}"

        if edge_id not in self.edges:
            self.edges[edge_id] = KnowledgeGraphEdge(
                id=edge_id,
                source=source,
                target=target,
                type=edge_type,
                label=label,
                attributes=attributes or {},
            )

        return edge_id

    def build(self) -> PaperKnowledgeGraph:
        metadata = self.extraction.paper_metadata

        self.add_node(
            NodeType.PAPER,
            metadata.title,
            attributes={
                "journal": metadata.journal,
                "publication_year": metadata.publication_year,
                "doi": metadata.doi,
            },
            fixed_id=self.paper_node_id,
        )

        self._add_authors()
        self._add_population()
        self._add_location()
        exposure_nodes = self._add_exposures()
        self._add_exposure_assessment(exposure_nodes)
        outcome_nodes = self._add_outcomes()
        self._add_study_design()
        self._add_statistical_methods()
        self._add_effects(exposure_nodes, outcome_nodes)
        self._add_relationship()
        self._add_conclusions()
        self._add_limitations()
        self._add_data_sources()

        return PaperKnowledgeGraph(
            paper_id=self.paper_id,
            title=metadata.title,
            nodes=list(self.nodes.values()),
            edges=list(self.edges.values()),
            node_count=len(self.nodes),
            edge_count=len(self.edges),
            generated_at=datetime.now(UTC),
        )

    def _add_authors(self) -> None:
        for author in self.extraction.paper_metadata.authors:
            node_id = self.add_node(NodeType.AUTHOR, author)
            self.add_edge(
                self.paper_node_id,
                node_id,
                EdgeType.AUTHORED_BY,
                "authored by",
            )

    def _add_population(self) -> None:
        population = self.extraction.population_studied
        node_id = self.add_node(
            NodeType.POPULATION,
            population.description,
            attributes={
                "sample_size": population.sample_size,
                "age_description": population.age_description,
            },
        )
        self.add_edge(
            self.paper_node_id,
            node_id,
            EdgeType.STUDIED_POPULATION,
            "studied population",
        )

    def _add_location(self) -> None:
        location = self.extraction.geographic_location
        node_id = self.add_node(
            NodeType.LOCATION,
            location.description,
            attributes={"setting": location.setting},
        )
        self.add_edge(
            self.paper_node_id,
            node_id,
            EdgeType.CONDUCTED_IN,
            "conducted in",
        )

    def _add_exposures(self) -> list[str]:
        result: list[str] = []

        for exposure in self.extraction.pollutants_or_exposures:
            node_id = self.add_node(
                NodeType.POLLUTANT,
                exposure.name,
                attributes={
                    "category": exposure.category.value,
                    "metric": exposure.metric,
                    "concentration_unit": exposure.concentration_unit,
                    "exposure_increment": exposure.exposure_increment,
                    "exposure_increment_unit": exposure.exposure_increment_unit,
                },
            )
            result.append(node_id)
            self.add_edge(
                self.paper_node_id,
                node_id,
                EdgeType.EXAMINED_EXPOSURE,
                "examined exposure",
            )

        return result

    def _add_exposure_assessment(self, exposure_nodes: list[str]) -> None:
        assessment = self.extraction.exposure_assessment
        method_label = "; ".join(assessment.measurement_methods)
        node_id = self.add_node(
            NodeType.EXPOSURE_ASSESSMENT,
            method_label or "Exposure assessment",
            description=assessment.exposure_period,
            attributes={
                "exposure_period": assessment.exposure_period,
                "averaging_period": assessment.averaging_period,
                "spatial_resolution": assessment.spatial_resolution,
                "temporal_resolution": assessment.temporal_resolution,
            },
        )

        for exposure_node in exposure_nodes:
            self.add_edge(
                exposure_node,
                node_id,
                EdgeType.ASSESSED_BY,
                "assessed by",
            )

    def _add_outcomes(self) -> list[str]:
        result: list[str] = []

        for outcome in self.extraction.health_outcomes:
            node_id = self.add_node(
                NodeType.HEALTH_OUTCOME,
                outcome.name,
                description=outcome.definition,
                attributes={
                    "category": outcome.category,
                    "measurement_method": outcome.measurement_method,
                },
            )
            result.append(node_id)
            self.add_edge(
                self.paper_node_id,
                node_id,
                EdgeType.MEASURED_OUTCOME,
                "measured outcome",
            )

        return result

    def _add_study_design(self) -> None:
        design = self.extraction.study_design
        node_id = self.add_node(
            NodeType.STUDY_DESIGN,
            design.description,
            attributes={
                "design": design.design.value,
                "prospective": design.prospective,
                "longitudinal": design.longitudinal,
                "unit_of_analysis": design.unit_of_analysis,
            },
        )
        self.add_edge(
            self.paper_node_id,
            node_id,
            EdgeType.USED_DESIGN,
            "used study design",
        )

    def _add_statistical_methods(self) -> None:
        methods = self.extraction.statistical_methods

        for method in methods.primary_models:
            method_node = self.add_node(NodeType.STATISTICAL_METHOD, method)
            self.add_edge(
                self.paper_node_id,
                method_node,
                EdgeType.USED_METHOD,
                "used statistical method",
            )

            for covariate in methods.covariates:
                covariate_node = self.add_node(NodeType.COVARIATE, covariate)
                self.add_edge(
                    method_node,
                    covariate_node,
                    EdgeType.ADJUSTED_FOR,
                    "adjusted for",
                )

    def _effect_label(self, effect: EffectEstimate) -> str:
        if effect.value is not None:
            label = f"{effect.measure_type.value}: {effect.value}"
            if (
                effect.confidence_interval_lower is not None
                and effect.confidence_interval_upper is not None
            ):
                label += (
                    f" ({effect.confidence_interval_lower}–"
                    f"{effect.confidence_interval_upper})"
                )
            return label

        return effect.reported_text[:160]

    def _add_effects(
        self,
        exposure_nodes: list[str],
        outcome_nodes: list[str],
    ) -> None:
        results = self.extraction.quantitative_results
        effects: list[EffectEstimate] = []

        if results.primary_result is not None:
            effects.append(results.primary_result)

        effects.extend(results.additional_results)

        exposure_by_label = {
            self.nodes[node_id].label.lower(): node_id
            for node_id in exposure_nodes
        }
        outcome_by_label = {
            self.nodes[node_id].label.lower(): node_id
            for node_id in outcome_nodes
        }

        for effect in effects:
            effect_node = self.add_node(
                NodeType.EFFECT_ESTIMATE,
                self._effect_label(effect),
                description=effect.reported_text,
                attributes={
                    "measure_type": effect.measure_type.value,
                    "value": effect.value,
                    "ci_lower": effect.confidence_interval_lower,
                    "ci_upper": effect.confidence_interval_upper,
                    "p_value": effect.p_value,
                    "exposure_contrast": effect.exposure_contrast,
                    "population_subgroup": effect.population_subgroup,
                },
            )

            self.add_edge(
                self.paper_node_id,
                effect_node,
                EdgeType.REPORTED_EFFECT,
                "reported effect",
            )

            exposure_target = exposure_by_label.get(
                effect.exposure_name.lower()
            )
            if exposure_target is None and exposure_nodes:
                exposure_target = exposure_nodes[0]

            outcome_target = outcome_by_label.get(effect.outcome_name.lower())
            if outcome_target is None and outcome_nodes:
                outcome_target = outcome_nodes[0]

            if exposure_target:
                self.add_edge(
                    effect_node,
                    exposure_target,
                    EdgeType.EFFECT_FOR_EXPOSURE,
                    "effect for exposure",
                )

            if outcome_target:
                self.add_edge(
                    effect_node,
                    outcome_target,
                    EdgeType.EFFECT_ON_OUTCOME,
                    "effect on outcome",
                )

    def _add_relationship(self) -> None:
        relationship = self.extraction.relationship
        node_id = self.add_node(
            NodeType.RELATIONSHIP,
            relationship.direction.value.replace("_", " "),
            description=relationship.description,
            attributes={
                "statistically_significant": (
                    relationship.statistically_significant
                ),
                "dose_response_reported": (
                    relationship.dose_response_reported
                ),
                "consistent_across_analyses": (
                    relationship.consistent_across_analyses
                ),
            },
        )
        self.add_edge(
            self.paper_node_id,
            node_id,
            EdgeType.FOUND_RELATIONSHIP,
            "found relationship",
        )

    def _add_conclusions(self) -> None:
        for conclusion in self.extraction.key_conclusions.conclusions:
            node_id = self.add_node(
                NodeType.CONCLUSION,
                conclusion[:180],
                description=conclusion,
            )
            self.add_edge(
                self.paper_node_id,
                node_id,
                EdgeType.CONCLUDED,
                "concluded",
            )

    def _add_limitations(self) -> None:
        for limitation in self.extraction.limitations.limitations:
            node_id = self.add_node(
                NodeType.LIMITATION,
                limitation.description[:180],
                description=limitation.description,
                attributes={
                    "category": limitation.category,
                    "potential_impact": limitation.potential_impact,
                    "acknowledged_by_authors": (
                        limitation.acknowledged_by_authors
                    ),
                },
            )
            self.add_edge(
                self.paper_node_id,
                node_id,
                EdgeType.HAS_LIMITATION,
                "has limitation",
            )

    def _add_data_sources(self) -> None:
        sources = self.extraction.data_sources
        grouped = {
            "exposure": sources.exposure_sources,
            "health": sources.health_sources,
            "demographic": sources.demographic_sources,
            "environmental": sources.environmental_sources,
            "other": sources.other_sources,
        }

        for group_name, group_sources in grouped.items():
            for source in group_sources:
                node_id = self.add_node(
                    NodeType.DATA_SOURCE,
                    source.name,
                    attributes={
                        "source_group": group_name,
                        "source_type": source.source_type,
                        "provider": source.provider,
                        "geographic_coverage": source.geographic_coverage,
                        "temporal_coverage": source.temporal_coverage,
                    },
                )
                self.add_edge(
                    self.paper_node_id,
                    node_id,
                    EdgeType.USED_DATA_SOURCE,
                    f"used {group_name} data source",
                )


def generate_knowledge_graph(
    paper_id: UUID,
    extraction: PaperExtraction,
) -> PaperKnowledgeGraph:
    return GraphBuilder(paper_id, extraction).build()


def save_knowledge_graph(
    graph: PaperKnowledgeGraph,
    processed_directory: Path,
) -> Path:
    output_directory = processed_directory / str(graph.paper_id)
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / "knowledge_graph.json"

    output_path.write_text(
        json.dumps(
            graph.model_dump(mode="json"),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return output_path


def load_knowledge_graph(
    paper_id: UUID,
    processed_directory: Path,
) -> PaperKnowledgeGraph | None:
    path = processed_directory / str(paper_id) / "knowledge_graph.json"

    if not path.exists():
        return None

    return PaperKnowledgeGraph.model_validate_json(
        path.read_text(encoding="utf-8")
    )


def to_cytoscape(graph: PaperKnowledgeGraph) -> CytoscapeGraph:
    elements: list[CytoscapeElement] = []

    for node in graph.nodes:
        elements.append(
            CytoscapeElement(
                data=CytoscapeElementData(
                    id=node.id,
                    label=node.label,
                    type=node.type.value,
                    description=node.description,
                )
            )
        )

    for edge in graph.edges:
        elements.append(
            CytoscapeElement(
                data=CytoscapeElementData(
                    id=edge.id,
                    label=edge.label,
                    type=edge.type.value,
                    source=edge.source,
                    target=edge.target,
                )
            )
        )

    return CytoscapeGraph(
        paper_id=graph.paper_id,
        title=graph.title,
        elements=elements,
    )
