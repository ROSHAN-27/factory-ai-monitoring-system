import { ReportsPanel } from "../../features/reports/components/ReportsPanel";
import { WidgetFrame } from "../../shared/layouts/WidgetFrame";

export function ReportsWidget() {
  return (
    <WidgetFrame title="Reports">
      <ReportsPanel />
    </WidgetFrame>
  );
}
