"""Rate sampled HN comments with a decision model (Jev or OpenAI Decisions).

Both providers rate the same deterministic per-month sample, so results can be compared comment by comment.
Results stream to a resumable JSONL file, then get written to parquet.
"""

import argparse
import asyncio
import json

import duckdb

from hn_quality import jev, openai_decisions
from hn_quality.states import FIRST_MONTH, ROOT, load_states

PROVIDERS = {"jev": jev, "openai": openai_decisions}
OUT_DIR = ROOT / "data/raw_analysis"


async def run(args: argparse.Namespace) -> None:
    provider = PROVIDERS[args.provider]
    name = args.name or f"{args.provider}-monthly-v4"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    jsonl = OUT_DIR / f"{name}.jsonl"
    done = {json.loads(line)["id"] for line in jsonl.open()} if jsonl.exists() else set()
    rows = [r for r in load_states(args.first, args.last, args.per_month) if r["id"] not in done]
    print(f"{len(rows)} comments to rate with {args.provider} -> {name} ({len(done)} already done)")
    if args.dry_run:
        print(json.dumps(rows[0], indent=2) if rows else "nothing to do")
        return

    client = provider.make_client()
    sem = asyncio.Semaphore(args.concurrency)

    async def one(row: dict):
        async with sem:
            return row, await provider.rate(client, row["state"])

    def cost(tokens: int) -> str:
        return f"~${tokens * provider.USD_PER_MTOK / 1e6:.2f}" if provider.USD_PER_MTOK else "cost unknown"

    tokens = errors = 0
    with jsonl.open("a") as f:
        for i, fut in enumerate(asyncio.as_completed([one(r) for r in rows]), 1):
            try:
                row, (answers, raw_answers, usage, model) = await fut
            except provider.ERRORS as e:
                errors += 1
                print(f"error: {str(e)[:300]}")
                continue
            tokens += usage["input_tokens"]
            f.write(json.dumps({**row, "model": model, "usage": usage, "answers": answers,
                                "raw_answers": raw_answers}) + "\n")
            f.flush()
            if i % 100 == 0:
                print(f"{i}/{len(rows)}  {tokens:,} input tokens  {cost(tokens)}")

    print(f"done: {len(rows) - errors} rated, {errors} errors, {tokens:,} input tokens, {cost(tokens)}")
    parquet = OUT_DIR / f"{name}.parquet"
    duckdb.sql(f"COPY (SELECT * FROM read_json_auto('{jsonl}')) TO '{parquet}' (FORMAT parquet)")
    print(f"wrote {parquet.relative_to(ROOT)}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("provider", choices=list(PROVIDERS))
    p.add_argument("--per-month", type=int, default=200, help="comments sampled per month")
    p.add_argument("--first", default=FIRST_MONTH, help="first month (YYYY-MM)")
    p.add_argument("--last", default=None, help="last month (YYYY-MM), default latest")
    p.add_argument("--name", default=None, help="output file stem in data/raw_analysis (default <provider>-monthly-v4)")
    p.add_argument("--concurrency", type=int, default=16)
    p.add_argument("--dry-run", action="store_true", help="build states and print one, without calling the API")
    asyncio.run(run(p.parse_args()))


if __name__ == "__main__":
    main()
