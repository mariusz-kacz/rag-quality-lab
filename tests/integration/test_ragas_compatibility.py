"""Real optional-library boundary; choices and limitations: ragas_compatibility.md."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import time

import httpx
import pytest
from openai import AsyncOpenAI

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def optional_eval_dependencies(monkeypatch):
    # Skip only absent extras, never a broken installed dependency or API import.
    for package in ("ragas", "ir_measures"):
        if importlib.util.find_spec(package) is None:
            pytest.skip("requires uv sync --locked --extra eval")
    monkeypatch.setenv("RAGAS_DO_NOT_TRACK", "true")


def offline_client(respond):
    return AsyncOpenAI(
        api_key="offline-only",
        base_url="https://foundry.invalid/api/projects/test/openai/v1/",
        max_retries=1,
        timeout=120,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)),
    )


def evaluator_config(client):
    from rag_quality_lab.eval.config import load_eval_config

    return load_eval_config(
        {
            "RAGLAB_EVAL_MODEL": "judge-deployment",
            "RAGLAB_EVAL_EMBEDDING_MODEL": "embedding-deployment",
            "RAGLAB_EVAL_BASE_URL": str(client.base_url),
            "RAGLAB_EVAL_API_KEY": "offline-only",
        }
    )


def completion(content):
    return httpx.Response(
        200,
        json={
            "id": "offline-completion",
            "object": "chat.completion",
            "created": 0,
            "model": "judge-deployment",
            "choices": [
                {
                    "index": 0,
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": content},
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        },
    )


def test_real_metrics_experiment_and_local_round_trip(tmp_path):
    from rag_quality_lab.eval.providers import evaluator_scope
    from ragas import Dataset, experiment
    from ragas.experiment import Experiment
    from ragas.metrics.collections import AnswerRelevancy, Faithfulness

    question = "Where is Warsaw?"
    answer = "Warsaw is in France. [source:1]"
    requests = []

    def respond(request):
        assert request.url.host == "foundry.invalid"
        body = json.loads(request.content)
        requests.append((request.url.path, body))
        if request.url.path.endswith("/embeddings"):
            texts = body["input"]
            texts = [texts] if isinstance(texts, str) else texts
            return httpx.Response(
                200,
                json={
                    "object": "list",
                    "model": "embedding-deployment",
                    "data": [
                        {
                            "object": "embedding",
                            "index": i,
                            "embedding": [1.0, 0.0]
                            if text == question
                            else [-1.0, 0.0],
                        }
                        for i, text in enumerate(texts)
                    ],
                    "usage": {"prompt_tokens": 2, "total_tokens": 2},
                },
            )
        assert request.url.path.endswith("/chat/completions")
        prompt = json.dumps(body["messages"])
        if "StatementGeneratorOutput" in prompt:
            output = {"statements": ["Warsaw is in France."]}
        elif "NLIStatementOutput" in prompt:
            output = {
                "statements": [
                    {
                        "statement": "Warsaw is in France.",
                        "reason": "Contradicted.",
                        "verdict": 0,
                    }
                ]
            }
        else:
            assert "AnswerRelevanceOutput" in prompt
            output = {"question": "Where is Paris?", "noncommittal": 0}
        return completion(json.dumps(output))

    async def run():
        async with (
            offline_client(respond) as client,
            evaluator_scope(evaluator_config(client), client=client) as evaluator,
        ):
            faithfulness = Faithfulness(llm=evaluator.llm)
            relevancy = AnswerRelevancy(
                llm=evaluator.llm, embeddings=evaluator.embeddings
            )
            dataset = Dataset(
                "compatibility", backend="local/jsonl", root_dir=str(tmp_path)
            )
            for qid in ("q-1", "q-2"):
                dataset.append({"question_id": qid, "status": "ok", "reason": None})
            for status, reason in (
                ("error", "provider_error"),
                ("not_applicable", "no_answer"),
                ("not_run", None),
            ):
                dataset.append(
                    {"question_id": status, "status": status, "reason": reason}
                )
            dataset.save()
            gate = asyncio.Semaphore(1)
            active = peak = 0

            @experiment()
            async def score(row):
                nonlocal active, peak
                async with gate:
                    active += 1
                    peak = max(peak, active)
                    try:
                        # Allow competing experiment rows to run.
                        await asyncio.sleep(0)
                        values = [None, None]
                        if row["status"] == "ok":
                            results = [
                                await evaluator.call(
                                    faithfulness.ascore,
                                    question,
                                    answer,
                                    ["Warsaw is in Poland."],
                                ),
                                await evaluator.call(
                                    relevancy.ascore, question, answer
                                ),
                            ]
                            values = [result.value for result in results]
                            assert all(
                                result.reason is None and result.traces is None
                                for result in results
                            )
                        return {
                            "question_id": row["question_id"],
                            "metrics": {
                                name: {
                                    "value": value,
                                    "status": row["status"],
                                    "reason": row["reason"],
                                }
                                for name, value in zip(
                                    ("faithfulness", "answer_relevancy"),
                                    values,
                                    strict=True,
                                )
                            },
                            "diagnostics": {
                                "context_tokens": 7,
                                "citation_valid": True,
                                "usage": None,
                            },
                        }
                    finally:
                        active -= 1

            result = await score.arun(dataset, name="compatibility-result")
            assert peak == 1
            return list(result)

    rows = asyncio.run(run())
    loaded = list(
        Experiment.load(
            "compatibility-result", backend="local/jsonl", root_dir=str(tmp_path)
        )
    )
    saved = [
        json.loads(line)
        for line in (tmp_path / "experiments/compatibility-result.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert loaded == saved == rows
    by_id = {row["question_id"]: row for row in loaded}
    assert len(loaded) == len(by_id) == 5
    assert all(
        row["diagnostics"]
        == {"context_tokens": 7, "citation_valid": True, "usage": None}
        for row in loaded
    )
    for qid in ("q-1", "q-2"):
        assert by_id[qid]["metrics"]["faithfulness"]["value"] == 0.0
        assert by_id[qid]["metrics"]["answer_relevancy"]["value"] == -1.0
    for status, reason in (
        ("error", "provider_error"),
        ("not_applicable", "no_answer"),
        ("not_run", None),
    ):
        assert all(
            outcome == {"value": None, "status": status, "reason": reason}
            for outcome in by_id[status]["metrics"].values()
        )
    chat = [body for path, body in requests if path.endswith("/chat/completions")]
    # Two faithfulness calls plus default strictness=3 per answer.
    assert len(chat) == 10
    assert all(body["model"] == "judge-deployment" for body in chat)
    assert all(body["response_format"] == {"type": "json_object"} for body in chat)
    assert all(
        body["temperature"] == 0.01
        and body["top_p"] == 0.1
        and body["max_tokens"] == 1024
        for body in chat
    )


@pytest.mark.parametrize(
    ("failure", "expected_requests", "code", "fatal"),
    [
        ("authentication", 1, "authentication", True),
        ("configuration", 1, "configuration", True),
        ("unavailable", 2, "provider_error", False),
        ("timeout", 2, "timeout", False),
        ("malformed", 1, "invalid_output", False),
    ],
)
def test_adapter_has_one_transport_retry_owner(
    failure, expected_requests, code, fatal, capsys, caplog
):
    from rag_quality_lab.eval.providers import EvalProviderError, evaluator_scope
    from ragas.metrics.collections import Faithfulness

    requests = []

    def respond(request):
        requests.append(request)
        if failure == "timeout":
            raise httpx.ReadTimeout("secret-token", request=request)
        if failure == "malformed":
            return completion("not JSON")
        return httpx.Response(
            {"authentication": 401, "configuration": 400}.get(failure, 503),
            json={"error": {"message": "secret-token", "type": failure}},
        )

    async def run():
        async with offline_client(respond) as client:
            config = evaluator_config(client)
            async with evaluator_scope(config, client=client) as evaluator:
                metric = Faithfulness(llm=evaluator.llm)
                with pytest.raises(EvalProviderError) as error:
                    await evaluator.call(
                        metric.ascore, "Question", "Answer", ["Context"]
                    )
                assert error.value.code == code
                assert error.value.fatal is fatal
                assert "secret-token" not in json.dumps(error.value.as_dict())
                if fatal:
                    with pytest.raises(EvalProviderError, match="stopped"):
                        await evaluator.call(
                            metric.ascore, "Next", "Answer", ["Context"]
                        )
                assert len(requests) == expected_requests
            assert not client.is_closed()

    asyncio.run(run())
    assert len(requests) == expected_requests
    captured = capsys.readouterr()
    assert "secret-token" not in captured.out + captured.err + caplog.text


def test_ir_backend_preserves_cutoff_and_empty_queries():
    import ir_measures as ir

    judgments = [ir.Qrel(qid, "relevant", 1) for qid in ("first", "later", "empty")]
    ranking = [
        ir.ScoredDoc("first", "relevant", 2.0),
        ir.ScoredDoc("later", "unjudged", 2.0),
        ir.ScoredDoc("later", "relevant", 1.0),
    ]
    measures = [ir.Success @ 1, ir.RR @ 1, ir.Success @ 2, ir.RR @ 2]
    # Dispatch to supported providers: pytrec_eval for Success, msmarco for RR@K.
    evaluator = ir.evaluator(measures, judgments)
    scores = {(r.query_id, r.measure): r.value for r in evaluator.iter_calc(ranking)}
    assert scores == {
        (qid, measure): value
        for qid, values in (
            ("first", (1.0, 1.0, 1.0, 1.0)),
            ("later", (0.0, 0.0, 1.0, 0.5)),
            ("empty", (0.0, 0.0, 0.0, 0.0)),
        )
        for measure, value in zip(measures, values, strict=True)
    }
    assert evaluator.calc_aggregate(ranking) == pytest.approx(
        dict(zip(measures, (1 / 3, 1 / 3, 2 / 3, 0.5), strict=True))
    )
    assert evaluator.calc_aggregate([]) == dict.fromkeys(measures, 0.0)


@pytest.mark.parametrize("borrowed_credential", [False, True])
def test_owned_evaluator_refreshes_auth(monkeypatch, borrowed_credential):
    from azure.core.credentials import AccessToken
    from azure.core.exceptions import ClientAuthenticationError
    from azure.identity import aio
    from rag_quality_lab.eval import providers
    from rag_quality_lab.eval.config import load_eval_config

    class Credential:
        requests = 0
        closed = False

        async def get_token(self, *scopes, **kwargs):
            assert scopes == ("https://cognitiveservices.azure.com/.default",)
            self.requests += 1
            if self.requests == 3:
                raise ClientAuthenticationError("secret-auth-detail")
            # Near-expiry tokens force the real Azure bearer provider to refresh.
            return AccessToken(f"token-{self.requests}", int(time.time()) + 60)

        async def close(self):
            self.closed = True

    credential = Credential()
    monkeypatch.setattr(aio, "DefaultAzureCredential", lambda: credential)
    requests = []

    def respond(request):
        requests.append(request)
        assert request.headers["authorization"] == f"Bearer token-{len(requests)}"
        assert json.loads(request.content)["model"] == "evaluator-embedding"
        response = {
            "data": [{"embedding": [1.0, 0.0], "index": 0, "object": "embedding"}],
            "model": "evaluator-embedding",
            "object": "list",
        }
        return httpx.Response(200, json=response)

    actual_client = providers.AsyncOpenAI
    clients = []

    def create_client(**kwargs):
        client = actual_client(
            **kwargs,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)),
        )
        clients.append(client)
        return client

    monkeypatch.setattr(providers, "AsyncOpenAI", create_client)
    config = load_eval_config(
        {
            "FOUNDRY_OPENAI_BASE_URL": "https://foundry.invalid/v1",
            "RAGLAB_EVAL_MODEL": "evaluator-judge",
            "RAGLAB_EVAL_EMBEDDING_MODEL": "evaluator-embedding",
        }
    )

    async def run():
        async with providers.evaluator_scope(
            config, credential=credential if borrowed_credential else None
        ) as evaluator:
            assert await evaluator.call(evaluator.embeddings.aembed_text, "First") == [
                1.0,
                0.0,
            ]
            await evaluator.call(evaluator.embeddings.aembed_text, "Second")
            with pytest.raises(providers.EvalProviderError) as error:
                await evaluator.call(evaluator.embeddings.aembed_text, "Auth failure")
            assert error.value.code == "authentication"
            assert "secret-auth-detail" not in json.dumps(error.value.as_dict())
            with pytest.raises(providers.EvalProviderError, match="stopped"):
                await evaluator.call(evaluator.embeddings.aembed_text, "Blocked")
            assert not credential.closed
        assert clients[0].is_closed()

    asyncio.run(run())
    assert credential.requests == 3
    assert len(requests) == 2
    assert credential.closed is (not borrowed_credential)
