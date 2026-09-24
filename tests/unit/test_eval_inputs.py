"""Validation of original golden questions and subset selection."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

pytestmark = pytest.mark.unit


def test_full_benchmark_validation_precedes_selection():
    from rag_quality_lab.schemas.eval import GoldenDataset

    data = json.loads(Path("golden/questions.json").read_text())
    dataset = GoldenDataset.model_validate(data)
    # A benchmark may be a single targeted case or grow beyond the original 16.
    assert len(GoldenDataset(questions=dataset.questions[:1]).questions) == 1
    larger = [
        dataset.questions[0].model_copy(update={"question_id": f"q-{i}"})
        for i in range(21)
    ]
    assert len(GoldenDataset(questions=larger).questions) == 21
    ids = [q.question_id for q in dataset.questions]
    assert [q.question_id for q in dataset.select([ids[2], ids[0]])] == ids[:1] + ids[
        2:3
    ]
    for selection in (["unknown"], [ids[0], ids[0]]):
        with pytest.raises(ValueError):
            dataset.select(selection)
    for corruption in (
        "duplicate",
        "missing_labels",
        "missing_id",
        "missing_notes",
        "blank_notes",
        "empty",
    ):
        invalid = json.loads(json.dumps(data))
        if corruption == "duplicate":
            invalid["questions"][-1] = invalid["questions"][0]
        elif corruption == "missing_labels":
            invalid["questions"][-1]["expected_relevant_sources"] = []
        elif corruption == "missing_notes":
            invalid["questions"][-1].pop("grading_notes")
        elif corruption == "blank_notes":
            invalid["questions"][-1]["grading_notes"] = " "
        elif corruption == "missing_id":
            invalid["questions"][-1].pop("question_id")
        else:
            invalid["questions"] = []
        with pytest.raises(ValidationError):
            GoldenDataset.model_validate(invalid)
