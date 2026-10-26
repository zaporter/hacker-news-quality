<script lang="ts">
  import * as d3 from 'd3'

  let { values, domain, bins: nBins = 20 }: { values: number[]; domain: [number, number]; bins?: number } = $props()

  let width = $state(600)
  const height = 220
  const m = { top: 12, right: 16, bottom: 28, left: 44 }

  const bins = $derived(d3.bin().domain(domain).thresholds(d3.ticks(domain[0], domain[1], nBins))(values))
  const x = $derived(d3.scaleLinear(domain, [m.left, width - m.right]))
  const y = $derived(d3.scaleLinear([0, d3.max(bins, (b) => b.length) ?? 1], [height - m.bottom, m.top]).nice())
</script>

<div bind:clientWidth={width}>
  <svg {width} {height} role="img">
    {#each y.ticks(4) as t}
      <line class="grid" x1={m.left} x2={width - m.right} y1={y(t)} y2={y(t)} />
      <text x={m.left - 6} y={y(t)} dy="0.32em" text-anchor="end">{t}</text>
    {/each}
    {#each bins as b}
      <rect
        class="bar"
        x={x(b.x0!) + 1}
        width={Math.max(0, x(b.x1!) - x(b.x0!) - 2)}
        y={y(b.length)}
        height={y(0) - y(b.length)}
      ><title>{b.x0}–{b.x1}: {b.length}</title></rect>
    {/each}
    {#each x.ticks(Math.max(2, Math.floor(width / 80))) as t}
      <text x={x(t)} y={height - m.bottom + 18} text-anchor="middle">{t}</text>
    {/each}
  </svg>
</div>
