import json
from pathlib import Path

from app.schemas.extraction import PaperExtraction


def export_schema() -> Path:
    output_directory = Path("storage/processed")
    output_directory.mkdir(parents=True, exist_ok=True)

    output_path = output_directory / "paper_extraction_schema.json"
    output_path.write_text(
        json.dumps(
            PaperExtraction.model_json_schema(),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return output_path


if __name__ == "__main__":
    result = export_schema()
    print(f"Schema exported to {result}")
