import { StatusBadge } from "../../../shared/ui/StatusBadge";
import type { ViolationSummary } from "../../../shared/types/domain";

export function ViolationDashboard({ violations }: { violations: ViolationSummary[] }) {
  return (
    <div className="grid gap-2">
      {violations.map((violation) => (
        <div key={violation.type} className="flex items-center justify-between gap-3 rounded-lg border border-white/8 bg-white/[0.035] p-3">
          <div>
            <p className="text-sm font-medium text-white">{violation.type}</p>
            <p className="text-xs text-slate-500">Auto-classified by compliance policy</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-lg font-semibold text-white">{violation.count}</span>
            <StatusBadge severity={violation.severity}>{violation.severity}</StatusBadge>
          </div>
        </div>
      ))}
    </div>
  );
}
