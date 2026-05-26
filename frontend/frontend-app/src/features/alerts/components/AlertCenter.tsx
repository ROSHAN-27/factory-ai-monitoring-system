import { Check } from "lucide-react";
import { useLiveMonitoringStore } from "../../../app/store/liveMonitoringStore";
import { minutesAgo } from "../../../shared/lib/date";
import { StatusBadge } from "../../../shared/ui/StatusBadge";
import { EmptyState } from "../../../shared/ui/EmptyState";
import type { MonitoringAlert } from "../../../shared/types/domain";

export function AlertCenter({ alerts }: { alerts: MonitoringAlert[] }) {
  const acknowledgeAlert = useLiveMonitoringStore((state) => state.acknowledgeAlert);

  if (alerts.length === 0) {
    return <EmptyState title="No active alerts" message="Low-confidence events and violations will be routed here." />;
  }

  return (
    <div className="space-y-2">
      {alerts.slice(0, 6).map((alert) => (
        <div key={alert.id} className="rounded-lg border border-white/8 bg-white/[0.035] p-3">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <p className="text-sm font-medium text-white">{alert.title}</p>
                <StatusBadge severity={alert.severity}>{alert.severity}</StatusBadge>
              </div>
              <p className="mt-1 text-xs text-slate-400">{alert.message}</p>
              <p className="mt-2 text-xs text-slate-600">{minutesAgo(alert.createdAt)}</p>
            </div>
            {alert.status === "open" ? (
              <button
                type="button"
                onClick={() => acknowledgeAlert(alert.id)}
                className="grid h-8 w-8 shrink-0 place-items-center rounded-md border border-white/10 text-slate-300 transition hover:bg-white/8 hover:text-white"
                title="Acknowledge alert"
              >
                <Check className="h-4 w-4" />
              </button>
            ) : null}
          </div>
        </div>
      ))}
    </div>
  );
}
