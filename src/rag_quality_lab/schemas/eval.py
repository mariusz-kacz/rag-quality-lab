"""Validation of golden questions and subset selection."""

from typing import Self

from pydantic import Field, model_validator

from rag_quality_lab.schemas.base import SchemaModel
from rag_quality_lab.schemas.query import Question


class GoldenDataset(SchemaModel):
    """Named questions and expected labels, with no fixed size or case mix."""

    questions: list[Question] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_dataset(self) -> Self:
        ids = [q.question_id for q in self.questions]
        if any(not qid for qid in ids) or len(set(ids)) != len(ids):
            raise ValueError("golden questions require unique nonempty IDs")
        for question in self.questions:
            if not question.grading_notes or not question.grading_notes.strip():
                raise ValueError("golden questions require grading notes")
            labels = question.expected_relevant_sources
            if any(not label.strip() for label in labels) or len(set(labels)) != len(
                labels
            ):
                raise ValueError("relevance labels must be nonempty and unique")
            if question.answerability == "answerable" and not labels:
                raise ValueError("answerable questions require relevance labels")
            if question.answerability == "no_answer" and labels:
                raise ValueError("no-answer questions cannot have relevance labels")
        return self

    def select(self, question_ids: list[str] | None = None) -> list[Question]:
        if question_ids is None:
            return list(self.questions)
        requested = set(question_ids)
        if not requested or len(requested) != len(question_ids):
            raise ValueError("selection must contain unique nonempty question IDs")
        if requested - {q.question_id for q in self.questions}:
            raise ValueError("selection contains unknown question IDs")
        return [q for q in self.questions if q.question_id in requested]
