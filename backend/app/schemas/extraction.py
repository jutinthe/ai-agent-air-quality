from __future__ import annotations

from datetime import date
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import Field, model_validator

from app.schemas.common import ExtractionEvidence, StrictBaseModel


class PollutantCategory(StrEnum):
    PM25 = "pm2.5"
    PM10 = "pm10"
    OZONE = "ozone"
    NITROGEN_DIOXIDE = "nitrogen_dioxide"
    SULFUR_DIOXIDE = "sulfur_dioxide"
    CARBON_MONOXIDE = "carbon_monoxide"
    BLACK_CARBON = "black_carbon"
    WILDFIRE_SMOKE = "wildfire_smoke"
    TRAFFIC_POLLUTION = "traffic_related_air_pollution"
    HEAT = "heat"
    OTHER = "other"
    NOT_REPORTED = "not_reported"


class StudyDesignType(StrEnum):
    COHORT = "cohort"
    CASE_CONTROL = "case_control"
    CROSS_SECTIONAL = "cross_sectional"
    TIME_SERIES = "time_series"
    CASE_CROSSOVER = "case_crossover"
    PANEL = "panel"
    ECOLOGICAL = "ecological"
    RANDOMIZED_TRIAL = "randomized_controlled_trial"
    QUASI_EXPERIMENTAL = "quasi_experimental"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    MODELING = "modeling"
    OTHER = "other"
    UNCLEAR = "unclear"


class RelationshipDirection(StrEnum):
    INCREASED_RISK = "increased_risk"
    DECREASED_RISK = "decreased_risk"
    POSITIVE_ASSOCIATION = "positive_association"
    NEGATIVE_ASSOCIATION = "negative_association"
    NO_CLEAR_ASSOCIATION = "no_clear_association"
    MIXED = "mixed"
    NONLINEAR = "nonlinear"
    UNCLEAR = "unclear"


class EffectMeasureType(StrEnum):
    RISK_RATIO = "risk_ratio"
    RELATIVE_RISK = "relative_risk"
    ODDS_RATIO = "odds_ratio"
    HAZARD_RATIO = "hazard_ratio"
    RATE_RATIO = "rate_ratio"
    PERCENT_CHANGE = "percent_change"
    MEAN_DIFFERENCE = "mean_difference"
    REGRESSION_COEFFICIENT = "regression_coefficient"
    OTHER = "other"
    NOT_REPORTED = "not_reported"


class PaperMetadata(StrictBaseModel):
    title: str = Field(min_length=1)
    authors: list[str] = Field(default_factory=list)
    journal: str | None = None
    publication_year: int | None = Field(default=None, ge=1800, le=2200)
    doi: str | None = None
    abstract: str | None = None


# Required field 1
class PopulationStudied(StrictBaseModel):
    description: str = Field(min_length=1)
    sample_size: int | None = Field(default=None, ge=0)
    age_description: str | None = None
    sex_or_gender: list[str] = Field(default_factory=list)
    inclusion_criteria: list[str] = Field(default_factory=list)
    exclusion_criteria: list[str] = Field(default_factory=list)
    vulnerable_groups: list[str] = Field(default_factory=list)
    evidence: ExtractionEvidence = Field(default_factory=ExtractionEvidence)


# Required field 2
class GeographicLocation(StrictBaseModel):
    description: str = Field(min_length=1)
    countries: list[str] = Field(default_factory=list)
    states_or_provinces: list[str] = Field(default_factory=list)
    cities_or_regions: list[str] = Field(default_factory=list)
    setting: str | None = None
    evidence: ExtractionEvidence = Field(default_factory=ExtractionEvidence)


# Required field 3
class PollutantExposure(StrictBaseModel):
    name: str = Field(min_length=1)
    category: PollutantCategory
    metric: str | None = None
    concentration_unit: str | None = None
    exposure_increment: float | None = None
    exposure_increment_unit: str | None = None
    coexposures: list[str] = Field(default_factory=list)
    evidence: ExtractionEvidence = Field(default_factory=ExtractionEvidence)


# Required field 4
class ExposureAssessment(StrictBaseModel):
    exposure_period: str = Field(min_length=1)
    study_start_date: date | None = None
    study_end_date: date | None = None
    averaging_period: str | None = None
    lag_periods: list[str] = Field(default_factory=list)
    measurement_methods: list[str] = Field(min_length=1)
    spatial_resolution: str | None = None
    temporal_resolution: str | None = None
    exposure_assignment_method: str | None = None
    evidence: ExtractionEvidence = Field(default_factory=ExtractionEvidence)

    @model_validator(mode="after")
    def validate_dates(self) -> "ExposureAssessment":
        if (
            self.study_start_date is not None
            and self.study_end_date is not None
            and self.study_start_date > self.study_end_date
        ):
            raise ValueError(
                "study_start_date cannot be after study_end_date"
            )
        return self


# Required field 5
class HealthOutcome(StrictBaseModel):
    name: str = Field(min_length=1)
    category: str | None = None
    definition: str | None = None
    measurement_method: str | None = None
    diagnostic_codes: list[str] = Field(default_factory=list)
    follow_up_period: str | None = None
    evidence: ExtractionEvidence = Field(default_factory=ExtractionEvidence)


# Required field 6
class StudyDesign(StrictBaseModel):
    design: StudyDesignType
    description: str = Field(min_length=1)
    prospective: bool | None = None
    longitudinal: bool | None = None
    unit_of_analysis: str | None = None
    comparison_group: str | None = None
    evidence: ExtractionEvidence = Field(default_factory=ExtractionEvidence)


# Required field 7
class StatisticalMethod(StrictBaseModel):
    primary_models: list[str] = Field(min_length=1)
    secondary_models: list[str] = Field(default_factory=list)
    covariates: list[str] = Field(default_factory=list)
    confounder_strategy: str | None = None
    sensitivity_analyses: list[str] = Field(default_factory=list)
    missing_data_method: str | None = None
    software: list[str] = Field(default_factory=list)
    evidence: ExtractionEvidence = Field(default_factory=ExtractionEvidence)


# Required field 8
class EffectEstimate(StrictBaseModel):
    outcome_name: str = Field(min_length=1)
    exposure_name: str = Field(min_length=1)
    measure_type: EffectMeasureType
    value: float | None = None
    confidence_interval_lower: float | None = None
    confidence_interval_upper: float | None = None
    p_value: float | None = Field(default=None, ge=0, le=1)
    exposure_contrast: str | None = None
    population_subgroup: str | None = None
    reported_text: str = Field(min_length=1)
    evidence: ExtractionEvidence = Field(default_factory=ExtractionEvidence)

    @model_validator(mode="after")
    def validate_confidence_interval(self) -> "EffectEstimate":
        lower = self.confidence_interval_lower
        upper = self.confidence_interval_upper

        if lower is not None and upper is not None and lower > upper:
            raise ValueError(
                "confidence_interval_lower cannot exceed "
                "confidence_interval_upper"
            )

        return self


class QuantitativeResults(StrictBaseModel):
    primary_result: EffectEstimate | None = None
    additional_results: list[EffectEstimate] = Field(default_factory=list)
    narrative_result: str | None = None
    evidence: ExtractionEvidence = Field(default_factory=ExtractionEvidence)


# Required field 9
class RelationshipAssessment(StrictBaseModel):
    direction: RelationshipDirection
    description: str = Field(min_length=1)
    statistically_significant: bool | None = None
    dose_response_reported: bool | None = None
    consistent_across_analyses: bool | None = None
    evidence: ExtractionEvidence = Field(default_factory=ExtractionEvidence)


# Required field 10
class KeyConclusions(StrictBaseModel):
    conclusions: list[str] = Field(min_length=1)
    authors_interpretation: str | None = None
    public_health_implications: list[str] = Field(default_factory=list)
    causal_language_used: bool | None = None
    evidence: ExtractionEvidence = Field(default_factory=ExtractionEvidence)


# Required field 11
class StudyLimitation(StrictBaseModel):
    description: str = Field(min_length=1)
    category: str | None = None
    potential_impact: str | None = None
    acknowledged_by_authors: bool = True
    evidence: ExtractionEvidence = Field(default_factory=ExtractionEvidence)


class LimitationsAssessment(StrictBaseModel):
    limitations: list[StudyLimitation] = Field(default_factory=list)
    overall_notes: str | None = None
    evidence: ExtractionEvidence = Field(default_factory=ExtractionEvidence)


# Required field 12
class ResearchDataSource(StrictBaseModel):
    name: str = Field(min_length=1)
    source_type: str
    provider: str | None = None
    variables_used: list[str] = Field(default_factory=list)
    geographic_coverage: str | None = None
    temporal_coverage: str | None = None
    access_url: str | None = None
    access_restrictions: str | None = None
    evidence: ExtractionEvidence = Field(default_factory=ExtractionEvidence)


class DataSources(StrictBaseModel):
    exposure_sources: list[ResearchDataSource] = Field(default_factory=list)
    health_sources: list[ResearchDataSource] = Field(default_factory=list)
    demographic_sources: list[ResearchDataSource] = Field(default_factory=list)
    environmental_sources: list[ResearchDataSource] = Field(default_factory=list)
    other_sources: list[ResearchDataSource] = Field(default_factory=list)
    evidence: ExtractionEvidence = Field(default_factory=ExtractionEvidence)


class PaperExtraction(StrictBaseModel):
    extraction_id: UUID = Field(default_factory=uuid4)
    paper_metadata: PaperMetadata

    population_studied: PopulationStudied
    geographic_location: GeographicLocation
    pollutants_or_exposures: list[PollutantExposure] = Field(min_length=1)
    exposure_assessment: ExposureAssessment
    health_outcomes: list[HealthOutcome] = Field(min_length=1)
    study_design: StudyDesign
    statistical_methods: StatisticalMethod
    quantitative_results: QuantitativeResults
    relationship: RelationshipAssessment
    key_conclusions: KeyConclusions
    limitations: LimitationsAssessment
    data_sources: DataSources

    extraction_model: str | None = None
    extraction_prompt_version: str | None = None
    schema_version: str = "1.0.0"
