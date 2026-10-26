<script lang="ts">
  import * as d3 from 'd3'

  type Item = { key: string; value: number }
  let { items, max = 1, format = d3.format('.2f'), selected = null, onselect }: {
    items: Item[]
    max?: number
    format?: (v: number) => string
    selected?: string | null
    onselect?: (key: string) => void
  } = $props()

  let width = $state(600)
  const row = 22
  const m = { top: 4, right: 56, bottom: 4, left: 300 }
  const height = $derived(m.top + m.bottom + items.length * row)
  // Negative values (e.g. downward trends) extend left of a zero line
  const min = $derived(Math.min(0, d3.min(items, (d) => d.value) ?? 0))
  const x = $derived(d3.scaleLinear([min, Math.max(max, 0)], [m.left, width - m.right]))
</script>

<div bind:clientWidth={width}>
  <svg {width} {height} role="group">
    {#if min < 0}
      <line class="grid" x1={x(0)} x2={x(0)} y1={m.top} y2={height - m.bottom} />
    {/if}
    {#each items as d, i (d.key)}
      <g
        transform="translate(0,{m.top + i * row})"
        class:selected={d.key === selected}
        class:clickable={!!onselect}
        onclick={() => onselect?.(d.key)}
        onkeydown={(e) => e.key === 'Enter' && onselect?.(d.key)}
        role="button"
        tabindex={onselect ? 0 : -1}
      >
        <text x={m.left - 8} y={row / 2} dy="0.32em" text-anchor="end">{d.key}</text>
        <rect
          class="bar"
          class:negative={d.value < 0}
          x={x(Math.min(0, d.value))}
          y="3"
          width={Math.abs(x(d.value) - x(0))}
          height={row - 6}
        />
        <text x={x(Math.max(0, d.value)) + 6} y={row / 2} dy="0.32em">{format(d.value)}</text>
      </g>
    {/each}
  </svg>
</div>
