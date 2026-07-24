import { motion } from "framer-motion";
import { useLabStore } from "../store/useLabStore";
import type { View } from "../lib/types";

const NAV: Array<{ id: View; label: string; meta: string }> = [
  { id: "overview", label: "Overview", meta: "00" },
  { id: "search", label: "Search Lab", meta: "01" },
  { id: "compare", label: "Compare", meta: "02" },
  { id: "learning", label: "Q-Learning", meta: "03" },
];

export function Navigation() {
  const view = useLabStore((state) => state.view);
  const setView = useLabStore((state) => state.setView);
  const environment = useLabStore((state) => state.environment);
  const loading = useLabStore((state) => state.environmentLoading);

  return (
    <header className="sticky top-0 z-50 border-b border-white/[0.06] bg-[#070a12]/80 backdrop-blur-2xl">
      <div className="mx-auto flex max-w-[1480px] items-center gap-5 px-4 py-3 md:px-8">
        <button onClick={() => setView("overview")} className="group flex shrink-0 items-center gap-3 text-left">
          <span className="brand-mark"><i /><b /></span>
          <span>
            <strong className="font-display block text-sm tracking-tight text-white">Warehouse Intelligence</strong>
            <small className="block text-[9px] uppercase tracking-[0.22em] text-slate-500">CSAI 301 / Summer 2026</small>
          </span>
        </button>

        <nav className="no-scrollbar mx-auto flex min-w-0 items-center gap-1 overflow-x-auto rounded-full border border-white/[0.07] bg-white/[0.025] p-1">
          {NAV.map((item) => (
            <button
              key={item.id}
              onClick={() => setView(item.id)}
              className={`relative whitespace-nowrap rounded-full px-3 py-2 text-xs transition-colors md:px-4 ${
                view === item.id ? "text-white" : "text-slate-500 hover:text-slate-300"
              }`}
            >
              {view === item.id && (
                <motion.span
                  layoutId="active-navigation"
                  className="absolute inset-0 rounded-full border border-cyan-300/15 bg-cyan-300/[0.08]"
                  transition={{ type: "spring", stiffness: 420, damping: 34 }}
                />
              )}
              <span className="relative"><em className="mr-1.5 hidden font-mono text-[8px] not-italic text-cyan-300/60 sm:inline">{item.meta}</em>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="hidden shrink-0 items-center gap-2 text-[10px] uppercase tracking-[0.16em] text-slate-500 lg:flex">
          <span className={`status-dot ${loading ? "status-loading" : environment ? "status-live" : ""}`} />
          {loading ? "Generating" : environment ? `${environment.state_space_size.toLocaleString()} states` : "Offline"}
        </div>
      </div>
    </header>
  );
}

