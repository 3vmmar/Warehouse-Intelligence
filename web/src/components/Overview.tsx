import { motion } from "framer-motion";
import { ALGORITHMS, FAMILY_LABELS } from "../data/algorithms";
import { useLabStore } from "../store/useLabStore";
import { GlassCard, SectionHeading } from "./Primitives";

export function Overview() {
  const setView = useLabStore((state) => state.setView);
  const setAlgorithm = useLabStore((state) => state.setAlgorithm);
  const environment = useLabStore((state) => state.environment);

  return (
    <div className="space-y-28 pb-24">
      <section className="relative grid min-h-[640px] items-center gap-12 overflow-hidden py-16 lg:grid-cols-[1.05fr_0.95fr] lg:py-24">
        <div className="relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-7 inline-flex items-center gap-2 rounded-full border border-emerald-300/20 bg-emerald-300/[0.07] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-emerald-200"
          >
            <span className="status-dot status-live" /> Integrated system operational
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08, duration: 0.7 }}
            className="font-display max-w-4xl text-5xl font-semibold leading-[0.96] tracking-[-0.065em] text-white sm:text-7xl xl:text-[88px]"
          >
            One warehouse.
            <span className="hero-gradient block">Every search paradigm.</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.18, duration: 0.6 }}
            className="mt-7 max-w-2xl text-base leading-8 text-slate-400 md:text-lg"
          >
            A complete artificial intelligence laboratory: nine algorithm families and configurations,
            two admissible heuristics, weighted terrain, reproducible experiments, and a Q-learning agent
            that learns the same pickup-to-delivery mission.
          </motion.p>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.28 }}
            className="mt-9 flex flex-wrap gap-3"
          >
            <button onClick={() => setView("search")} className="primary-button px-6">Enter search lab <span>↗</span></button>
            <button onClick={() => setView("learning")} className="secondary-button px-6">Train the agent <span>→</span></button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.36, duration: 0.55 }}
            className="team-credit"
            aria-label="Project authors and supervisor"
          >
            <span className="team-credit-label">Made by</span>
            <div className="team-credit-names">
              <strong>Ammar Ahmed</strong>
              <i aria-hidden="true" />
              <strong>Ahmed Sameh</strong>
              <i aria-hidden="true" />
              <strong>Kareem Wael</strong>
            </div>
            <p>Under the supervision of <strong>Dr Doaa</strong></p>
          </motion.div>

          <div className="mt-8 grid max-w-2xl grid-cols-2 gap-px overflow-hidden rounded-2xl border border-white/[0.07] bg-white/[0.07] sm:grid-cols-4">
            {[
              ["11", "evaluated configurations"],
              ["02", "admissible heuristics"],
              [environment?.state_space_size.toLocaleString() ?? "1K+", "modeled states"],
              ["01", "integrated AI system"],
            ].map(([value, label]) => (
              <div key={label} className="bg-[#0b0f19] px-4 py-4">
                <div className="font-mono text-xl font-semibold text-white">{value}</div>
                <div className="mt-1 text-[9px] uppercase leading-4 tracking-[0.14em] text-slate-600">{label}</div>
              </div>
            ))}
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0, scale: 0.92 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.9, delay: 0.15 }}
          className="relative mx-auto aspect-square w-full max-w-[620px]"
        >
          <div className="hero-orbit hero-orbit-outer" />
          <div className="hero-orbit hero-orbit-middle" />
          <div className="hero-orbit hero-orbit-inner" />
          <div className="hero-beam" />
          <div className="hero-core">
            <span>AI</span>
            <small>LAB</small>
          </div>
          {ALGORITHMS.slice(0, 8).map((algorithm, index) => (
            <motion.div
              key={algorithm.id}
              animate={{ y: [0, -6, 0] }}
              transition={{ duration: 3.2 + index * 0.25, repeat: Infinity, ease: "easeInOut" }}
              className={`orbit-node orbit-node-${index + 1}`}
            >
              {algorithm.short}
            </motion.div>
          ))}
        </motion.div>
      </section>

      <section className="space-y-10">
        <SectionHeading
          eyebrow="Integrated architecture"
          title="One system. One consistent world model."
          description="The same state, action, transition, and cost definitions flow through planning, optimization, and reinforcement learning as one coherent intelligent system."
        />
        <div className="grid gap-5 lg:grid-cols-2">
          <GlassCard className="group overflow-hidden p-7 md:p-9">
            <div className="system-card-accent search-accent" />
            <div className="relative">
              <div className="flex items-start justify-between gap-4">
                <div><span className="eyebrow">Search engine / Planning</span><h3 className="mt-3 font-display text-3xl font-semibold tracking-tight text-white">Search and optimization</h3></div>
                <span className="score-chip">11 configs</span>
              </div>
              <p className="mt-5 max-w-xl text-sm leading-7 text-slate-400">Uninformed, informed, and local search compete on the same weighted warehouse. Every run exposes path quality, work, memory, runtime, completeness, and optimality.</p>
              <button onClick={() => setView("search")} className="text-link mt-7">Explore search lab <span>→</span></button>
            </div>
          </GlassCard>
          <GlassCard className="group overflow-hidden p-7 md:p-9" delay={0.08}>
            <div className="system-card-accent learning-accent" />
            <div className="relative">
              <div className="flex items-start justify-between gap-4">
                <div><span className="eyebrow">Learning engine / Adaptation</span><h3 className="mt-3 font-display text-3xl font-semibold tracking-tight text-white">Reinforcement learning</h3></div>
                <span className="score-chip score-green">Q-policy</span>
              </div>
              <p className="mt-5 max-w-xl text-sm leading-7 text-slate-400">Tabular Q-learning learns a pickup-and-delivery policy using explicit α, γ, ε-decay, midpoint/final Q snapshots, reward analysis, and a measurable final policy.</p>
              <button onClick={() => setView("learning")} className="text-link mt-7 text-emerald-300">Explore learning lab <span>→</span></button>
            </div>
          </GlassCard>
        </div>
      </section>

      <section className="space-y-10">
        <SectionHeading
          eyebrow="Algorithm deck"
          title="Every method earns its place."
          description="Select any card to open it inside the live search laboratory. The implementation stays deliberately explicit so every trade-off can be defended orally."
        />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {ALGORITHMS.map((algorithm, index) => (
            <motion.button
              key={algorithm.id}
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ delay: (index % 3) * 0.05 }}
              whileHover={{ y: -5 }}
              onClick={() => { setAlgorithm(algorithm.id); setView("search"); }}
              className={`algorithm-card family-${algorithm.family}`}
            >
              <div className="flex items-start justify-between gap-3">
                <span className="algorithm-code">{algorithm.short}</span>
                <span className="algorithm-badge">{algorithm.badge}</span>
              </div>
              <h3>{algorithm.name}</h3>
              <p>{algorithm.description}</p>
              <div className="mt-5 flex items-center justify-between text-[10px] uppercase tracking-[0.16em] text-slate-600">
                <span>{FAMILY_LABELS[algorithm.family]}</span><span>Open ↗</span>
              </div>
            </motion.button>
          ))}
        </div>
      </section>

      <section className="space-y-10">
        <SectionHeading
          eyebrow="Full-mark readiness"
          title="Built around the rubric, not around a demo."
          description="The system pairs implementation evidence with the analysis artifacts required for grading and oral discussion."
        />
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[
            ["01", "Modeled rigor", "1K–10K states, explicit assumptions, weighted transitions, reproducible seeds."],
            ["02", "Fair experiments", "Eleven configurations, shared worlds, stochastic repeats, CSV and JSON exports."],
            ["03", "Visual evidence", "Search playback, evolving local candidates, comparison charts, learned policy."],
            ["04", "Defensible theory", "Complexity, completeness, optimality, reward design, and oral-defense guide."],
          ].map(([number, title, description], index) => (
            <GlassCard key={number} delay={index * 0.05} className="p-6">
              <span className="font-mono text-xs text-cyan-300/60">/{number}</span>
              <h3 className="mt-7 font-display text-xl font-semibold text-white">{title}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-500">{description}</p>
            </GlassCard>
          ))}
        </div>
      </section>
    </div>
  );
}
