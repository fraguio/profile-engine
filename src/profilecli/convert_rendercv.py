from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

SCHEMA_HEADER = (
    "# yaml-language-server: "
    "$schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v2.6/schema.json"
)


def load_jsonresume(input_path: Path) -> dict[str, Any]:
    with input_path.open("r", encoding="utf-8") as input_file:
        payload = json.load(input_file)
    if isinstance(payload, dict):
        return payload
    return {}


def normalize_date(
    value: object,
    *,
    is_end: bool = False,
    in_progress: bool = False,
) -> str | None:
    if is_end and in_progress:
        return "present"

    if value is None:
        return None

    raw = str(value).strip()
    if not raw:
        return None

    if re.fullmatch(r"\d{4}", raw):
        return f"{raw}-01"

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        return raw[:7]

    if re.fullmatch(r"\d{4}-\d{2}", raw):
        return raw

    return raw


def _join_location(location: dict[str, Any]) -> str | None:
    if not isinstance(location, dict):
        return None
    parts = []
    for key in ("city", "region", "countryCode"):
        value = location.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())
    if not parts:
        return None
    return ", ".join(parts)


def _split_paragraphs(summary: object) -> list[str]:
    if not isinstance(summary, str):
        return []
    return [part.strip() for part in re.split(r"\n\s*\n", summary) if part.strip()]


def build_cv_section(basics: dict[str, Any]) -> dict[str, Any]:
    cv: dict[str, Any] = {}

    name = basics.get("name")
    if isinstance(name, str) and name.strip():
        cv["name"] = name.strip()

    label = basics.get("label")
    if isinstance(label, str) and label.strip():
        cv["headline"] = label.strip()

    location = _join_location(basics.get("location", {}))
    if location:
        cv["location"] = location

    paragraphs = _split_paragraphs(basics.get("summary"))
    if paragraphs:
        cv["sections"] = {"Summary": paragraphs}

    return cv


def _list_from_text_or_list(value: object) -> list[str]:
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                result.append(item.strip())
        return result
    return []


def map_experience(work_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    experience: list[dict[str, Any]] = []
    for item in work_items:
        if not isinstance(item, dict):
            continue
        mapped: dict[str, Any] = {}

        name = item.get("name")
        if isinstance(name, str) and name.strip():
            mapped["company"] = name.strip()

        position = item.get("position")
        if isinstance(position, str) and position.strip():
            mapped["position"] = position.strip()

        location = item.get("location")
        if isinstance(location, str) and location.strip():
            mapped["location"] = location.strip()

        date: dict[str, str] = {}
        start_date = normalize_date(item.get("startDate"))
        if start_date:
            date["start_date"] = start_date

        end_date = normalize_date(item.get("endDate"), is_end=True)
        date["end_date"] = end_date if end_date else "present"
        if date:
            mapped["date"] = date

        summary = item.get("summary")
        if isinstance(summary, str) and summary.strip():
            mapped["summary"] = summary.strip()

        highlights = _list_from_text_or_list(item.get("highlights"))
        if highlights:
            mapped["highlights"] = highlights

        experience.append(prune_empty(mapped))

    return experience


def map_education(education_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    education: list[dict[str, Any]] = []
    for item in education_items:
        if not isinstance(item, dict):
            continue
        mapped: dict[str, Any] = {}

        institution = item.get("institution")
        if isinstance(institution, str) and institution.strip():
            mapped["institution"] = institution.strip()

        title = item.get("title")
        if isinstance(title, str) and title.strip():
            mapped["area"] = title.strip()

        study_type = item.get("studyType")
        if isinstance(study_type, str) and study_type.strip():
            mapped["degree"] = study_type.strip()

        date: dict[str, str] = {}
        start_date = normalize_date(item.get("startDate"))
        if start_date:
            date["start_date"] = start_date

        is_in_progress = item.get("status") == "in_progress"
        end_date = normalize_date(
            item.get("endDate"),
            is_end=True,
            in_progress=is_in_progress,
        )
        if end_date:
            date["end_date"] = end_date
        if date:
            mapped["date"] = date

        details = _list_from_text_or_list(item.get("details"))
        notes = item.get("notes")
        if isinstance(notes, str) and notes.strip():
            details.append(notes.strip())
        if details:
            mapped["highlights"] = details

        education.append(prune_empty(mapped))

    return education


def map_skills(
    skills_items: list[dict[str, Any]],
    languages_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    skills: list[dict[str, Any]] = []

    for item in skills_items:
        if not isinstance(item, dict):
            continue
        mapped: dict[str, Any] = {}

        name = item.get("name")
        if isinstance(name, str) and name.strip():
            mapped["label"] = name.strip()

        keywords = _list_from_text_or_list(item.get("keywords"))
        if keywords:
            mapped["details"] = ", ".join(keywords)

        cleaned = prune_empty(mapped)
        if cleaned:
            skills.append(cleaned)

    idioma_parts: list[str] = []
    for language in languages_items:
        if not isinstance(language, dict):
            continue
        name = language.get("language")
        if not isinstance(name, str) or not name.strip():
            continue
        fluency = language.get("fluency")
        if isinstance(fluency, str) and fluency.strip():
            idioma_parts.append(f"{name.strip()} ({fluency.strip()})")
        else:
            idioma_parts.append(name.strip())

    if idioma_parts:
        skills.append({"label": "Idiomas", "details": ", ".join(idioma_parts)})

    return skills


def prune_empty(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, item in value.items():
            pruned = prune_empty(item)
            if pruned in (None, "", [], {}):
                continue
            cleaned[key] = pruned
        return cleaned

    if isinstance(value, list):
        cleaned_list = [prune_empty(item) for item in value]
        return [item for item in cleaned_list if item not in (None, "", [], {})]

    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else None

    return value


def convert_jsonresume_to_rendercv(payload: dict[str, Any]) -> dict[str, Any]:
    basics_raw = payload.get("basics")
    work_raw = payload.get("work")
    education_raw = payload.get("education")
    skills_raw = payload.get("skills")
    languages_raw = payload.get("languages")

    basics: dict[str, Any] = basics_raw if isinstance(basics_raw, dict) else {}
    work: list[dict[str, Any]] = [item for item in work_raw if isinstance(item, dict)] if isinstance(work_raw, list) else []
    education: list[dict[str, Any]] = [
        item for item in education_raw if isinstance(item, dict)
    ] if isinstance(education_raw, list) else []
    skills: list[dict[str, Any]] = [item for item in skills_raw if isinstance(item, dict)] if isinstance(skills_raw, list) else []
    languages: list[dict[str, Any]] = [
        item for item in languages_raw if isinstance(item, dict)
    ] if isinstance(languages_raw, list) else []

    doc: dict[str, Any] = {
        "cv": prune_empty(build_cv_section(basics)),
        "experience": map_experience(work),
        "education": map_education(education),
        "skills": map_skills(skills, languages),
        "design": {"theme": "classic"},
    }

    # Required top-level keys must always exist.
    if not isinstance(doc.get("cv"), dict):
        doc["cv"] = {}
    if not isinstance(doc.get("experience"), list):
        doc["experience"] = []
    if not isinstance(doc.get("education"), list):
        doc["education"] = []
    if not isinstance(doc.get("skills"), list):
        doc["skills"] = []
    if not isinstance(doc.get("design"), dict):
        doc["design"] = {"theme": "classic"}

    return doc


def dump_rendercv_yaml(doc: dict[str, Any]) -> str:
    dumped = yaml.safe_dump(doc, sort_keys=False, allow_unicode=True)
    return f"{SCHEMA_HEADER}\n{dumped}"


def convert_file(input_path: Path, output_path: Path | None) -> str | None:
    payload = load_jsonresume(input_path)
    rendercv_doc = convert_jsonresume_to_rendercv(payload)
    yaml_output = dump_rendercv_yaml(rendercv_doc)

    if output_path is None:
        return yaml_output

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml_output, encoding="utf-8")
    return None
