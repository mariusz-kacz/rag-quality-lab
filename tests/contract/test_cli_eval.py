"""Evaluation has one command: run fresh questions and print their scores."""

from typer.testing import CliRunner

from rag_quality_lab.cli import app


def test_eval_exposes_only_run():
    cli = CliRunner()
    help_result = cli.invoke(app, ["eval", "--help"])
    assert help_result.exit_code == 0
    assert "run" in help_result.stdout
    assert "rescore" not in help_result.stdout
    assert "compare" not in help_result.stdout
    assert cli.invoke(app, ["eval", "run", "--help"]).exit_code == 0
    for removed in ("rescore", "compare"):
        result = cli.invoke(app, ["eval", removed])
        assert result.exit_code == 2
        assert "No such command" in result.output
