import { AnimatePresence, motion } from "framer-motion";
import { lazy, Suspense, useEffect } from "react";
import { Navigation } from "./components/Navigation";
import { LoadingPanel } from "./components/Primitives";
import { useLabStore } from "./store/useLabStore";

const Overview = lazy(() => import("./components/Overview").then((module) => ({ default: module.Overview })));
const SearchLab = lazy(() => import("./components/SearchLab").then((module) => ({ default: module.SearchLab })));
const ComparisonLab = lazy(() => import("./components/ComparisonLab").then((module) => ({ default: module.ComparisonLab })));
const RLLab = lazy(() => import("./components/RLLab").then((module) => ({ default: module.RLLab })));

function App() {
  const view = useLabStore((state) => state.view);
  const regenerate = useLabStore((state) => state.regenerate);
  const isPlaying = useLabStore((state) => state.isPlaying);
  const playbackSpeed = useLabStore((state) => state.playbackSpeed);
  const tick = useLabStore((state) => state.tick);

  useEffect(() => {
    void regenerate();
  }, [regenerate]);

  useEffect(() => {
    if (!isPlaying) return undefined;
    const interval = window.setInterval(tick, Math.max(8, 1000 / playbackSpeed));
    return () => window.clearInterval(interval);
  }, [isPlaying, playbackSpeed, tick]);

  return (
    <div className="min-h-screen overflow-hidden bg-[#070a12] text-slate-200">
      <div className="site-aurora site-aurora-one" aria-hidden="true" />
      <div className="site-aurora site-aurora-two" aria-hidden="true" />
      <div className="site-grid" aria-hidden="true" />
      <Navigation />
      <main className="relative z-10 mx-auto max-w-[1480px] px-4 md:px-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={view}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.28, ease: [0.2, 0.8, 0.2, 1] }}
          >
            <Suspense fallback={<div className="py-16"><LoadingPanel label="Loading laboratory" /></div>}>
              {view === "overview" && <Overview />}
              {view === "search" && <SearchLab />}
              {view === "compare" && <ComparisonLab />}
              {view === "learning" && <RLLab />}
            </Suspense>
          </motion.div>
        </AnimatePresence>
      </main>
      <footer className="relative z-10 border-t border-white/[0.06] px-4 py-7 md:px-8">
        <div className="mx-auto grid max-w-[1480px] gap-3 text-[10px] uppercase tracking-[0.16em] text-slate-600 md:grid-cols-[1fr_auto_1fr] md:items-center">
          <span>CSAI 301 / Artificial Intelligence Project</span>
          <span className="footer-credit">Ammar Ahmed · Ahmed Sameh · Kareem Wael</span>
          <span className="md:text-right">Supervised by <strong>Dr Doaa</strong></span>
        </div>
      </footer>
    </div>
  );
}

export default App;
