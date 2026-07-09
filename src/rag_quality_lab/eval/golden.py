"""Golden question-set loading and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from rag_quality_lab.schemas import GoldenSet


DEFAULT_GOLDEN_PATH = Path("golden") / "questions.json"


class GoldenSetValidationError(Exception):
    """Raised when the golden question set cannot be loaded or validated."""


def load_golden_set(path: str | Path = DEFAULT_GOLDEN_PATH) -> GoldenSet:
    """Load a golden question set from JSON and validate it against the schema."""

    golden_path = Path(path)
    payload = _read_json_object(golden_path)
    try:
        return GoldenSet.model_validate(payload)
    except ValidationError as exc:
        raise GoldenSetValidationError(
            f"Invalid golden question set at {golden_path}: {_format_validation_error(exc)}"
        ) from exc


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GoldenSetValidationError(f"Missing golden question file at {path}") from exc
    except json.JSONDecodeError as exc:
        raise GoldenSetValidationError(
            f"Invalid JSON in golden question file at {path}: {exc.msg}"
        ) from exc
    except OSError as exc:
        raise GoldenSetValidationError(
            f"Unable to read golden question file at {path}: {exc}"
        ) from exc

    if not isinstance(payload, dict):
        raise GoldenSetValidationError(
            f"Golden question file at {path} must contain a JSON object"
        )
    return payload


def _format_validation_error(exc: ValidationError) -> str:
    first_error = exc.errors()[0]
    location = ".".join(str(part) for part in first_error.get("loc", ())) or "<root>"
    message = first_error.get("msg", "validation failed")
    return f"{location}: {message}"
