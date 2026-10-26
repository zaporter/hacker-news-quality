<script lang="ts">
  import * as d3 from 'd3'

  type Week = { x: Date; shares: Record<string, number> }
  let { weeks, labels }: { weeks: Week[]; labels: string[] } = $props()

  let width = $state(600)
  const height = 260
  const m = { top: 16, right: 16, bottom: 28, left: 44 }

  const x = $derived(d3.scaleUtc(d3.extent(weeks, (d) => d.x) as [Date, Date], [m.left, width - m.right]))
  const y = d3.scaleLinear([0, 1], [height - m.bottom, m.top])
  // labels are ordered (e.g. reading levels), so use a sequential palette
  const color = $derived(d3.scaleOrdinal(labels, d3.quantize(d3.interpolateViridis, Math.max(labels.length, 2))))
  const series = $derived(
    d3.stack<Week>().keys(labels).value((d, k) => d.shares[k] ?? 0)(weeks),
  )
  const area = $derived(
    d3.area<d3.SeriesPoint<Week>>().x((d) => x(d.data.x)).y0((d) => y(d[0])).y1((d) => y(d[1])),
  )
</script>

<div bind:clientWidth={width}>
  <svg {width} {height} role="img">
    {#each series as s (s.key)}
      <path d={area(s)} fill={color(s.key)} opacity="0.9"><title>{s.key}</title></path>
    {/each}
    {#each y.ticks(5) as t}
      <text x={m.left - 6} y={y(t)} dy="0.32em" text-anchor="end">{d3.format('.0%')(t)}</text>
    {/each}
    {#each x.ticks(Math.max(2, Math.floor(width / 100))) as t}
      <text x={x(t)} y={height - m.bottom + 18} text-anchor="middle">{x.tickFormat()(t)}</text>
    {/each}
  </svg>
  <div class="legend">
    {#each labels as l}
      <span><i style:background={color(l)}></i>{l}</span>
    {/each}
  </div>
</div>
