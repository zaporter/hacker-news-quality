"""Aggregate raw decision-model results into a single JSON file for the web viewer."""

import json
import random
import sys
from collections import defaultdict

import duckdb

from hn_quality.questions import QUESTIONS
from hn_quality.states import FIRST_MONTH, ROOT

RAW_DIR = ROOT / "data/raw_analysis"
OUT_DIR = ROOT / "web/public"
SAMPLE_SIZE = 5000


def main() -> None:
    """Usage: export <raw_analysis name> <model label>; writes web/public/data-<label>.json."""
    name, label = sys.argv[1], sys.argv[2]
    parquet = RAW_DIR / f"{name}.parquet"
    if not parquet.exists():
        print(f"skipping {label}: {parquet.relative_to(ROOT)} not found")
        return
    out = OUT_DIR / f"data-{label}.json"
    rel = f"(SELECT * FROM read_parquet('{parquet}') WHERE month >= '{FIRST_MONTH}')"
    rows = duckdb.sql(f"SELECT id, month, answers FROM {rel}").fetchall()

    answers_by_id = {}
    buckets: dict[str, list[dict]] = defaultdict(list)
    for id_, month, answers in rows:
        a = {q: answers.get(q) for q in QUESTIONS}
        answers_by_id[id_] = a
        buckets[month].append(a)

    monthly = []
    for month, group in sorted(buckets.items()):
        means, choices = {}, {}
        for q, spec in QUESTIONS.items():
            vals = [a[q] for a in group if a.get(q) is not None]
            if not vals:
                continue
            if spec["type"] == "choice":
                choices[q] = {label: vals.count(label) / len(vals) for label in spec["criteria"]}
            else:
                means[q] = sum(vals) / len(vals)
        monthly.append({"month": month, "n": len(group), "means": means, "choices": choices})

    # Sorted first so every model's export shows the same example comments
    sample_ids = random.Random(0).sample(sorted(answers_by_id), min(SAMPLE_SIZE, len(rows)))
    comments = [
        {"id": id_, "time": time, "post_title": state.get("post_title"), "post_id": post_id,
         "comment_text": state.get("comment_text"), "parent_comment_text": state.get("parent_comment_text"),
         "answers": answers_by_id[id_]}
        for id_, post_id, time, state in duckdb.sql(
            f"SELECT id, post_id, time::VARCHAR, state FROM {rel} WHERE list_contains(?, id)", params=[sample_ids]
        ).fetchall()
    ]

    questions = {
        q: {"type": s["type"], "instructions": s["instructions"],
            "labels": list(s["criteria"]) if "criteria" in s else None}
        for q, s in QUESTIONS.items()
    }
    out.write_text(json.dumps({"n": len(rows), "questions": questions, "monthly": monthly, "comments": comments}))
    print(f"wrote {out.relative_to(ROOT)}: {len(rows)} rows, {len(monthly)} months, {len(comments)} sample comments")


if __name__ == "__main__":
    main()
