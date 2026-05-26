import { ErrorState } from "../../shared/ui/ErrorState";
import { useDashboardModel } from "../../features/dashboard/hooks/useDashboardModel";
import { ReportsWidget } from "../../widgets/reports-widget/ReportsWidget";
import { ComplianceWidget } from "../../widgets/compliance-widget/ComplianceWidget";
import { ModuleHeader } from "../shared/ModuleHeader";

export function ReportsPage() {
  const model = useDashboardModel();

  return (
    <div className="space-y-5 pb-20 lg:pb-0">
      <ModuleHeader
        title="Reports"
        description="Daily, compliance, operator, supervisor, and repeat offender reports for export workflows."
        onRefresh={() => void model.query.refetch()}
      />
      {model.query.isError ? <ErrorState message="Reports are showing the latest buffered analytics until the API recovers." /> : null}
      <div className="grid gap-5 2xl:grid-cols-[.75fr_1.25fr]">
        <ReportsWidget />
        <ComplianceWidget departments={model.departments} trends={model.trends} />
      </div>
    </div>
  );
}
