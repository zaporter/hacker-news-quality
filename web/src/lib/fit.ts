import * as d3 from 'd3'

export type Point = { x: Date; y: number; n: number }

/** Ordinary least squares of y on time. `relPerYear` is the yearly slope as a fraction of the mean of y. */
export function fitLine(ps: Point[]) {
  if (ps.length < 2) return null
  const xs = ps.map((p) => +p.x)
  const ys = ps.map((p) => p.y)
  const mx = d3.mean(xs)!
  const my = d3.mean(ys)!
  const slope = d3.sum(xs, (v, i) => (v - mx) * (ys[i] - my)) / d3.sum(xs, (v) => (v - mx) ** 2)
  const at = (t: number) => my + slope * (t - mx)
  const r2 = 1 - d3.sum(xs, (v, i) => (ys[i] - at(v)) ** 2) / d3.sum(ys, (v) => (v - my) ** 2)
  const perYear = slope * 365.25 * 864e5
  const [x0, x1] = [xs[0], xs.at(-1)!]
  return { perYear, relPerYear: my ? perYear / my : 0, mean: my, r2, x0, x1, y0: at(x0), y1: at(x1) }
}

export const formatRel = d3.format('+.1%')
