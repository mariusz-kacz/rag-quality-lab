"""Canonical evaluator configuration and resource-ownership contracts."""

import asyncio
from types import SimpleNamespace

import httpx
import pytest

from rag_quality_lab.config import InvalidConfigurationError, MissingSettingError


def environment(**overrides):
    return {
        "FOUNDRY_OPENAI_BASE_URL": "https://foundry.invalid/openai/v1/responses",
        "FOUNDRY_API_KEY": "generator-secret",
        "FOUNDRY_CHAT_MODEL": "generator",
        "FOUNDRY_EMBEDDING_MODEL": "retriever",
        "RAGLAB_EVAL_MODEL": "judge",
        "RAGLAB_EVAL_EMBEDDING_MODEL": "eval-embedding",
        **overrides,
    }


@pytest.mark.parametrize(
    "missing", ["RAGLAB_EVAL_MODEL", "RAGLAB_EVAL_EMBEDDING_MODEL"]
)
def test_models_are_required_even_when_generator_models_exist(missing):
    from rag_quality_lab.eval.config import load_eval_config

    with pytest.raises(MissingSettingError) as error:
        load_eval_config(environment(**{missing: " "}))
    assert error.value.missing_settings == (missing,)


@pytest.mark.parametrize(
    "overrides, endpoint_source, auth_source, key",
    [
        ({}, "foundry", "foundry_api_key", "generator-secret"),
        (
            {
                "RAGLAB_EVAL_BASE_URL": "https://FOUNDRY.invalid:443/openai/v1/embeddings/"
            },
            "explicit",
            "foundry_api_key",
            "generator-secret",
        ),
        ({"FOUNDRY_API_KEY": ""}, "foundry", "entra", None),
        (
            {
                "RAGLAB_EVAL_BASE_URL": "https://judge.invalid/v1",
                "RAGLAB_EVAL_API_KEY": "eval-secret",
            },
            "explicit",
            "eval_api_key",
            "eval-secret",
        ),
    ],
)
def test_endpoint_authentication_and_safe_effective_settings(
    overrides, endpoint_source, auth_source, key
):
    from rag_quality_lab.eval.config import load_eval_config

    config = load_eval_config(environment(**overrides))
    assert config.endpoint_source == endpoint_source
    assert config.auth_source == auth_source
    assert (config.api_key.get_secret_value() if config.api_key else None) == key
    assert config.model == "judge"
    assert config.embedding_model == "eval-embedding"
    assert config.timeout_seconds == 120
    assert config.max_retries == 1
    serialized = config.model_dump_json()
    assert "api_key" not in config.model_dump()
    assert "generator-secret" not in serialized + repr(config)
    assert "eval-secret" not in serialized + repr(config)


@pytest.mark.parametrize(
    "endpoint",
    ["https://other.invalid/v1", "https://foundry.invalid/another-project/v1"],
)
def test_different_endpoint_requires_explicit_credentials(endpoint):
    from rag_quality_lab.eval.config import load_eval_config

    with pytest.raises(InvalidConfigurationError, match="RAGLAB_EVAL_API_KEY"):
        load_eval_config(environment(RAGLAB_EVAL_BASE_URL=endpoint))


@pytest.mark.parametrize(
    "name, value",
    [
        ("RAGLAB_EVAL_TIMEOUT_SECONDS", "0"),
        ("RAGLAB_EVAL_TIMEOUT_SECONDS", "nan"),
        ("RAGLAB_EVAL_TIMEOUT_SECONDS", "inf"),
        ("RAGLAB_EVAL_MAX_RETRIES", "-1"),
        ("RAGLAB_EVAL_MAX_RETRIES", "1.5"),
        ("RAGLAB_EVAL_BASE_URL", "https://user:secret@foundry.invalid/v1"),
        ("RAGLAB_EVAL_BASE_URL", "https://foundry.invalid/v1?token=secret"),
        ("RAGLAB_EVAL_BASE_URL", "https://foundry.invalid/v1#secret"),
    ],
)
def test_invalid_configuration_does_not_echo_values(name, value):
    from rag_quality_lab.eval.config import load_eval_config

    with pytest.raises(InvalidConfigurationError) as error:
        load_eval_config(environment(**{name: value}))
    assert value not in str(error.value)


def test_explicit_settings_work_without_generation_or_qdrant_configuration(
    monkeypatch, tmp_path
):
    from rag_quality_lab.cli import load_env_file
    from rag_quality_lab.eval.config import load_eval_config

    for name in environment():
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("RAGLAB_EVAL_MODEL", "process-judge")
    path = tmp_path / "eval.env"
    path.write_text(
        "RAGLAB_EVAL_MODEL=file-judge\nRAGLAB_EVAL_EMBEDDING_MODEL=embed\n"
        "RAGLAB_EVAL_BASE_URL=https://judge.invalid/v1\nRAGLAB_EVAL_API_KEY=key\n"
        "RAGLAB_EVAL_TIMEOUT_SECONDS=5.5\nRAGLAB_EVAL_MAX_RETRIES=0\n",
        encoding="utf-8",
    )
    for name in (
        "RAGLAB_EVAL_BASE_URL",
        "RAGLAB_EVAL_API_KEY",
        "RAGLAB_EVAL_TIMEOUT_SECONDS",
        "RAGLAB_EVAL_MAX_RETRIES",
    ):
        monkeypatch.delenv(name, raising=False)
    load_env_file(path)
    config = load_eval_config()
    assert config.model == "process-judge"
    assert config.timeout_seconds == 5.5
    assert config.max_retries == 0


@pytest.mark.parametrize(
    "failure, borrowed",
    [
        (None, False),
        (None, True),
        ("client_setup", False),
        ("adapter_setup", False),
        ("adapter_setup", True),
        ("scoring", False),
        ("scoring", True),
        ("client_close", False),
    ],
)
def test_scope_closes_only_owned_resources_on_all_exit_paths(
    monkeypatch, failure, borrowed
):
    from azure.identity import aio
    from rag_quality_lab.eval import providers
    from rag_quality_lab.eval.config import load_eval_config

    closed = []

    class Credential:
        async def close(self):
            closed.append("credential")

    class Client:
        base_url = "https://foundry.invalid/openai/v1"
        max_retries = 1
        timeout = httpx.Timeout(120)

        async def close(self):
            closed.append("client")
            if failure == "client_close":
                raise RuntimeError("secret-in-cleanup")

    credential, client = Credential(), Client()
    monkeypatch.setattr(aio, "DefaultAzureCredential", lambda: credential)

    def create_client(**kwargs):
        if failure == "client_setup":
            raise ValueError("secret-in-setup")
        return client

    def adapters(config, client):
        if failure == "adapter_setup":
            raise ValueError("secret-in-setup")
        return SimpleNamespace(), SimpleNamespace()

    monkeypatch.setattr(providers, "AsyncOpenAI", create_client)
    monkeypatch.setattr(providers, "_build_adapters", adapters)
    config = load_eval_config(environment(FOUNDRY_API_KEY=""))

    async def run():
        async with providers.evaluator_scope(
            config,
            client=client if borrowed else None,
            credential=credential if borrowed else None,
        ):
            if failure == "scoring":
                raise RuntimeError("caller-failure")

    if failure == "scoring":
        with pytest.raises(RuntimeError, match="caller-failure"):
            asyncio.run(run())
    elif failure in ("adapter_setup", "client_setup", "client_close"):
        with pytest.raises(providers.EvalProviderError) as error:
            asyncio.run(run())
        assert "secret-in-setup" not in str(error.value)
        assert "secret-in-cleanup" not in str(error.value)
    else:
        asyncio.run(run())
    expected = (
        []
        if borrowed
        else ["credential"]
        if failure == "client_setup"
        else ["client", "credential"]
    )
    assert sorted(closed) == sorted(expected)
