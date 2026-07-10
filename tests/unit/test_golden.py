from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from rag_quality_lab.schemas import REQUIRED_KNOWLEDGE_CATEGORIES, GoldenSet, Question


pytestmark = pytest.mark.unit


def test_load_golden_set_reads_valid_question_file(tmp_path: Path) -> None:
    from rag_quality_lab.eval.golden import load_golden_set

    golden_path = tmp_path / "questions.json"
    golden_path.write_text(
        json.dumps({"questions": valid_question_payloads()}),
        encoding="utf-8",
    )

    golden_set = load_golden_set(golden_path)

    assert isinstance(golden_set, GoldenSet)
    assert len(golden_set.questions) == 12
    assert golden_set.questions[0].question_id == "q-answerable-001"
    assert golden_set.questions[0].expected_relevant_sources == ["rag-overview"]


def test_golden_set_requires_all_case_types() -> None:
    questions = [
        question(f"q-answerable-{index:03d}", case_type="answerable")
        for index in range(1, 13)
    ]

    with pytest.raises(ValidationError, match="missing required case types"):
        GoldenSet(questions=questions)


def test_golden_set_requires_valid_answerability_label() -> None:
    payloads = valid_question_payloads()
    payloads[0]["answerability"] = "partial"

    with pytest.raises(ValidationError, match="answerability"):
        GoldenSet.model_validate({"questions": payloads})


def test_golden_set_rejects_no_answer_with_answerable_case_type() -> None:
    payloads = valid_question_payloads()
    payloads[0]["answerability"] = "no_answer"
    payloads[0]["case_type"] = "answerable"

    with pytest.raises(ValidationError, match="no_answer questions"):
        GoldenSet.model_validate({"questions": payloads})


def test_golden_set_requires_expected_sources_for_answerable_cases() -> None:
    payloads = valid_question_payloads()
    payloads[0]["expected_relevant_sources"] = []

    with pytest.raises(ValidationError, match="expected_relevant_sources"):
        GoldenSet.model_validate({"questions": payloads})


def test_golden_set_accepts_no_answer_without_expected_sources() -> None:
    payloads = valid_question_payloads()
    no_answer_payload = next(
        item for item in payloads if item["case_type"] == "no_answer"
    )
    no_answer_payload["expected_relevant_sources"] = []

    golden_set = GoldenSet.model_validate({"questions": payloads})

    no_answer_question = next(
        question
        for question in golden_set.questions
        if question.case_type == "no_answer"
    )
    assert no_answer_question.answerability == "no_answer"
    assert no_answer_question.expected_relevant_sources == []


def test_golden_set_requires_question_id() -> None:
    payloads = valid_question_payloads()
    payloads[0].pop("question_id")

    with pytest.raises(ValidationError, match="golden questions require question_id"):
        GoldenSet.model_validate({"questions": payloads})


def test_golden_set_rejects_duplicate_question_id() -> None:
    payloads = valid_question_payloads()
    payloads[1]["question_id"] = payloads[0]["question_id"]

    with pytest.raises(ValidationError, match="question_id values must be unique"):
        GoldenSet.model_validate({"questions": payloads})


def test_checked_in_routing_cases_distinguish_multi_category_and_fallback() -> None:
    from rag_quality_lab.eval.golden import load_golden_set

    golden_set = load_golden_set(Path("golden/questions.json"))
    multi_category = [
        question
        for question in golden_set.questions
        if question.case_type == "multi_category_routing"
    ]
    fallback = [
        question
        for question in golden_set.questions
        if question.case_type == "fallback_routing"
    ]

    assert len(multi_category) == 2
    assert all(
        question.expected_fallback_all_categories is False
        and len(question.expected_searched_categories) > 1
        for question in multi_category
    )
    assert len(fallback) == 2
    assert all(
        question.expected_fallback_all_categories is True
        and set(question.expected_searched_categories)
        == set(REQUIRED_KNOWLEDGE_CATEGORIES)
        for question in fallback
    )


def valid_question_payloads() -> list[dict[str, object]]:
    questions = [
        question_payload(
            "q-answerable-001",
            case_type="answerable",
            answerability="answerable",
            expected_category="RAG and context handling",
            expected_relevant_sources=["rag-overview"],
        ),
        question_payload(
            "q-no-answer-001",
            case_type="no_answer",
            answerability="no_answer",
            expected_category="RAG evaluation and quality",
            expected_relevant_sources=[],
        ),
        question_payload(
            "q-ambiguous-001",
            case_type="ambiguous_boundary",
            answerability="answerable",
            expected_category="RAG evaluation and quality",
            expected_relevant_sources=["wikipedia-ir-evaluation-measures"],
        ),
        question_payload(
            "q-multi-category-001",
            case_type="multi_category_routing",
            answerability="answerable",
            expected_category=None,
            expected_relevant_sources=["rag-overview"],
        ),
        question_payload(
            "q-fallback-001",
            case_type="fallback_routing",
            answerability="answerable",
            expected_category=None,
            expected_relevant_sources=["openai-token-counting"],
        ),
    ]
    questions.extend(
        question_payload(
            f"q-answerable-{index:03d}",
            case_type="answerable",
            answerability="answerable",
            expected_category="RAG and context handling",
            expected_relevant_sources=["rag-overview"],
        )
        for index in range(2, 9)
    )
    return questions


def question(
    question_id: str,
    *,
    case_type: str,
    answerability: str = "answerable",
) -> Question:
    return Question.model_validate(
        question_payload(
            question_id,
            case_type=case_type,
            answerability=answerability,
            expected_category="RAG and context handling",
            expected_relevant_sources=["rag-overview"],
        )
    )


def question_payload(
    question_id: str,
    *,
    case_type: str,
    answerability: str,
    expected_category: str | None,
    expected_relevant_sources: list[str],
) -> dict[str, object]:
    payload: dict[str, object] = {
        "question_id": question_id,
        "text": f"Golden question {question_id}?",
        "expected_category": expected_category,
        "expected_relevant_sources": expected_relevant_sources,
        "answerability": answerability,
        "case_type": case_type,
    }
    if case_type == "multi_category_routing":
        payload["expected_fallback_all_categories"] = False
        payload["expected_searched_categories"] = [
            "RAG and context handling",
            "RAG evaluation and quality",
        ]
    elif case_type == "fallback_routing":
        payload["expected_fallback_all_categories"] = True
        payload["expected_searched_categories"] = [
            "prompting techniques",
            "RAG and context handling",
            "RAG evaluation and quality",
            "LLM security and risks",
            "LLM settings, cost, and tokens",
        ]
    return payload
