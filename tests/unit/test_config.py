from pathlib import Path

import pytest

from rag_quality_lab.config import (
    MissingSettingError,
    load_app_config,
    load_azure_openai_config,
    load_runtime_config,
)


def valid_environment() -> dict[str, str]:
    return {
        "AZURE_OPENAI_ENDPOINT": "https://example.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "text-embedding-3-small",
        "AZURE_OPENAI_CHAT_DEPLOYMENT": "gpt-4o-mini",
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_API_KEY": "",
        "RAGLAB_QDRANT_COLLECTION": "rag_quality_lab",
    }


def test_load_app_config_reads_required_environment() -> None:
    config = load_app_config(valid_environment())

    assert config.azure_openai.endpoint == "https://example.openai.azure.com"
    assert config.azure_openai.api_key.get_secret_value() == "test-key"
    assert config.azure_openai.embedding_deployment == "text-embedding-3-small"
    assert config.azure_openai.chat_deployment == "gpt-4o-mini"
    assert config.qdrant.url == "http://localhost:6333"
    assert config.qdrant.api_key is None
    assert config.qdrant.collection == "rag_quality_lab"
    assert config.runtime.top_k == 6


def test_missing_required_settings_names_all_missing_values() -> None:
    env = valid_environment()
    env["AZURE_OPENAI_API_KEY"] = " "
    del env["AZURE_OPENAI_CHAT_DEPLOYMENT"]

    with pytest.raises(MissingSettingError) as exc_info:
        load_app_config(env)

    assert exc_info.value.missing_settings == (
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_CHAT_DEPLOYMENT",
    )
    assert "Azure OpenAI" in str(exc_info.value)


def test_embedding_only_config_does_not_require_chat_deployment() -> None:
    env = valid_environment()
    del env["AZURE_OPENAI_CHAT_DEPLOYMENT"]

    config = load_azure_openai_config(env, require_chat=False)

    assert config.embedding_deployment == "text-embedding-3-small"
    assert config.chat_deployment is None


def test_runtime_config_uses_environment_and_explicit_overrides() -> None:
    runtime = load_runtime_config(
        {
            "RAGLAB_TOP_K": "8",
            "RAGLAB_MAX_CONTEXT_TOKENS": "3000",
            "RAGLAB_OUTPUT_TOKEN_LIMIT": "700",
            "RAGLAB_ROUTER_CONFIDENCE_THRESHOLD": "0.42",
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
    assert runtime.trace_dir == Path("custom/traces")
    assert runtime.eval_artifacts_dir == Path("custom/eval")
    assert runtime.schema_version == "1.1"
