from pathlib import Path

import pytest

from rag_quality_lab.config import (
    MissingSettingError,
    load_app_config,
    load_foundry_openai_config,
    load_runtime_config,
)


def valid_environment() -> dict[str, str]:
    return {
        "FOUNDRY_OPENAI_BASE_URL": (
            "https://example.services.ai.azure.com/api/projects/proj/openai/v1"
        ),
        "FOUNDRY_API_KEY": "test-key",
        "FOUNDRY_EMBEDDING_MODEL": "text-embedding-3-small",
        "FOUNDRY_CHAT_MODEL": "gpt-4o-mini",
        "FOUNDRY_REASONING_EFFORT": "None",
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_API_KEY": "",
        "RAGLAB_QDRANT_COLLECTION": "rag_quality_lab",
    }


def test_load_app_config_reads_required_environment() -> None:
    config = load_app_config(valid_environment())

    assert config.foundry_openai.base_url == (
        "https://example.services.ai.azure.com/api/projects/proj/openai/v1"
    )
    assert config.foundry_openai.api_key is not None
    assert config.foundry_openai.api_key.get_secret_value() == "test-key"
    assert config.foundry_openai.embedding_model == "text-embedding-3-small"
    assert config.foundry_openai.chat_model == "gpt-4o-mini"
    assert config.foundry_openai.reasoning_effort == "none"
    assert config.qdrant.url == "http://localhost:6333"
    assert config.qdrant.api_key is None
    assert config.qdrant.collection == "rag_quality_lab"
    assert config.runtime.top_k == 6


def test_load_app_config_normalizes_foundry_responses_url() -> None:
    env = valid_environment()
    env["FOUNDRY_OPENAI_BASE_URL"] = (
        "https://example.services.ai.azure.com/api/projects/proj/openai/v1/responses"
    )

    config = load_app_config(env)

    assert config.foundry_openai.base_url == (
        "https://example.services.ai.azure.com/api/projects/proj/openai/v1"
    )


def test_missing_required_settings_names_all_missing_values() -> None:
    env = valid_environment()
    env["FOUNDRY_OPENAI_BASE_URL"] = " "
    del env["FOUNDRY_CHAT_MODEL"]

    with pytest.raises(MissingSettingError) as exc_info:
        load_app_config(env)

    assert exc_info.value.missing_settings == (
        "FOUNDRY_OPENAI_BASE_URL",
        "FOUNDRY_CHAT_MODEL",
    )
    assert "Foundry" in str(exc_info.value)


def test_foundry_embedding_only_config_does_not_require_chat_model() -> None:
    config = load_foundry_openai_config(
        {
            "FOUNDRY_OPENAI_BASE_URL": (
                "https://example.services.ai.azure.com/api/projects/proj/openai/v1"
            ),
            "FOUNDRY_EMBEDDING_MODEL": "text-embedding-3-small",
        },
        require_chat=False,
    )

    assert config.embedding_model == "text-embedding-3-small"
    assert config.chat_model is None


def test_runtime_config_uses_environment_and_explicit_overrides() -> None:
    runtime = load_runtime_config(
        {
            "RAGLAB_TOP_K": "8",
            "RAGLAB_MAX_CONTEXT_TOKENS": "3000",
            "RAGLAB_OUTPUT_TOKEN_LIMIT": "700",
            "RAGLAB_ROUTER_CONFIDENCE_THRESHOLD": "0.42",
            "RAGLAB_ROUTER_CATEGORY_MARGIN": "0.12",
            "RAGLAB_TRACE_DIR": "custom/traces",
            "RAGLAB_EVAL_ARTIFACTS_DIR": "custom/eval",
            "RAGLAB_SCHEMA_VERSION": "1.1",
        },
        top_k=4,
    )

    assert runtime.top_k == 4
    assert runtime.max_context_tokens == 3000
    assert runtime.output_token_limit == 700
    assert runtime.router_confidence_threshold == 0.42
    assert runtime.router_category_margin == 0.12
    assert runtime.trace_dir == Path("custom/traces")
    assert runtime.eval_artifacts_dir == Path("custom/eval")
    assert runtime.schema_version == "1.1"
