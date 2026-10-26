<script lang="ts">
  import type { Answer, Comment, Question } from './types'

  // One example at a time, ranked by the average of both models' answers
  let { comments, other, key, q, names }: {
    comments: Comment[]
    other: Map<number, Comment>
    key: string
    q: Question
    names: [string, string]
  } = $props()

  const COUNT = 20
  let mode = $state<'high' | 'low'>('high')
  let index = $state(0)

  const score = (c: Comment) => {
    const vs = [c.answers[key], other.get(c.id)?.answers[key]].filter((v): v is number => typeof v === 'number')
    return vs.length ? vs.reduce((a, b) => a + b) / vs.length : null
  }
  const shown = $derived.by(() => {
    const sorted = comments
      .map((c) => ({ c, s: score(c) }))
      .filter((d): d is { c: Comment; s: number } => d.s !== null)
      .toSorted((a, b) => b.s - a.s)
      .map((d) => d.c)
    return (mode === 'high' ? sorted : sorted.toReversed()).slice(0, COUNT)
  })
  const c = $derived(shown[Math.min(index, shown.length - 1)])

  // Score labels look like "Expert. Comment author is ..."; the part before the first period names the level
  const short = (l: string) => l.split('.')[0]
  const modes = $derived(
    q.type === 'score'
      ? { high: `closest to “${short(q.labels!.at(-1)!)}”`, low: `closest to “${short(q.labels![0])}”` }
      : { high: 'clearest yes', low: 'clearest no' },
  )
  const fmt = (v: Answer | undefined) =>
    typeof v !== 'number' ? '–' : q.type === 'score' ? `${short(q.labels![Math.round(v)])} (${v.toFixed(1)})` : `${Math.round(v * 100)}% yes`
  const hn = (id: number) => `https://news.ycombinator.com/item?id=${id}`
  const setMode = (m: typeof mode) => ((mode = m), (index = 0))
</script>

<div class="examples">
  <div class="bar">
    <h3>Example comments</h3>
    <span class="comhead">
      {#each ['high', 'low'] as const as m, i}
        {#if i}|{/if}
        <button class="link" class:active={mode === m} onclick={() => setMode(m)}>{modes[m]}</button>
      {/each}
    </span>
    <span class="comhead nav">
      <button class="link" disabled={index === 0} onclick={() => index--}>‹ prev</button>
      | {index + 1} / {shown.length} |
      <button class="link" disabled={index >= shown.length - 1} onclick={() => index++}>next ›</button>
    </span>
  </div>

  {#if c}
    <div class="thread">
      <div class="comhead">
        on: <a href={hn(c.post_id)} target="_blank" rel="noreferrer">{c.post_title}</a>
      </div>
      {#if c.parent_comment_text}
        <div class="comment parent">
          <span class="vote">▲</span>
          <div>
            <div class="comhead">parent</div>
            <div class="text clamp">{c.parent_comment_text}</div>
          </div>
        </div>
      {/if}
      <div class="comment" class:reply={!!c.parent_comment_text}>
        <span class="vote">▲</span>
        <div>
          <div class="comhead">
            {c.time.slice(0, 10)} | <a href={hn(c.id)} target="_blank" rel="noreferrer">link</a>
            | {names[0]}: <b>{fmt(c.answers[key])}</b> | {names[1]}: <b>{fmt(other.get(c.id)?.answers[key])}</b>
          </div>
          <div class="text">{c.comment_text}</div>
        </div>
      </div>
    </div>
  {:else}
    <p class="comhead">No comments.</p>
  {/if}
</div>

<style>
  /* Mimics news.ycombinator.com's comment styling */
  .examples { font-family: Verdana, Geneva, sans-serif; font-size: 13px; }
  .bar { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 12px; margin-bottom: 12px; }
  h3 { font-family: system-ui, -apple-system, sans-serif; font-size: 15px; margin: 0; }
  .nav { margin-left: auto; }
  .comhead { color: #828282; font-size: 11px; }
  .comhead a { color: #828282; }
  .comhead b { color: #555; font-weight: normal; }
  button.link {
    font: inherit; color: #828282; background: none; border: 0; padding: 0 2px; cursor: pointer;
  }
  button.link.active { color: #000; text-decoration: underline; }
  button.link:disabled { opacity: 0.4; cursor: default; }
  .thread { display: grid; gap: 10px; }
  .comment { display: flex; gap: 6px; }
  .comment.reply { margin-left: 40px; }
  .vote { color: #9a9a9a; font-size: 10px; line-height: 1.6; }
  .text { color: #000; line-height: 1.45; white-space: pre-line; max-height: 22em; overflow: auto; margin-top: 2px; }
  .parent .text { color: #828282; }
  .clamp { display: -webkit-box; -webkit-line-clamp: 4; line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
</style>
