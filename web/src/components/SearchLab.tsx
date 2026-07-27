import { motion } from "framer-motion";
import { useMemo } from "react";
import { ALGORITHMS, FAMILY_LABELS } from "../data/algorithms";
import { useLabStore } from "../store/useLabStore";
import { ErrorBanner, MetricCard, NumberField, PrimaryButton, SectionHeading } from "./Primitives";
import { GridCanvas } from "./GridCanvas";

export function SearchLab() {
  const store = useLabStore();
  const selected = ALGORITHMS.find((item) => item.id === store.algorithm)!;
  const needsHeuristic = store.algorithm === "greedy" || store.algorithm === "astar";
  const result = store.searchResult;
  const work = result?.family === "local" ? result.metrics.evaluations : result?.metrics.nodes_expanded;
  const fullyPlayed = result ? store.playbackStep >= result.events.length : false;
  const visibleWork = useMemo(() => {
    if (!result) return 0;
    if (fullyPlayed || result.family === "local") return work ?? 0;
    return result.events.slice(0, store.playbackStep).filter((event) => event.kind === "expand").length;
  }, [fullyPlayed, result, store.playbackStep, work]);

  return (
    <div className="space-y-10 pb-24 pt-12">
      <SectionHeading
        eyebrow="Search engine / Interactive laboratory"
        title="Watch intelligence search."
        description="Generate a rubric-compliant weighted warehouse, select any required algorithm, replay its reasoning, and inspect empirical metrics beside theoretical guarantees."
      />

      <ErrorBanner message={store.environmentError} />
      <ErrorBanner message={store.searchError} />

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-5">
          <GridCanvas />
          {result && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
              <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
                <MetricCard label={result.family === "local" ? "Evaluations" : "Nodes expanded"} value={visibleWork.toLocaleString()} detail={result.family === "local" ? "candidate solutions" : `${result.metrics.nodes_generated.toLocaleString()} generated`} tone="violet" />
                <MetricCard label="Path cost" value={result.metrics.path_cost?.toFixed(1) ?? "—"} detail={`${result.metrics.path_length ?? 0} moves`} tone="cyan" />
                <MetricCard label="Memory units" value={result.metrics.memory_units.toLocaleString()} detail={result.family === "local" ? "encoded actions" : "peak frontier proxy"} tone="amber" />
                <MetricCard label="Runtime" value={`${result.metrics.runtime_ms.toFixed(1)} ms`} detail={result.metrics.solution_found ? "solution verified" : "no solution"} tone="green" />
              </div>

              <div className="glass-card grid gap-6 p-6 lg:grid-cols-[1fr_auto]">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`proof-chip ${result.guarantees.complete ? "proof-yes" : "proof-no"}`}>{result.guarantees.complete ? "✓ Complete" : "○ Not complete"}</span>
                    <span className={`proof-chip ${result.guarantees.optimal ? "proof-yes" : "proof-no"}`}>{result.guarantees.optimal ? "✓ Cost optimal" : "○ Not cost optimal"}</span>
                    {result.events_truncated && <span className="proof-chip">Trace safely sampled</span>}
                  </div>
                  <p className="mt-4 text-sm leading-6 text-slate-400">{result.guarantees.optimality_scope}</p>
                  <div className="mt-4 grid gap-2 font-mono text-[10px] text-slate-500 sm:grid-cols-2">
                    <span>TIME / {result.guarantees.time_complexity}</span>
                    <span>SPACE / {result.guarantees.space_complexity}</span>
                  </div>
                </div>
                <div className="min-w-56">
                  <div className="flex items-center gap-2">
                    <button onClick={store.isPlaying ? store.pause : store.play} className="play-button" aria-label={store.isPlaying ? "Pause playback" : "Play playback"}>{store.isPlaying ? "Ⅱ" : "▶"}</button>
                    <input className="range-control flex-1" type="range" min={0} max={result.events.length} value={store.playbackStep} onChange={(event) => store.setPlaybackStep(Number(event.target.value))} aria-label="Playback position" />
                  </div>
                  <label className="mt-3 flex items-center gap-2 text-[10px] uppercase tracking-[0.16em] text-slate-600">Speed<input className="range-control flex-1" type="range" min={10} max={400} value={store.playbackSpeed} onChange={(event) => store.setPlaybackSpeed(Number(event.target.value))} /><span className="w-12 text-right font-mono">{store.playbackSpeed}/s</span></label>
                </div>
              </div>
            </motion.div>
          )}
        </div>

        <aside className="space-y-4">
          <div className="control-card">
            <div className="control-title"><span>01</span> Environment</div>
            <div className="grid grid-cols-2 gap-2">
              <NumberField label="Rows" value={store.rows} min={26} max={60} onChange={(rows) => store.setEnvironmentParams({ rows })} />
              <NumberField label="Columns" value={store.cols} min={26} max={60} onChange={(cols) => store.setEnvironmentParams({ cols })} />
              <NumberField label="Obstacles" value={store.obstacleRatio} min={0.05} max={0.45} step={0.01} onChange={(obstacleRatio) => store.setEnvironmentParams({ obstacleRatio })} />
              <NumberField label="Seed" value={store.seed} min={0} max={99999} onChange={(seed) => store.setEnvironmentParams({ seed })} />
            </div>
            <div className={`target-meter ${store.environment && store.environment.state_space_size >= 1000 ? "target-valid" : ""}`}>
              <span>Assignment target</span><strong>{store.environment?.state_space_size.toLocaleString() ?? "—"} / 1K–10K</strong>
            </div>
            <button onClick={store.regenerate} disabled={store.environmentLoading} className="secondary-button w-full">{store.environmentLoading ? "Synthesizing…" : "Regenerate warehouse"}</button>
          </div>

          <div className="control-card">
            <div className="control-title"><span>02</span> Algorithm</div>
            <div className="space-y-4">
              {(["uninformed", "informed", "local"] as const).map((family) => (
                <div key={family}>
                  <div className={`family-label family-text-${family}`}>{FAMILY_LABELS[family]}</div>
                  <div className="mt-2 grid grid-cols-2 gap-1.5">
                    {ALGORITHMS.filter((item) => item.family === family).map((item) => (
                      <button key={item.id} onClick={() => store.setAlgorithm(item.id)} className={`algorithm-option ${store.algorithm === item.id ? "algorithm-option-active" : ""}`}>
                        <span>{item.short}</span><small>{item.name.replace("Search", "").replace("Algorithm", "")}</small>
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {needsHeuristic && (
              <div className="mt-4 grid grid-cols-2 gap-2 rounded-xl border border-white/[0.06] bg-black/20 p-1.5">
                {(["manhattan", "euclidean"] as const).map((heuristic) => (
                  <button key={heuristic} onClick={() => store.setHeuristic(heuristic)} className={`heuristic-option ${store.heuristic === heuristic ? "heuristic-active" : ""}`}>{heuristic}</button>
                ))}
              </div>
            )}
            <div className="mt-4 rounded-xl border border-white/[0.06] bg-white/[0.025] p-3">
              <div className="flex items-center justify-between"><strong className="text-xs text-white">{selected.name}</strong><span className="algorithm-badge">{selected.badge}</span></div>
              <p className="mt-2 text-xs leading-5 text-slate-500">{selected.description}</p>
            </div>
            <PrimaryButton onClick={store.runSearch} disabled={!store.environment || store.searchLoading} className="mt-4 w-full">
              {store.searchLoading ? <><span className="button-spinner" /> Solving mission</> : <>Run {selected.short} <span>↗</span></>}
            </PrimaryButton>
          </div>
        </aside>
      </div>
    </div>
  );
}
