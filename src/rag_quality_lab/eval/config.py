"""Resolved evaluator settings, independent of generation and Qdrant setup."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Literal
from urllib.parse import urlsplit, urlunsplit

from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError

from rag_quality_lab.config import InvalidConfigurationError, MissingSettingError


def normalize_endpoint(value: str) -> str:
    """Compare service endpoints without forwarding URL-embedded credentials."""
    try:
        parts = urlsplit(value.strip())
        if (
            parts.scheme not in ("http", "https")
            or not parts.hostname
            or parts.username is not None
            or parts.password is not None
            or parts.query
            or parts.fragment
        ):
            raise ValueError
        port = parts.port
        host = parts.hostname.lower()
        if ":" in host:
            host = f"[{host}]"
        if port is not None and (parts.scheme, port) not in (
            ("http", 80),
            ("https", 443),
        ):
            host += f":{port}"
        path = parts.path.rstrip("/")
        for suffix in ("/responses", "/chat/completions", "/embeddings"):
            if path.endswith(suffix):
                path = path.removesuffix(suffix)
                break
        return urlunsplit((parts.scheme, host, path, "", ""))
    except ValueError:
        raise InvalidConfigurationError(
            "Evaluator endpoint must be an HTTP(S) URL without credentials, query, or fragment"
        ) from None


class EvalConfig(BaseModel):
    """Use load_eval_config to resolve once; model_dump is safe for provenance."""

    model_config = ConfigDict(frozen=True)

    model: str = Field(min_length=1)
    embedding_model: str = Field(min_length=1)
    base_url: str
    endpoint_source: Literal["explicit", "foundry"]
    auth_source: Literal["eval_api_key", "foundry_api_key", "entra"]
    api_key: SecretStr | None = Field(default=None, exclude=True, repr=False)
    timeout_seconds: float = Field(default=120, gt=0, allow_inf_nan=False)
    max_retries: int = Field(default=1, ge=0)
    transport_retry_owner: Literal["openai"] = "openai"
    structured_output_retries: Literal[0] = 0


def load_eval_config(environ: Mapping[str, str] | None = None) -> EvalConfig:
    """Respect the CLI's already-loaded environment; never load generator models."""
    env = os.environ if environ is None else environ

    def read(name: str) -> str | None:
        return env.get(name, "").strip() or None

    missing = [
        name
        for name in ("RAGLAB_EVAL_MODEL", "RAGLAB_EVAL_EMBEDDING_MODEL")
        if not read(name)
    ]
    endpoint = read("RAGLAB_EVAL_BASE_URL") or read("FOUNDRY_OPENAI_BASE_URL")
    if not endpoint:
        missing.append("RAGLAB_EVAL_BASE_URL")
    if missing:
        raise MissingSettingError(missing, stage="evaluation")
    base_url = normalize_endpoint(endpoint)
    key = read("RAGLAB_EVAL_API_KEY")
    auth_source = "eval_api_key"
    if key is None:
        foundry_url = read("FOUNDRY_OPENAI_BASE_URL")
        if not foundry_url or base_url != normalize_endpoint(foundry_url):
            raise InvalidConfigurationError(
                "A different evaluator endpoint requires RAGLAB_EVAL_API_KEY"
            )
        key = read("FOUNDRY_API_KEY")
        auth_source = "foundry_api_key" if key else "entra"
    try:
        return EvalConfig(
            model=read("RAGLAB_EVAL_MODEL"),
            embedding_model=read("RAGLAB_EVAL_EMBEDDING_MODEL"),
            base_url=base_url,
            endpoint_source="explicit" if read("RAGLAB_EVAL_BASE_URL") else "foundry",
            auth_source=auth_source,
            api_key=SecretStr(key) if key else None,
            timeout_seconds=read("RAGLAB_EVAL_TIMEOUT_SECONDS") or 120,
            max_retries=read("RAGLAB_EVAL_MAX_RETRIES") or 1,
        )
    except ValidationError as exc:
        fields = sorted({str(error["loc"][0]) for error in exc.errors()})
        raise InvalidConfigurationError(
            f"Invalid evaluation configuration: {', '.join(fields)}"
        ) from None
