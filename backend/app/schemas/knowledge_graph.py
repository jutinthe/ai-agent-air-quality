from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from app.schemas.common import StrictBaseModel


class NodeType(StrEnum):
    PAPER = "paper"
    AUTHOR = "author"
    POPULATION = "population"
    LOCATION = "location"
    POLLUTANT = "pollutant"
    EXPOSURE_ASSESSMENT = "exposure_assessment"
    HEALTH_OUTCOME = "health_outcome"
    STUDY_DESIGN = "study_design"
    STATISTICAL_METHOD = "statistical_method"
    EFFECT_ESTIMATE = "effect_estimate"
    RELATIONSHIP = "relationship"
    CONCLUSION = "conclusion"
    LIMITATION = "limitation"
    DATA_SOURCE = "data_source"
    COVARIATE = "covariate"


class EdgeType(StrEnum):
    AUTHORED_BY = "authored_by"
    STUDIED_POPULATION = "studied_population"
    CONDUCTED_IN = "conducted_in"
    EXAMINED_EXPOSURE = "examined_exposure"
    ASSESSED_BY = "assessed_by"
    MEASURED_OUTCOME = "measured_outcome"
    USED_DESIGN = "used_design"
    USED_METHOD = "used_method"
    ADJUSTED_FOR = "adjusted_for"
    REPORTED_EFFECT = "reported_effect"
    EFFECT_FOR_EXPOSURE = "effect_for_exposure"
    EFFECT_ON_OUTCOME = "effect_on_outcome"
    FOUND_RELATIONSHIP = "found_relationship"
    CONCLUDED = "concluded"
    HAS_LIMITATION = "has_limitation"
    USED_DATA_SOURCE = "used_data_source"


class KnowledgeGraphNode(StrictBaseModel):
    id: str
    type: NodeType
    label: str
    description: str | None = None
    attributes: dict[str, str | int | float | bool | None] = Field(
        default_factory=dict
    )


class KnowledgeGraphEdge(StrictBaseModel):
    id: str
    source: str
    target: str
    type: EdgeType
    label: str
    attributes: dict[str, str | int | float | bool | None] = Field(
        default_factory=dict
    )


class PaperKnowledgeGraph(StrictBaseModel):
    paper_id: UUID
    title: str
    nodes: list[KnowledgeGraphNode]
    edges: list[KnowledgeGraphEdge]
    node_count: int = Field(ge=1)
    edge_count: int = Field(ge=0)
    schema_version: str = "1.0.0"
    generated_at: datetime


class CytoscapeElementData(StrictBaseModel):
    id: str
    label: str
    type: str
    source: str | None = None
    target: str | None = None
    description: str | None = None


class CytoscapeElement(StrictBaseModel):
    data: CytoscapeElementData


class CytoscapeGraph(StrictBaseModel):
    paper_id: UUID
    title: str
    elements: list[CytoscapeElement]
