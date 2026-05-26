import { ErrorState } from "../../shared/ui/ErrorState";
import { useDashboardModel } from "../../features/dashboard/hooks/useDashboardModel";
import { ViolationWidget } from "../../widgets/violation-widget/ViolationWidget";
import { AlertWidget } from "../../widgets/alert-widget/AlertWidget";
import { ModuleHeader } from "../shared/ModuleHeader";

export function ViolationsPage() {
  const model = useDashboardModel();

  return (
    <div className="space-y-5 pb-20 lg:pb-0">
      <ModuleHeader
        title="Violations"
        description="Unauthorized access, long absence, early exit, dormitory movement, and repeat offender queues."
        onRefresh={() => void model.query.refetch()}
      />
      {model.query.isError ? <ErrorState message="Violation data is using local derivations until the backend is reachable." /> : null}
      <div className="grid gap-5 xl:grid-cols-[.9fr_1.1fr]">
        <ViolationWidget violations={model.violations} />
        <AlertWidget alerts={model.alerts} />
      </div>
    </div>
  );
}
