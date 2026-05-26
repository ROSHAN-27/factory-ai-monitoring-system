import type { FactoryMetric } from "../../../shared/types/domain";
import { cn } from "../../../shared/lib/cn";

const toneClass: Record<FactoryMetric["tone"], string> = {
  cyan: "text-signal-cyan",
  green: "text-signal-green",
  amber: "text-signal-amber",
  red: "text-signal-red"
};

export function MetricGrid({ metrics }: { metrics: FactoryMetric[] }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric) => (
        <div key={metric.label} className="rounded-lg border border-white/10 bg-industrial-900/80 p-4 shadow-glow">
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">{metric.label}</p>
          <div className="mt-3 flex items-end justify-between gap-3">
            <span className={cn("text-3xl font-semibold", toneClass[metric.tone])}>{metric.value}</span>
            {metric.delta ? <span className="pb-1 text-xs text-slate-400">{metric.delta}</span> : null}
          </div>
        </div>
      ))}
    </div>
  );
}
