import { ErrorState } from "../../shared/ui/ErrorState";
import { MetricGrid } from "../../features/dashboard/components/MetricGrid";
import { useDashboardModel } from "../../features/dashboard/hooks/useDashboardModel";
import { ComplianceWidget } from "../../widgets/compliance-widget/ComplianceWidget";
import { OperatorTrackingWidget } from "../../widgets/operator-tracking-widget/OperatorTrackingWidget";
import { ModuleHeader } from "../shared/ModuleHeader";

export function FactoryPage() {
  const model = useDashboardModel();

  return (
    <div className="space-y-5 pb-20 lg:pb-0">
      <ModuleHeader
        title="Factory Overview"
        description="Shift-level operator coverage, department occupancy, compliance, and live movement trends."
        onRefresh={() => void model.query.refetch()}
      />
      {model.query.isError ? <ErrorState message="Factory metrics are using buffered data because the API request failed." /> : null}
      <MetricGrid metrics={model.metrics} />
      <div className="grid gap-5 2xl:grid-cols-[1.25fr_.75fr]">
        <ComplianceWidget departments={model.departments} trends={model.trends} />
        <OperatorTrackingWidget events={model.events} />
      </div>
    </div>
  );
}
