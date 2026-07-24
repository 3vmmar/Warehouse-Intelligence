import { useCallback, useEffect, useMemo, useRef } from "react";
import { useLabStore } from "../store/useLabStore";
import type { Cell, StateTuple } from "../lib/types";

const COLORS = {
  background: "#070a12",
  free: "#111827",
  terrain2: "#24213a",
  terrain4: "#43301f",
  wall: "#30394b",
  grid: "rgba(255,255,255,.055)",
  explored: "#6d4aff",
  current: "#54e7ff",
  path: "#8c7bff",
  localPath: "#ffb866",
  policy: "#50e3a4",
  start: "#54e7ff",
  pickup: "#ffbd59",
  delivery: "#50e3a4",
};

export function GridCanvas({ mode = "search" }: { mode?: "search" | "policy" }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const environment = useLabStore((state) => state.environment);
  const result = useLabStore((state) => state.searchResult);
  const step = useLabStore((state) => state.playbackStep);
  const qLearning = useLabStore((state) => state.qLearning);

  const policyIndex = useMemo(() => {
    if (!qLearning) return new Map<string, number>();
    return new Map(qLearning.state_lookup.map((state, index) => [state.join(":"), index]));
  }, [qLearning]);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container || !environment) return;
    const context = canvas.getContext("2d");
    if (!context) return;

    const width = container.clientWidth;
    const height = Math.max(420, Math.min(760, width * 0.82));
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    context.setTransform(dpr, 0, 0, dpr, 0, 0);

    const cell = Math.min((width - 28) / environment.cols, (height - 28) / environment.rows);
    const gridWidth = cell * environment.cols;
    const gridHeight = cell * environment.rows;
    const offsetX = (width - gridWidth) / 2;
    const offsetY = (height - gridHeight) / 2;
    context.fillStyle = COLORS.background;
    context.fillRect(0, 0, width, height);

    const qRange = mode === "policy" && qLearning
      ? getQRange(qLearning.q_values_final, environment, policyIndex)
      : null;

    for (let row = 0; row < environment.rows; row += 1) {
      for (let col = 0; col < environment.cols; col += 1) {
        const wall = environment.grid[row][col] === 1;
        const terrain = environment.terrain_costs[row][col];
        let fill = wall ? COLORS.wall : terrain >= 4 ? COLORS.terrain4 : terrain >= 2 ? COLORS.terrain2 : COLORS.free;
        if (!wall && qRange && qLearning) {
          const index = policyIndex.get(`${row}:${col}:false`);
          if (index !== undefined) {
            const value = Math.max(...qLearning.q_values_final[index]);
            const normalized = (value - qRange.min) / Math.max(0.0001, qRange.max - qRange.min);
            fill = mixColor("#121927", "#164f43", normalized * 0.88);
          }
        }
        context.fillStyle = fill;
        context.fillRect(offsetX + col * cell, offsetY + row * cell, cell + 0.4, cell + 0.4);
        if (cell >= 7) {
          context.strokeStyle = COLORS.grid;
          context.lineWidth = 0.5;
          context.strokeRect(offsetX + col * cell, offsetY + row * cell, cell, cell);
        }
      }
    }

    if (mode === "search" && result) {
      const visible = result.events.slice(0, step);
      const explored = new Set<string>();
      visible.forEach((event) => {
        if (event.state) explored.add(`${event.state[0]}:${event.state[1]}`);
      });
      explored.forEach((key) => {
        const [row, col] = key.split(":").map(Number);
        context.fillStyle = "rgba(109,74,255,.34)";
        context.fillRect(offsetX + col * cell + 1, offsetY + row * cell + 1, cell - 2, cell - 2);
      });
      const current = visible.at(-1)?.state;
      if (current) glowCell(context, current, cell, offsetX, offsetY, COLORS.current);

      const candidatePath = visible.at(-1)?.extra.best?.path;
      const fullyPlayed = step >= result.events.length;
      const path = fullyPlayed ? result.path : candidatePath;
      if (path && path.length > 1) {
        drawPath(context, path, cell, offsetX, offsetY, result.family === "local" ? COLORS.localPath : COLORS.path);
      }
    }

    if (mode === "policy" && qLearning?.policy_path) {
      drawPath(context, qLearning.policy_path, cell, offsetX, offsetY, COLORS.policy);
      if (cell >= 13 && qLearning.policy_actions) {
        qLearning.policy_path.slice(0, -1).forEach((state, index) => {
          if (index % 2 !== 0) return;
          context.fillStyle = "rgba(231,236,247,.72)";
          context.font = `600 ${Math.max(7, cell * 0.38)}px ui-monospace`;
          context.textAlign = "center";
          context.textBaseline = "middle";
          context.fillText(
            { UP: "↑", DOWN: "↓", LEFT: "←", RIGHT: "→" }[qLearning.policy_actions![index]] ?? "",
            offsetX + state[1] * cell + cell / 2,
            offsetY + state[0] * cell + cell / 2,
          );
        });
      }
    }

    marker(context, environment.start, "S", COLORS.start, cell, offsetX, offsetY);
    marker(context, environment.pickup, "P", COLORS.pickup, cell, offsetX, offsetY);
    marker(context, environment.delivery, "D", COLORS.delivery, cell, offsetX, offsetY);
  }, [environment, mode, policyIndex, qLearning, result, step]);

  useEffect(() => draw(), [draw]);
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const observer = new ResizeObserver(draw);
    observer.observe(container);
    return () => observer.disconnect();
  }, [draw]);

  return (
    <div ref={containerRef} className="grid-stage">
      {environment ? <canvas ref={canvasRef} className="block w-full" aria-label="Warehouse grid visualization" /> : null}
      <div className="pointer-events-none absolute left-5 top-5 flex flex-wrap gap-2">
        <Legend color={COLORS.start} label="Start" />
        <Legend color={COLORS.pickup} label="Pickup" />
        <Legend color={COLORS.delivery} label="Delivery" />
        <Legend color={COLORS.terrain4} label="Heavy terrain" />
      </div>
      <div className="pointer-events-none absolute bottom-5 right-5 rounded-full border border-white/10 bg-[#070a12]/75 px-3 py-1.5 font-mono text-[9px] uppercase tracking-[0.16em] text-slate-500 backdrop-blur-xl">
        {environment ? `${environment.rows} × ${environment.cols} / weighted grid` : "Awaiting environment"}
      </div>
    </div>
  );
}

function Legend({ color, label }: { color: string; label: string }) {
  return <span className="legend-chip"><i style={{ backgroundColor: color }} />{label}</span>;
}

function marker(ctx: CanvasRenderingContext2D, position: Cell, label: string, color: string, cell: number, ox: number, oy: number) {
  const [row, col] = position;
  const x = ox + col * cell + cell / 2;
  const y = oy + row * cell + cell / 2;
  ctx.save();
  ctx.shadowColor = color;
  ctx.shadowBlur = Math.max(8, cell * 0.75);
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(x, y, Math.max(4, cell * 0.34), 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
  ctx.fillStyle = "#071018";
  ctx.font = `800 ${Math.max(7, cell * 0.42)}px ui-monospace`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(label, x, y + 0.5);
}

function glowCell(ctx: CanvasRenderingContext2D, state: StateTuple, cell: number, ox: number, oy: number, color: string) {
  ctx.save();
  ctx.shadowColor = color;
  ctx.shadowBlur = Math.max(8, cell);
  ctx.fillStyle = color;
  ctx.globalAlpha = 0.78;
  ctx.fillRect(ox + state[1] * cell + 2, oy + state[0] * cell + 2, cell - 4, cell - 4);
  ctx.restore();
}

function drawPath(ctx: CanvasRenderingContext2D, path: StateTuple[], cell: number, ox: number, oy: number, color: string) {
  ctx.save();
  ctx.strokeStyle = color;
  ctx.shadowColor = color;
  ctx.shadowBlur = Math.max(6, cell * 0.6);
  ctx.lineWidth = Math.max(2, cell * 0.24);
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.beginPath();
  path.forEach((state, index) => {
    const x = ox + state[1] * cell + cell / 2;
    const y = oy + state[0] * cell + cell / 2;
    if (index === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.stroke();
  ctx.restore();
}

function getQRange(values: number[][], environment: { grid: number[][] }, index: Map<string, number>) {
  const candidates: number[] = [];
  environment.grid.forEach((row, r) => row.forEach((cell, c) => {
    const stateIndex = index.get(`${r}:${c}:false`);
    if (cell === 0 && stateIndex !== undefined) candidates.push(Math.max(...values[stateIndex]));
  }));
  return { min: Math.min(...candidates), max: Math.max(...candidates) };
}

function mixColor(from: string, to: string, amount: number) {
  const parse = (color: string) => color.match(/\w\w/g)!.map((value) => Number.parseInt(value, 16));
  const a = parse(from); const b = parse(to);
  return `rgb(${a.map((value, index) => Math.round(value + (b[index] - value) * amount)).join(",")})`;
}

