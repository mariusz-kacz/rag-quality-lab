from typing import cast

from rag_quality_lab.schemas import RetrievalMode


class RetrievalModeError(Exception):
    pass


def supported_retrieval_modes() -> tuple[RetrievalMode, ...]:
    return (
        "baseline-vector",
        "routed-vector",
    )


def validate_retrieval_mode(retrieval_mode: str) -> RetrievalMode:
    if retrieval_mode not in supported_retrieval_modes():
        raise RetrievalModeError(retrieval_mode)

    return cast(RetrievalMode, retrieval_mode)
