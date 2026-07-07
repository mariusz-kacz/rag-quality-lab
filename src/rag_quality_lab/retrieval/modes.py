from typing import Tuple


class RetrievalModeError(Exception):
    pass


def supported_retrieval_modes() -> Tuple[str, ...]:
    return (
        "baseline-vector",
        "routed-vector",
        "routed-hybrid",
    )


def validate_retrieval_mode(retrieval_mode: str) -> str:
    if retrieval_mode not in supported_retrieval_modes():
        raise RetrievalModeError(retrieval_mode)

    return retrieval_mode
