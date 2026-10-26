"""Build Jev `state` objects for sampled HN comments from the raw monthly parquet dump."""

import html
import re
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw_comments/data"
LOOKBACK_MONTHS = 3  # months before the sampled month to load posts/parents that comments may point to
LOOKAHEAD_MONTHS = 1  # months after, for replies (children) posted later
FIRST_MONTH = "2012-01"  # earlier HN was too small to be representative


def clean(text: str | None) -> str | None:
    if not text:
        return None
    text = text.replace("<p>", "\n\n")
    text = re.sub(r'<a href="([^"]*)"[^>]*>.*?</a>', r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip() or None


def month_files() -> dict[str, str]:
    """'YYYY-MM' -> parquet path, in order."""
    return {p.stem: str(p) for p in sorted(RAW.glob("*/*.parquet"))}


def load_month(db: duckdb.DuckDBPyConnection, month: str, per_month: int) -> list[dict]:
    """Deterministically sample `per_month` live comments from `month` (ordered by hash(id), so a larger
    sample is a superset of a smaller one) and attach the root post, parent and top-ranked child."""
    files = month_files()
    months = list(files)
    i = months.index(month)
    window = [files[m] for m in months[max(0, i - LOOKBACK_MONTHS) : i + LOOKAHEAD_MONTHS + 1]]
    # The dump's `kids` lists are empty for much of 2023+, so rebuild them from `parent` for every month.
    # HN's display rank isn't available that way; rank live replies by their own reply count, then earliest.
    db.execute(f"""
        CREATE OR REPLACE TEMP TABLE items AS
        WITH raw AS (
            SELECT id, type, text, title, url, parent, time, deleted, dead, filename
            FROM read_parquet({window!r}, filename = true)
        ),
        replies AS (SELECT parent AS id, count(*) AS n FROM raw WHERE type = 2 GROUP BY parent),
        kids AS (
            SELECT r.parent AS id, list(r.id ORDER BY coalesce(rp.n, 0) DESC, r.time, r.id) AS kids
            FROM raw r LEFT JOIN replies rp ON rp.id = r.id
            WHERE r.type = 2 AND r.deleted = 0 AND r.dead = 0
            GROUP BY r.parent
        )
        SELECT raw.*, coalesce(kids.kids, []) AS kids FROM raw LEFT JOIN kids USING (id)
    """)
    db.execute("""
        CREATE OR REPLACE TEMP TABLE sample AS
        SELECT id, parent, kids, text, time FROM items
        WHERE filename = ? AND type = 2 AND deleted = 0 AND dead = 0 AND coalesce(text, '') <> ''
        ORDER BY hash(id) LIMIT ?
    """, [files[month], per_month])
    rows = db.execute("""
        WITH RECURSIVE chain(comment_id, cur) AS (
            SELECT id, parent FROM sample
            UNION ALL
            SELECT c.comment_id, i.parent FROM chain c JOIN items i ON i.id = c.cur WHERE i.type = 2
        )
        SELECT s.id, s.time AT TIME ZONE 'UTC', p.id, p.title, p.url, p.text, s.text, par.text, child.text
        FROM sample s
        JOIN chain c ON c.comment_id = s.id
        JOIN items p ON p.id = c.cur AND p.type <> 2
        LEFT JOIN items par ON par.id = s.parent AND par.type = 2
        LEFT JOIN items child ON child.id = s.kids[1]
        ORDER BY s.id
    """).fetchall()
    states = []
    for id_, time, post_id, title, url, post_text, text, parent_text, child_text in rows:
        state = {
            "post_title": clean(title),
            "post_url": url or None,
            "post_content": clean(post_text),
            "comment_text": clean(text),
            "parent_comment_text": clean(parent_text),
            "most_upvoted_child_comment_text": clean(child_text),
        }
        states.append({
            "id": id_,
            "post_id": post_id,
            "month": month,
            "time": time.isoformat(),
            "state": {k: v for k, v in state.items() if v},
        })
    return states


def load_states(first: str, last: str | None, per_month: int) -> list[dict]:
    db = duckdb.connect()
    months = [m for m in month_files() if m >= first and (last is None or m <= last)]
    states = []
    for month in months:
        got = load_month(db, month, per_month)
        print(f"{month}: {len(got)} comments", flush=True)
        states += got
    return states
