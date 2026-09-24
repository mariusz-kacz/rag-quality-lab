"""Real Ragas persistence and metric calls over offline lab/query providers."""

import json
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from openai import AsyncOpenAI
from typer.testing import CliRunner

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("ragas") is None, reason="requires eval extra"
)


@pytest.fixture
def judge_env(monkeypatch):
    from rag_quality_lab.eval import providers

    monkeypatch.setenv("RAGAS_DO_NOT_TRACK", "true")
    for key, value in {
        "RAGLAB_EVAL_MODEL": "judge",
        "RAGLAB_EVAL_BASE_URL": "https://judge.invalid/openai/v1",
        "RAGLAB_EVAL_API_KEY": "secret-key",
        "RAGLAB_EVAL_MAX_RETRIES": "0",
    }.items():
        monkeypatch.setenv(key, value)
    state = SimpleNamespace(requests=[], fail=False, clients=[], verdict="pass")

    def respond(request):
        body = json.loads(request.content)
        state.requests.append(body)
        if state.fail:
            return httpx.Response(401, json={"error": {"message": "secret-key"}})
        assert request.url.path.endswith("/chat/completions")
        prompt = json.dumps(body["messages"])
        if "StatementGeneratorOutput" in prompt:
            content = {"statements": ["Evidence from the index."]}
        elif "NLIStatementOutput" in prompt:
            content = {
                "statements": [
                    {
                        "statement": "Evidence from the index.",
                        "reason": "Supported",
                        "verdict": 1,
                    }
                ]
            }
        else:
            assert "DiscreteResponseModel" in prompt
            content = {"value": state.verdict, "reason": "Offline fixture verdict."}
        return httpx.Response(
            200,
            json={
                "id": "offline",
                "object": "chat.completion",
                "created": 0,
                "model": "judge",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": json.dumps(content),
                        },
                    }
                ],
                "usage": {
                    "prompt_tokens": 1,
                    "completion_tokens": 1,
                    "total_tokens": 2,
                },
            },
        )

    def client(**kwargs):
        result = AsyncOpenAI(
            **kwargs,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)),
        )
        state.clients.append(result)
        return result

    monkeypatch.setattr(providers, "AsyncOpenAI", client)
    return state


def read_rows(path):
    return [
        json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()
    ]


def test_run_both_modes_with_real_ragas(tmp_path, capture_env, judge_env):
    from rag_quality_lab.eval.runner import run_evaluation

    ids = [q["question_id"] for q in capture_env.data["questions"][:2]]
    for mode in ("baseline-vector", "routed-vector"):
        result = run_evaluation(
            mode=mode,
            config=capture_env.config,
            question_ids=ids,
            artifacts_dir=tmp_path,
        )
        rows = read_rows(result["results_path"])
        assert {r["question_id"] for r in rows} == set(ids)
        assert all(r["response"] and r["contexts"] and r["mode"] == mode for r in rows)
        assert result["metrics"]["faithfulness"] == {
            "mean": 1.0,
            "scored_count": 2,
            "eligible_count": 2,
        }
        assert result["metrics"]["answer_success"]["mean"] == 1
        assert len(read_rows(result["dataset_path"])) == 2
        root = Path(result["dataset_path"]).parent.parent
        assert not (root / "manifest.json").exists()
        assert not (root / "inputs.jsonl").exists()
        assert not (root / "summary.json").exists()
    assert all(client.is_closed() for client in judge_env.clients)
    assert (
        capture_env.opened.count("embedding")
        == capture_env.closed.count("embedding")
        == 2
    )
    assert capture_env.opened.count("chat") == capture_env.closed.count("chat") == 2
    assert capture_env.category_calls == 1


def test_fatal_judge_failure_preserves_results_and_stops_calls(
    tmp_path, capture_env, judge_env
):
    from rag_quality_lab.eval.runner import EvaluationError, run_evaluation

    judge_env.fail = True
    ids = [q["question_id"] for q in capture_env.data["questions"][:2]]
    with pytest.raises(EvaluationError) as error:
        run_evaluation(
            config=capture_env.config, question_ids=ids, artifacts_dir=tmp_path
        )
    rows = read_rows(error.value.results_path)
    assert len(rows) == 2
    statuses = [
        r["metrics"][name]["status"]
        for r in rows
        for name in ("faithfulness", "answer_success")
    ]
    assert statuses.count("error") == 1 and statuses.count("not_run") == 3
    assert len(judge_env.requests) == 1
    assert all(r["metrics"]["source_hit_at_k"]["status"] == "ok" for r in rows)
    assert "secret-key" not in str(error.value) + error.value.results_path.read_text()
    assert all(client.is_closed() for client in judge_env.clients)


def test_cli_outputs_one_json_and_reports_saved_failure(
    tmp_path, capture_env, judge_env, monkeypatch
):
    from rag_quality_lab.cli import app
    from rag_quality_lab.eval import runner

    monkeypatch.setattr(runner, "load_app_config", lambda: capture_env.config)
    qid = capture_env.data["questions"][0]["question_id"]
    cli = CliRunner()
    result = cli.invoke(
        app,
        [
            "eval",
            "run",
            "--question-id",
            qid,
            "--artifacts-dir",
            str(tmp_path),
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    saved = json.loads(result.stdout)
    assert (
        Path(saved["dataset_path"]).is_file() and Path(saved["results_path"]).is_file()
    )
    judge_env.fail = True
    failed = cli.invoke(
        app,
        [
            "eval",
            "run",
            "--question-id",
            qid,
            "--artifacts-dir",
            str(tmp_path),
            "--json",
        ],
    )
    assert failed.exit_code == 4 and not failed.stdout
    payload = json.loads(failed.stderr.splitlines()[-1])
    assert not payload["ok"] and Path(payload["results_path"]).is_file()
    assert "secret-key" not in failed.output


def test_partial_query_run_keeps_failure_unscored(tmp_path, capture_env, judge_env):
    from rag_quality_lab.eval.runner import EvaluationError, run_evaluation, summarize

    ids = [q["question_id"] for q in capture_env.data["questions"][:2]]
    capture_env.fail_at = 1
    with pytest.raises(EvaluationError) as error:
        run_evaluation(
            mode="routed-vector",
            config=capture_env.config,
            question_ids=ids,
            artifacts_dir=tmp_path,
        )
    rows = read_rows(error.value.results_path)
    assert len(rows) == 2
    failed = next(row for row in rows if row["error"] is not None)
    assert failed["metrics"]["answer_success"]["value"] is None
    assert failed["metrics"]["answer_success"]["status"] == "not_run"
    assert summarize(rows)["metrics"]["faithfulness"] == {
        "mean": 1.0,
        "scored_count": 1,
        "eligible_count": 2,
    }
    assert capture_env.opened.count("chat") == capture_env.closed.count("chat")


def test_no_answer_cases_are_judged_against_notes(tmp_path, capture_env, judge_env):
    from rag_quality_lab.eval.runner import run_evaluation

    ids = [
        q["question_id"]
        for q in capture_env.data["questions"]
        if q["answerability"] == "no_answer"
    ]
    result = run_evaluation(
        config=capture_env.config, question_ids=ids, artifacts_dir=tmp_path
    )
    assert result["metrics"]["faithfulness"]["mean"] is None
    assert result["metrics"]["faithfulness"]["eligible_count"] == 0
    assert result["metrics"]["answer_success"]["scored_count"] == len(ids)
    assert len(judge_env.requests) == len(ids)


def test_source_coverage_survives_empty_retrieval(
    tmp_path, capture_env, judge_env, monkeypatch
):
    from rag_quality_lab.eval.runner import run_evaluation
    from rag_quality_lab.retrieval.qdrant_store import QdrantStore

    questions = capture_env.data["questions"][:2]
    source = questions[0]["expected_relevant_sources"][0]
    questions[1]["expected_relevant_sources"] = [f"{source}:chunk"]
    golden = tmp_path / "golden.json"
    golden.write_text(json.dumps({"questions": questions}))
    monkeypatch.setattr(QdrantStore, "search_chunks", lambda *args, **kwargs: [])
    result = run_evaluation(
        config=capture_env.config, golden_path=golden, artifacts_dir=tmp_path
    )
    rows = read_rows(result["dataset_path"])
    assert rows[0]["relevant_ids"] and rows[1]["relevant_ids"] == [f"{source}:chunk"]
    assert all(row["ranked_ids"] == [] for row in rows)
    assert result["metrics"]["source_hit_at_k"]["mean"] == 0
    assert result["metrics"]["source_mrr_at_k"]["mean"] == 0


def test_query_setup_failure_closes_owned_clients(tmp_path, capture_env, judge_env):
    from rag_quality_lab.eval.runner import EvaluationError, run_evaluation

    capture_env.setup_fail = True
    with pytest.raises(EvaluationError) as error:
        run_evaluation(config=capture_env.config, artifacts_dir=tmp_path)
    assert error.value.dataset_path is None and error.value.results_path is None
    assert capture_env.closed.count("embedding") == 1
    assert not judge_env.requests
    assert "secret-key" not in str(error.value)


def test_failed_answer_is_a_quality_result_not_a_provider_failure(
    tmp_path, capture_env, judge_env
):
    from rag_quality_lab.eval.runner import run_evaluation

    judge_env.verdict = "fail"
    result = run_evaluation(
        config=capture_env.config,
        artifacts_dir=tmp_path,
        question_ids=[capture_env.data["questions"][0]["question_id"]],
    )
    assert result["metrics"]["answer_success"]["mean"] == 0
    assert result["metrics"]["answer_success"]["scored_count"] == 1
    assert result["metrics"]["faithfulness"]["mean"] == 1
    row = read_rows(result["results_path"])[0]
    assert row["metrics"]["answer_success"]["reason"] == "Offline fixture verdict."
    assert row["question"]["grading_notes"]


@pytest.mark.parametrize("json_output", [False, True])
def test_legacy_index_reports_recovery_before_any_model_calls(
    tmp_path, capture_env, judge_env, monkeypatch, json_output
):
    from qdrant_client import models
    from rag_quality_lab.cli import app
    from rag_quality_lab.eval import runner

    capture_env.client.delete_payload(
        collection_name="capture",
        keys=["index_fingerprint"],
        points=models.FilterSelector(filter=models.Filter()),
    )
    monkeypatch.setattr(runner, "load_app_config", lambda: capture_env.config)
    args = ["eval", "run", "--artifacts-dir", str(tmp_path)]
    if json_output:
        args.append("--json")
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 4
    if json_output:
        assert not result.stdout
        payload = json.loads(result.stderr)
        assert payload["stage"] == "retrieval"
        assert payload["dataset_path"] is None
        message = payload["message"]
    else:
        message = result.stderr
    assert "index_fingerprint" in message and "corpus ingest --recreate" in message
    assert not judge_env.requests and not capture_env.query_calls
    assert capture_env.closed.count("store") == 1
    assert not list(tmp_path.rglob("answers.jsonl"))


def test_remote_index_error_does_not_expose_provider_details(
    tmp_path, capture_env, judge_env, monkeypatch
):
    from rag_quality_lab.eval.runner import EvaluationError, run_evaluation

    def fail_scroll(**kwargs):
        raise RuntimeError("Authorization: Bearer secret-key")

    monkeypatch.setattr(capture_env.client, "scroll", fail_scroll)
    with pytest.raises(EvaluationError) as error:
        run_evaluation(config=capture_env.config, artifacts_dir=tmp_path)
    assert "secret-key" not in str(error.value)
    assert "Qdrant" in str(error.value)
    assert error.value.stage == "retrieval"
    assert not judge_env.requests and not capture_env.query_calls
