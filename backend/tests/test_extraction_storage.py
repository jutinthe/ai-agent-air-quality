from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.schemas.extraction import (
    DataSources,
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
from app.schemas.llm_extraction import (
    ExtractionRunMetadata,
    StoredExtraction,
)
from app.services.llm_extraction_service import (
    load_extraction,
    save_extraction,
)


def make_extraction() -> PaperExtraction:
    return PaperExtraction(
        paper_metadata=PaperMetadata(title="Test Paper"),
        population_studied=PopulationStudied(
            description="Adults"
        ),
        geographic_location=GeographicLocation(
            description="United States"
        ),
        pollutants_or_exposures=[
            PollutantExposure(
                name="PM2.5",
                category=PollutantCategory.PM25,
            )
        ],
        exposure_assessment=ExposureAssessment(
            exposure_period="Annual",
            measurement_methods=["Air monitors"],
        ),
        health_outcomes=[
            HealthOutcome(name="Mortality")
        ],
        study_design=StudyDesign(
            design=StudyDesignType.COHORT,
            description="Cohort study",
        ),
        statistical_methods=StatisticalMethod(
            primary_models=["Cox regression"]
        ),
        quantitative_results=QuantitativeResults(),
        relationship=RelationshipAssessment(
            direction=RelationshipDirection.INCREASED_RISK,
            description="Increased risk",
        ),
        key_conclusions=KeyConclusions(
            conclusions=["Higher risk"]
        ),
        limitations=LimitationsAssessment(),
        data_sources=DataSources(),
    )


def test_save_and_load_extraction(tmp_path: Path) -> None:
    paper_id = uuid4()

    stored = StoredExtraction(
        extraction=make_extraction(),
        run_metadata=ExtractionRunMetadata(
            paper_id=paper_id,
            model="test-model",
            prompt_version="3.0.0",
            input_character_count=100,
            sections_used=["methods", "results"],
            sections_omitted=["references"],
            attempts=1,
            created_at=datetime.now(UTC),
        ),
    )

    path = save_extraction(
        paper_id=paper_id,
        stored_extraction=stored,
        processed_directory=tmp_path,
    )

    assert path.exists()

    loaded = load_extraction(
        paper_id=paper_id,
        processed_directory=tmp_path,
    )

    assert loaded is not None
    assert loaded.extraction.paper_metadata.title == "Test Paper"
