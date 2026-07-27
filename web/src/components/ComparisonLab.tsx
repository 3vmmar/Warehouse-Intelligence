import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ComparisonRow } from "../lib/types";
import { useLabStore } from "../store/useLabStore";
import { ErrorBanner, LoadingPanel, MetricCard, PrimaryButton, SectionHeading } from "./Primitives";

type Metric = "mean_path_cost" | "mean_runtime_ms" | "mean_work_units" | "mean_memory_units";

const METRICS: Array<{ id: Metric; label: string; unit: string }> = [
  { id: "mean_path_cost", label: "Path cost", unit: "cost units" },
  { id: "mean_runtime_ms", label: "Runtime", unit: "milliseconds" },
  { id: "mean_work_units", label: "Search work", unit: "nodes / evaluations" },
  { id: "mean_memory_units", label: "Memory", unit: "memory units" },
];

const FAMILY_COLORS: Record<string, string> = {
  uninformed: "#54e7ff",
  informed: "#9d83ff",
  local: "#ffb866",
};

export function ComparisonLab() {
  const environment = useLabStore((state) => state.environment);
  const comparison = useLabStore((state) => state.comparison);
  const loading = useLabStore((state) => state.comparisonLoading);
  const error = useLabStore((state) => state.comparisonError);
  const runComparison = useLabStore((state) => state.runComparison);
  const [metric, setMetric] = useState<Metric>("mean_path_cost");

  const chartData = useMemo(() => (
    comparison?.summary
      .filter((row) => row[metric] !== null)
      .map((row) => ({ ...row, value: row[metric] as number })) ?? []
  ), [comparison, metric]);

  const best = useMemo(() => {
    if (!comparison) return null;
    const successful = comparison.summary.filter((row) => row.mean_path_cost !== null);
    return successful.reduce<ComparisonRow | null>((winner, row) => (
      !winner || (row.mean_path_cost ?? Infinity) < (winner.mean_path_cost ?? Infinity) ? row : winner
    ), null);
  }, [comparison]);

  const leanest = useMemo(() => {
    if (!comparison) return null;
    return comparison.summary.reduce<ComparisonRow | null>((winner, row) => (
      !winner || row.mean_memory_units < winner.mean_memory_units ? row : winner
    ), null);
  }, [comparison]);

  return (
    <div className="space-y-10 pb-24 pt-12">
      <SectionHeading
        eyebrow="Evaluation / Controlled experiment"
        title="Compare evidence, not impressions."
        description="All eleven required configurations solve the same warehouse. The table separates measured behavior from theoretical guarantees so the conclusions stay fair and defensible."
      />

      <ErrorBanner message={error} />

      {!comparison && !loading && (
        <section className="comparison-launch glass-card">
          <div className="comparison-rings" aria-hidden="true"><i /><i /><i /></div>
          <div className="relative z-10 max-w-2xl">
            <span className="eyebrow">Shared-world benchmark</span>
            <h3 className="font-display mt-4 text-3xl font-semibold tracking-tight text-white md:text-5xl">
              Eleven configurations.<br />One honest scoreboard.
            </h3>
            <p className="mt-5 max-w-xl text-sm leading-7 text-slate-400">
              BFS, DFS, UCS, IDS, Greedy and A* with both heuristics, plus all three local methods. Runtime, work,
              memory, path quality, success, completeness, and optimality are captured together.
            </p>
            <div className="mt-6 flex flex-wrap gap-2">
              {["Same environment", "Fixed seed", "Weighted costs", "Theory + metrics"].map((label) => (
                <span key={label} className="proof-chip proof-yes">{label}</span>
              ))}
            </div>
            <PrimaryButton onClick={runComparison} disabled={!environment} className="mt-8 px-7">
              Run complete benchmark <span aria-hidden="true">&#8599;</span>
            </PrimaryButton>
          </div>
        </section>
      )}

      {loading && <LoadingPanel label="Running eleven algorithm configurations" />}

      {comparison && !loading && (
        <div className="space-y-5">
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
            <MetricCard label="Configurations" value={comparison.summary.length} detail="all assignment methods" tone="violet" />
            <MetricCard label="Modeled states" value={comparison.state_space_size.toLocaleString()} detail="within 1K-10K target" tone="cyan" />
            <MetricCard label="Lowest cost" value={best?.mean_path_cost?.toFixed(1) ?? "--"} detail={best?.display_name ?? "no successful run"} tone="green" />
            <MetricCard label="Leanest memory" value={Math.round(leanest?.mean_memory_units ?? 0).toLocaleString()} detail={`${leanest?.display_name ?? "no result"} / units`} tone="amber" />
            <MetricCard label="Successful" value={`${comparison.summary.filter((row) => row.success_rate > 0).length}/${comparison.summary.length}`} detail="configurations finding a route" tone="amber" />
          </div>

          <section className="glass-card overflow-hidden p-5 md:p-7">
            <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <span className="eyebrow">Empirical profile</span>
                <h3 className="font-display mt-2 text-xl font-semibold text-white">Algorithm performance</h3>
              </div>
              <div className="metric-tabs">
                {METRICS.map((item) => (
                  <button key={item.id} onClick={() => setMetric(item.id)} className={metric === item.id ? "active" : ""}>
                    {item.label}
                  </button>
                ))}
              </div>
            </div>
            <div className="mt-7 h-[390px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 12, right: 8, bottom: 50, left: 2 }}>
                  <CartesianGrid stroke="rgba(255,255,255,.055)" vertical={false} />
                  <XAxis dataKey="algorithm" angle={-35} textAnchor="end" interval={0} tick={{ fill: "#788399", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#667085", fontSize: 10 }} axisLine={false} tickLine={false} width={55} />
                  <Tooltip content={<ChartTooltip label={METRICS.find((item) => item.id === metric)!.label} unit={METRICS.find((item) => item.id === metric)!.unit} />} cursor={{ fill: "rgba(255,255,255,.025)" }} />
                  <Bar dataKey="value" radius={[6, 6, 1, 1]} maxBarSize={44}>
                    {chartData.map((row) => <Cell key={row.algorithm} fill={FAMILY_COLORS[row.family] ?? "#54e7ff"} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="memory-method-note">
              <span>Memory methodology</span>
              <p>Graph search reports peak frontier states; local search reports encoded action slots retained by its active trajectory or population. These deterministic implementation units support fair within-family comparisons without pretending to be operating-system byte measurements.</p>
            </div>
          </section>

          <section className="glass-card overflow-hidden">
            <div className="flex flex-col gap-2 border-b border-white/[0.06] p-5 md:flex-row md:items-end md:justify-between md:p-7">
              <div><span className="eyebrow">Decision matrix</span><h3 className="font-display mt-2 text-xl font-semibold text-white">Measured and theoretical results</h3></div>
              <p className="text-xs text-slate-600">Lower cost, runtime, work, and memory are better.</p>
            </div>
            <div className="overflow-x-auto">
              <table className="results-table">
                <thead><tr><th>Configuration</th><th>Family</th><th>Success</th><th>Cost</th><th>Runtime</th><th>Work</th><th>Memory</th><th>Complete</th><th>Optimal</th></tr></thead>
                <tbody>
                  {comparison.summary.map((row) => (
                    <tr key={row.algorithm}>
                      <td><strong>{row.display_name}</strong><small>{row.algorithm}</small></td>
                      <td><span className={`family-pill family-pill-${row.family}`}>{row.family}</span></td>
                      <td>{(row.success_rate * 100).toFixed(0)}%</td>
                      <td>{row.mean_path_cost?.toFixed(1) ?? "--"}</td>
                      <td>{row.mean_runtime_ms.toFixed(1)} ms</td>
                      <td>{Math.round(row.mean_work_units).toLocaleString()}</td>
                      <td>{Math.round(row.mean_memory_units).toLocaleString()}</td>
                      <td><TheoryMark value={row.theoretically_complete} /></td>
                      <td><TheoryMark value={row.theoretically_optimal} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="flex flex-wrap items-center justify-between gap-3 border-t border-white/[0.06] px-5 py-4 md:px-7">
              <p className="text-xs text-slate-500">Optimality labels apply under each algorithm's stated assumptions.</p>
              <button onClick={runComparison} className="text-link">Re-run benchmark <span aria-hidden="true">&#8635;</span></button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

function TheoryMark({ value }: { value: boolean }) {
  return <span className={`theory-mark ${value ? "yes" : "no"}`}>{value ? "YES" : "NO"}</span>;
}

function ChartTooltip({ active, payload, label, unit }: { active?: boolean; payload?: Array<{ value: number; payload: ComparisonRow }>; label: string; unit: string }) {
  if (!active || !payload?.length) return null;
  const point = payload[0];
  return (
    <div className="chart-tooltip">
      <strong>{point.payload.display_name}</strong>
      <span>{label}: {point.value.toLocaleString(undefined, { maximumFractionDigits: 2 })} {unit}</span>
    </div>
  );
}
