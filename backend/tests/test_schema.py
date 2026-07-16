from app.schemas.extraction import PaperExtraction


REQUIRED_FIELDS = {
    "population_studied",
    "geographic_location",
    "pollutants_or_exposures",
    "exposure_assessment",
    "health_outcomes",
    "study_design",
    "statistical_methods",
    "quantitative_results",
    "relationship",
    "key_conclusions",
    "limitations",
    "data_sources",
}


def test_schema_contains_all_required_fields() -> None:
    schema = PaperExtraction.model_json_schema()
    properties = set(schema["properties"])

    assert REQUIRED_FIELDS.issubset(properties)


def test_schema_version_default() -> None:
    schema = PaperExtraction.model_json_schema()
    version_schema = schema["properties"]["schema_version"]

    assert version_schema["default"] == "1.0.0"
