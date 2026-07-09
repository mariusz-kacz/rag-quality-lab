import json
import os
from pathlib import Path

import typer
from typer.testing import CliRunner

from rag_quality_lab import __version__
from rag_quality_lab.cli import (
    ExitCode,
    app,
    build_shared_options,
    exit_code_for_error,
    load_env_file,
    run_cli_command,
    stage_for_error,
)
from rag_quality_lab.config import MissingSettingError
from rag_quality_lab.providers import ProviderError
from rag_quality_lab.schemas import ArtifactIOError


runner = CliRunner()


def test_root_help_exposes_base_command_groups() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "corpus" in result.output
    assert "trace" in result.output
    assert "eval" in result.output
    assert "version" in result.output


def test_version_command_prints_package_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert result.output.strip() == __version__


def test_shared_options_records_json_output_preference() -> None:
    options = build_shared_options(json_output=True)

    assert options.json_output is True


def test_env_file_loader_sets_missing_values_without_overriding_process_env(
    monkeypatch,
    tmp_path: Path,
) -> None:
    env_file = tmp_path / ".env.local"
    env_file.write_text(
        "\n".join(
            [
                "# Local live-service settings",
                "RAGLAB_TEST_FROM_FILE=loaded",
                "RAGLAB_TEST_ALREADY_SET=from-file",
                "export RAGLAB_TEST_QUOTED='quoted value'",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("RAGLAB_TEST_FROM_FILE", raising=False)
    monkeypatch.setenv("RAGLAB_TEST_ALREADY_SET", "from-process")
    monkeypatch.delenv("RAGLAB_TEST_QUOTED", raising=False)

    loaded = load_env_file(env_file)

    assert loaded == {
        "RAGLAB_TEST_FROM_FILE": "loaded",
        "RAGLAB_TEST_QUOTED": "quoted value",
    }
    assert os.environ["RAGLAB_TEST_FROM_FILE"] == "loaded"
    assert os.environ["RAGLAB_TEST_ALREADY_SET"] == "from-process"
    assert os.environ["RAGLAB_TEST_QUOTED"] == "quoted value"


def test_env_file_global_option_loads_values_before_command(
    monkeypatch,
    tmp_path: Path,
) -> None:
    env_file = tmp_path / ".env.local"
    env_file.write_text("RAGLAB_TEST_CLI_ENV_FILE=loaded\n", encoding="utf-8")
    monkeypatch.delenv("RAGLAB_TEST_CLI_ENV_FILE", raising=False)

    result = runner.invoke(app, ["--env-file", str(env_file), "version"])

    assert result.exit_code == 0
    assert os.environ["RAGLAB_TEST_CLI_ENV_FILE"] == "loaded"


def test_known_errors_map_to_stable_exit_codes_and_stages() -> None:
    missing = MissingSettingError(["FOUNDRY_OPENAI_BASE_URL"], stage="Foundry")

    assert exit_code_for_error(missing) == ExitCode.CONFIGURATION
    assert stage_for_error(missing) == "Foundry"
    assert exit_code_for_error(ArtifactIOError("bad json")) == ExitCode.ARTIFACT
    assert exit_code_for_error(ProviderError("provider failed")) == ExitCode.PROVIDER


def test_run_cli_command_renders_human_error_to_stderr() -> None:
    test_app = typer.Typer()

    @test_app.command()
    def fail() -> None:
        run_cli_command(
            lambda: (_ for _ in ()).throw(
                MissingSettingError(["FOUNDRY_OPENAI_BASE_URL"], stage="Foundry")
            )
        )

    result = runner.invoke(test_app)

    assert result.exit_code == ExitCode.CONFIGURATION
    assert "Error [Foundry]" in result.stderr
    assert "FOUNDRY_OPENAI_BASE_URL" in result.stderr


def test_run_cli_command_renders_json_error_to_stderr() -> None:
    test_app = typer.Typer()

    @test_app.command()
    def fail() -> None:
        run_cli_command(
            lambda: (_ for _ in ()).throw(ProviderError("provider failed")),
            json_output=True,
        )

    result = runner.invoke(test_app)

    assert result.exit_code == ExitCode.PROVIDER
    payload = json.loads(result.stderr)
    assert payload == {
        "ok": False,
        "stage": "provider",
        "error_type": "ProviderError",
        "message": "provider failed",
    }
