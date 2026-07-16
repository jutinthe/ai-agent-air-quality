from uuid import uuid4

from app.schemas.extraction import (
    DataSources,
    EffectEstimate,
    EffectMeasureType,
    ExposureAssessment,
    GeographicLocation,
    HealthOutcome,
    KeyConclusions,
    LimitationsAssessment,
    PaperExtraction,
    PaperMetadata,
    PollutantCategory,
    PollutantExposure,
    PopulationStudied,
    QuantitativeResults,
    RelationshipAssessment,
    RelationshipDirection,
    StatisticalMethod,
    StudyDesign,
    StudyDesignType,
)
from app.services.knowledge_graph_service import generate_knowledge_graph


def make_extraction() -> PaperExtraction:
    return PaperExtraction(
        paper_metadata=PaperMetadata(
            title="PM2.5 and Mortality",
            authors=["Alice Smith", "Brian Chen"],
        ),
        population_studied=PopulationStudied(
            description="Adults aged 65 years and older",
            sample_size=100000,
        ),
        geographic_location=GeographicLocation(
            description="United States"
        ),
        pollutants_or_exposures=[
            PollutantExposure(
                name="PM2.5",
                category=PollutantCategory.PM25,
                concentration_unit="µg/m³",
            )
        ],
        exposure_assessment=ExposureAssessment(
            exposure_period="Annual average",
            measurement_methods=["Ground monitors"],
        ),
        health_outcomes=[
            HealthOutcome(name="All-cause mortality")
        ],
        study_design=StudyDesign(
            design=StudyDesignType.COHORT,
            description="Retrospective cohort study",
        ),
        statistical_methods=StatisticalMethod(
            primary_models=["Cox proportional hazards model"],
            covariates=["Age", "Sex"],
        ),
        quantitative_results=QuantitativeResults(
            primary_result=EffectEstimate(
                outcome_name="All-cause mortality",
                exposure_name="PM2.5",
                measure_type=EffectMeasureType.HAZARD_RATIO,
                value=1.08,
                confidence_interval_lower=1.05,
                confidence_interval_upper=1.11,
                reported_text="HR 1.08 (95% CI 1.05–1.11)",
            )
        ),
        relationship=RelationshipAssessment(
            direction=RelationshipDirection.INCREASED_RISK,
            description="Higher exposure was associated with increased risk.",
        ),
        key_conclusions=KeyConclusions(
            conclusions=["PM2.5 was associated with mortality."]
        ),
        limitations=LimitationsAssessment(),
        data_sources=DataSources(),
    )


def test_generates_paper_graph() -> None:
    paper_id = uuid4()
    graph = generate_knowledge_graph(paper_id, make_extraction())

    node_types = {node.type.value for node in graph.nodes}
    edge_types = {edge.type.value for edge in graph.edges}

    assert graph.paper_id == paper_id
    assert graph.node_count == len(graph.nodes)
    assert graph.edge_count == len(graph.edges)
    assert "paper" in node_types
    assert "pollutant" in node_types
    assert "health_outcome" in node_types
    assert "effect_estimate" in node_types
    assert "examined_exposure" in edge_types
    assert "measured_outcome" in edge_types
    assert "reported_effect" in edge_types
