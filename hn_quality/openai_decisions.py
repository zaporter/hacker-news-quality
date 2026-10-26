"""OpenAI Decisions API provider for hn_quality.rate. Translates our Jev-style QUESTIONS into Decisions questions."""

import asyncio
import random

from openai import APIError, AsyncOpenAI, RateLimitError

from hn_quality.questions import QUESTIONS
from hn_quality.states import ROOT

MODEL = "gpt-6-luna"
USD_PER_MTOK = None  # pricing not confirmed yet
ERRORS = (APIError,)
VALUE_FIELD = {"predicate": "probability", "score": "score", "choice": "choice"}


def to_decision_question(name: str, q: dict) -> dict:
    base = {"name": name, "instructions": q["instructions"]}
    match q["type"]:
        case "noul":
            return {**base, "type": "predicate"}
        case "score":
            return {**base, "type": "score", "levels": [{"label": c} for c in q["criteria"]]}
        case "choice":
            return {**base, "type": "choice",
                    "choices": [{"value": k, "description": v} for k, v in q["criteria"].items()]}
    raise ValueError(f"unsupported question type {q['type']!r} for {name}")


DECISION_QUESTIONS = [to_decision_question(k, v) for k, v in QUESTIONS.items()]


def make_client() -> AsyncOpenAI:
    key = (ROOT / "openai-api.txt").read_text().strip()
    return AsyncOpenAI(api_key=key, max_retries=3, timeout=120)


async def rate(client: AsyncOpenAI, state: dict) -> tuple[dict, dict, dict, str]:
    # Same evidence as Jev's `state`: the raw JSON object, no extra framing text.
    # The SDK's own retries are too short for sustained tokens-per-minute limits, so back off (with jitter) here.
    for attempt in range(12):
        try:
            d = await client.decisions.create(
                model=MODEL,
                input=[{"role": "user", "content": [{"type": "input_json", "data": state}]}],
                questions=DECISION_QUESTIONS,
            )
            break
        except RateLimitError:
            if attempt == 11:
                raise
            await asyncio.sleep(min(30, 2**attempt) * (0.5 + random.random()))
    raw = {a.name: a.model_dump() for a in d.answers}
    answers = {a.name: None if a.type == "refusal" else getattr(a, VALUE_FIELD[a.type]) for a in d.answers}
    return answers, raw, d.usage.model_dump(), d.model
