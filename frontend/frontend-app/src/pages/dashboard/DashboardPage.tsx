import { ErrorState } from "../../shared/ui/ErrorState";
import { MetricGrid } from "../../features/dashboard/components/MetricGrid";
import { useDashboardModel } from "../../features/dashboard/hooks/useDashboardModel";
import { LiveFeedWidget } from "../../widgets/live-feed-widget/LiveFeedWidget";
import { AlertWidget } from "../../widgets/alert-widget/AlertWidget";
import { ComplianceWidget } from "../../widgets/compliance-widget/ComplianceWidget";
import { ViolationWidget } from "../../widgets/violation-widget/ViolationWidget";
import { CameraHealthWidget } from "../../widgets/camera-health-widget/CameraHealthWidget";
import { ReportsWidget } from "../../widgets/reports-widget/ReportsWidget";
import { OperatorTrackingWidget } from "../../widgets/operator-tracking-widget/OperatorTrackingWidget";
import { ModuleHeader } from "../shared/ModuleHeader";

export function DashboardPage() {
  const model = useDashboardModel();

  return (
    <div className="space-y-5 pb-20 lg:pb-0">
      <ModuleHeader
        title="Operations Overview"
        description="Live movement, compliance, camera health, and operator exceptions in one operations view."
        onRefresh={() => void model.query.refetch()}
      />

      {model.query.isError ? (
        <ErrorState message="Backend API request failed. The dashboard will continue using any buffered realtime events." />
      ) : null}

      <MetricGrid metrics={model.metrics} />

      <div className="grid gap-5 xl:grid-cols-[1.25fr_.75fr]">
        <LiveFeedWidget events={model.events} />
        <AlertWidget alerts={model.alerts} />
      </div>

      <div className="grid gap-5 2xl:grid-cols-[1.2fr_.8fr]">
        <ComplianceWidget departments={model.departments} trends={model.trends} />
        <ViolationWidget violations={model.violations} />
      </div>

      <div className="grid gap-5 2xl:grid-cols-[1fr_.85fr]">
        <CameraHealthWidget cameras={model.cameras} />
        <OperatorTrackingWidget events={model.events} />
      </div>

      <ReportsWidget />
    </div>
  );
}
