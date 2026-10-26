<script lang="ts">
  import * as d3 from 'd3'
  import type { Data } from './lib/types'
  import BarChart from './lib/BarChart.svelte'
  import QuestionSection from './lib/QuestionSection.svelte'
  import { fitLine, formatRel } from './lib/fit'

  // Same comment sample, rated by different decision models
  const SAMPLES = {
    jev: 'Jev (TypeSafe)',
    openai: '"Open"AI Decisions',
  } as const
  type Sample = keyof typeof SAMPLES

  let datasets = $state<Partial<Record<Sample, Data>>>({})
  for (const s of Object.keys(SAMPLES) as Sample[]) {
    fetch(`${import.meta.env.BASE_URL}data-${s}.json`)
      .then((r) => r.json())
      .then((d: Data) => (datasets[s] = d))
      .catch(() => {}) // sample not exported yet
  }

  const jev = $derived(datasets.jev ?? null)
  const openai = $derived(datasets.openai ?? null)
  const toPoints = (d: Data, key: string) =>
    d.monthly.filter((w) => key in w.means).map((w) => ({ x: new Date(w.month), y: w.means[key], n: w.n }))
  const otherById = $derived(new Map((openai?.comments ?? []).map((c) => [c.id, c])))
  const range = $derived(jev?.monthly.length ? `${jev.monthly[0].month} – ${jev.monthly.at(-1)!.month}` : '')

  // Ranked by the average of both models' trend slope relative to the question's mean
  const ranked = $derived(
    Object.entries(jev?.questions ?? {})
      .filter(([, q]) => q.type !== 'choice')
      .map(([key, q]) => {
        const rels = [jev, openai]
          .filter((d): d is Data => !!d?.questions[key])
          .map((d) => fitLine(toPoints(d, key))?.relPerYear ?? 0)
        return { key, q, value: d3.mean(rels) ?? 0 }
      })
      .toSorted((a, b) => Math.abs(b.value) - Math.abs(a.value)),
  )
  const jump = (key: string) => document.getElementById(key)?.scrollIntoView({ behavior: 'smooth' })
</script>

<main>
  <h1>Hacker News Comment Quality (2026)</h1>
  <p class="intro">
    As an avid reader of HN, I will occasionally stumble upon some comments and wonder if comment quality really has changed over time (or if I'm just nostalgic).

    <br/>
    As a fun weekend project, I decided that I wanted to answer this with decision models.
    I selected 200 comments per month from 2012-01 to 2026-08. Using <a href="https://typesafe.ai/blog/introducing-system-one-models-and-jev">jev</a> and the
    <a href="https://developers.openai.com/api/docs/guides/decisions">"Open"AI Decisions API</a>,
    I evaluated comments from <a href="https://huggingface.co/datasets/open-index/hacker-news">open-index/hacker-news</a> on various metrics of "quality" (loosely derived from the HN guidelines)
    to see if decision models can provide some insight into how Hacker News is changing with the times.

    </p>
    <details>
    <summary>
    Comment Selection Methodology
    </summary>
    <div>To keep things simple, I select 200 random comments (uniformly) from each month. I have experimented with significantly
     more complex selection schemes like:
     <ul>
     <li>Only selecting comments from the top 3% of posts</li>
     <li>Weighting comments proportionally to how they are ordered by HN</li>
     <li>Selecting comments that had reply chains with at least 10 comments in the whole chain</li>
     </ul>
     However, the data was nearly identical and it made the sampling mechanism significantly harder to explain and justify.
     If you (yes you) are a statistics fanatic and know the "ideal/correct" sampling strategy, I am happy to try it.
     <br/>
     Note: some sampled comments are dropped because the dataset is missing their parent or post, leaving us with {jev ? jev.n.toLocaleString() : "loading..."}
     comments instead of a multiple of 200.
     </div>
    </details>
         <details>
    <summary>
    Why start at 2012?
    </summary>
    <div>
    Some of the first few years have noisy data that skew the trend. Also, I started reading around then.
    </div>
    </details>
    <details>
    <summary>
    AI Disclaimer
    </summary>
    <div>
    All code for this project was written with Devin + Fusion. I wrote the questions and the prose.
    </div>
    </details>
<p>
    
  </p>
  {#if jev}
    

    {#each ranked as r (r.key)}
      <QuestionSection
        id={r.key}
        q={r.q}
        models={[
          { name: SAMPLES.jev, points: toPoints(jev, r.key) },
          openai?.questions[r.key] ? { name: SAMPLES.openai, points: toPoints(openai, r.key) } : null,
        ]}
        comments={jev.comments}
        other={otherById}
      />
    {/each}

    <section class="summary">
      <h2>
        Relative Growth Comparison
        <span class="muted">(average of both models' linear trend per year)</span>
      </h2>
      <BarChart items={ranked} max={d3.max(ranked, (d) => d.value) ?? 0} format={formatRel} onselect={jump} />
      
    </section>
    <section>
    <h2>
    Conclusions
    </h2>
    I am surprised at how unsurprising this data is. Generally, HN has stayed consistent in its good and bad traits, with small upticks in ideological speech and generic comments, but only by a few percent.
    (AI has obviously grown as a topic but that isn't too surprising)
    We will see how our speech changes as a result of everyone talking to agents constantly...
<br/>
Stay kind & thoughtful! Till next time.
    </section>
  {:else}
    <p class="muted">Loading…</p>
  {/if}
</main>
