import type { DailyTrendPoint, DepartmentOccupancy } from "../../../shared/types/domain";
import { OperationsBarChart } from "../../../shared/charts/OperationsBarChart";

export function FactoryOverview({
  departments,
  trends
}: {
  departments: DepartmentOccupancy[];
  trends: DailyTrendPoint[];
}) {
  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_1.2fr]">
      <div className="space-y-3">
        {departments.map((department) => (
          <div key={department.department} className="rounded-lg border border-white/8 bg-white/[0.035] p-3">
            <div className="flex items-center justify-between gap-3 text-sm">
              <span className="font-medium text-white">{department.department}</span>
              <span className="text-slate-400">{department.activeOperators} active</span>
            </div>
            <div className="mt-3 h-2 rounded-full bg-white/8">
              <div
                className="h-full rounded-full bg-signal-green"
                style={{ width: `${department.compliance}%` }}
              />
            </div>
            <p className="mt-2 text-xs text-slate-500">{department.compliance}% compliance</p>
          </div>
        ))}
      </div>
      <div className="h-72">
        <OperationsBarChart data={trends} />
      </div>
    </div>
  );
}
