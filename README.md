# hacker-news-quality

Is Hacker News getting worse, or does it just feel that way?

## Hypothesis

A common belief is that online discussion, and Hacker News in particular, is declining: comments are snarkier,
shallower, less literate, and less engaged with the article, and LLM use is often blamed for speeding this up,
since HN readers now spend much of their day working with LLMs.

We test that belief against the null hypothesis that **comment quality has stayed roughly the same** since 2012.
The working framing is that the perceived decline is mostly perception, not something measurable in the comments
themselves.

## Experiment

Each month from 2012 onward, sample 200 random comments (deterministically), attach their context (post, parent
comment, top reply), and have decision models rate each comment on a fixed set of questions: literacy level,
engagement with the post, tone (snarky, kind, curious, dismissive, helpful, thoughtful, ideological), tangents,
use of evidence or personal experience, and topics (AI, programming languages). The same
comments are rated by Jev (TypeSafe.ai) and by OpenAI's Decisions API, so the two models can be compared.

Preliminary result (Jev, v4 questions): most measures move less than about 1% of their mean per year across
2012–2026, and literacy shows no trend at all. The quality changes that do show up all point the way people
complain, but they are small: ideological tone (+2.0%/yr), less evidence (−1.2%/yr), less kindness (−1.1%/yr),
more snark (+1.0%/yr), and slightly less engagement with the post (−0.9%/yr). The largest change is topical
rather than qualitative: comments mentioning AI rise from about 2% to about 29% (+17%/yr), while comments about
programming languages fall from 15% to 10%.

State:
```json5
{
    post_title: "",
    post_url: "", // Can be omitted if post is text-only
    post_content: "", // Text content of the post. Omitted if post is link-only
    comment_text: "",
    parent_comment_text: "", // omitted if this comment is directly on the post.
    most_upvoted_child_comment_text: "", // most liked child comment (omitted if no responses)
}
```

Questions: see [`hn_quality/questions.py`](hn_quality/questions.py), the single source of truth used for every run.

## Outputs:
1. Average number of responses per-post that come from the post-submitter
2. Outputs from jev


## Analysis 

```
data/
 | raw_comments: (folder with raw hn data)
 | raw_analysis: ex:
    jev-2015-2026.parquet (parquet data from all of the raw jev calls)
    openai-2015-2026.parquet (parquet data from "Open"AI's decision API)
 | analysis:
    jev-2015-2026.parquet (derived statistics / analytics from the raw data)
    openai-2015-2026.parquet (ditto)
```

## View

Data is presented in a simple svelte site, enabling both viewing of overall statistics (how have hacker news comments changed over time?) and viewing of random hacker news comments along with associated statistics so readers can decide if they agree or disagree with the ratings.

