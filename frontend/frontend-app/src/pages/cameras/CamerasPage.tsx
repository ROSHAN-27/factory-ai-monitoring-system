import { ErrorState } from "../../shared/ui/ErrorState";
import { useDashboardModel } from "../../features/dashboard/hooks/useDashboardModel";
import { CameraHealthWidget } from "../../widgets/camera-health-widget/CameraHealthWidget";
import { LiveFeedWidget } from "../../widgets/live-feed-widget/LiveFeedWidget";
import { ModuleHeader } from "../shared/ModuleHeader";

export function CamerasPage() {
  const model = useDashboardModel();

  return (
    <div className="space-y-5 pb-20 lg:pb-0">
      <ModuleHeader
        title="Camera Health"
        description="Camera status, FPS, stream heartbeat, AI confidence, and recognition feed by source."
        onRefresh={() => void model.query.refetch()}
      />
      {model.query.isError ? <ErrorState message="Camera health is degraded because the API request failed." /> : null}
      <CameraHealthWidget cameras={model.cameras} />
      <LiveFeedWidget events={model.events} />
    </div>
  );
}
