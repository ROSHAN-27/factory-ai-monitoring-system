import { ErrorState } from "../../shared/ui/ErrorState";
import { useDashboardModel } from "../../features/dashboard/hooks/useDashboardModel";
import { LiveFeedWidget } from "../../widgets/live-feed-widget/LiveFeedWidget";
import { OperatorTrackingWidget } from "../../widgets/operator-tracking-widget/OperatorTrackingWidget";
import { AlertWidget } from "../../widgets/alert-widget/AlertWidget";
import { ModuleHeader } from "../shared/ModuleHeader";

export function LiveMonitoringPage() {
  const model = useDashboardModel();

  return (
    <div className="space-y-5 pb-20 lg:pb-0">
      <ModuleHeader
        title="Live Monitoring"
        description="Realtime recognition events, operator movement, and active exception signals."
        onRefresh={() => void model.query.refetch()}
      />
      {model.query.isError ? <ErrorState message="Live data API failed. WebSocket/polling buffer will continue to render available events." /> : null}
      <div className="grid gap-5 xl:grid-cols-[1.25fr_.75fr]">
        <LiveFeedWidget events={model.events} />
        <OperatorTrackingWidget events={model.events} />
      </div>
      <AlertWidget alerts={model.alerts} />
    </div>
  );
}
