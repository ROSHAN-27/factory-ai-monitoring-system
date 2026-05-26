import { ErrorState } from "../../shared/ui/ErrorState";
import { useDashboardModel } from "../../features/dashboard/hooks/useDashboardModel";
import { AlertWidget } from "../../widgets/alert-widget/AlertWidget";
import { ViolationWidget } from "../../widgets/violation-widget/ViolationWidget";
import { ModuleHeader } from "../shared/ModuleHeader";

export function AlertsPage() {
  const model = useDashboardModel();

  return (
    <div className="space-y-5 pb-20 lg:pb-0">
      <ModuleHeader
        title="Alert Center"
        description="Prioritized realtime alerts with acknowledgement workflow and escalation context."
        onRefresh={() => void model.query.refetch()}
      />
      {model.query.isError ? <ErrorState message="Alert data is using buffered events because the API request failed." /> : null}
      <div className="grid gap-5 xl:grid-cols-[1.1fr_.9fr]">
        <AlertWidget alerts={model.alerts} />
        <ViolationWidget violations={model.violations} />
      </div>
    </div>
  );
}
