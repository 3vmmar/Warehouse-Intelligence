import { useMemo } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useLabStore } from "../store/useLabStore";
import { ErrorBanner, LoadingPanel, MetricCard, NumberField, PrimaryButton, SectionHeading } from "./Primitives";
import { GridCanvas } from "./GridCanvas";

const ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT"];

export function RLLab() {
  const store = useLabStore();
  const result = store.qLearning;
  const startStateIndex = useMemo(() => {
    if (!result || !store.environment) return -1;
    return result.state_lookup.findIndex((state) => (
      state[0] === store.environment?.start[0]
      && state[1] === store.environment?.start[1]
      && state[2] === false
    ));
  }, [result, store.environment]);

  return (
    <div className="space-y-10 pb-24 pt-12">
      <SectionHeading
        eyebrow="Phase 02 / Reinforcement learning"
        title="Turn experience into policy."
        description="The robot learns the exact same pickup-and-delivery problem through tabular Q-learning. Tune the core hyperparameters, inspect learning progress, and compare midpoint Q-values with the final policy."
      />
      <ErrorBanner message={store.qError} />

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-5">
          <GridCanvas mode="policy" />
          {store.qLoading && <LoadingPanel label="Exploring, updating Q-values, and evaluating policy" />}
          {result && !store.qLoading && (
            <>
              <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
                <MetricCard label="Final success" value={`${(result.final_100_success_rate * 100).toFixed(0)}%`} detail="last 100 episodes" tone="green" />
                <MetricCard label="Policy cost" value={result.policy_cost?.toFixed(1) ?? "--"} detail={`${result.policy_actions?.length ?? 0} moves`} tone="cyan" />
                <MetricCard label="Training wins" value={`${result.training_successes}/${result.config.episodes}`} detail="completed missions" tone="violet" />
                <MetricCard label="Train time" value={`${result.training_runtime_ms.toFixed(0)} ms`} detail={result.evaluation_success ? "policy verified" : "evaluation incomplete"} tone="amber" />
              </div>

              <section className="glass-card p-5 md:p-7">
                <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
                  <div><span className="eyebrow">Learning evidence</span><h3 className="font-display mt-2 text-xl font-semibold text-white">Reward and success over time</h3></div>
                  <span className="proof-chip proof-yes">epsilon: {result.config.epsilon_start.toFixed(2)} to {result.config.epsilon_end.toFixed(2)}</span>
                </div>
                <div className="mt-7 h-[360px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={result.training_curve} margin={{ top: 8, right: 16, bottom: 8, left: 2 }}>
                      <CartesianGrid stroke="rgba(255,255,255,.055)" vertical={false} />
                      <XAxis dataKey="episode" tick={{ fill: "#667085", fontSize: 10 }} axisLine={false} tickLine={false} />
                      <YAxis yAxisId="reward" tick={{ fill: "#667085", fontSize: 10 }} axisLine={false} tickLine={false} width={52} />
                      <YAxis yAxisId="success" orientation="right" domain={[0, 1]} tickFormatter={(value) => `${Math.round(value * 100)}%`} tick={{ fill: "#667085", fontSize: 10 }} axisLine={false} tickLine={false} width={48} />
                      <Tooltip contentStyle={{ background: "#0b101b", border: "1px solid rgba(255,255,255,.1)", borderRadius: 12, fontSize: 11 }} />
                      <Legend wrapperStyle={{ fontSize: 11, paddingTop: 12 }} />
                      <Line yAxisId="reward" name="Average reward" type="monotone" dataKey="average_reward" stroke="#9d83ff" strokeWidth={2.4} dot={false} />
                      <Line yAxisId="success" name="Success rate" type="monotone" dataKey="success_rate" stroke="#50e3a4" strokeWidth={2.4} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </section>

              {startStateIndex >= 0 && (
                <section className="glass-card overflow-hidden">
                  <div className="border-b border-white/[0.06] p-5 md:p-7">
                    <span className="eyebrow">Required snapshots</span>
                    <h3 className="font-display mt-2 text-xl font-semibold text-white">Q-values at the initial state</h3>
                    <p className="mt-2 text-xs leading-5 text-slate-500">A concrete midpoint-to-final view of how action preferences changed at S before pickup.</p>
                  </div>
                  <div className="grid md:grid-cols-2">
                    <QSnapshot title={`Midpoint / episode ${result.midpoint_episode}`} values={result.q_values_midpoint[startStateIndex]} />
                    <QSnapshot title={`Final / episode ${result.config.episodes}`} values={result.q_values_final[startStateIndex]} final />
                  </div>
                </section>
              )}

              <section className="grid gap-4 md:grid-cols-2">
                <div className="glass-card p-6">
                  <span className="eyebrow">Reward design</span>
                  <div className="mt-5 space-y-3">
                    {Object.entries(result.reward_design).map(([key, value]) => (
                      <div key={key} className="reward-row"><span>{key.replaceAll("_", " ")}</span><strong>{value}</strong></div>
                    ))}
                  </div>
                </div>
                <div className="glass-card p-6">
                  <span className="eyebrow">Policy analysis</span>
                  <p className="mt-5 text-sm leading-7 text-slate-400">
                    The final greedy policy is evaluated without exploration. A successful path must visit pickup before delivery,
                    respects walls and weighted transitions, and is rendered over the learned state-value field above.
                  </p>
                  <div className="mt-5 flex flex-wrap gap-2">
                    <span className={`proof-chip ${result.evaluation_success ? "proof-yes" : "proof-no"}`}>{result.evaluation_success ? "Policy reaches goal" : "Policy incomplete"}</span>
                    <span className="proof-chip proof-yes">Shared MDP</span>
                    <span className="proof-chip proof-yes">No eval exploration</span>
                  </div>
                </div>
              </section>
            </>
          )}
        </div>

        <aside className="space-y-4">
          <div className="control-card">
            <div className="control-title"><span>01</span> Learning setup</div>
            <div className="space-y-2">
              <NumberField label="Episodes" value={store.episodes} min={300} max={5000} step={100} onChange={(episodes) => store.setLearningParams({ episodes })} />
              <NumberField label="Learning rate / alpha" value={store.learningRate} min={0.01} max={1} step={0.01} onChange={(learningRate) => store.setLearningParams({ learningRate })} />
              <NumberField label="Discount / gamma" value={store.discountFactor} min={0.1} max={0.999} step={0.01} onChange={(discountFactor) => store.setLearningParams({ discountFactor })} />
            </div>
            <div className="mt-4 space-y-2 rounded-2xl border border-white/[0.06] bg-black/20 p-4 font-mono text-[10px] text-slate-500">
              <div className="flex justify-between"><span>EXPLORATION</span><strong className="text-slate-300">epsilon-greedy</strong></div>
              <div className="flex justify-between"><span>EPSILON</span><strong className="text-slate-300">1.00 to 0.04</strong></div>
              <div className="flex justify-between"><span>MAX STEPS</span><strong className="text-slate-300">420 / episode</strong></div>
              <div className="flex justify-between"><span>STATE SPACE</span><strong className="text-slate-300">{store.environment?.state_space_size.toLocaleString() ?? "--"}</strong></div>
            </div>
            <PrimaryButton onClick={store.trainAgent} disabled={!store.environment || store.qLoading} className="mt-4 w-full">
              {store.qLoading ? <><span className="button-spinner" /> Training agent</> : <>Train Q-learning <span aria-hidden="true">&#8599;</span></>}
            </PrimaryButton>
          </div>

          <div className="control-card">
            <div className="control-title"><span>02</span> Bellman update</div>
            <div className="formula-card">
              <span>Q(s,a)</span>
              <strong>+= alpha [r + gamma max Q(s',a') - Q(s,a)]</strong>
            </div>
            <p className="mt-4 text-xs leading-6 text-slate-500">Alpha controls adaptation speed. Gamma values future reward. Decaying epsilon shifts the agent from broad exploration toward exploitation.</p>
          </div>
        </aside>
      </div>
    </div>
  );
}

function QSnapshot({ title, values, final = false }: { title: string; values: number[]; final?: boolean }) {
  const best = Math.max(...values);
  return (
    <div className={`q-snapshot ${final ? "q-snapshot-final" : ""}`}>
      <p>{title}</p>
      <div className="mt-4 grid grid-cols-2 gap-2">
        {ACTIONS.map((action, index) => (
          <div key={action} className={`q-action ${values[index] === best ? "best" : ""}`}>
            <span>{action}</span><strong>{values[index].toFixed(3)}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}
