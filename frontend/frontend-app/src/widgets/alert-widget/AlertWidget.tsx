import { AlertCenter } from "../../features/alerts/components/AlertCenter";
import { WidgetFrame } from "../../shared/layouts/WidgetFrame";
import type { MonitoringAlert } from "../../shared/types/domain";

export function AlertWidget({ alerts }: { alerts: MonitoringAlert[] }) {
  return (
    <WidgetFrame title="Alert Center">
      <AlertCenter alerts={alerts} />
    </WidgetFrame>
  );
}
