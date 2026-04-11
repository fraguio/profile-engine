from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tests.subprocess_cli import run_profilecli_subprocess
from profilecli.convert_rendercv import convert_jsonresume_to_rendercv, normalize_date


def _sample_payload() -> dict:
    return {
        "basics": {
            "name": "Jane Doe",
            "label": "Backend Engineer",
            "email": "jane.doe@example.com",
            "phone": "+34111222333",
            "url": "https://janedoe.dev",
            "summary": "First paragraph.\n\nSecond paragraph.",
            "location": {"city": "A Coruna", "region": "Galicia", "countryCode": "ES"},
        },
        "work": [
            {
                "name": "Acme",
                "position": "Engineer",
                "startDate": "2024",
            },
            {
                "name": "Globex",
                "position": "Senior Engineer",
                "startDate": "2024-01-20",
                "endDate": "2024-05-15",
            },
        ],
        "education": [
            {
                "institution": "University X",
                "title": "Computer Science",
                "studyType": "BS",
                "startDate": "2020",
                "status": "in_progress",
                "details": ["Core systems"],
                "notes": "Final thesis ongoing",
            }
        ],
        "skills": [{"name": "Backend", "keywords": ["Python", "SQL"]}],
        "languages": [
            {"language": "Espanol", "fluency": "Nativo"},
            {"language": "Ingles", "fluency": "Profesional"},
        ],
    }


def test_convert_sets_cv_name_and_design_theme() -> None:
    result = convert_jsonresume_to_rendercv(_sample_payload())
    assert result["cv"]["name"] == "Jane Doe"
    assert result["design"]["theme"] == "profileengine01classic"
    assert result["locale"]["language"] == "spanish"


def test_basics_contact_fields_map_to_rendercv_cv() -> None:
    result = convert_jsonresume_to_rendercv(_sample_payload())
    assert result["cv"]["email"] == "jane.doe@example.com"
    assert result["cv"]["phone"] == "+34111222333"
    assert result["cv"]["website"] == "https://janedoe.dev"


def test_basics_contact_fields_skip_blank_values() -> None:
    payload = _sample_payload()
    payload["basics"]["email"] = "   "
    payload["basics"]["phone"] = ""
    payload["basics"]["url"] = "  "

    result = convert_jsonresume_to_rendercv(payload)

    assert "email" not in result["cv"]
    assert "phone" not in result["cv"]
    assert "website" not in result["cv"]


def test_experience_count_matches_work_length() -> None:
    payload = _sample_payload()
    result = convert_jsonresume_to_rendercv(payload)
    assert len(result["cv"]["sections"]["experience"]) == len(payload["work"])


def test_education_area_from_title() -> None:
    result = convert_jsonresume_to_rendercv(_sample_payload())
    assert result["cv"]["sections"]["education"][0]["area"] == "Computer Science"


def test_education_in_progress_sets_end_date_present() -> None:
    result = convert_jsonresume_to_rendercv(_sample_payload())
    assert result["cv"]["sections"]["education"][0]["end_date"] == "present"


def test_skills_appends_idiomas_entry_from_languages() -> None:
    result = convert_jsonresume_to_rendercv(_sample_payload())
    idiomas_entry = next(
        (item for item in result["cv"]["sections"]["skills"] if item.get("label") == "Idiomas"),
        None,
    )
    assert idiomas_entry is not None
    assert "Espanol (Nativo)" in idiomas_entry["details"]
    assert "Ingles (Profesional)" in idiomas_entry["details"]


def test_date_normalization_cases() -> None:
    assert normalize_date("2024") == "2024-01"
    assert normalize_date("2024-07-15") == "2024-07"
    assert normalize_date("2024-07") == "2024-07"

    payload = _sample_payload()
    payload["work"] = [{"name": "Acme", "position": "Engineer", "startDate": "2023-02"}]
    payload["education"] = [{"institution": "Uni", "title": "Math", "startDate": "2020-01"}]
    result = convert_jsonresume_to_rendercv(payload)

    assert result["cv"]["sections"]["experience"][0]["end_date"] == "present"
    assert "start_date" in result["cv"]["sections"]["education"][0]
    assert "end_date" not in result["cv"]["sections"]["education"][0]


def test_required_top_level_keys_present_when_empty() -> None:
    result = convert_jsonresume_to_rendercv({})
    assert set(result.keys()) == {"cv", "design", "locale"}
    assert result["cv"] == {}
    assert result["design"] == {"theme": "profileengine01classic"}
    assert result["locale"] == {"language": "spanish"}


def test_cli_rendercv_stdout_contains_schema_header(tmp_path) -> None:
    input_file = tmp_path / "resume.json"
    input_file.write_text(json.dumps(_sample_payload()), encoding="utf-8")

    result = run_profilecli_subprocess(["rendercv", str(input_file)])

    assert result.returncode == 0
    first_line = result.stdout.splitlines()[0]
    assert (
        first_line
        == "# yaml-language-server: $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v2.8/schema.json"
    )


def test_cli_rendercv_writes_output_file(tmp_path) -> None:
    input_file = tmp_path / "resume.json"
    output_file = tmp_path / "out.yaml"
    input_file.write_text(json.dumps(_sample_payload()), encoding="utf-8")

    result = run_profilecli_subprocess(["rendercv", str(input_file), "-o", str(output_file)])

    assert result.returncode == 0
    assert output_file.exists()
    first_line = output_file.read_text(encoding="utf-8").splitlines()[0]
    assert (
        first_line
        == "# yaml-language-server: $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v2.8/schema.json"
    )
