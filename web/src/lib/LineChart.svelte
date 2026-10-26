<script lang="ts">
  import * as d3 from 'd3'
  import { fitLine, formatRel, type Point } from './fit'

  let { points, label = '', compare = null, yDomain, format = d3.format('.2f'), height = 260, legend = true }: {
    points: Point[]
    label?: string
    compare?: { label: string; points: Point[] } | null
    yDomain: [number, number]
    format?: (v: number) => string
    height?: number
    legend?: boolean
  } = $props()

  let width = $state(600)
  const m = { top: 16, right: 16, bottom: 28, left: 44 }

  const all = $derived([...points, ...(compare?.points ?? [])])
  const x = $derived(d3.scaleUtc(d3.extent(all, (d) => d.x) as [Date, Date], [m.left, width - m.right]))
  const y = $derived(d3.scaleLinear(yDomain, [height - m.bottom, m.top]))
  const line = $derived(d3.line<Point>((d) => x(d.x), (d) => y(d.y)))
  let hover = $state<Point | null>(null)

  const fit = $derived(fitLine(points))
  const compareFit = $derived(compare ? fitLine(compare.points) : null)
  const describe = (f: NonNullable<ReturnType<typeof fitLine>>) =>
    `${d3.format('+.4f')(f.perYear)} / year (${formatRel(f.relPerYear)} of mean / year) · R² ${d3.format('.2f')(f.r2)}`

  function onmove(e: PointerEvent) {
    const [px] = d3.pointer(e)
    hover = points[d3.leastIndex(points, (p) => Math.abs(x(p.x) - px)) ?? 0]
  }
</script>

<div bind:clientWidth={width}>
  {#if fit && legend}
    <p class="trend-label">
      <i class="swatch main"></i>{label} trend: {describe(fit)}
      {#if compare && compareFit}
        &nbsp;&nbsp;<i class="swatch other"></i>{compare.label} trend: {describe(compareFit)}
      {/if}
    </p>
  {/if}
  <svg {width} {height} onpointermove={onmove} onpointerleave={() => (hover = null)} role="img">
    {#each y.ticks(5) as t}
      <line class="grid" x1={m.left} x2={width - m.right} y1={y(t)} y2={y(t)} />
      <text x={m.left - 6} y={y(t)} dy="0.32em" text-anchor="end">{format(t)}</text>
    {/each}
    {#each x.ticks(Math.max(2, Math.floor(width / 100))) as t}
      <text x={x(t)} y={height - m.bottom + 18} text-anchor="middle">{x.tickFormat()(t)}</text>
    {/each}
    {#if compare}
      <path class="line other" d={line(compare.points)} />
      {#if compareFit}
        <line class="trend other" x1={x(new Date(compareFit.x0))} x2={x(new Date(compareFit.x1))}
          y1={y(compareFit.y0)} y2={y(compareFit.y1)} />
      {/if}
    {/if}
    <path class="line" d={line(points)} />
    {#each points as p}
      <circle class="dot" cx={x(p.x)} cy={y(p.y)} r="2.5" />
    {/each}
    {#if fit}
      <line class="trend" x1={x(new Date(fit.x0))} x2={x(new Date(fit.x1))} y1={y(fit.y0)} y2={y(fit.y1)} />
    {/if}
    {#if hover}
      {@const hx = x(hover.x)}
      <line class="rule" x1={hx} x2={hx} y1={m.top} y2={height - m.bottom} />
      <text x={hx > width / 2 ? hx - 6 : hx + 6} y={m.top} text-anchor={hx > width / 2 ? 'end' : 'start'}>
        {d3.utcFormat('%Y-%m')(hover.x)}: {format(hover.y)} (n={hover.n})
      </text>
    {/if}
  </svg>
</div>
