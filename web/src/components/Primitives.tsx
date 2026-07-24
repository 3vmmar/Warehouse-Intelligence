import { motion } from "framer-motion";
import type { ReactNode } from "react";

export function SectionHeading({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <div className="max-w-3xl space-y-3">
      <div className="eyebrow">{eyebrow}</div>
      <h2 className="font-display text-3xl font-semibold tracking-[-0.04em] text-white md:text-5xl">
        {title}
      </h2>
      <p className="max-w-2xl text-sm leading-7 text-slate-400 md:text-base">{description}</p>
    </div>
  );
}

export function GlassCard({
  children,
  className = "",
  delay = 0,
}: {
  children: ReactNode;
  className?: string;
  delay?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay, ease: [0.2, 0.8, 0.2, 1] }}
      className={`glass-card ${className}`}
    >
      {children}
    </motion.div>
  );
}

export function MetricCard({
  label,
  value,
  detail,
  tone = "cyan",
}: {
  label: string;
  value: string | number;
  detail?: string;
  tone?: "cyan" | "violet" | "green" | "amber";
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      className="metric-card"
    >
      <div className={`metric-glow metric-${tone}`} />
      <div className="relative">
        <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">{label}</p>
        <p className="mt-2 font-mono text-2xl font-semibold tracking-tight text-white">{value}</p>
        {detail && <p className="mt-1 text-xs text-slate-500">{detail}</p>}
      </div>
    </motion.div>
  );
}

export function ErrorBanner({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <div role="alert" className="rounded-2xl border border-rose-400/25 bg-rose-400/8 px-4 py-3 text-sm text-rose-200">
      <span className="mr-2">●</span>
      {message}
    </div>
  );
}

export function LoadingPanel({ label }: { label: string }) {
  return (
    <div className="flex min-h-56 flex-col items-center justify-center gap-4 rounded-3xl border border-white/8 bg-white/[0.025]">
      <div className="loader-orbit"><span /></div>
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">{label}</p>
    </div>
  );
}

export function NumberField({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step?: number;
}) {
  return (
    <label className="field-shell">
      <span>{label}</span>
      <input
        type="number"
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}

export function PrimaryButton({
  children,
  onClick,
  disabled = false,
  className = "",
}: {
  children: ReactNode;
  onClick: () => void;
  disabled?: boolean;
  className?: string;
}) {
  return (
    <motion.button
      whileHover={disabled ? undefined : { y: -2, scale: 1.01 }}
      whileTap={disabled ? undefined : { scale: 0.98 }}
      onClick={onClick}
      disabled={disabled}
      className={`primary-button ${className}`}
    >
      {children}
    </motion.button>
  );
}

