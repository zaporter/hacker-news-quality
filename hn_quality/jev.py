"""TypeSafe Jev provider for hn_quality.rate."""

import asyncio

import httpx

from hn_quality.questions import QUESTIONS
from hn_quality.states import ROOT

API_URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
USD_PER_MTOK = 0.042
ERRORS = (httpx.HTTPError,)


def make_client() -> httpx.AsyncClient:
    key = (ROOT / "typesafe-key.txt").read_text().strip()
    return httpx.AsyncClient(headers={"Authorization": f"Bearer {key}"}, timeout=120)


async def rate(client: httpx.AsyncClient, state: dict) -> tuple[dict, dict, dict, str]:
    body = {"model": MODEL, "state": state, "questions": QUESTIONS}
    for attempt in range(6):
        r = await client.post(API_URL, json=body)
        if r.status_code != 429 and r.status_code < 500:
            break
        await asyncio.sleep(2**attempt)
    r.raise_for_status()
    resp = r.json()
    answers = {k: a.get(a["type"]) for k, a in resp["answers"].items()}
    return answers, resp["answers"], resp["usage"], resp["model"]
