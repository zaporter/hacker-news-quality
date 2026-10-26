<script lang="ts">
  import * as d3 from 'd3'
  import type { Comment, Question } from './types'
  import LineChart from './LineChart.svelte'
  import Comments from './Comments.svelte'
  import { fitLine, formatRel, type Point } from './fit'

  type Model = { name: string; points: Point[] }
  let { id, q, models, comments, other }: {
    id: string
    q: Question
    models: [Model, Model | null]
    comments: Comment[]
    other: Map<number, Comment>
  } = $props()

  const max = $derived(q.type === 'score' ? q.labels!.length - 1 : 1)
  const fmt = $derived(q.type === 'score' ? d3.format('.2f') : d3.format('.0%'))
  const yearMean = (ps: Point[], year: number) => d3.mean(ps.filter((p) => p.x.getUTCFullYear() === year), (p) => p.y)
  const rows = $derived(
    models.filter((m): m is Model => !!m).map((m) => {
      const [first, last] = [m.points[0].x.getUTCFullYear(), m.points.at(-1)!.x.getUTCFullYear()]
      return { ...m, fit: fitLine(m.points)!, first, last, from: yearMean(m.points, first)!, to: yearMean(m.points, last)! }
    }),
  )
</script>

<section class="question" {id}>
  <div class="info">
    <h2>{q.instructions}</h2>
    <p class="muted kicker">
      {q.type === 'score' ? `Scored 0–${max} on the scale below` : "Yes or no, answered as each model's probability of yes"}
    </p>
    {#if q.type === 'score'}
      <ol start="0" class="muted">{#each q.labels ?? [] as l}<li>{l}</li>{/each}</ol>
    {/if}
    <table class="trends">
      <tbody>
        {#each rows as r, i}
          <tr>
            <td><i class="swatch" class:main={i === 0} class:other={i === 1}></i>{r.name}</td>
            <td class="rel" class:negative={r.fit.relPerYear < 0}>{formatRel(r.fit.relPerYear)}/yr</td>
            <td class="muted">{r.first}: {fmt(r.from)} → {r.last}: {fmt(r.to)}</td>
            <td class="muted">R² {d3.format('.2f')(r.fit.r2)}</td>
          </tr>
        {/each}
      </tbody>
    </table>
    <LineChart
      points={models[0].points}
      compare={models[1] && { label: models[1].name, points: models[1].points }}
      yDomain={[0, max]}
      format={fmt}
      height={200}
      legend={false}
    />
  </div>
  <Comments {comments} {other} key={id} {q} names={[models[0].name, models[1]?.name ?? '']} />
</section>
