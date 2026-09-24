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


def test_eval_reranking_options_use_same_runtime_configuration(monkeypatch):
    from rag_quality_lab.eval import runner

    captured = {}

    def run(**kwargs):
        captured.update(kwargs)
        return {
            "dataset_path": "answers.jsonl",
            "results_path": "scores.jsonl",
            "metrics": {},
            "diagnostics": {},
        }

    monkeypatch.setattr(runner, "run_evaluation", run)
    result = CliRunner().invoke(
        app,
        [
            "eval",
            "run",
            "--rerank",
            "--candidate-k",
            "20",
            "--top-k",
            "3",
            "--max-context-tokens",
            "1000",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    runtime = captured["runtime"]
    assert runtime.rerank_enabled is True
    assert (runtime.candidate_k, runtime.top_k, runtime.max_context_tokens) == (
        20,
        3,
        1000,
    )
