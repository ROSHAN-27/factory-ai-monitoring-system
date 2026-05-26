import { cn } from "../lib/cn";
import type { Severity } from "../types/domain";

const severityClass: Record<Severity, string> = {
  low: "border-signal-cyan/30 bg-signal-cyan/10 text-cyan-100",
  medium: "border-signal-amber/30 bg-signal-amber/10 text-amber-100",
  high: "border-signal-red/30 bg-signal-red/10 text-red-100",
  critical: "border-red-400/40 bg-red-500/20 text-red-50"
};

export function StatusBadge({
  children,
  severity = "low",
  className
}: {
  children: React.ReactNode;
  severity?: Severity;
  className?: string;
}) {
  return (
    <span className={cn("inline-flex items-center rounded-md border px-2 py-1 text-xs font-medium", severityClass[severity], className)}>
      {children}
    </span>
  );
}
