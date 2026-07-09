"""Environment and runtime configuration for RAG Quality Lab."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    ValidationError,
    field_validator,
)


FOUNDRY_BASE_URL_ENV_VAR = "FOUNDRY_OPENAI_BASE_URL"
FOUNDRY_API_KEY_ENV_VAR = "FOUNDRY_API_KEY"
FOUNDRY_EMBEDDING_MODEL_ENV_VAR = "FOUNDRY_EMBEDDING_MODEL"
FOUNDRY_CHAT_MODEL_ENV_VAR = "FOUNDRY_CHAT_MODEL"
FOUNDRY_REASONING_EFFORT_ENV_VAR = "FOUNDRY_REASONING_EFFORT"
QDRANT_REQUIRED_ENV_VARS = (
    "QDRANT_URL",
    "RAGLAB_QDRANT_COLLECTION",
)


class ConfigurationError(Exception):
    """Base exception for configuration failures that should surface cleanly in the CLI."""


class MissingSettingError(ConfigurationError):
    """Raised when one or more required environment variables are missing."""

    def __init__(
        self, missing_settings: list[str], *, stage: str = "application"
    ) -> None:
        self.missing_settings = tuple(missing_settings)
        self.stage = stage
        joined = ", ".join(self.missing_settings)
        super().__init__(
            f"Missing required configuration for {stage}: {joined}. "
            "Set the missing environment variable(s) before running this command."
        )


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration values are present but fail validation."""


class FoundryOpenAIConfig(BaseModel):
    """OpenAI-compatible Azure AI Foundry project endpoint settings."""

    model_config = ConfigDict(frozen=True)

    base_url: str = Field(min_length=1)
    api_key: SecretStr | None = None
    embedding_model: str | None = None
    chat_model: str | None = None
    reasoning_effort: str | None = None

    @field_validator("base_url")
    @classmethod
    def normalize_base_url(cls, value: str) -> str:
        clean = value.strip().rstrip("/")
        if not clean.startswith(("https://", "http://")):
            raise ValueError(
                "FOUNDRY_OPENAI_BASE_URL must start with http:// or https://"
            )
        for suffix in ("/responses", "/chat/completions", "/embeddings"):
            if clean.endswith(suffix):
                clean = clean[: -len(suffix)]
        return clean

    @field_validator("embedding_model", "chat_model", "reasoning_effort")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("reasoning_effort")
    @classmethod
    def normalize_reasoning_effort(cls, value: str | None) -> str | None:
        return value.lower() if value is not None else None

    def require_embedding(self) -> None:
        """Validate that embedding configuration is available."""

        if not self.embedding_model:
            raise MissingSettingError(
                [FOUNDRY_EMBEDDING_MODEL_ENV_VAR], stage="Foundry embeddings"
            )

    def require_chat(self) -> None:
        """Validate that chat configuration is available."""

        if not self.chat_model:
            raise MissingSettingError(
                [FOUNDRY_CHAT_MODEL_ENV_VAR], stage="Foundry chat"
            )


class QdrantConfig(BaseModel):
    """Qdrant vector store connection settings."""

    model_config = ConfigDict(frozen=True)

    url: str = Field(min_length=1)
    api_key: SecretStr | None = None
    collection: str = Field(min_length=1)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        stripped = value.strip().rstrip("/")
        if not stripped.startswith(("https://", "http://")):
            raise ValueError("QDRANT_URL must start with http:// or https://")
        return stripped

    @field_validator("collection")
    @classmethod
    def strip_collection(cls, value: str) -> str:
        return value.strip()


class RuntimeConfig(BaseModel):
    """Local runtime defaults used by CLI commands unless options override them."""

    model_config = ConfigDict(frozen=True)

    top_k: int = Field(default=6, ge=1)
    max_context_tokens: int = Field(default=2500, ge=1)
    output_token_limit: int = Field(default=500, ge=1)
    router_confidence_threshold: float = Field(default=0.18, ge=0.0, le=1.0)
    router_category_margin: float = Field(default=0.15, ge=0.0, le=1.0)
    trace_dir: Path = Path("artifacts/traces")
    eval_artifacts_dir: Path = Path("artifacts/eval")
    schema_version: str = Field(default="1.0", min_length=1)


class AppConfig(BaseModel):
    """Complete application configuration for commands that need all integrations."""

    model_config = ConfigDict(frozen=True)

    foundry_openai: FoundryOpenAIConfig
    qdrant: QdrantConfig
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)


def load_app_config(environ: Mapping[str, str] | None = None) -> AppConfig:
    """Load complete application configuration from environment variables."""

    foundry_openai = load_foundry_openai_config(environ)
    qdrant = load_qdrant_config(environ)
    runtime = load_runtime_config(environ)
    return AppConfig(
        foundry_openai=foundry_openai,
        qdrant=qdrant,
        runtime=runtime,
    )


def load_foundry_openai_config(
    environ: Mapping[str, str] | None = None,
    *,
    require_embedding: bool = True,
    require_chat: bool = True,
) -> FoundryOpenAIConfig:
    """Load Foundry project OpenAI-compatible endpoint configuration."""

    env = _environment(environ)
    required = [FOUNDRY_BASE_URL_ENV_VAR]
    if require_embedding:
        required.append(FOUNDRY_EMBEDDING_MODEL_ENV_VAR)
    if require_chat:
        required.append(FOUNDRY_CHAT_MODEL_ENV_VAR)
    _raise_for_missing(env, required, stage="Foundry")

    api_key = _read(env, FOUNDRY_API_KEY_ENV_VAR)
    config = _build_model(
        FoundryOpenAIConfig,
        {
            "base_url": _read(env, FOUNDRY_BASE_URL_ENV_VAR),
            "api_key": SecretStr(api_key) if api_key else None,
            "embedding_model": _read(env, FOUNDRY_EMBEDDING_MODEL_ENV_VAR),
            "chat_model": _read(env, FOUNDRY_CHAT_MODEL_ENV_VAR),
            "reasoning_effort": _read(env, FOUNDRY_REASONING_EFFORT_ENV_VAR),
        },
        stage="Foundry",
    )
    if require_embedding:
        config.require_embedding()
    if require_chat:
        config.require_chat()
    return config


def load_qdrant_config(environ: Mapping[str, str] | None = None) -> QdrantConfig:
    """Load Qdrant configuration from environment variables."""

    env = _environment(environ)
    _raise_for_missing(env, list(QDRANT_REQUIRED_ENV_VARS), stage="Qdrant")
    api_key = _read(env, "QDRANT_API_KEY")
    return _build_model(
        QdrantConfig,
        {
            "url": _read(env, "QDRANT_URL"),
            "api_key": SecretStr(api_key) if api_key else None,
            "collection": _read(env, "RAGLAB_QDRANT_COLLECTION"),
        },
        stage="Qdrant",
    )


def load_runtime_config(
    environ: Mapping[str, str] | None = None,
    **overrides: Any,
) -> RuntimeConfig:
    """Load runtime defaults from environment variables and explicit overrides."""

    env = _environment(environ)
    values: dict[str, Any] = {
        "top_k": _read(env, "RAGLAB_TOP_K"),
        "max_context_tokens": _read(env, "RAGLAB_MAX_CONTEXT_TOKENS"),
        "output_token_limit": _read(env, "RAGLAB_OUTPUT_TOKEN_LIMIT"),
        "router_confidence_threshold": _read(env, "RAGLAB_ROUTER_CONFIDENCE_THRESHOLD"),
        "router_category_margin": _read(env, "RAGLAB_ROUTER_CATEGORY_MARGIN"),
        "trace_dir": _read(env, "RAGLAB_TRACE_DIR"),
        "eval_artifacts_dir": _read(env, "RAGLAB_EVAL_ARTIFACTS_DIR"),
        "schema_version": _read(env, "RAGLAB_SCHEMA_VERSION"),
    }
    values = {key: value for key, value in values.items() if value is not None}
    values.update({key: value for key, value in overrides.items() if value is not None})
    return _build_model(RuntimeConfig, values, stage="runtime")


def _environment(environ: Mapping[str, str] | None) -> Mapping[str, str]:
    return os.environ if environ is None else environ


def _read(environ: Mapping[str, str], name: str) -> str | None:
    value = environ.get(name)
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _raise_for_missing(
    environ: Mapping[str, str], names: list[str], *, stage: str
) -> None:
    missing = [name for name in names if _read(environ, name) is None]
    if missing:
        raise MissingSettingError(missing, stage=stage)


def _build_model[T: BaseModel](
    model_type: type[T], values: dict[str, Any], *, stage: str
) -> T:
    try:
        return model_type.model_validate(values)
    except ValidationError as exc:
        raise InvalidConfigurationError(
            f"Invalid configuration for {stage}: {exc.errors(include_url=False)}"
        ) from exc
